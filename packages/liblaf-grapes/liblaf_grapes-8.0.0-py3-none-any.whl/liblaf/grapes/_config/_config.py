from liblaf.grapes.conf import BaseConfig

from ._joblib import ConfigJoblib
from ._logging import ConfigLogging
from ._pretty import ConfigPretty
from ._traceback import ConfigTraceback


class Config(BaseConfig):
    joblib: ConfigJoblib
    logging: ConfigLogging
    pretty: ConfigPretty
    traceback: ConfigTraceback


config: Config = Config()
