"""
Advanced Logging System mit strukturierter Ausgabe und Correlation-ID.
"""

from __future__ import annotations

import contextvars
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys
import uuid
from typing import Optional

import colorama
from colorama import Fore, Style

colorama.init()

_correlation_id = contextvars.ContextVar("correlation_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", _correlation_id.get()),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


class CorrelationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = _correlation_id.get()
        return True


class BlackOpsLogger:
    def __init__(self, name: str = "BlackOps", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        for handler in list(self.logger.handlers):
            handler.close()
        self.logger.handlers = []
        self.logger.filters = []
        self.logger.addFilter(CorrelationFilter())

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())

        text_file = self.log_dir / f"blackops_{datetime.now().strftime('%Y%m%d')}.log"
        text_handler = logging.FileHandler(text_file)
        text_handler.setLevel(logging.DEBUG)
        text_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s")
        )

        json_file = self.log_dir / f"blackops_{datetime.now().strftime('%Y%m%d')}.jsonl"
        json_handler = logging.FileHandler(json_file)
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(JsonFormatter())

        self.logger.addHandler(console_handler)
        self.logger.addHandler(text_handler)
        self.logger.addHandler(json_handler)

        self.audit_logger = self._setup_audit_logger()

    def _setup_audit_logger(self) -> logging.Logger:
        audit_logger = logging.getLogger(f"{self.name}.audit")
        audit_logger.setLevel(logging.INFO)
        audit_logger.propagate = False
        for handler in list(audit_logger.handlers):
            handler.close()
        audit_logger.handlers = []
        audit_logger.filters = []
        audit_logger.addFilter(CorrelationFilter())

        audit_dir = self.log_dir / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_file = audit_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        audit_handler = logging.FileHandler(audit_file)
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(correlation_id)s - %(user)s - %(action)s - %(target)s - %(status)s")
        )
        audit_logger.addHandler(audit_handler)
        return audit_logger

    def set_correlation_id(self, correlation_id: Optional[str] = None) -> str:
        value = correlation_id or str(uuid.uuid4())
        _correlation_id.set(value)
        return value

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def audit(self, user: str, action: str, target: str, status: str = "SUCCESS") -> None:
        extra = {"user": user, "action": action, "target": target, "status": status}
        self.audit_logger.info("", extra=extra)

    def print_banner(self) -> None:
        banner = f"""
{Fore.RED}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      ██████╗ ██╗      █████╗  ██████╗██╗  ██╗██████╗ ███████╗║
║      ██╔══██╗██║     ██╔══██╗██╔════╝██║  ██║██╔══██╗██╔════╝║
║      ██████╔╝██║     ███████║██║     ███████║██████╔╝███████╗║
║      ██╔══██╗██║     ██╔══██║██║     ██╔══██║██╔═══╝ ╚════██║║
║      ██████╔╝███████╗██║  ██║╚██████╗██║  ██║██║     ███████║║
║      ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚══════╝║
║                                                              ║
║                   FRAMEWORK v2.2                             ║
║              FOR ETHICAL SECURITY RESEARCH                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(banner)


class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: Fore.CYAN + "[DEBUG] %(message)s" + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + "[INFO] %(message)s" + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + "[WARNING] %(message)s" + Style.RESET_ALL,
        logging.ERROR: Fore.RED + "[ERROR] %(message)s" + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + "[CRITICAL] %(message)s" + Style.RESET_ALL,
    }

    def format(self, record):
        formatter = logging.Formatter(self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO]))
        return formatter.format(record)
