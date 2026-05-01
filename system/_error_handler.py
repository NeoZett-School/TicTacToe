# This module captures unhandled exceptions and writes them to a log file instead of printing them to the console.
# In normal cases, both stdout and stderr are redirected to log.txt, so unhandled exceptions would be logged there anyway. 
# However, in some cases (like when running as a Windows service or when stdout/stderr are not properly redirected), 
# unhandled exceptions might not be captured. This module ensures that all unhandled exceptions are 
# logged to log.txt regardless of the environment. You may regard this as a failsafe.

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