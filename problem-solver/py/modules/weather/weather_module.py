from sc_kpm import ScModule

from .LLMPredprocessingAgent import LLMPredprocessingAgent
from .weather_agent import WeatherAgent


class WeatherModule(ScModule):
    def __init__(self):
        super().__init__(WeatherAgent(), LLMPredprocessingAgent())