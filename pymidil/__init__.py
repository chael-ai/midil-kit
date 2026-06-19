from pymidil.cli.main import cli
from pymidil.version import __service_version__, __version__
from pymidil.logger.setup import setup_logger
from pymidil.settings import LoggerSettings


__all__ = ["cli", "__service_version__", "__version__"]

logger_settings = LoggerSettings().logger
print(logger_settings)
setup_logger(
    level=logger_settings.log_level,
    enable_http_logging=logger_settings.enable_http_logging,
)
