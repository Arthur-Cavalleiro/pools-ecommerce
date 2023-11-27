from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, lpSum, LpStatus
import json
import requests

pools = []

def calcBestPool():
  data = requests.get('http://localhost:5173/get-all-pools')
  if data.content:
    try:
        all = json.loads(data.content)
        pools.clear()
        for pool in all:
            pools.append(pool)
    except json.decoder.JSONDecodeError:
        print("A resposta não é um JSON válido")
  else:
    print("A resposta está vazia")

calcBestPool()
print(pools)
piscinas = pools

# Fatores de adequação para cada formato de piscina
fatores_de_adequacao = {"Retangular": 1.0, "Quadrada": 0.8, "Redonda": 0.6, "Oval": 0.7}

# Crie o problema de otimização
problema = LpProblem("OtimizacaoDePiscinas", LpMaximize)

# Variáveis de decisão
variaveis_decisao = LpVariable.dicts("variaveis_decisao", [piscina["pool_id"] for piscina in piscinas], 0, 1, LpBinary)

# Função objetivo: maximizar o volume, o fator de adequação e minimizar o preço
objetivo_volume = 0
objetivo_adequacao = 0
objetivo_preco = 10000
for piscina in piscinas:
    i = piscina["pool_id"]
    # Converte o preço para um número
    preco = float(piscina["price"].replace("R$ ", "").replace(".", "").replace(",", "."))
    objetivo_volume += piscina["volume"] * variaveis_decisao[i]
    objetivo_adequacao += fatores_de_adequacao[piscina["format"]] * variaveis_decisao[i]
    objetivo_preco += preco * variaveis_decisao[i]
problema += objetivo_volume + objetivo_adequacao - objetivo_preco

# Restrição: a área total das piscinas selecionadas não deve exceder a área disponível
area_disponivel = 10000  # mude para a área disponível
restricao_area = 0
for piscina in piscinas:
    i = piscina["pool_id"]
    restricao_area += (piscina["length"] * piscina["width"]) * variaveis_decisao[i]
problema += restricao_area <= area_disponivel

# Resolva o problema
problema.solve()

# Imprima os resultados
print("Status:", LpStatus[problema.status])
for piscina in piscinas:
    i = piscina["pool_id"]
    if variaveis_decisao[i].varValue > 0:
        print("Selecionado:", piscina["pool_name"])