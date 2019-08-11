class ConfigHelper(object):
    @staticmethod
    def get_database_connection_uri(config, default_value=None):
        return config.get("database", "connection_uri", fallback=default_value)

    @staticmethod
    def get_daemon_log_level(config, default_value="INFO"):
        return config.get("daemon", "log_level", fallback=default_value)

    @staticmethod
    def get_daemon_log_file_name(config, default_value=None):
        return config.get("daemon", "log_file", fallback=default_value)

    @staticmethod
    def get_daemon_log_file_rotation(config, default_value="2 Mb"):
        return config.get("daemon", "log_file_rotation", fallback=default_value)

    @staticmethod
    def get_daemon_log_file_compression(config, default_value=None):
        return config.get("daemon", "log_file_compression", fallback=default_value)

    @staticmethod
    def get_daemon_log_backtrace(config, default_value=False):
        return config.getboolean("daemon", "log_backtrace", fallback=default_value)

    @staticmethod
    def get_daemon_log_diagnose(config, default_value=False):
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
