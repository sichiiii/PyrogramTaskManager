import os
import configparser

from typing import Dict, Optional


class Configuration(configparser.RawConfigParser):

    def __init__(self) -> None:
        configparser.RawConfigParser.__init__(self, allow_no_value=True)
        self.path = None  # type: Optional[str]

    def __load_section(self, conf: str) -> None:
        self.read(os.path.join(self.include, conf))

    def get_section(self, section: str) -> Dict[str, str]:
        return dict(self[section])

    def load(self, path: str) -> None:
        self.path = path
        self.read(self.path)
