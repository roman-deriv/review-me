import anthropic
import logger


async def chat_completion(
        system_prompt: str,
        prompt: str,
        model: str,
):
    logger.log.debug(f"Starting chat completion using {model}")
    client = anthropic.AsyncClient()

    message = await client.messages.create(
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
        ],
    )
    return message.content


async def tool_completion(
        system_prompt: str,
        prompt: str,
        model: str,
        tools: list[dict],
        tool_override: str = "",
):
    client = anthropic.AsyncClient()

    if tool_override == "any":
        tool_choice = {"type": "any"}
    elif tool_override:
        tool_choice = {"type": "tool", "name": tool_override}
    else:
        tool_choice = {"type": "auto"}

    message = await client.messages.create(
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
        ],
        tools=tools,
        tool_choice=tool_choice,
    )
    if message.stop_reason == "tool_use":
        for response in message.content:
            if response.type == "tool_use":
                logger.log.debug(f"Tool completion finished with {response.input}")
                return response.input
    else:
        logger.log.debug(f"Tool completion finished without tool use: {message.content[0].text}")
        return message.content[0].text
