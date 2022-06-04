import re
import time

from app_logger import get_logger
from datetime import date, datetime


class TimeMesParser:
    def __init__(self):
        self.logger = get_logger(__name__)

    def parse_time_message(self, message_text: str):
        try:
            if re.match(r'^(2[0-3]|[01]?\d):([0-5]?\d)$', message_text):
                now = datetime.now()
                current_time = datetime.strptime(now.strftime('%H:%M:%S'), '%H:%M:%S').time()
                message_time_obj = datetime.strptime(message_text, '%H:%M').time()
                if message_time_obj > current_time:  # eto pizdec
                    return (int(str(message_time_obj)[:-6]) - int(str(current_time)[:-6])) * 3600 + \
                           ((int(str(message_time_obj)[3:-3]) - int(str(current_time)[3:-3])) * 60)
                else:
                    return (24 - int(str(current_time)[:-6]) + int(str(message_time_obj)[:-6])) * 3600 + (60 - (
                                 - int(str(current_time)[3:-3]) + int(str(message_time_obj)[3:-3])) * 60)
            else:
                try:
                    buffer = float(message_text) * 3600
                    return float(message_text)
                except ValueError:
                    return None
        except Exception as ex:
            self.logger.error(str(ex))
            return None


if __name__ == '__main__':
    tmp = TimeMesParser()
    print(tmp.parse_time_message('01:42'))
