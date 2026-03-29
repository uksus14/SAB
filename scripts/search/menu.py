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

object_oriented_programming = URLCode("Object-Oriented Programming", 15546, "proc.webp", "414", "object", "ob", "oop")
fundamentals_of_web_technology = URLCode("Fundamentals of Web Technology", 15501, "proc.webp", "417", "web")
information_system_analysis = URLCode("Information System Analysis", 21025, "proc.webp", "419", "system", "info", "anal")
automata_and_formal_languages = URLCode("Automata and Formal Languages", 15437, "proc.webp", "421", "auto", "automata", "formal")
procedural_programming = URLCode("Procedural Programming", 16154, "proc.webp", "proc", "prog", "procedural")
professional_research_practice = URLCode("Professional and Research Practice", 15555, "proc.webp", "427", "prac", "res", "prof")
computer_systems_and_networks = URLCode("Computer Systems and Networks", 15462, "proc.webp", "net", "comp", "networks", "computer", "system")
logic_and_discrete_structures = URLCode("Logic and Discrete Structures", 15523, "proc.webp", "logic", "discrete", "dis", "struc", "struct")
jhub = URLCode("JHub", "https://hub.comp-teach.qmul.ac.uk/hub/spawn-pending/ec24641", "java.jpg", "jhub", "hub", "jupyter")
youtube = URLCode("Youtube", "https://www.youtube.com", "youtube.png", "youtube", "you", "y")
evisa = URLCode("E-Visa", "https://user-auth.apply-to-visit-or-stay-in-the-uk.homeoffice.gov.uk/auth/realms/AUK/protocol/openid-connect/auth?redirect_uri=https%3A%2F%2Fview-immigration-status.service.gov.uk%2Fstatus%2Feua&response_type=code&scope=openid%20email%20profile&state=0f93596581ac601f880b4baf85ab06f7&client_id=status&nonce=f7732044fbe907daab1deb9435570b24", "evisa.jpg", "evisa", "visa")
grades = URLCode("Grade Guide", "https://www.gradeguide.co.uk/app/degree", "grades.png", "grades", "grade")
iq = URLCode("IQ accommodation", "https://www.iqstudentaccommodation.com/user/dashboard", "IQ.png", "iq", "accom")
address = URLCode("address", "https://www.royalmail.com/find-a-postcode", "royal_mail.png", "address", "get address")
weather = URLCode("Weather", "https://weather.metoffice.gov.uk/forecast/gcpvj0v07", "weather.png", "weather", "w", "погода")
powerpoint = URLCode("Google Slides", "https://docs.google.com/presentation/", "slides.jpg", "ppt", "slides", "powerpoint")
excel = URLCode("Google Sheets", "https://docs.google.com/spreadsheets/", "sheets.png", "excel", "sheets")
word = URLCode("Google Docs", "https://docs.google.com/document/", "docs.png", "word", "docs")
translator = URLCode("Google Translator", "https://translate.google.com/?hl=en&sl=auto&tl=en&op=translate", "translate.webp", "translate", "!t", "translator", "переводчик", "пере")
two_gis = URLCode("2Gis", r"https://2gis.kg/bishkek/directions/points/74.613519%2C42.852692%3B70030076446486931?m=74.613519%2C42.852692%2F16", "2gis.png", "2gis", "2гис")
mysis = URLCode("Queen Mary Mysis", "https://mysis.qmul.ac.uk/", "mysis.webp", "mysis")
menu = URLCode("Menu", "menu", "menu.png", "menu")
test = URLCode("Tests", "test", "menu.png", "test")