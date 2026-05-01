import sys
import traceback
from datetime import datetime
from contextvars import ContextVar

log_file = ContextVar("log_file", default="log.txt")

def handle_exception(exc_type, exc_value, exc_traceback):
    """Captures unhandled exceptions and writes them to log.txt"""
    # Don't log keyboard interrupts (Ctrl+C)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    with open(log_file.get(), "a") as f:
        f.write(f"\n--- CRASH REPORT: {datetime.now()} ---\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

def enable_traceback(file):
    # This replaces the default 'quit and print to console' behavior
    log_file.set(file)
    sys.excepthook = handle_exception