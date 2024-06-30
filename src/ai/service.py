def chat_completion(strategy):
    if strategy == "anthropic":
        from .anthropic import chat_completion
        return chat_completion
    elif strategy == "openai":
        from .openai import chat_completion
        return chat_completion
    else:
        raise ValueError(f"Strategy '{strategy}' is not supported")


def tool_completion(strategy):
    if strategy == "anthropic":
        from .anthropic import tool_completion
        return tool_completion
    elif strategy == "openai":
        raise NotImplementedError("TODO: Implement openai tool completion")
    else:
        raise ValueError(f"Strategy '{strategy}' is not supported")
