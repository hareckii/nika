from sc_kpm import ScModule

from modules.yandex.yandex_disc.agents import (
    YandexDiscInfoAgent,
    YandexPostAuthAgent,
    YandexDiscResourcesAgent   
)


class YandexDiscModule(ScModule):
    def __init__(self):
        super().__init__(
            YandexPostAuthAgent(),
            # YandexDiscInfoAgent(),
            # YandexDiscResourcesAgent()   
        )
