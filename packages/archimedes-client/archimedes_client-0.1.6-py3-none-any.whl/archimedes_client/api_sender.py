__all__ = ["OrchestratorAPIClient"]
from typing import  Dict, Any, List
import requests
import logging
import time

logger = logging.getLogger(__name__)

class OrchestratorAPIClient:
    """
    Cliente de integração com o Orquestrador Archimedes.

    Responsável por autenticar, consultar e gerenciar tarefas e subtarefas 
    via API REST do orquestrador.
    """
    def __init__(self, archimedes_url, uuid_agent):
        """
        Inicializa a instância do cliente de API.

        Args:
            archimedes_url (str): URL base da API Archimedes (ex: http://127.0.0.1:8000).
            uuid_agent (str): UUID único do agente vinculado à execução do RPA.
        """
        self.archimedes_host = archimedes_url
        self.uuid_agent = uuid_agent
        self.headers = {'Content-Type': 'application/json'}
        self.max_retries = 3
        self.retry_delay_seconds = 5
        self.timeout = 10
    
    def __make_request(self, method, endpoint, data=None):
        url = f"{self.archimedes_host}/api/{endpoint.lstrip('/')}" 

        for attempt in range(self.max_retries):
            try:
                if method == 'GET':
                    response = requests.get(url, headers=self.headers, timeout=self.timeout)
                elif method == 'POST':
                    response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
                elif method == 'PATCH':
                    response = requests.patch(url, headers=self.headers, json=data, timeout=self.timeout)
                elif method == 'PUT': 
                    response = requests.put(url, headers=self.headers, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Método HTTP não suportado: {method}")

                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                logger.error(f"Timeout ao conectar a {url} (Tentativa {attempt + 1}/{self.max_retries})")
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Erro de conexão com {url}: {e} (Tentativa {attempt + 1}/{self.max_retries})")
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro na requisição para {url}: {e} (Tentativa {attempt + 1}/{self.max_retries}). Resposta: {e.response.text if e.response else 'N/A'}")
            except Exception as e:
                logger.error(f"Erro inesperado ao fazer requisição para {url}: {e} (Tentativa {attempt + 1}/{self.max_retries})", exc_info=True)

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay_seconds)

        logger.error(f"Falha em todas as {self.max_retries} tentativas para {url}. Retornando None.")
        return None
    
    def autenticar(self, email, password):
        """
        Autentica o cliente na API do Orquestrador Archimedes.

        Args:
            email (str): E-mail do usuário.
            password (str): Senha do usuário.

        Returns:
            bool: True se autenticado com sucesso, False caso contrário.
        """
        if not email or not password:
            logger.error("Credenciais inválidas: email e senha são obrigatórios.")
            return False
        
        payload = {"email": email, "password": password}
        response = self.__make_request('POST', '/login', payload)
        print("?Chama: ", response)
        if response == None:
            logging.warning('Autenticação falhou..')
            return False
        
        if  response['token']:
            self.token = response['token']
            self.headers["Authorization"] = f"Bearer {self.token}"
            logging.info("Autenticação realizada com sucesso! Token atualizado.")
            return True
        else:
            logging.error(f"Resposta inesperada no login: {response}")

    def retornar_tarefa_run_agente(self):
        """
        Retorna a tarefa atualmente em execução ('executando') para o agente configurado.

        Returns:
            dict | None: Dados da tarefa em execução ou None caso nenhuma esteja ativa.
        """
        response_data = self.__make_request('GET', f"jobs/executando/{self.uuid_agent}")

        if response_data['id']:
            self.current_job_id = response_data['id']

            logger.info(f"Job em execução encontrado: ID {self.current_job_id}")
            return response_data
    
    def criar_sub_tarefa(self, name, id_tarefa, initial_status='executando',  log_output=None):
        """
        Cria uma nova subtarefa vinculada a uma tarefa existente.

        Args:
            name (str): Nome da subtarefa.
            id_tarefa (int): ID da tarefa principal.
            initial_status (str, optional): Status inicial da subtarefa. Default: 'executando'.
            log_output (str, optional): Texto adicional de log inicial.

        Returns:
            int | None: ID da subtarefa criada, ou None em caso de falha.
        """
        if not name:
            logger.error("O nome da subtarefa é obrigatório.")
            return None
        
        if not id_tarefa:
            logger.error("O ID da tarefa precisa ser informado para a criação de uma nova subtarefa.")
            return None
        
        payload = {
            'name': name,
            'status': initial_status,
            'log_output': log_output,
        }

        logger.info(f"Criando subtarefa '{name}' para tarefa ID: {id_tarefa}")
        
        try:
            response = self.__make_request('POST', f"sub-task/jobs/{id_tarefa}", payload)

            subtarefa_id = response['sub_task']['id']
            
            if subtarefa_id:
                logger.info(f"Subtarefa '{name}' criada. ID: {subtarefa_id}")
                return subtarefa_id
            else:
                logger.error(f"Erro ao criar subtarefa '{name}'. Resposta: {response}")
                return None
        except requests.exceptions.RequestException as e:
            error_message = f"Erro de requisição ao criar subtarefa '{name}': {e}. Resposta: {getattr(e.response, 'text', 'N/A')}"
            logger.error(error_message)
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao criar subtarefa '{name}': {e}")
            return None
        
    def atualizar_subtarefa(self, id_subtarefa, status, log_output=None):
        """
        Atualiza o status e/ou log de uma subtarefa existente.

        Args:
            id_subtarefa (int): ID da subtarefa.
            status (str): Novo status.
            log_output (str, optional): Mensagem de log adicional.

        Returns:
            bool: True se atualizado com sucesso, False caso contrário.
        """
        if not status:
            logger.error("O status da subtarefa é obrigatório.")
            return None
        
        if not id_subtarefa:
            logger.error("O ID da subtarefa precisa ser informado para realizar a sua atualização.")
            return None
        
        payload = {
            'status': status,
            'log_output': log_output,
        }

        try:
            logging.info(f"Tentando atualizar subtarefa: {id_subtarefa}; para status: {status};")
            self.__make_request('PUT', f"sub-task/subtasks/{id_subtarefa}", data=payload)
            logging.info(f"Subtarefa: {id_subtarefa}; atualizada para status: {status};")
            return True
        except requests.exceptions.RequestException as e:
            error_message_full = f"Erro de requisição ao atualizar subtarefa: {id_subtarefa}; para status: {status};  {e}. Resposta: {getattr(e.response, 'text', 'N/A')}"
            logging.error(error_message_full)
            return False
        except Exception as e:
            logging.error(f"Erro inesperado ao atualizar subtarefa: {id_subtarefa}: {e}")
            return False
        
    def atualizar_tarefa(self, id_tarefa, status):
        """
        Atualiza o status de uma tarefa existente.

        Args:
            id_tarefa (int): ID da tarefa principal.
            status (str): Novo status da tarefa.

        Returns:
            bool: True se atualizado com sucesso, False caso contrário.
        """
        if not status:
            logger.error("O status da subtarefa é obrigatório.")
            return None
        
        if not id_tarefa:
            logger.error("O ID da tarefa precisa ser informado para realizar a sua atualização.")
            return None
        
        try:
            logging.info(f"Tentando atualizar tarefa: {id_tarefa}; para status: {status}; ")
            self.__make_request('PATCH', f"jobs/{id_tarefa}/{status}")

            logging.info(f"Tarefa {id_tarefa} atualizada para status '{status}'.")
            return True
        except requests.exceptions.RequestException as e:
            error_message_full = f"Erro de requisição ao atualizar Tarefa {id_tarefa} para status '{status}': {e}. Resposta: {getattr(e.response, 'text', 'N/A')}"
            logging.error(error_message_full)
            return False
        except Exception as e:
            logging.error(f"Erro inesperado ao atualizar tarefa {id_tarefa}: {e}")
            return False
        
    def send_logs(self, logs: List[Dict[str, Any]]) -> bool:
        """
        Envia múltiplos logs para o orquestrador.

        Args:
            logs (list[dict]): Lista de logs formatados.

        Returns:
            bool: True se enviados com sucesso, False caso contrário.
        """
        if not logs:
            return False

        for attempt in range(3):
            try:
                response = self.__make_request('POST', 'logs-all', logs)
                if response:
                    logger.info(f"📤 {len(logs)} logs enviados ao Orquestrador.")
                    return True
            except Exception as e:
                logger.warning(f"Tentativa {attempt+1}/3 falhou: {e}")
                time.sleep(2)
            return False