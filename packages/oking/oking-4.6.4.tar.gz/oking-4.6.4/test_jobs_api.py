import json
import urllib.request

# Teste simples da API
api_base = "https://oking-openk.oking.openk.com.br"
token = "d9c2f6d9cc1bbfd62fb8c88ee0bf41b3e55bf58c98eec00ff8877e931e51c7fe"

full_url = f"{api_base}/api/consulta/oking_hub/filtros?token={token}"

print(f"URL: {full_url}\n")

req = urllib.request.Request(full_url)
with urllib.request.urlopen(req, timeout=10) as response:
    data = json.loads(response.read().decode())
    
    print(f"Sucesso: {data.get('sucesso')}")
    
    jobs = data.get('modulos', [])
    print(f"Total de jobs: {len(jobs)}\n")
    
    if jobs:
        primeiro = jobs[0]
        print(f"Primeiro job:")
        print(f"  Nome: {primeiro.get('nome_job')}")
        print(f"  Ativo: '{primeiro.get('ativo')}' (tipo: {type(primeiro.get('ativo'))})")
        print(f"  É 'S'?: {primeiro.get('ativo') == 'S'}")
        print()
    
    # Contar ativos
    ativos = 0
    pausados = 0
    
    for job in jobs:
        ativo_val = job.get('ativo')
        print(f"Job: {job.get('job'):<30} Ativo: '{ativo_val}'", end="")
        
        if ativo_val == 'S':
            ativos += 1
            print(" -> ATIVO")
        else:
            pausados += 1
            print(" -> PAUSADO")
    
    print(f"\n=== RESULTADO ===")
    print(f"Total: {len(jobs)}")
    print(f"Ativos: {ativos}")
    print(f"Pausados: {pausados}")
