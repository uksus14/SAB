from scripts.utils import page_size, all_ways, pattern_or
from constants import weather_codes
from geopy.distance import geodesic
from scripts.codes import Code
from datetime import datetime
import requests

class PlaceCode(Code[tuple[float, float]]):
    _list = []
    MAX_DISTANCE_KM = 50
    @classmethod
    def closest(cls, coords: tuple[float, float]) -> tuple[str, tuple[float, float]]|None:
        distance, coords, place = min((geodesic(place.value, coords).km, place.value, place.codes[0]) for place in cls._list)
        if distance > cls.MAX_DISTANCE_KM: return None
        return place, coords

london = PlaceCode((51.522627, -0.049864), "london", "лондон", "mile end", "майл энд")
hatfield = PlaceCode((51.750057, -0.238140), "hatfield", "хатфилд", "herts", "хертс")
korea = PlaceCode((37.564208, 126.97767), "korea", "корея", "seoul", "сеул")
bishkek = PlaceCode((42.852608, 74.613493), "bishkek", "бишкек", "home", "дом")

def bad_weather_hours(data: list[int]) -> tuple[int, int]:
    rain_start, rain_end = -1, -1
    tmp = -1
    for i, code in enumerate(data[1:]):
        if code > 50:
            if rain_start == -1:
                rain_start = i
            elif tmp == -1 and rain_end != -1:
                tmp = i
        elif rain_start != -1:
            if rain_end == -1:
                rain_end = i
            if tmp != -1:
                if i-tmp-abs(15-(i+tmp)/2)/12 > rain_end-rain_start-abs(15-(rain_end+rain_start)/2)/12:
                    rain_start = tmp
                    rain_end = i
                tmp = -1
    if rain_start != -1:
        if rain_end == -1:
            rain_end = 0
        if tmp != -1:
            if 24-tmp-abs(3-tmp/2)/12 > rain_end-rain_start-abs(15-(rain_end+rain_start)/2)/12:
                rain_start = tmp
                rain_end = 24
    return rain_start, rain_end

def approx_coords():
    lat, lon = requests.get("https://ipinfo.io/json").json()["loc"].split(",")
    return float(lat), float(lon)

def weather(call: str, place: str=None, lon: float=None, lat: float=None) -> list[str]:
    if place: coords = PlaceCode.resolve(place)
    elif lon and lat: place, coords = "custom coords", (lon, lat)
    else: place, coords = PlaceCode.closest(approx_coords())
    if coords is None:
        return f"Place {place} not found" if place else "Too far from closest place, try adding using https://www.latlong.net/"
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords[0],
        "longitude": coords[1],
        "current_weather": True,
        "hourly": "weather_code",
        "daily": "apparent_temperature_max,apparent_temperature_min,precipitation_probability_mean,weather_code",
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    data = response.json()
    current = data['current_weather']['temperature']
    days_text = []
    for i in range(page_size()):
        day_max = data['daily']['apparent_temperature_max'][i]
        day_min = data['daily']['apparent_temperature_min'][i]
        day = f"{day_min} °C - {day_max} °C"
        day_weather = data['daily']['weather_code'][i]
        if day_weather > 50:
            rain_start, rain_end = bad_weather_hours(data["hourly"]["weather_code"][i*24:(i+1)*24])
            day_rain_chance = data['daily']['precipitation_probability_mean'][i]
            day += f", {weather_codes.get(day_weather, day_weather)}, rain chance: {day_rain_chance}% from hours {rain_start} to {rain_end}"
        days_text.append(day)
    current_weekday = datetime.now().weekday()
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return [f"Temperature in {place} : {current} °C"]+[f"Temperature range for {weekdays[(current_weekday+i)%7]}: {days_text[i]}" for i in range(len(days_text))]

from scripts.suggestion import Suggest
weather = Suggest(fr"{pattern_or(*all_ways('weather', 'погода', 'temp', 'темп'))}( (?P<place>\p{{L}}+)| (?P<lon>-?\d+\.\d+),? (?P<lat>-?\d+\.\d+))?", weather)

from scripts.testing import Tester
weather_tester = Tester(weather)
weather_tester("weather").claim(True)
weather_tester("temp london").claim(True)
weather_tester("погода корея").claim(True)
weather_tester("темп herts").claim(True)