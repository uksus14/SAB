from datetime import datetime, timedelta

def approx_time(time: timedelta|datetime) -> str:
    if isinstance(time, datetime): time = datetime.now() - time
    if time.days > 0: return f"{time.days} days"
    if time.seconds >= 3600: return f"{time.seconds//3600} hours"
    if time.seconds >= 60: return f"{time.seconds//60} minutes"
    return f"{time.seconds} seconds"