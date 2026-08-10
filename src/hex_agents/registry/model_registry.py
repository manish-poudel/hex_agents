from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI


class ModelRegistry:

    @staticmethod
    def create(model_config: dict):

        provider = model_config["provider"]

        if provider == "ollama":

            return ChatOllama(
                model=model_config["name"],
                temperature=0,
            )

        if provider == "google":

            print("Creating Google Generative AI model with config:", model_config)
            return ChatGoogleGenerativeAI(
                model=model_config["name"],
                google_api_key=model_config["google_api_key"],
            )

        raise ValueError(
            f"Unknown provider: {provider}"
        )