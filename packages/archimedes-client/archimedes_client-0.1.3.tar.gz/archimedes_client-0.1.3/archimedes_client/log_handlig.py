import logging
import sys
import time
import os
from logging.handlers import RotatingFileHandler


LOG_FILE = "automation.log"
MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3

# Mapeia níveis de log para os status esperados pelo Orquestrador
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
      ✅ API do Orquestrador (via api_sender)
    """

    def __init__(self, api_sender, automation_id, job_bot_id, job_schedules_id,
                 save_local_log=True, max_buffer_size=10, max_time_seconds=5):
        self.api_sender = api_sender
        self.automation_id = automation_id
        self.job_bot_id = job_bot_id
        self.job_schedules_id = job_schedules_id
        self.save_local_log = save_local_log

        self._log_buffer = []
        self._last_send_time = 0
        self._max_buffer_size = max_buffer_size
        self._max_time_seconds = max_time_seconds

        self._configure_logger()

    def _configure_logger(self):
        """Configura console + arquivo (se habilitado)."""
        self.logger = logging.getLogger("automation_logger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler do console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler de arquivo (opcional)
        if self.save_local_log:
            file_path = os.path.join(os.getcwd(), LOG_FILE)
            file_handler = RotatingFileHandler(
                file_path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _add_log(self, level, message):
        """Cria e adiciona o log ao buffer + exibe no console/arquivo."""
        level_name = logging.getLevelName(level)
        self.logger.log(level, message)

        status = STATUS_MAP.get(level_name, 'execucao')
        log_entry = {
            'automation_id': self.automation_id,
            'job_bot_id': self.job_bot_id,
            'job_schedules_id': self.job_schedules_id,
            'status': status,
            'info': message,
        }

        self._log_buffer.append(log_entry)

        # Condições para envio automático
        if len(self._log_buffer) >= self._max_buffer_size or \
           (time.time() - self._last_send_time) >= self._max_time_seconds:
            self._flush_logs()

    def _flush_logs(self):
        """Envia todos os logs acumulados à API."""
        if not self._log_buffer or not self.api_sender:
            self._last_send_time = time.time()
            return

        try:
            logs_to_send = self._log_buffer.copy()
            self._log_buffer.clear()

            response = self.api_sender.send_logs(logs_to_send)
            if not response:
                self.logger.warning("⚠️ Falha ao enviar logs para o Orquestrador.")
        except Exception as e:
            self.logger.error(f"Erro no envio de logs: {e}")
        finally:
            self._last_send_time = time.time()

    # ---------- Métodos públicos ----------
    def info(self, message: str): self._add_log(logging.INFO, message)
    def warning(self, message: str): self._add_log(logging.WARNING, message)
    def error(self, message: str): self._add_log(logging.ERROR, message)
    def critical(self, message: str): self._add_log(logging.CRITICAL, message)
    def debug(self, message: str): self._add_log(logging.DEBUG, message)
    def action(self, message: str): self._add_log(logging.INFO, f"[AÇÃO] {message}")