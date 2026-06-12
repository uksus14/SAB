from scripts.actions import Action
from commons import BASE_FOLDER
import openai

try: openai.api_key = (BASE_FOLDER / "openai_key.txt").read_text().strip()
except FileNotFoundError:
    print("OpenAI key file not found")
    Action.disable["llmask"] = "OpenAI key not found"

def llmask_inner(call: str, query: str) -> list[str]|str:
    prep = "You are a helpful assistant. Respond with a very short factual answer, ideally one phrase or a few words"
    query = query.strip()+"?"
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prep}, {"role": "user", "content": query}],
        temperature=0.1,
        max_tokens=100,
    )
    ans = response.choices[0].message.content
    return ans.strip() if ans is not None else "There was a problem with llm ask"

from scripts.suggestion import Suggest
from scripts.decorators import AccessLimiter
from datetime import timedelta
llmask = Suggest(r"(?P<query>.+)!!\?", llmask_inner, cache=True, limit=AccessLimiter.prep(50, timedelta(days=1), timedelta(microseconds=100)))