import re

from app_logger import get_logger
from datetime import datetime


class TimeMesParser:
    def __init__(self):
        self.logger = get_logger(__name__)

    def parse_time_message(self, message_text: str):
        try:
            if re.match(r'^(2[0-3]|[01]?\d):([0-5]?\d)$', message_text): # TODO: make regex grouping
                now = datetime.now()
                current_time = datetime.strptime(now.strftime('%H:%M:%S'), '%H:%M:%S').time()
                message_time_obj = datetime.strptime(message_text, '%H:%M').time()
                current_hours, current_minutes = int(str(current_time)[:-6]), int(str(current_time)[3:-3])
                future_hours,  future_minutes = int(str(message_time_obj)[:-6]), int(str(message_time_obj)[3:-3])
                if message_time_obj > current_time:
                    return (future_hours - current_hours) * 3600 + (future_minutes - current_minutes) * 60
                else:
                    return (24 - current_hours + future_hours) * 3600 + (60 - current_minutes + future_minutes) * 60
            else:
                try:
                    buffer = float(message_text) * 3600
                    return float(message_text)
                except ValueError:
                    return None
        except Exception as ex:
            self.logger.error(str(ex))
            return None
