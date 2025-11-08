import os
import logging
from pathlib import Path


class KeyManager:
    def __init__(self):

        # Get a path to root directory
        self.project_root = Path(__file__).parent.parent.parent

        # Load the encryption key
        self.encryption_key = self._load_encryption_key()

    def _load_encryption_key(self):
        """
        Load the encryption key.
        """
        # Get the key path
        key_file = self.project_root / "key.bin"

        # Check if the key file exists
        if not os.path.exists(key_file):
            raise FileNotFoundError("Encryption key file not found.")

        # Read the key
        with open(key_file, "rb") as f:
            key = f.read()

        return key

    def _decrypt_api_key(self, encrypted_text: str, key: bytes) -> str:
        """
        Decrypt the API key using the encryption key.
        """
        import base64
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        try:
            encrypted_data = base64.b64decode(encrypted_text)
            iv = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]

            cipher = Cipher(
                algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()
            )
            decryptor = cipher.decryptor()

            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext.decode()

        except Exception as e:
            logging.error(f"Failed to decrypt API key: {e}")
            return None

    def fetch_user_keys_from_db(self, username: str):
        """
        Fetch user keys from the mongoDB.

        Args:
            username (str): The username to fetch keys for.

        Returns:
            dict: A dictionary containing the user's API keys.
            example:
            {
                "default": {
                    "company": "company_name",
                    "api_key": "encrypted_api_key"
                },
                "backup": {
                    "company": "company_name",
                    "api_key": "encrypted_api_key"
                }
            }
        """

        from utils.atlas_client import AtlasClient

        mongo_client = AtlasClient()

        # get the user vault
        user_vault = mongo_client.find("quAPIVault", {"username": username})

        if not user_vault:
            raise ValueError(f"No API keys found for user: {username}")

        user_keys = {}

        # process the default and backup keys
        for entry in user_vault:
            company = entry.get("company").lower()
            encrypted_key = entry.get("key")
            key_type = entry.get("key_type")

            user_keys[key_type] = {"company": company, "api_key": encrypted_key}

        return user_keys

    def get_user_key(self, username: str):
        """
        Process the decryption of user keys.

        Args:
            username (str): The username to fetch and decrypt keys for.

        Returns:
            dict: A dictionary containing the user's decrypted API keys.
            example:
            {
                "default": {
                    "company": "company_name",
                    "api_key": "decrypted_api_key"
                },
                "backup": {
                    "company": "company_name",
                    "api_key": "decrypted_api_key"
                }
            }
        """
        try:

            # Fetch user keys from the database
            user_keys = self.fetch_user_keys_from_db(username)

            decrypted_keys = {}
            for key_type, key_info in user_keys.items():
                encrypted_api_key = key_info["api_key"]
                decrypted_api_key = self._decrypt_api_key(
                    encrypted_api_key, self.encryption_key
                )
                decrypted_keys[key_type] = {
                    "company": key_info["company"],
                    "api_key": decrypted_api_key,
                }

            return decrypted_keys

        except Exception as e:
            logging.error(f"Could not retrieve user keys: {e}")
            return None

    def get_user_type(self, username: str) -> str:
        """
        Get the user type from the database.

        Args:
            username (str): The username to fetch the user type for.

        Returns:
            str: The user type (e.g., "use_user_key", "use_default_key").
        """
        from utils.atlas_client import AtlasClient

        mongo_client = AtlasClient()

        user = mongo_client.find("qucreate_users", {"username": username})

        if not user:
            logging.error(f"User not found: {username}")
            return None

        user_doc = user[0]

        user_type = user_doc.get("llm_call_type", "use_default_keys")

        return user_type
