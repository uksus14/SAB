import openai

def llmask(call: str, query: str) -> list[str]:
    prep = "You are a helpful assistant. Respond with a very short factual answer, ideally one phrase or a few words"
    query = query.strip()+"?"
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prep}, {"role": "user", "content": query}],
        temperature=0.1,
        max_tokens=100,
    )
    return response.choices[0].message.content.strip()

from scripts.suggestion import Suggest
llmask = Suggest(r"(?P<query>.+)!!\?", llmask, cache=True, limit=True)