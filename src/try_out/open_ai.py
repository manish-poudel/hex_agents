
    
from langchain_openai import ChatOpenAI


def run_test():
    
    model = ChatOpenAI(
                model="gpt-5.6-luna",
                api_key = "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"
            )
    messages = [
        (
            "system",
            "You are a helpful translator. Translate the user sentence to French.",
        ),
        ("human", "I love programming."),
    ]

    response = model.invoke(messages)

    print("CONTENT:")
    print(response.content)

    print("\nUSAGE METADATA:")
    print(response.usage_metadata)

    print("\nRESPONSE METADATA:")
    print(response.response_metadata)


if __name__ == "__main__":
    run_test()