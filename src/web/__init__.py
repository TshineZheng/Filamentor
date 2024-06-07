# Define the filter
import logging


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and record.args[2] != "/api/sys/sync"

# Add filter to the logger
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())