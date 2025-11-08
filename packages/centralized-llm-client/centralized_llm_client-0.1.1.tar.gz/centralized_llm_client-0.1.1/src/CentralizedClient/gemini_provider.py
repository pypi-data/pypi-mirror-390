import logging
from google import genai
from google.genai import types
from typing import Any, Dict
from .file_processor import FileProcessor


class GeminiProvider:
    def __init__(self, api_key, model):

        self.model = model
        self.gemini_client = genai.Client(api_key=api_key)
        self.file_processor = FileProcessor()

    def _enable_research(self):
        """
        Enable research tools if specified.

        Returns:
            types.GenerateContentConfig: The configuration with research tools enabled.
        """
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )

        return config

    def extract_usage(self, response: Any) -> Dict[str, int]:
        """
        Extract the usage from response.

        Args:
            response (Any): The response object from Gemini.

        Returns:
            Dict[str, int]: A dictionary containing 'input_tokens', 'output_tokens' and 'total_tokens'.
        """
        usage_metadata = response.usage_metadata

        try:
            extracted_usage = {
                "input_tokens": usage_metadata.prompt_token_count,
                "output_tokens": usage_metadata.candidates_token_count,
                "total_tokens": usage_metadata.total_token_count,
            }

            return extracted_usage

        except AttributeError:
            logging.warning("Usage metadata not found in the response.")
            return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    def extract_response_text(self, response: Any) -> str:
        """
        Extract the text content from the response.
        Args:
            response (Any): The response object from Gemini.
        Returns:
            str: The extracted text content.
        """
        return response.text

    async def upload_files_to_gemini(self, file_paths):
        """
        Upload the files to Gemini and return the file ID.

        Args:
            file_path (str): procssed file paths to the file to be uploaded.

        Returns:
            str: The uploaded file ID.
        """
        # Preprocess files in temp directory
        processed_file_paths, unique_id = await self.file_processor.process_file(
            provider="gemini", files=file_paths
        )

        uploaded_files = []

        # Upload each file to Gemini
        for file in processed_file_paths:
            upload_file = self.gemini_client.files.upload(file=file)
            uploaded_files.append(upload_file)

        logging.info(f"Uploaded {len(uploaded_files)} files to Gemini.")

        # clean up the local files at extracted id
        self.file_processor.cleanup_temp_dir("gemini", unique_id)
        logging.info(f"[local] Cleaned up temporary files at ID: {unique_id}")

        return uploaded_files

    async def completion(self, prompt, research = False):
        """
        Generate a text completion using the Gemini model.

        Args:
            prompt (str): The input prompt for the model.
            research (bool): Whether to use grounding tools.

        Returns:
            dict: The response from the Gemini model.
        """
        kwargs = {
            "model": self.model,
            "contents": prompt,
        }

        # Research tool for grounding
        if research:
            config = self._enable_research()
            kwargs["config"] = config

        response = self.gemini_client.models.generate_content(**kwargs)

        # Extract usage info
        response_usage = self.extract_usage(response)

        # Extract response text
        response_text = self.extract_response_text(response)

        return response_text, response_usage

    async def completion_with_files(self, prompt, file_paths, research = False):
        """
        Generate a text completion using the Gemini model with file inputs.
        Args:
            prompt (str): The input prompt for the model.
            file_paths (list): List of file paths to include in the prompt.
            research (bool): Whether to use grounding tools.

        Returns:
            dict: The response from the Gemini model.
        """
        # Upload files and get their IDs
        files = await self.upload_files_to_gemini(file_paths)

        kwargs = {
            "model": self.model,
            "contents": [prompt, files],
        }

        # Research tool for grounding
        if research:
            config = self._enable_research()
            kwargs["config"] = config

        # Generate completion with files attched
        response = self.gemini_client.models.generate_content(**kwargs)

        # ones the response is received, clean up the uploaded files from Gemini
        for file in files:
            self.gemini_client.files.delete(name=file.name)

        logging.info(f"Deleted uploaded files: {len(files)}")

        # Extract usage info
        response_usage = self.extract_usage(response)

        # Extract response text
        response_text = self.extract_response_text(response)

        return response_text, response_usage

    async def structured_completion(self, prompt, file_paths: list | None = None, model = None, research = False):
        """
        Generate a structured completion using the Gemini model.
        Args:
            prompt (str): The input prompt for the model.
            file_paths (list): List of file paths to include in the prompt.
            model (dict): The Pydantic model defining the response schema.
            research (bool): Whether to use grounding tools. (Not supported for structured completions)

        Returns:
            dict: The JSON structured response from the Gemini model.
        """

        if research:
            logging.warning("Research tools are not supported for structured completions in Gemini.")

        # Only upload files if they are provided
        contents = [prompt]
        files = []
        if file_paths:
            files = await self.upload_files_to_gemini(file_paths)
            contents.extend(files)

        response = self.gemini_client.models.generate_content(
            model=self.model,
            contents=contents,
            config={
                "response_mime_type": "application/json",
                "response_schema": model,
            },
        )

        # Clean up uploaded files if any were uploaded
        if file_paths and files:
            for file in files:
                self.gemini_client.files.delete(name=file.name)
            logging.info(f"Deleted uploaded files: {len(files)}")

        # Extract usage info
        response_usage = self.extract_usage(response)

        # Extract response text
        response_text = self.extract_response_text(response)

        return response_text, response_usage
