from typing import Self

russian = "ё\"№;%:?йцукенгшщзхъфывапролджэячсмитьбю"
english = "`@#$%^&qwertyuiop[]asdfghjkl;'zxcvbnm,."
ru_en = {r: e for r, e in zip(russian, english)}
en_ru = {e: r for e, r in zip(english, russian)}
def translit(text: str, d: dict[str, str]):
    ans = ""
    prev = ""
    for l in text.lower():
        if l in d and prev != '!':
            ans+=d[l]
        else: ans+=l
        prev = l
    return ans
def all_ways(text: str) -> list[str]:
    return [text, translit(text, en_ru), translit(text, ru_en)]
def is_same_keys(text: str, codes: list[str]):
    text = text.lower().strip()
    for way in [text, translit(text, en_ru), translit(text, ru_en)]:
        if way in codes: return way
    return False

class Code:
    all: dict[type, list[Self]] = {}
    def __init__(self, value, *codes: str):
        self.value = value
        self.codes = codes
        if type(self) not in self.all:
            self.all[type(self)] = []
        self.all[type(self)].append(self)
    def main(self):
        return self.value
    @classmethod
    def resolve(cls, query: str):
        for code in cls.all[cls]:
            if is_same_keys(query, code.codes):
                return code.main()
        return None
    
class URLCode(Code):
    def __init__(self, name: str, url: str|int, img: str, *codes: str):
        self.name = name
        if isinstance(url, int) or url.isdigit():
            url = f"https://qmplus.qmul.ac.uk/course/view.php?id={url}"
        elif "/" not in url: url = f"http://127.0.0.1:5000/{url}"
        self.url = url
        self.img = img if "/" in img else f"http://127.0.0.1:5000/static/{img}"
        self.codes = codes
        super().__init__(url, *codes)
    @classmethod
    def menu_data(cls) -> list[tuple[str, str, str]]:
        return [(code.name, code.url, code.img) for code in cls.all[cls]]

class CurrencyCode(Code): pass

URLCode("Online Exams", 27089, "exam.jpg", "exam", "exams")
URLCode("Mathematics B", 26196, "math.jpg", "math")
URLCode("Science and Engineering Success", 24587, "succ.jpg", "succ", "success")
URLCode("Foundations of Chemical Science", 24589, "chem.png", "chem", "chemistry")
URLCode("Foundations of Physics", 24591, "phys.jpg", "phys", "physics")
URLCode("Foundations of Engineering", 24595, "engin.jpg", "eng", "engin", "engineer", "engineering")
URLCode("Further Mathematics", 24583, "furth.jpg", "furth", "further")
URLCode("Youtube", "https://www.youtube.com", "youtube.png", "youtube", "you", "y")
URLCode("Grade Guide", "https://www.gradeguide.co.uk/app/degree", "grades.png", "grades", "grade")
URLCode("Weather", "https://weather.metoffice.gov.uk/forecast/gcpvj0v07", "weather.png", "weather", "w", "погода")
URLCode("Google Slides", "https://docs.google.com/presentation/", "slides.jpg", "ppt", "slides", "powerpoint")
URLCode("Google Sheets", "https://docs.google.com/spreadsheets/", "sheets.png", "excel", "sheets")
URLCode("Google Docs", "https://docs.google.com/document/", "docs.png", "word", "docs")
URLCode("Google Translator", "https://translate.google.com/?hl=en&sl=auto&tl=en&op=translate", "translate.webp", "translate", "!t", "translator", "переводчик", "пере")
URLCode("Queen Mary Mysis", "https://mysis.qmul.ac.uk/", "mysis.webp", "mysis")
URLCode("Menu", "menu", "menu.png", "menu")



CurrencyCode("usd", "us", "dollar", "dol", "d", "доллар", "долларов", "доллара", "доллару", "долларах", "дол", "д")
CurrencyCode("rub", "ru", "ruble", "r", "рубль", "рублей", "рублях", "рублям", "рубля", "рублю", "руб", "р")
CurrencyCode("kgs", "kg", "som", "k", "s", "сом", "сомам", "сомах", "сома", "сомов", "с")
CurrencyCode("gbp", "gb", "pound", "pnd", "p", "фунт", "фунтам", "фунтах", "фунта", "фунтов", "ф")
CurrencyCode("eur", "er", "euro", "eu", "e", "евро", "е")