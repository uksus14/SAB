from scripts.searching import Search
from scripts.utils import ischrome
from flask import render_template

def timer(call: str, min_only: int=0, hour: int=0, min: int=0, sec: int=0, **kwargs):
    return render_template("timer.html", ischrome=ischrome(), total_secs=(hour*60+min+min_only)*60+sec, **kwargs)

timer_regex = r"(?P<timer>timer|таймер)( (?P<min_only>\d+)| (?P<title>.+?))??(?P<words>" + \
    r"( (?P<hour>\d+)( ?h| ?ч| hours?| час(а|ов)?))?" + \
    r"( (?P<min>\d+)( ?m| ?м| min(ute)?s?| мин(ут|ута|уты)?))?" + \
    r"( (?P<sec>\d+)( ?s| ?с| sec(ond)?s?| сек(унд|унда|унды)?))?)"
    
timer = Search(timer_regex, timer)