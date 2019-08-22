import sys

from demo_impl.shared.support.config_helper import WebAppConfigHelper
from demo_impl.shared.support.config_support import get_config
from demo_impl.webui import app

from loguru import logger as initial_logger


def init_logger(config):
    initial_logger.remove()

    log_format = "{time:YYYY-MM-DD at HH:mm:ss} {level} {file}:{line} {function}() : {message}"

    initial_logger.add(
        sys.stderr,
        format=log_format,
        level=WebAppConfigHelper.get_log_level(config),
        backtrace=WebAppConfigHelper.get_log_backtrace(config),
        diagnose=WebAppConfigHelper.get_log_diagnose(config)
    )

    log_file_name = WebAppConfigHelper.get_log_file_name(config)
    if log_file_name:
        initial_logger.add(
            log_file_name,
            format=log_format,
            level=WebAppConfigHelper.get_log_level(config),
            rotation=WebAppConfigHelper.get_log_file_rotation(config),
            compression=WebAppConfigHelper.get_log_file_compression(config),
            backtrace=WebAppConfigHelper.get_log_backtrace(config),
            diagnose=WebAppConfigHelper.get_log_diagnose(config)
        )

    return initial_logger


def main():
    config = get_config()

    web_host = WebAppConfigHelper.get_web_app_host(config)
    web_port = WebAppConfigHelper.get_web_app_port(config)
    logger = init_logger(config)

    logger.info(f"web_host: {web_host}")
    logger.info(f"web_port: {web_port}")

    app.run(web_host, web_port)
    return 0


if __name__ == "__main__":
    res = main()

    exit(res)
