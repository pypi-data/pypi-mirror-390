import requests
import json
import base64
import logging
from pathlib import Path
from typing import Any, Dict
from .file_processor import FileProcessor


class OpenRouterProvider:
    def __init__(self, api_key, model):

        self.model = model
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.file_processor = FileProcessor()

    def _make_request(self, messages, plugins=None, schema=None):
        """
        Make a request to the OpenRouter API.

        Args:
            messages (list): List of message dictionaries for the chat completion.
            plugins (list, optional): List of plugin configurations.
            schema (dict, optional): The response schema for structured completions.

        Returns:
            dict: The response from the OpenRouter API.
        """

        request_data = {"model": self.model, "messages": messages}

        # Add plugins if provided
        if plugins:
            request_data["plugins"] = plugins

        # Add schema if provided
        if schema:
            request_data["response_format"] = schema

        response = requests.post(
            url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(request_data),
        )

        response.raise_for_status()
        return response.json()

    async def upload_files_to_openrouter(self, file_paths):
        """
        Process files and convert them to data URLs for OpenRouter.

        Args:
            file_paths (list): List of file paths to be process.

        Returns:
            list: List of data URLs for the files.
        """
        # Preprocess files in temp directory
        processed_file_paths, unique_id = await self.file_processor.process_file(
            provider="openrouter", files=file_paths
        )

        files_data = []

        # Convert each file to data URL with file name
        for original_path, processed_path in zip(file_paths, processed_file_paths):
            # Get the filename - handle both UploadFile objects and string paths
            if hasattr(original_path, "filename"):
                # It's an UploadFile object
                filename = original_path.filename
            else:
                # It's a string path
                filename = Path(original_path).name

            with open(processed_path, "rb") as f:
                file_data = base64.b64encode(f.read()).decode("utf-8")
                files_data.append(
                    {
                        "filename": filename,
                        "data_url": f"data:application/pdf;base64,{file_data}",
                    }
                )

        logging.info(f"Processed {len(files_data)} files for OpenRouter.")

        # Clean up the local files at extracted id
        self.file_processor.cleanup_temp_dir("openrouter", unique_id)
        logging.info(f"[local] Cleaned up temporary files at ID: {unique_id}")

        return files_data

    def extract_usage(self, response: Any) -> Dict[str, int]:
        """
        Extract the usage from response.

        Args:
            response (Any): The response object from OpenRouter.

        Returns:
            Dict[str, int]: A dictionary containing 'input_tokens', 'output_tokens' and 'total_tokens'.
        """
        usage_metadata = response.get("usage", {})

        try:
            extracted_usage = {
                "input_tokens": usage_metadata.get("prompt_tokens", 0),
                "output_tokens": usage_metadata.get("completion_tokens", 0),
                "total_tokens": usage_metadata.get("total_tokens", 0),
            }

            return extracted_usage

        except AttributeError:
            logging.warning("Usage metadata not found in the response.")
            return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    def extract_response_text(self, response: Any) -> str:
        """
        Extract the text content from the response.
        Args:
            response (Any): The response object from OpenRouter.
        Returns:
            str: The extracted text content.
        """
        return response["choices"][0]["message"]["content"]

    async def completion(self, prompt, research: bool = False):
        """
        Generate a text completion using the OpenRouter model.
        Args:
            prompt (str): The input prompt for the model.
            research (bool): Whether to use grounding tools. (Not Supported yet)
        Returns:
            dict: The response from the OpenRouter model.
        """
        messages = [{"role": "user", "content": prompt}]

        if research:
            logging.warning("Research mode is not supported in OpenRouterProvider.")

        response = self._make_request(messages)

        # Extract usage info
        response_usage = self.extract_usage(response)

        # Extract response text
        response_text = self.extract_response_text(response)

        return response_text, response_usage

    async def completion_with_files(self, prompt, file_paths, research: bool = False):
        """
        Generate a text completion using the OpenRouter model with file inputs.

        Args:
            prompt (str): The input prompt for the model.
            file_paths (list): List of file paths to include in the prompt.
            research (bool): Whether to use grounding tools. (Not Supported yet)

        Returns:
            dict: The response from the OpenRouter model.
        """

        # Upload files and get their data URLs
        files = await self.upload_files_to_openrouter(file_paths)

        # Build content list with all files
        content = []

        # Add the text prompt
        content.append(
            {
                "type": "text",
                "text": prompt,
            }
        )

        # Add all files to content at end
        for file in files:
            content.append(
                {
                    "type": "file",
                    "file": {
                        "filename": file["filename"],
                        "file_data": file["data_url"],
                    },
                }
            )

        messages = [{"role": "user", "content": content}]

        plugins = [
            {
                "id": "file-parser",
                "pdf": {"engine": "pdf-text"},
            },
        ]

        if research:
            logging.warning("Research mode is not supported in OpenRouterProvider.")

        # Generate completion with files attched
        response = self._make_request(messages, plugins=plugins)

        # Extract usage info
        response_usage = self.extract_usage(response)

        # Extract response text
        response_text = self.extract_response_text(response)

        return response_text, response_usage

    async def structured_completion(self, prompt, file_paths, model, research: bool = False):
        """
        Generate a structured completion using the OpenRouter model.
        Args:
            prompt (str): The input prompt for the model.
            file_paths (list): List of file paths to attch with the prompt.
            model (dict): The Pydantic model defining the response schema.
            research (bool): Whether to use grounding tools. (Not Supported yet)

        Returns:
            dict: The JSON structured response from the OpenRouter model.
        """

        # Build content list with all files
        content = []

        # Add the text prompt
        content.append(
            {
                "type": "text",
                "text": prompt,
            }
        )

        # Only upload and add files if they are provided
        if file_paths:
            # Upload files and get their data URLs
            files = await self.upload_files_to_openrouter(file_paths)
            
            # Add all files to content at end
            for file in files:
                content.append(
                    {
                        "type": "file",
                        "file": {
                            "filename": file["filename"],
                            "file_data": file["data_url"],
                        },
                    }
                )

        messages = [{"role": "user", "content": content}]

        plugins = [
            {
                "id": "file-parser",
                "pdf": {"engine": "pdf-text"},
            },
        ]

        if research:
            logging.warning("Research mode is not supported in OpenRouterProvider.")

        schema = model.model_json_schema()

        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema.get("title", "response"),
                "strict": True,
                "schema": schema,
            },
        }

        response = self._make_request(messages, plugins=plugins, schema=response_format)

        # Extract usage info
        response_usage = self.extract_usage(response)

        # Extract response text
        response_text = self.extract_response_text(response)

        return response_text, response_usage
