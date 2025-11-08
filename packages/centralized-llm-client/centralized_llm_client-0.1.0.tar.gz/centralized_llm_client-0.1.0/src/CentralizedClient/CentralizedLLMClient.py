import os
import logging
from .gemini_provider import GeminiProvider
from .openrouter_provider import OpenRouterProvider
from .openai_provider import OpenAIProvider
from .llm_logger import LLMCallLogger, CallStatus
from .key_manager import KeyManager
from typing import Any, List

logging.basicConfig(level=logging.INFO)


class CentralizedLLMClient:
    def __init__(self, username: str, gemini_model: str | None = None, openai_model: str | None = None, openrouter_model: str | None = None):

        self.username = username
        self.key_manager = KeyManager()
        self.llm_logger = LLMCallLogger(username=username)
        self.providers = []

        self.default_models = {
            "openai": "gpt-4o",
            "gemini": "gemini-2.5-flash",
            "openrouter": "openai/gpt-oss-20b:free",
        }
        
        self.gemini_model = gemini_model or self.default_models["gemini"]
        self.openai_model = openai_model or self.default_models["openai"]
        self.openrouter_model = openrouter_model or self.default_models["openrouter"]

        # Initialize providers based on user type
        self._initialize_providers()

    def _create_provider(self, company: str, api_key: str):
        """
        Create a provider instance based on the company name.

        Args:
            company (str): The name of the LLM provider company.
            api_key (str): The API key for the provider.

        Returns:
            Provider instance (OpenAIProvider, GeminiProvider, OpenRouterProvider).
        """

        company = company.lower()

        if company == "gemini":
            return GeminiProvider(api_key=api_key, model=self.default_models["gemini"])
        elif company == "openai":
            return OpenAIProvider(api_key=api_key, model=self.default_models["openai"])
        elif company == "openrouter":
            return OpenRouterProvider(
                api_key=api_key, model=self.default_models["openrouter"]
            )
        else:
            raise ValueError(f"This provider is not supported: {company}")

    def _add_provider_to_list(
        self, user_keys: dict, key_type: str, label: str, key_source: str
    ):
        """
        Helper function to add a provider to the providers list.
        Args:
            user_keys (dict): The dictionary of user keys.
            key_type (str): The type of key to add ("default" or "backup").
            label (str): The label for logging purposes.
            key_source (str): The source of the key ("user" or "system").
        Returns:
            bool: True if the provider was added, False otherwise.
        """

        key_info = user_keys.get(key_type)

        if key_info and key_info.get("company") and key_info.get("api_key"):
            try:
                company = key_info["company"]
                api_key = key_info["api_key"]

                provider = self._create_provider(company=company, api_key=api_key)

                self.providers.append(
                    {
                        "provider": provider,
                        "label": label,
                        "company": company,
                        "key_source": key_source,
                    }
                )

                logging.info(f"Added {label} provider: {company}")
                return True

            except ValueError as e:
                logging.error(f"Error adding {label} provider: {e}")
                return False

    def _initialize_providers(self):
        """
        Initialize providers based on user type with appropriate fallback chain.

        Priority user flow:
        1. User's primary provider (user's API key)
        2. User's secondary provider (user's API key)
        3. System primary provider (system API key)
        4. System secondary provider (system API key)

        Non-priority user flow:
        1. User's primary provider (user's API key)
        2. User's secondary provider (user's API key)
        """

        user_type = self.key_manager.get_user_type(self.username)
        logging.info(f"User {self.username} is {user_type} user.")

        user_keys = self.key_manager.get_user_key(self.username)

        # Get user keys and add to providers list
        self._add_provider_to_list(user_keys, "default", "User Primary", "user")
        self._add_provider_to_list(user_keys, "backup", "User Secondary", "user")

        # If priority user
        if user_type == "use_default_keys":

            system_keys = {}

            system_keys["default"] = {
                "company": "gemini",
                "api_key": os.getenv("GEMINI_API_KEY"),
            }
            system_keys["backup"] = {
                "company": "openai",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }

            # add system keys as fallback
            self._add_provider_to_list(
                system_keys, "default", "System Primary", "system"
            )
            self._add_provider_to_list(
                system_keys, "backup", "System Secondary", "system"
            )

            if not self.providers:
                raise ValueError(
                    f"No providers could be initialized for user: {self.username}"
                )

        logging.info(f"Total providers initialized: {len(self.providers)}")

    async def _execute_with_fallback(self, method_name: str, *args, **kwargs) -> Any:
        """
        Execute a method with fallback across providers.
        Args:
            method_name (str): The name of the method to execute on the provider.
            *args: Positional arguments to pass to the method.
            **kwargs: Keyword arguments to pass to the method.
        Returns:
            Any: The result from the first successful provider call.

        Raises:
            Exception: If all providers fail
        """

        error = []

        for i, provider_info in enumerate(self.providers):
            provider = provider_info["provider"]
            label = provider_info["label"]
            company = provider_info["company"]
            key_source = provider_info["key_source"]

            try:
                logging.info(
                    f"Attempting {method_name} with {label} (Provider: {i+1}/{len(self.providers)})"
                )
                method = getattr(provider, method_name)

                # Extract response text and usage
                response_text, response_usage = await method(*args, **kwargs)

                # Get prompt from args
                prompt = args[0] if args else ""

                # Log the successful call
                self.llm_logger.log_call(
                    prompt=prompt,
                    response=response_text,
                    response_usage=response_usage,
                    keys_used=key_source,
                    provider=company,
                    model=provider.model,
                    status=CallStatus.SUCCESS,
                    method_name=method_name,
                    error_msg="",
                )

                logging.info(f"{label} completed successfully.")

                # Return just the response text
                return response_text

            except Exception as e:

                error_msg = f"{label} failed: {e}"
                logging.error(error_msg)
                error.append(error_msg)

                # Log the failed call
                prompt = args[0] if args else ""
                self.llm_logger.log_call(
                    prompt=prompt,
                    response="",
                    response_usage={},
                    keys_used=key_source,
                    provider=company,
                    model=provider.model,
                    status=CallStatus.FAILED,
                    method_name=method_name,
                    error_msg=str(e),
                )

        all_errors = "\n".join(error)
        raise Exception(f"All providers failed for {method_name}:\n{all_errors}")

    async def completion(self, prompt: str, research: bool = False) -> Any:
        """
        Generate a text completion with automatic fallback.
        Args:
            prompt (str): The input prompt for the model.
            research (bool): Whether to use grounding tools.
        Returns:
            Any: The response from the LLM provider.
        """
        return await self._execute_with_fallback("completion", prompt, research)

    async def completion_with_files(self, prompt: str, file_paths: List[str], research: bool = False) -> Any:
        """
        Generate a text completion using provided files with automatic fallback.

        Args:
            prompt (str): The input prompt for the model.
            file_paths (List[str]): List of file paths to attch with the prompt.
            research (bool): Whether to use grounding tools.

        Returns:
            Any: The response from the LLM provider.
        """
        return await self._execute_with_fallback(
            "completion_with_files", prompt, file_paths, research
        )

    async def structured_completion(
        self, prompt: str, file_paths: List[str] | None = None, model: Any = None, research: bool = False
    ) -> Any:
        """
        Generate a strctured text completion with automatic fallback.

        Args:
            prompt (str): The input prompt for the model.
            file_paths (List[str]): List of file paths to attch with the prompt.
            model (Any): The Pydantic model defining the response schema.
            research (bool): Whether to use grounding tools.

        Returns:
            Any: The structured response from the LLM provider.
        """
        return await self._execute_with_fallback(
            "structured_completion", prompt, file_paths, model, research
        )

