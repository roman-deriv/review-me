import voyageai


async def get_embedding(text: str) -> list[float]:
    vo = voyageai.AsyncClient()
    result = await vo.embed([text], model="voyage-large-2-instruct")
    return result.embeddings[0]


async def get_embeddings(texts: list[str]) -> list[list[float]]:
    vo = voyageai.AsyncClient()
    result = await vo.embed(texts, model="voyage-large-2-instruct")
    return result.embeddings
