from googletrans import Translator
import asyncio
translator = Translator()

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

russian = "йцукенгшщзхъфывапролджэячсмитьбю"
english = "qwertyuiopasdfghjklzxcvbnm"

def translate(call: str, query: str) -> list[str]:
    query = query.rstrip("-").strip()
    langs = ['en', 'ru']
    is_ru = next((letter for letter in query.lower() if letter in russian+english), ' ') in russian
    promise = translator.translate(query, src=langs[is_ru], dest=langs[not is_ru])
    return loop.run_until_complete(promise).text

from scripts.suggestion import Suggest
from datetime import timedelta
translate = Suggest(r"(?P<query>.+) (!t|пере(вод)?)", translate, cache=timedelta(minutes=5))

from scripts.testing import Tester
translate_tester = Tester(translate)
translate_tester("conscience !t").claim("совесть")
translate_tester("клептомания пере").claim("kleptomania")   