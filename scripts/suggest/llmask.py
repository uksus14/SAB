from scripts.actions import Action
from commons import BASE_FOLDER
import openai

try: openai.api_key = (BASE_FOLDER / "openai_key.txt").read_text().strip()
except FileNotFoundError:
    print("OpenAI key file not found")
    Action.disable["llmask"] = "OpenAI key not found"

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