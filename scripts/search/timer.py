from scripts.utils import ischrome
from flask import render_template
import regex

def timer(call: str, min_only: int=0, hour: int=0, min: int=0, sec: int=0, **kwargs):
    return render_template("timer.html", ischrome=ischrome(), total_secs=(hour*60+min+min_only)*60+sec, **kwargs)

timer_regex = r"(?P<timer>timer|таймер)( (?P<min_only>\d+)| (?P<title>.+?))??(?P<words>" + \
    r"( (?P<hour>\d+)( ?h| ?ч| hours?| час(а|ов)?))?" + \
    r"( (?P<min>\d+)( ?m| ?м| min(ute)?s?| мин(ут|ута|уты)?))?" + \
    r"( (?P<sec>\d+)( ?s| ?с| sec(ond)?s?| сек(унд|унда|унды)?))?)"

from scripts.searching import Search
timer = Search(timer_regex, timer)

def claim_timer(seconds: int):
    def claim(html: str):
        html = html.partition("<script")[2].partition("</script>")[0]
        re = r"let totalSeconds *= *(?P<seconds>\d+)"
        return seconds == int(regex.search(re, html).group("seconds"))
    claim.__doc__ = f"""checking if total_seconds in timer is {seconds}"""
    return claim
        
from scripts.testing import Tester
timer_tester = Tester(timer, claim_timer)
timer_tester("asdfasdf").claim(None)
timer_tester("timer ").claim(0)
timer_tester("timer 14").claim(14*60)
timer_tester("timer 2h 4 min 14 seconds").claim(2*3600+4*60+14)
