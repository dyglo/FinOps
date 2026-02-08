import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from finops_api.config import get_settings


def configure_logging() -> None:
    settings = get_settings()

    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s '
        '%(trace_id)s %(method)s %(path)s %(status_code)s %(response_time_ms)s'
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())
