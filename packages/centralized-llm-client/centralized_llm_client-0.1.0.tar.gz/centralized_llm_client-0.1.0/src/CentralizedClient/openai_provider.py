import logging
from typing import Any, Dict
from openai import OpenAI
from .file_processor import FileProcessor


class OpenAIProvider:
    def __init__(self, api_key, model):

        self.model = model
        self.openai_client = OpenAI(api_key=api_key)
        self.file_processor = FileProcessor()

    def _enable_research(self):
        """
        Enable research tools for grounding.

        Returns:
            List[Dict[str, str]]: List of tools to be used for grounding.
        """
        
        tools = [{"type": "web_search"}]
        
        return tools
    
    def extract_usage(self, response: Any) -> Dict[str, int]:
        """
        Extract the usage from response.

        Args:
            response (Any): The response object from OpenAI.

        Returns:
            Dict[str, int]: A dictionary containing 'input_tokens', 'output_tokens' and 'total_tokens'.
        """
        usage_metadata = response.usage

        try:
            extracted_usage = {
                "input_tokens": usage_metadata.input_tokens,
                "output_tokens": usage_metadata.output_tokens,
                "total_tokens": usage_metadata.total_tokens,
            }

            return extracted_usage

        except AttributeError:
            logging.warning("Usage metadata not found in the response.")
            return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    def extract_response_text(self, response: Any) -> str:
        """
        Extract the text content from the response.
        Args:
            response (Any): The response object from OpenAI.
        Returns:
            str: The extracted text content.
        """
        return response.output_text

    async def upload_files_to_openai(self, file_paths):
        """
        Upload the files to OpenAI and return the file ID.

        Args:
            file_path (str): procssed file paths to the file to be uploaded.

        Returns:
            str: The uploaded file ID.
        """
        # Preprocess files in temp directory
        processed_file_paths, unique_id = await self.file_processor.process_file(
            provider="openai", files=file_paths
        )

        uploaded_files = []

        # Upload each file to OpenAI
        for file in processed_file_paths:
            upload_file = self.openai_client.files.create(
                file=open(file, "rb"), purpose="user_data"
            )
            uploaded_files.append(upload_file.id)

        logging.info(f"Uploaded {len(uploaded_files)} files to OpenAI.")

        # clean up the local files at extracted id
        self.file_processor.cleanup_temp_dir("openai", unique_id)
        logging.info(f"[local] Cleaned up temporary files at ID: {unique_id}")

        return uploaded_files

    async def completion(self, prompt, research=False):
        """
        Generate a text completion using the OpenAI model.

        Args:
            prompt (str): The input prompt for the model.
            research (bool): Whether to use grounding tools.

        Returns:
            dict: The response from the OpenAI model.
        """

        kwargs = {
            "model": self.model,
            "input": prompt,
        }


        if research:
            tools = self._enable_research()
            kwargs["tools"] = tools

        response = self.openai_client.responses.create(**kwargs)       

        # Extract usage info
        response_usage = self.extract_usage(response)

        # Extract response text
        response_text = self.extract_response_text(response)

        return response_text, response_usage

    async def completion_with_files(self, prompt, file_paths, research=False):
        """
        Generate a text completion using the OpenAI model with file inputs.
        Args:
            prompt (str): The input prompt for the model.
            file_paths (list): List of file paths (Only Suppoerts PDFs) to include in the prompt.
            research (bool): Whether to use grounding tools.

        Returns:
            dict: The response from the OpenAI model.
        """
        # Upload files and get their IDs
        files = await self.upload_files_to_openai(file_paths)

        # Build content list with all files
        content = []

        # Add all files to content
        for file in files:
            content.append(
                {
                    "type": "input_file",
                    "file_id": file,
                }
            )

        # Add the text prompt at the end
        content.append(
            {
                "type": "input_text",
                "text": prompt,
            }
        )

        kwargs = {
            "model": self.model,
            "input": [{"role": "user", "content": content}]
        }

        if research:
            kwargs["tools"] = self._enable_research()

        # Generate completion with files attached
        response = self.openai_client.responses.create(**kwargs)

        # ones the response is received, clean up the uploaded files from Gemini
        for file in files:
            self.openai_client.files.delete(file_id=file)

        logging.info(f"Deleted uploaded files: {len(files)}")

        # Extract usage info
        response_usage = self.extract_usage(response)

        # Extract response text
        response_text = self.extract_response_text(response)

        return response_text, response_usage

    async def structured_completion(self, prompt, file_paths, model, research=False):
        """
        Generate a structured completion using the OpenAI model.
        Args:
            prompt (str): The input prompt for the model.
            file_paths (list): List of file paths to attch with the prompt.
            model (dict): The Pydantic model defining the response schema.
            research (bool): Whether to use grounding tools.

        Returns:
            dict: The JSON structured response from the OpenAI model.
        """

        # Build content list with all files
        content = []

        # Only upload and add files if they are provided
        if file_paths:
            # Upload files and get their IDs
            files = await self.upload_files_to_openai(file_paths)
            
            # Add all files to content
            for file in files:
                content.append(
                    {
                        "type": "input_file",
                        "file_id": file,
                    }
                )

        # Add the text prompt at the end
        content.append(
            {
                "type": "input_text",
                "text": prompt,
            }
        )

        kwargs = {
            "model": self.model,
            "input": [{"role": "user", "content": content}],
            "text_format": model,
        }

        if research:
            kwargs["tools"] = self._enable_research()

        response = self.openai_client.responses.parse(**kwargs)

        # Extract usage info
        response_usage = self.extract_usage(response)

        # Extract response text
        response_text = self.extract_response_text(response)

        return response_text, response_usage
