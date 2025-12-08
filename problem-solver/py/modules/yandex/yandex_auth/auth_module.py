from sc_kpm import ScModule

from modules.yandex.yandex_auth.agents import (
    CheckYandexTokenAgent,
    CreateYandexAuthorAgent,
    YandexCreateTokensAgent,
)


class YandexAuthModule(ScModule):
    def __init__(self):
        super().__init__(
            CheckYandexTokenAgent(),
            CreateYandexAuthorAgent(),
            YandexCreateTokensAgent(),
        )
