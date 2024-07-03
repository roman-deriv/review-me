import anthropic
import logging


logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('review-me.log'), logging.StreamHandler()])

logger = logging.getLogger(__name__)


def chat_completion(
        system_prompt: str,
        prompt: str,
        model: str,
):
    logger.debug("chat_completion start")
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
        ],
    )
    logger.debug("chat_completion finish")
    return message.content


def tool_completion(
        system_prompt: str,
        prompt: str,
        model: str,
        tools: list[dict],
        tool_override: str = "",
):
    logger.debug("tool_completion start")
    client = anthropic.Anthropic()

    if tool_override == "any":
        tool_choice = {"type": "any"}
    elif tool_override:
        tool_choice = {"type": "tool", "name": tool_override}
    else:
        tool_choice = {"type": "auto"}

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
        ],
        tools=tools,
        tool_choice=tool_choice,
    )
    if message.stop_reason == "tool_use":
        for response in message.content:
            if response.type == "tool_use":
                logger.debug("tool_completion finish tool use")
                return response.input
    else:
        logger.debug("tool_completion finish else")
        return message.content[0].text
