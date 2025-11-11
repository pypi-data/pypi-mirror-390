import logging
import sys
import os
import time
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Any
from .api_sender import OrchestratorAPIClient 

LOG_FILE = "automation.log"
MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3

STATUS_MAP = {
    'INFO': 'execucao',
    'WARNING': 'alerta',
    'ERROR': 'falha',
    'CRITICAL': 'erro_critico',
    'DEBUG': 'debug',
    'ACTION': 'acao'
}


class AutomationLogger:
    """
    Logger customizado para automações.
    Envia logs para:
      ✅ Console
      ✅ Arquivo local (opcional)
      ✅ API do Orquestrador (via ApiSender)
    """

    def __init__(
        self,
        api_sender: OrchestratorAPIClient,
        automation_id: int,
        job_bot_id: int,
        job_schedules_id: int,
        save_local_log=True,
        max_buffer_size=10,
        max_time_seconds=5
    ):
        self.api_sender = api_sender
        self.automation_id = automation_id
        self.job_bot_id = job_bot_id
        self.job_schedules_id = job_schedules_id
        self.save_local_log = save_local_log

        self._log_buffer: List[Dict[str, Any]] = []
        self._last_send_time = 0
        self._max_buffer_size = max_buffer_size
        self._max_time_seconds = max_time_seconds

        self._configure_logger()

    def _configure_logger(self):
        """Configura console + arquivo (opcional)."""
        self.logger = logging.getLogger("automation_logger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if self.save_local_log:
            file_handler = RotatingFileHandler(
                os.path.join(os.getcwd(), LOG_FILE),
                maxBytes=MAX_BYTES,
                backupCount=BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _add_log(self, level, message):
        """Adiciona log no buffer + printa no console."""
        self.logger.log(level, message)
        level_name = logging.getLevelName(level)

        log_entry = {
            "automation_id": self.automation_id,
            "job_bot_id": self.job_bot_id,
            "job_schedules_id": self.job_schedules_id,
            "status": STATUS_MAP.get(level_name, "execucao"),
            "info": message
        }

        self._log_buffer.append(log_entry)

        if len(self._log_buffer) >= self._max_buffer_size or \
           (time.time() - self._last_send_time) >= self._max_time_seconds:
            self._flush_logs()

    def _flush_logs(self):
        """Envia logs acumulados para o orquestrador."""
        if not self._log_buffer:
            self._last_send_time = time.time()
            return

        try:
            logs_to_send = self._log_buffer.copy()
            self._log_buffer.clear()
            self.api_sender.send_logs(logs_to_send)
        except Exception as e:
            self.logger.error(f"Erro ao enviar logs: {e}")
        finally:
            self._last_send_time = time.time()

    def info(self, msg): self._add_log(logging.INFO, msg)
    def warning(self, msg): self._add_log(logging.WARNING, msg)
    def error(self, msg): self._add_log(logging.ERROR, msg)
    def critical(self, msg): self._add_log(logging.CRITICAL, msg)
    def debug(self, msg): self._add_log(logging.DEBUG, msg)
    def action(self, msg): self._add_log(logging.INFO, f"[AÇÃO] {msg}")
