import openai


def chat_completion(
        system_prompt: str,
        prompt: str,
        model: str,
):
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1_000,
    )
    return response.choices[0].message.content.strip()
