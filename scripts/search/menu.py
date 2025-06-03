from scripts.codes import Code
from commons import BASE_URL

class URLCode(Code):
    _list = []
    def __init__(self, name: str, url: str|int, img: str, *codes: str):
        self.name = name
        if isinstance(url, int): url = f"https://qmplus.qmul.ac.uk/course/view.php?id={url}"
        elif "/" not in url: url = f"{BASE_URL}/{url}"
        self.img = img if "/" in img else f"{BASE_URL}/static/{img}"
        super().__init__(url, *codes)
    @classmethod
    def menu_data(cls) -> list[tuple[str, str, str]]:
        return [(code.name, code.value, code.img) for code in cls.iter()]

def url_code(call: str) -> str|None: return URLCode.resolve(call)

from scripts.searching import Search
Search(r".+", url_code)

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