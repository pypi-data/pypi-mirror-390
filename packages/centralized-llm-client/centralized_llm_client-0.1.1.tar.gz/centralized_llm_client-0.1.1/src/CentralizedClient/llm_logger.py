from enum import Enum
import datetime


class CallStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"


class LLMCallLogger:
    def __init__(self, username: str):

        self.username = username

    def _save_log(self, log_entry: dict):
        """
        Save the log entry to the database.
        Args:
            log_entry (dict): The log entry to be saved.
        """
        from .utils.atlas_client import AtlasClient

        mongo_client = AtlasClient()

        mongo_client.insert("llm_logs", log_entry)

    def log_call(
        self,
        prompt: str,
        response: str,
        response_usage: dict,
        keys_used: str,
        provider: str,
        model: str,
        status: CallStatus,
        method_name: str,
        error_msg: str,
    ):
        """
        Log an LLM call.
        Args:
            prompt (str): The input prompt for the LLM.
            response (str): The response from the LLM.
            response_usage (dict): Usage details from the LLM call.
            keys_used (str): The keys used for the LLM call.
            provider (str): The name of the LLM provider.
            model (str): The model used for the LLM call.
            status (CallStatus): The status of the LLM call (SUCCESS or FAILURE).
            method_name (str): The method used for the LLM call.
            error_msg (str): Error message if the call failed.
        """
        log_entry = {
            "username": self.username,
            "timestamp": datetime.datetime.utcnow(),
            "prompt": prompt,
            "response": response,
            "response_usage": response_usage,
            "keys_used": keys_used,
            "provider": provider,
            "model": model,
            "status": status.value,
            "method_name": method_name,
            "error_msg": error_msg,
        }

        # save log entry to database
        self._save_log(log_entry)
