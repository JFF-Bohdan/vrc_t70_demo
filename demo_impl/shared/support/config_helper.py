class BaseConfigHelper(object):
    @staticmethod
    def get_database_connection_uri(config, default_value=None):
        return config.get("database", "connection_uri", fallback=default_value)


class DaemonConfigHelper(BaseConfigHelper):
    @staticmethod
    def get_log_level(config, default_value="INFO"):
        return config.get("daemon", "log_level", fallback=default_value)

    @staticmethod
    def get_log_file_name(config, default_value=None):
        return config.get("daemon", "log_file", fallback=default_value)

    @staticmethod
    def get_log_file_rotation(config, default_value="2 Mb"):
        return config.get("daemon", "log_file_rotation", fallback=default_value)

    @staticmethod
    def get_log_file_compression(config, default_value=None):
        return config.get("daemon", "log_file_compression", fallback=default_value)

    @staticmethod
    def get_log_backtrace(config, default_value=False):
        return config.getboolean("daemon", "log_backtrace", fallback=default_value)

    @staticmethod
    def get_log_diagnose(config, default_value=False):
        return config.getboolean("daemon", "log_diagnose", fallback=default_value)

    @staticmethod
    def get_uart_name(config, defaul_value=None):
        return config.get("daemon", "uart_name", fallback=defaul_value)

    @staticmethod
    def get_devices_address(config):
        res = config.get("daemon", "devices", fallback=None)
        if not res:
            return []

        res = [item for item in str(res).strip().split(",") if item]
        return [int(item) for item in res if str(item).isdecimal()]

    @staticmethod
    def get_uart_speed(config, defaul_value=None):
        return config.getint("daemon", "speed", fallback=defaul_value)


class WebAppConfigHelper(BaseConfigHelper):
    @staticmethod
    def get_web_app_host(config, defaul_value="localhost"):
        return config.get("web_ui", "host", fallback=defaul_value)

    @staticmethod
    def get_web_app_port(config, defaul_value=10000):
        return config.getint("web_ui", "port", fallback=defaul_value)

    @staticmethod
    def get_log_level(config, default_value="INFO"):
        return config.get("web_ui", "log_level", fallback=default_value)

    @staticmethod
    def get_log_file_name(config, default_value=None):
        return config.get("web_ui", "log_file", fallback=default_value)

    @staticmethod
    def get_log_file_rotation(config, default_value="2 Mb"):
        return config.get("web_ui", "log_file_rotation", fallback=default_value)

    @staticmethod
    def get_log_file_compression(config, default_value=None):
        return config.get("web_ui", "log_file_compression", fallback=default_value)

    @staticmethod
    def get_log_backtrace(config, default_value=False):
        return config.getboolean("web_ui", "log_backtrace", fallback=default_value)

    @staticmethod
    def get_log_diagnose(config, default_value=False):
        return config.getboolean("web_ui", "log_diagnose", fallback=default_value)
