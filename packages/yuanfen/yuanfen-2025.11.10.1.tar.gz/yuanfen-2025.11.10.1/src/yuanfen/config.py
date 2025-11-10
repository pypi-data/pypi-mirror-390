import configparser
import json
import os
from typing import Any

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from .logger import Logger


class Config:
    instances = {}

    def __init__(self, path, poll=True, logger=None):
        # 只在新实例创建时初始化
        if not hasattr(self, "_initialized"):
            self.file_path: str = os.path.abspath(path)
            self.logger: Logger = logger or Logger()
            self.data: dict = {}
            self.load()
            self.observer = PollingObserver() if poll else Observer()
            self.observer.schedule(ConfigChangeHandler(self), path=self.file_path, recursive=False)
            self.observer.start()
            self._initialized = True

    def __new__(cls, path, poll=True, logger=None):
        if path not in cls.instances:
            instance = super().__new__(cls)
            cls.instances[path] = instance
            return instance
        else:
            return cls.instances[path]

    def __getitem__(self, key: str) -> Any:
        """获取配置项,如果键不存在则抛出 KeyError"""
        if key not in self.data:
            raise KeyError(f"Configuration key '{key}' not found")
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def load(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            if self.file_path.endswith(".json"):
                self.data = json.load(f)
            elif self.file_path.endswith(".yaml") or self.file_path.endswith(".yml"):
                self.data = yaml.safe_load(f)
            elif self.file_path.endswith(".ini"):
                parser = configparser.ConfigParser()
                parser.read_file(f)
                for section in parser.sections():
                    self.data[section] = {}
                    for key, value in parser.items(section):
                        self.data[section][key] = value
            else:
                raise ValueError("Unsupported config file format")


class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config

    def on_modified(self, event):
        self.config.logger.info(f"{self.config.file_path} modified")
        self.config.load()

    def on_created(self, event):
        self.config.logger.info(f"{self.config.file_path} created")
        self.config.load()
