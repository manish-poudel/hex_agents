from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI



class ModelRegistry:

    def __init__(self, provider_configs: dict[str, dict]):
        self.provider_configs = provider_configs
        self._instances: dict[str, BaseChatModel] = {}

    def get_model(
        self,
        provider: str,
        model_name: str,
    ) -> BaseChatModel:

        key = f"{provider}:{model_name}"

        if key in self._instances:
            return self._instances[key]

        config = self.provider_configs.get(provider)

        if config is None:
            raise ValueError(f"Unknown model provider: {provider}")

        model = self._create_model(
            provider=provider,
            model_name=model_name,
            config=config,
        )

        self._instances[key] = model

        return model

    def _create_model(
        self,
        provider: str,
        model_name: str,
        config: dict,
    ) -> BaseChatModel:

        if provider == "ollama":
            return ChatOllama(
                model=model_name,
                **config,
            )

        if provider == "google":
            return ChatGoogleGenerativeAI(
                model=model_name,
                **config,
            )
        # if provider == "openai":

        #     return ChatOpenAI(
        #         model=model_name,
        #         **config,
        #     )

        raise ValueError(f"Unknown model provider: {provider}")
