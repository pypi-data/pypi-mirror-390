# Utilizar o padrÃ£o x.x.x.xxxx para caso precise subir versÃ£o de testes para o respositorio test-pypi
# Utilizar o padrÃ£o x.x.x para subir em produÃ§Ã£o
__version__ = '4.6.5'

import logging
import os
from datetime import datetime
from typing import Tuple
import requests

import src
from src.api import oking
import src.api.okinghub as api_okinghub
import sys
from src.entities.log import Log
from src.interface_grafica import exibir_janela_shortname
from src.jobs.utils import setup_logger
from src.layout import layout_shortname, layout_token
from src.imports import install_package_database
import re

global is_connected_oracle_client, client_data, start_time, shortname_interface, token_interface, conexao, \
    token_param, token_total, createDatabase, nome_token, job_console
nome_token = ''
createDatabase = False
shortname_interface = ''
token_interface = ''
token_total = ''
client_not_exists = True
exibir_interface_grafica = True
token_param = ''
job_console = ''
conexao = False
print_payloads: bool = False
jobs_qtd = 0

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s] %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S')
logger = logging.getLogger()


# -- Ver Primeira linha deste arquivo
version = __version__  # <-- Nova forma de obter a versÃ£o


def print_version():
    print(version)
    exit()


def get_token_from_params(args: list) -> Tuple[str, bool]:
    global usrMaster, pwdMaster, exibir_interface_grafica

    if len(args) >= 2:
        if args.__contains__('-p') or args.__contains__('--payload'):
            global print_payloads
            print_payloads = True

        # Modo de Console
        if args.__contains__('--console'):
            exibir_interface_grafica = False
            global job_console, token_param
            if len(args) >= 3:
                token_element = ("".join([i for i in args if '-t=' in i]))
                job_element = ("".join([i for i in args if '-j=' in i]))
                if token_element:
                    token_param = args[args.index(token_element)].replace("-t=", "")
                if job_element:
                    job_console = args[args.index(job_element)].replace("-j=", "")

        if args.__contains__('--a'):
            setup_logger(src.job_console)

        # Modo de CriaÃ§Ã£o de Banco de Dados
        if args.__contains__('--database'):
            exibir_interface_grafica = False
            src.createDatabase = True
            # Se [database] entÃ£o precisa da UsuÃ¡rio e Senha [MASTER]
            if len(args) < 5:
                logger.error('======================= MODO DATABASE ========================')
                logger.error('=== Necessita dos parÃ¢metros de UsuÃ¡rio e Senha master     ===')
                logger.error(' uso: oking [token] [--database] [usuarioMaster] [senhaMaster]')
                logger.error(' ')
                logger.error('--------------------------------------------------------------')
                exit(1)
            # Seta UsuÃ¡rio e Senha Master
            usrMaster = args[3]
            pwdMaster = args[4]

        if args[1] == '--version':
            print_version()

        if len(args) >= 3 and args[2] == '--dev':
            return args[1], True

        return '', False

    elif len(args) >= 1:
        return '', False

    else:
        logger.error('Informe o token da integracao como parametro')
        exit(1)


token_oking, is_dev = get_token_from_params(sys.argv)

start_time = datetime.now().isoformat()
logger.info('Iniciando oking __init__')
logger.info(f'Ambiente: {"Dev" if is_dev else "Prod"}')

try:
    # ==================== USAR TOKENMANAGER (MODO UNIFICADO) ====================
    from src.token_manager import TokenManager
    
    token_manager = TokenManager()
    
    if exibir_interface_grafica:
        # MODO GUI: Não faz nada aqui - deixa gui_main.py cuidar de tudo
        # O TokenManager será inicializado pelo gui_main.py
        # Pular toda a lógica de inicialização (API calls, logs, etc)
        pass
    else:
        # MODO CONSOLE: Usa TokenManager
        # Verifica se precisa fazer setup inicial
        if token_manager.needs_setup():
            # Passo 1: Shortname
            while True:
                shortname_interface = input('Digite o Shortname: ')
                try:
                    res = requests.get(f'https://{shortname_interface}.oking.openk.com.br/api/consulta/ping')
                    if not res.ok:
                        logger.warning(f'Ocorreu uma falha no test Ping: {res.text}')
                        continue
                    # Salva shortname no TokenManager
                    token_manager.set_shortname(shortname_interface)
                    logger.info(f'Shortname "{shortname_interface}" configurado com sucesso!')
                    break
                except Exception as e:
                    print(f'Shortname invalido! Erro: {str(e)}')
                    continue
            
            # Passo 2: Token
            nome_token = input('Informe o nome que deseja para essa integracao (a sua escolha): ')
            while True:
                token_input = input('Informe o Token: ')
                try:
                    # Valida token na API
                    client_data = oking.get(f'https://{shortname_interface}.oking.openk.com.br/api/consulta/oking_hub'
                                            f'/filtros?token={token_input}', None)
                    # Adiciona token ao TokenManager (já criptografa automaticamente)
                    token_manager.add_token(nome=nome_token, token=token_input, ativo=True)
                    client_not_exists = False
                    logger.info(f'Token "{nome_token}" adicionado e criptografado com sucesso!')
                    break
                except Exception as e:
                    print(f'Token invalido! Erro: {str(e)}')
                    continue
        
        # Carrega shortname e token ativo do TokenManager
        shortname_interface = token_manager.get_shortname()
        
        # Se token foi passado como parametro (-t=), usa ele
        if token_param:
            token_interface = token_param
        else:
            # Usa token ativo do TokenManager
            active_token_data = token_manager.get_active_token()
            if active_token_data:
                token_interface = active_token_data['token']  # Já vem descriptografado
                nome_token = active_token_data['nome']
                logger.info(f'Usando token ativo: {nome_token}')
            else:
                logger.error('Nenhum token ativo encontrado!')
                exit(1)

        # if shortname_interface is None or token_interface is None:
        #     exit()

        if not is_dev:
            # Consultar dados da integracao do cliente (modulos, tempo de execucao, dados api okvendas)
            if client_not_exists:
                client_data = oking.get(f'https://{shortname_interface}.oking.openk.com.br/api/consulta/oking_hub'
                                        f'/filtros?token={token_interface}', None)
            if (createDatabase):
                client_data['user'] = usrMaster
                client_data['password'] = pwdMaster
            api_okinghub.post_log(
                Log(
                    f'Oking inicializando {client_data["integracao_nome"]} - VersÃ£o {src.version}',
                    'INICIALIZACAO',
                    'OKING_INICIALIZACAO',
                    f'{client_data.get("integracao_id")}',
                    'X',
                    F'{client_data.get("seller_id")}'
                )
            )
        else:
            # Consultar dados da integracao do cliente em ambiente node-red local
            client_data = oking.get(f'http://127.0.0.1:1880/api/consulta/integracao_oking/filtros', None)
            api_okinghub.post_log(Log(f'Oking inicializando cliente id {client_data["integracao_nome"]} - '
                                      f'VersÃ£o {src.version}',
                                      '',
                                      'OKING_INICIALIZACAO',
                                      {client_data["integracao_id"]},
                                      'X',
                                      {client_data["seller_id"]}))
        install_package_database(client_data['db_type'])
        if client_data is not None:
            # assert client_data['integracao_id'] is not None, 'Id da integracao nao informado (Api Oking)'
            # assert client_data['db_type'] is not None, 'Tipo do banco de dados nao informado (Api Oking)'
            # assert client_data['host'] is not None, 'Host do banco de dados nao informado (Api Oking)'
            # assert client_data['database'] is not None, 'Nome do banco de dados nao informado (Api Oking)'
            # assert client_data['user'] is not None, 'Usuario do banco de dados nao informado (Api Oking)'
            # assert client_data['password'] is not None, 'Senha do banco de dados nao informado (Api Oking)'
            if client_data['operacao'].lower().__contains__('mplace'):
                assert client_data[
                           'url_api_principal'] is not None, 'Url Principal da api okvendas nao informado (Api Oking)'
                assert client_data[
                           'url_api_secundaria'] is not None, 'Url SecundÃ¡ria da api okvendas nao informado (Api Oking)'
                assert client_data['token_api_integracao'] is not None, 'Token da api Parceiro nao informado '
            assert client_data['token_oking'] is not None, 'Token da Api Oking nao informado '

            is_connected_oracle_client = False
        else:
            logger.warning(f'Cliente nao configurado no painel oking para o token: {token_interface}')

except Exception as e:
    logger.error(f'Erro: {str(e)}')
    exit()
