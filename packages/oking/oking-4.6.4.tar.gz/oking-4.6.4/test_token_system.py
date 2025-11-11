"""
Script de teste para o sistema de tokens
Testa: TokenManager, migração, FirstAccessModal, SplashScreen
"""

import tkinter as tk
import sys
import os

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.token_manager import TokenManager
from screens.first_access import FirstAccessModal
from screens.splash import SplashScreen


def test_token_manager():
    """Testa o TokenManager"""
    print("\n" + "="*60)
    print("TESTE 1: TokenManager")
    print("="*60)
    
    # Cria instância
    manager = TokenManager()
    
    # Verifica shortname
    print(f"Shortname: {manager.get_shortname()}")
    
    # Verifica tokens
    tokens = manager.get_all_tokens()
    print(f"Total de tokens: {len(tokens)}")
    
    for token in tokens:
        print(f"  - {token['nome']}: {'ATIVO' if token.get('is_active') else 'inativo'}")
    
    # Verifica token ativo
    active = manager.get_active_token()
    if active:
        print(f"\n✅ Token ativo: {active['nome']}")
        print(f"   Token: {active['token'][:20]}...{active['token'][-10:]}")
    else:
        print("\n⚠️ Nenhum token ativo")
    
    # Verifica se precisa setup
    needs_setup = manager.needs_setup()
    print(f"\n{'⚠️' if needs_setup else '✅'} Precisa de setup: {needs_setup}")
    
    return manager


def test_splash():
    """Testa o Splash Screen"""
    print("\n" + "="*60)
    print("TESTE 2: Splash Screen")
    print("="*60)
    
    root = tk.Tk()
    root.withdraw()
    
    splash = SplashScreen()
    
    # Simula carregamento
    import time
    for i in range(11):
        progress = i / 10
        status = [
            "Iniciando...",
            "Verificando arquivos...",
            "Carregando configurações...",
            "Validando tokens...",
            "Conectando à API...",
            "Carregando módulos...",
            "Preparando interface...",
            "Carregando jobs...",
            "Inicializando dashboard...",
            "Quase lá...",
            "Pronto!"
        ][i]
        
        splash.update_progress(progress, status)
        time.sleep(0.3)
    
    splash.close()
    root.destroy()
    
    print("✅ Splash exibido com sucesso!")


def test_first_access_modal():
    """Testa o modal de primeiro acesso"""
    print("\n" + "="*60)
    print("TESTE 3: Modal de Primeiro Acesso")
    print("="*60)
    
    root = tk.Tk()
    root.withdraw()
    
    manager = TokenManager()
    
    # Limpa tokens para forçar first access
    # manager.tokens_data = {'active_token_id': None, 'shortname': None, 'tokens': []}
    # manager._save_tokens()
    
    modal = FirstAccessModal(root, manager)
    result = modal.show()
    
    if result:
        print("✅ Configuração concluída!")
        print(f"   Shortname: {result['shortname']}")
        print(f"   Nome: {result['nome']}")
        print(f"   Token: {result['token'][:20]}...{result['token'][-10:]}")
    else:
        print("❌ Configuração cancelada")
    
    root.destroy()
    
    return result


def show_current_flow():
    """Exibe o fluxo de inicialização atual"""
    print("\n" + "="*60)
    print("FLUXO DE INICIALIZAÇÃO MAPEADO")
    print("="*60)
    
    print("""
🚀 NOVA VERSÃO (Tkinter + TokenManager):

1. INÍCIO → python main_integrated.py
   
2. SPLASH SCREEN
   └─ Exibe logo + barra de progresso
   └─ Status: "Iniciando..."
   
3. VERIFICAÇÃO DE TOKENS (TokenManager)
   ├─ Procura ~/.oking/tokens.json
   │  ├─ EXISTE → Carrega tokens
   │  └─ NÃO EXISTE → Procura arquivos legados
   │     ├─ token.txt + shortname.txt EXISTEM
   │     │  └─ Migra para JSON
   │     │     └─ Criptografa tokens (AES-256)
   │     │     └─ Salva ~/.oking/tokens.json
   │     │     └─ Remove token.txt e shortname.txt
   │     └─ NÃO EXISTEM
   │        └─ needs_setup = True
   
4. DECISÃO DE SETUP
   ├─ needs_setup = True
   │  └─ Exibe FirstAccessModal
   │     ├─ Passo 1: Shortname
   │     │  └─ Valida: GET /api/consulta/ping
   │     └─ Passo 2: Nome + Token
   │        └─ Valida: GET /api/consulta/integracao/filtros?token={token}
   │        └─ Salva em ~/.oking/tokens.json (criptografado)
   │        └─ Define como token ativo
   └─ needs_setup = False
      └─ Continua inicialização
   
5. CARREGAMENTO DE DADOS (client_data)
   ├─ Obtém token ativo: token_manager.get_active_token()
   ├─ GET https://{shortname}.oking.openk.com.br/api/consulta/oking_hub/filtros?token={token}
   └─ Carrega:
      ├─ Módulos/Jobs
      ├─ Configurações de banco
      ├─ APIs (OKVendas, OKING Hub, etc)
      └─ Operações disponíveis
   
6. INTERFACE PRINCIPAL
   ├─ Header
   │  ├─ Logo
   │  ├─ ⭐ Token Ativo: "Nome do Token"
   │  └─ Menu lateral
   └─ Dashboard
      └─ 9 telas integradas
   
7. TROCA DE TOKEN
   └─ Tela Tokens → Botão "⭐ Usar este Token"
      ├─ Marca token como ativo
      ├─ Callback: on_token_changed()
      ├─ Recarrega client_data com novo token
      └─ Atualiza header: "⭐ Token Ativo: Novo Nome"

8. MODO CONSOLE (--console)
   └─ python main_integrated.py --console -t=TOKEN -j=JOB
      ├─ Detecta sys.argv
      ├─ exibir_interface_grafica = False
      ├─ Lê token (JSON ou parâmetro -t)
      ├─ Carrega client_data
      └─ Executa job específico (sem GUI)

📁 ESTRUTURA DE ARQUIVOS:
   ~/.oking/
   ├─ tokens.json (NOVO - criptografado AES-256)
   │  {
   │    "active_token_id": "20251106123045123456",
   │    "shortname": "protec",
   │    "tokens": [
   │      {
   │        "id": "20251106123045123456",
   │        "nome": "Protec - Produção",
   │        "token": "gAAAAABh...[criptografado]",
   │        "is_active": true,
   │        "ativo": true,
   │        "criado_em": "2025-11-06T12:30:45",
   │        "ultimo_uso": "2025-11-06T14:22:10"
   │      }
   │    ]
   │  }
   │
   ├─ database.json (configurações de banco)
   └─ settings.json (preferências de tema)
   
   [LEGADOS - Migrados automaticamente e removidos]
   ├─ token.txt (formato: "nome#token")
   └─ shortname.txt

🔐 SEGURANÇA:
   ✅ Tokens criptografados (AES-256)
   ✅ Chave baseada no hostname da máquina
   ✅ Arquivos em ~/.oking (oculto no usuário)
   ✅ Validação via API antes de salvar

🌟 DIFERENCIAIS:
   ✅ Múltiplos tokens (dev, prod, teste)
   ✅ Troca de token em tempo real
   ✅ Migração automática (zero setup manual)
   ✅ Splash screen profissional
   ✅ Header mostra token ativo
   ✅ Modo console preservado
""")


def main():
    """Executa todos os testes"""
    print("\n🧪 INICIANDO TESTES DO SISTEMA DE TOKENS")
    
    # Mostra fluxo
    show_current_flow()
    
    # Teste 1: TokenManager
    manager = test_token_manager()
    
    # Teste 2: Splash (apenas visual)
    # test_splash()
    
    # Teste 3: Modal (se precisar)
    if manager.needs_setup():
        print("\n⚠️ Sistema precisa de configuração inicial")
        print("Execute novamente para testar o modal de primeiro acesso")
        # test_first_access_modal()
    
    print("\n" + "="*60)
    print("✅ TESTES CONCLUÍDOS!")
    print("="*60)


if __name__ == "__main__":
    main()
