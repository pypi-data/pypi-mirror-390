"""
Script de Teste - TokensScreen
Valida correções no bug de exclusão de tokens
"""
import tkinter as tk
from src.token_manager import TokenManager
from screens.tokens import TokensScreen

def test_tokens_screen():
    """Testa a TokensScreen com TokenManager"""
    print("=" * 60)
    print("🧪 TESTE: TokensScreen - Bug de Exclusão")
    print("=" * 60)
    
    # Inicializa TokenManager
    token_manager = TokenManager()
    
    print(f"\n✅ TokenManager inicializado")
    print(f"   Shortname: {token_manager.get_shortname()}")
    print(f"   Tokens cadastrados: {len(token_manager.get_all_tokens())}")
    
    # Lista tokens
    tokens = token_manager.get_all_tokens()
    print(f"\n📋 Tokens disponíveis:")
    for i, token in enumerate(tokens, 1):
        is_active = token.get('id') == token_manager.tokens_data.get('active_token_id')
        status = "⭐ ATIVO" if is_active else "⚪ Inativo"
        print(f"   {i}. {token['nome']} - {status}")
        print(f"      ID: {token['id']}")
    
    # Cria janela de teste
    print(f"\n🎨 Abrindo interface gráfica...")
    root = tk.Tk()
    root.title("Teste - TokensScreen")
    root.geometry("1200x800")
    
    # Cria TokensScreen
    tokens_screen = TokensScreen(root, token_manager=token_manager)
    tokens_screen.pack(fill='both', expand=True)
    
    print(f"\n✅ TokensScreen carregada com sucesso!")
    print(f"\n📝 Instruções de Teste:")
    print(f"   1. Tente excluir um token INATIVO (deve funcionar)")
    print(f"   2. Tente excluir o token ATIVO (deve mostrar aviso)")
    print(f"   3. Adicione um novo token")
    print(f"   4. Edite um token existente")
    print(f"   5. Mude o token ativo")
    print(f"\n🔍 Observe os comportamentos e confirme se tudo funciona!")
    print("=" * 60)
    
    root.mainloop()

if __name__ == "__main__":
    test_tokens_screen()
