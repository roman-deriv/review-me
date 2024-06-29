import anthropic


def chat_completion(
        system_prompt: str,
        prompt: str,
        model: str,
):
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ]
            }
        ]
    )
    return message.content
