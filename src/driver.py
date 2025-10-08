
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from injector import inject, singleton
from src.settings import Settings

@singleton
class Driver:
    @inject
    def __init__(self, setting: Settings):
        self.driver = None
        self.url = setting.url
        # 启动驱动
        self._setup_driver()
        self._load_game()
    
    def __del__(self):
        if self.driver: self.driver.quit()

    def _setup_driver(self) -> None:
        serv = Service(executable_path="msedgedriver.exe")
        self.driver = webdriver.Edge(service=serv)
        self.driver.maximize_window()
        
    def _load_game(self) -> None:
        self.driver.get(self.url)