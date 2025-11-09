from reboot.controller.application_config import (
    ApplicationConfig,
    LocalApplicationConfig,
    application_config_spec_from_routables,
)
from rebootdev.aio.servicers import Serviceable
from rebootdev.aio.types import ApplicationId
from typing import Optional


class LocalConfigExtractor:

    def __init__(self, application_id: ApplicationId):
        self._application_id = application_id

    def config_from_serviceables(
        self,
        serviceables: list[Serviceable],
        servers: Optional[int],
    ) -> ApplicationConfig:
        spec = application_config_spec_from_routables(
            routables=serviceables,
            servers=servers,
        )
        return LocalApplicationConfig(
            application_id=self._application_id,
            spec=spec,
        )
