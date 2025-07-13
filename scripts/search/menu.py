from scripts.codes import Code
from commons import BASE_URL

class URLCode(Code[str]):
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
url_code = Search(r".+", url_code)

from scripts.testing import Tester
code_tester = Tester(url_code)
code_tester("asdfasdf").claim(None)
code_tester("furth").claim("https://qmplus.qmul.ac.uk/course/view.php?id=24583")
code_tester("youtube").claim("https://www.youtube.com")
code_tester("погода").claim("https://weather.metoffice.gov.uk/forecast/gcpvj0v07")
code_tester("menu").claim(f"{BASE_URL}/menu")
code_tester("ьутг").claim(f"{BASE_URL}/menu")

further_math = URLCode("Further Mathematics", 24583, "furth.jpg", "furth", "further")
youtube = URLCode("Youtube", "https://www.youtube.com", "youtube.png", "youtube", "you", "y")
grades = URLCode("Grade Guide", "https://www.gradeguide.co.uk/app/degree", "grades.png", "grades", "grade")
weather = URLCode("Weather", "https://weather.metoffice.gov.uk/forecast/gcpvj0v07", "weather.png", "weather", "w", "погода")
powerpoint = URLCode("Google Slides", "https://docs.google.com/presentation/", "slides.jpg", "ppt", "slides", "powerpoint")
excel = URLCode("Google Sheets", "https://docs.google.com/spreadsheets/", "sheets.png", "excel", "sheets")
word = URLCode("Google Docs", "https://docs.google.com/document/", "docs.png", "word", "docs")
translator = URLCode("Google Translator", "https://translate.google.com/?hl=en&sl=auto&tl=en&op=translate", "translate.webp", "translate", "!t", "translator", "переводчик", "пере")
two_gis = URLCode("2Gis", r"https://2gis.kg/bishkek/directions/points/74.613519%2C42.852692%3B70030076446486931?m=74.613519%2C42.852692%2F16", "", "2gis", "2гис")
mysis = URLCode("Queen Mary Mysis", "https://mysis.qmul.ac.uk/", "mysis.webp", "mysis")
menu = URLCode("Menu", "menu", "menu.png", "menu")
test = URLCode("Tests", "test", "menu.png", "test")