import logging
from cezzis_otel.otel_settings import OTelSettings as OTelSettings
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk.trace import TracerProvider as TraceProvider
from typing import Callable

trace_provider: TraceProvider | None
log_provider: LoggerProvider | None

def initialize_otel(settings: OTelSettings, configure_tracing: Callable[[TraceProvider], None] | None = None, configure_logging: Callable[[LoggerProvider], None] | None = None) -> None: ...
def shutdown_otel() -> None: ...
def get_logger(name: str, level: int = ...) -> logging.Logger: ...
