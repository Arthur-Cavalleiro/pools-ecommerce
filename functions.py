from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, lpSum, LpStatus
import json
import requests

def request_pool_data():
    pools = []
    data = requests.get('http://127.0.0.1:5173/get-all-pools')
    if data.content:
        try:
            all_pools = json.loads(data.content)
            pools.clear()
            for pool in all_pools:
                pools.append(pool)
            return pools
        except json.decoder.JSONDecodeError:
            print("A resposta não é um JSON válido")
    else:
        print("A resposta está vazia")


def perform_area_calculation(comprimento_disponivel, largura_disponivel, orcamento):
    piscinas = request_pool_data()

    # Fatores de adequação
    fatores_de_adequacao = {"Retangular": 1.0, "Quadrada": 0.8}

    # Crie o problema de otimização
    problema = LpProblem("OtimizacaoDePiscinas", LpMaximize)

    # Variáveis de decisão
    variaveis_decisao = LpVariable.dicts("variaveis_decisao", [piscina["pool_id"] for piscina in piscinas], 0, 1, LpBinary)

    # Restrição de orçamento: o custo total das piscinas selecionadas não deve exceder o orçamento do usuário
    restricao_orcamento = 0
    for piscina in piscinas:
        i = piscina["pool_id"]
        # Converte o preço para um número
        preco = float(piscina["price"].replace("R$ ", "").replace(".", "").replace(",", "."))
        restricao_orcamento += preco * variaveis_decisao[i]
    problema += restricao_orcamento <= orcamento

    # Função objetivo: maximizar o volume, o fator de adequação e minimizar o preço
    objetivo_volume = 0
    objetivo_adequacao = 0
    objetivo_preco = 0
    for piscina in piscinas:
        i = piscina["pool_id"]
        # Converte o preço para um número
        preco = float(piscina["price"].replace("R$ ", "").replace(".", "").replace(",", "."))
        objetivo_volume += piscina["volume"] * variaveis_decisao[i]
        objetivo_adequacao += fatores_de_adequacao[piscina["format"]] * variaveis_decisao[i]
        objetivo_preco += preco * variaveis_decisao[i]
    problema += 0.001*objetivo_volume + 0.01*objetivo_adequacao - 0.00001*objetivo_preco

    # Restrição: a área total das piscinas selecionadas não deve exceder a área disponível
    area_disponivel = comprimento_disponivel * largura_disponivel
    restricao_area = 0
    for piscina in piscinas:
        i = piscina["pool_id"]
        restricao_area += (piscina["length"] * piscina["width"]) * variaveis_decisao[i]
    problema += restricao_area <= area_disponivel

    # Resolva o problema
    problema.solve()

    # Imprima os resultados
    # print("Status:", LpStatus[problema.status])

    pools_res = []
    for piscina in piscinas:
        i = piscina['pool_id']
        if variaveis_decisao[i].varValue > 0:
            # print(f"Selecionado -> Nome: {piscina['pool_name']} | ID: {i}")
            pools_res.append(piscina)
    # print(pools_res)
    return pools_res
