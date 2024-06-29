def chat_completion(strategy):
    if strategy == "anthropic":
        from .anthropic import chat_completion
        return chat_completion
    elif strategy == "openai":
        from .openai import chat_completion
        return chat_completion
    else:
        raise ValueError(f"Strategy '{strategy}' is not supported")
