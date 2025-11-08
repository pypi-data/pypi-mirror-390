import base64
import logging
from pathlib import Path
from typing import List
from starlette.datastructures import UploadFile


class FileProcessor:
    def __init__(self):

        # Get a path to root directory
        self.project_root = Path(__file__).parent.parent.parent

    def _create_unique_id(self):
        """
        Create a unique identifier.
        """
        import datetime
        from bson import ObjectId

        curr_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        obj_id = str(ObjectId())[:8]

        id = f"{curr_time}_{obj_id}"
        return id

    def get_id_from_path(self, provider: str, path: Path) -> List[str]:
        """
        Extract the unique identifier from a given path.
        Args:
            provider (str): The name of the provider (e.g., 'gemini', 'openai', 'openrouter').
            path (Path): The full path to extract the ID from.

        Returns:
            id (str): The extracted unique identifier.
        """
        temp_dir = self.project_root / "temp_files" / provider
        id = str(path).replace(str(temp_dir), "").strip("/").split("/")[0]
        return id

    def create_temp_dir(self, provider: str):
        """
        Create a temporary directory for file processing.

        Args:
            provider (str): The name of the provider (e.g., 'gemini', 'openai', 'openrouter').

        Returns:
            provider_dir (Path): created temporary directory.
        """

        temp_dir = self.project_root / "temp_files"
        temp_dir.mkdir(parents=True, exist_ok=True)

        id = self._create_unique_id()

        provider_dir = temp_dir / provider / id
        provider_dir.mkdir(parents=True, exist_ok=True)

        return provider_dir

    def cleanup_temp_dir(self, provider: str, id: str):
        """
        Cleanup temporary directories.

        Args:
            provider (str): The name of the provider (e.g., 'gemini', 'openai', 'openrouter').
            id (str): The unique identifier for the temporary directory.

        Returns:
            bool: True if the directory was deleted, False otherwise.
        """
        import shutil

        temp_dir = self.project_root / "temp_files" / provider / id

        if temp_dir.exists() and temp_dir.is_dir():
            shutil.rmtree(temp_dir)
            return True

        return False

    def extract_s3_key(self, s3_url: str) -> str:
        """
        Extracts the S3 key from a full S3 URL.

        Args:
            s3_url (str): The S3 Links

        Returns:
            key (str): The s3 key
        """
        from urllib.parse import urlparse

        parsed = urlparse(s3_url)
        # Remove leading slash if present
        key = parsed.path.lstrip("/")
        return key

    async def process_file(self, provider: str, files: List[str | UploadFile]):
        """
        Prepare file for llm calls. Automatically detects the type of input.
        Args:
            provider (str): The name of the provider (e.g., 'gemini', 'openai', 'openrouter').
            files (List[str | UploadFile]): List of file paths (local or S3 URLs) or UploadFile objects.

        Returns:
            local_paths (List[str]): List of local file paths ready for processing.
            unique_id (str): The unique identifier for the temporary directory.
        """
        import shutil
        from utils.s3_file_manager import S3FileManager

        # create temp dir
        temp_dir = self.create_temp_dir(provider)

        # Extract the ID from the created temp_dir path
        unique_id = self.get_id_from_path(provider, temp_dir)

        try:

            localPaths = []

            for file in files:
                # Check if it's an UploadFile object
                if isinstance(file, UploadFile):
                    dest = temp_dir / file.filename
                    with dest.open("wb") as buffer:
                        content = await file.read()
                        buffer.write(content)
                    localPaths.append(str(dest))

                # Check if it's a string (file path or S3 URL)
                elif isinstance(file, str):
                    # Check if it's an S3 URL
                    if file.startswith("https://") and "s3" in file:
                        s3 = S3FileManager()
                        key = self.extract_s3_key(file)
                        filename = Path(key).name
                        dest = temp_dir / filename
                        s3.download_file(key, dest)
                        localPaths.append(str(dest))

                    # It's a local file path
                    else:
                        src = Path(file)
                        dest = temp_dir / src.name
                        if src.exists():
                            shutil.copy(src, dest)
                            localPaths.append(str(dest))

            return localPaths, unique_id

        except Exception as e:
            # Cleanup in case of error
            self.cleanup_temp_dir(provider, unique_id)
            logging.error(f"Error processing files: {e}")
            raise e

    def encode_pdf_to_base64(self, file_path):
        """
        Encode a PDF file to a base64 string.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            str: The base64 encoded string of the PDF file.
        """

        with open(file_path, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read()).decode("utf-8")

        return encoded_string
