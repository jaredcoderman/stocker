from datetime import datetime, time
import pytz


def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

timezone = pytz.timezone('America/New_York')  # replace with the actual timezone

def is_weekday():
    # Get the current day of the week (Monday is 0, Sunday is 6)
    return datetime.now(timezone).weekday() < 5

def is_working_hours():
    # Get the current time in the specified timezone
    current_time = datetime.now(timezone).time()

    # Check if the current time is between 9:30 am and 4:00 pm
    return time(9, 30) <= current_time <= time(16, 0)