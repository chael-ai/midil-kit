from pymidil.cli.main import cli
from pymidil.version import __service_version__, __version__
from pymidil.logger.configure import setup_logger
from pymidil.settings import LoggerSettings
from pymidil.exceptions import MidilError


__all__ = ["cli", "__service_version__", "__version__", "MidilError"]

logger_settings = LoggerSettings().logger
setup_logger(
    level=logger_settings.log_level,
    enable_http_logging=logger_settings.enable_http_logging,
)
