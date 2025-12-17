from sc_kpm import ScModule
from .WeatherAgent import WeatherAgent
from .LLMPredprocessingAgent import LLMPredprocessingAgent

class WeatherModule(ScModule):
    def __init__(self):
        super().__init__(WeatherAgent(), LLMPredprocessingAgent())