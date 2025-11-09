import logging


class ProductionFormatter(logging.Formatter):
    default_time_format = "%Y-%m-%d %H:%M:%S %z"
    default_fmt = "[%(asctime)s] [%(process)d] [%(levelname)s] %(name)s %(message)s [User: %(requestuser)s]"

    def __init__(self, fmt=None, **kwargs):
        if not fmt:
            fmt = self.default_fmt
        super().__init__(fmt, **kwargs)

    def format(self, record):
        try:
            user = record.request.user
            record.requestuser = user
        except Exception:
            record.requestuser = "-"

        return super().format(record)
