"""
Teste da nova API /api/oking_atualiza_tarefa
Execute este arquivo para testar a atualização de tarefas
"""
import requests
import json

# Configurações (ajuste conforme necessário)
SHORTNAME = "protec"
TOKEN = "4f1c9ec13c01b4afdeba43d0f4bda11c49949e97F9ef1G11f0H9ebbJ02001706ead8"

def testar_atualizacao_sucesso():
    """Teste de atualização com sucesso"""
    print("\n" + "="*60)
    print("TESTE 1: Atualização com sucesso")
    print("="*60)
    
    url = f"https://{SHORTNAME}.oking.openk.com.br/api/oking_atualiza_tarefa"
    
    dados = {
        "comando": "SELECT * FROM TESTE WHERE ID > 100",
        "intervalo": 5,
        "observacao": "Teste de atualização via script Python",
        "job": "sincroniza_tipoclifor",
        "ativo": "S",
        "token": TOKEN
    }
    
    print(f"\n📤 URL: {url}")
    print(f"📦 Payload:")
    print(json.dumps(dados, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(url, json=dados, timeout=30)
        
        print(f"\n📥 Status HTTP: {response.status_code}")
        print(f"📄 Resposta:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            resultado = response.json()
            if isinstance(resultado, list):
                resultado = resultado[0]
            
            if resultado.get('sucesso'):
                print(f"\n✅ SUCESSO: {resultado.get('mensagem')}")
                return True
            else:
                print(f"\n❌ FALHA: {resultado.get('mensagem')}")
                return False
        else:
            print(f"\n❌ ERRO HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEÇÃO: {str(e)}")
        return False


def testar_token_invalido():
    """Teste com token inválido (deve retornar 401)"""
    print("\n" + "="*60)
    print("TESTE 2: Token inválido (esperado: HTTP 401)")
    print("="*60)
    
    url = f"https://{SHORTNAME}.oking.openk.com.br/api/oking_atualiza_tarefa"
    
    dados = {
        "comando": "SELECT * FROM TESTE",
        "intervalo": 5,
        "observacao": "Teste com token inválido",
        "job": "sincroniza_tipoclifor",
        "ativo": "S",
        "token": "token_invalido_123456"
    }
    
    print(f"\n📤 URL: {url}")
    print(f"📦 Token usado: token_invalido_123456")
    
    try:
        response = requests.post(url, json=dados, timeout=30)
        
        print(f"\n📥 Status HTTP: {response.status_code}")
        print(f"📄 Resposta:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 401:
            print(f"\n✅ COMPORTAMENTO ESPERADO: HTTP 401 retornado")
            return True
        else:
            print(f"\n⚠️ INESPERADO: Esperava HTTP 401, recebeu {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEÇÃO: {str(e)}")
        return False


def testar_campos_obrigatorios():
    """Teste sem campos obrigatórios (deve retornar 400)"""
    print("\n" + "="*60)
    print("TESTE 3: Campos obrigatórios faltando (esperado: HTTP 400)")
    print("="*60)
    
    url = f"https://{SHORTNAME}.oking.openk.com.br/api/oking_atualiza_tarefa"
    
    # Faltando 'comando' e 'intervalo'
    dados = {
        "observacao": "Teste sem campos obrigatórios",
        "job": "sincroniza_tipoclifor",
        "ativo": "S",
        "token": TOKEN
    }
    
    print(f"\n📤 URL: {url}")
    print(f"📦 Payload (faltando 'comando' e 'intervalo'):")
    print(json.dumps(dados, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(url, json=dados, timeout=30)
        
        print(f"\n📥 Status HTTP: {response.status_code}")
        print(f"📄 Resposta:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 400:
            print(f"\n✅ COMPORTAMENTO ESPERADO: HTTP 400 retornado")
            return True
        else:
            print(f"\n⚠️ INESPERADO: Esperava HTTP 400, recebeu {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEÇÃO: {str(e)}")
        return False


def testar_valor_ativo_invalido():
    """Teste com valor inválido no campo 'ativo' (deve retornar 400)"""
    print("\n" + "="*60)
    print("TESTE 4: Valor inválido em 'ativo' (esperado: HTTP 400)")
    print("="*60)
    
    url = f"https://{SHORTNAME}.oking.openk.com.br/api/oking_atualiza_tarefa"
    
    dados = {
        "comando": "SELECT * FROM TESTE",
        "intervalo": 5,
        "observacao": "Teste com ativo inválido",
        "job": "sincroniza_tipoclifor",
        "ativo": "X",  # Inválido, deve ser 'S' ou 'N'
        "token": TOKEN
    }
    
    print(f"\n📤 URL: {url}")
    print(f"📦 Payload (ativo='X' ao invés de 'S' ou 'N'):")
    print(json.dumps(dados, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(url, json=dados, timeout=30)
        
        print(f"\n📥 Status HTTP: {response.status_code}")
        print(f"📄 Resposta:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 400:
            print(f"\n✅ COMPORTAMENTO ESPERADO: HTTP 400 retornado")
            return True
        else:
            print(f"\n⚠️ INESPERADO: Esperava HTTP 400, recebeu {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEÇÃO: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "🧪 TESTE DA API /api/oking_atualiza_tarefa ".center(60, "="))
    print(f"\nShortname: {SHORTNAME}")
    print(f"Token: {TOKEN[:20]}...")
    
    resultados = []
    
    # Executar testes
    resultados.append(("Atualização com sucesso", testar_atualizacao_sucesso()))
    resultados.append(("Token inválido", testar_token_invalido()))
    resultados.append(("Campos obrigatórios", testar_campos_obrigatorios()))
    resultados.append(("Valor ativo inválido", testar_valor_ativo_invalido()))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    for nome, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{nome:<30} {status}")
    
    total = len(resultados)
    passou = sum(1 for _, s in resultados if s)
    
    print(f"\n{passou}/{total} testes passaram")
    
    if passou == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️ {total - passou} teste(s) falharam")
