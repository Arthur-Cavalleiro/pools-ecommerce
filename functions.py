from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, lpSum, LpStatus
import json
import requests


def request_pool_data():
    pools = []
    data = requests.get('http://127.0.0.1:5000/get-all-pools')
    if data.content:
        try:
            all_pools = json.loads(data.content)
            pools.clear()
            for pool in all_pools:
                pools.append(pool)
            print(pools)
            return pools
        except json.decoder.JSONDecodeError:
            print("A resposta não é um JSON válido")
    else:
        print("A resposta está vazia")


def perform_area_calculation(comprimento_disponivel, largura_disponivel, orcamento):
    piscinas = request_pool_data()

    # Fatores de adequação com base no formato do espaço disponível
    if comprimento_disponivel > largura_disponivel:
        # Espaço é mais longo do que largo, então piscinas retangulares são mais adequadas
        fatores_de_adequacao = {"Retangular": 1.0, "Quadrada": 0.8, "Redonda": 0.6, "Oval": 0.7}
    else:
        # Espaço é mais quadrado, então piscinas redondas ou ovais são mais adequadas
        fatores_de_adequacao = {"Retangular": 0.8, "Quadrada": 0.8, "Redonda": 1.0, "Oval": 1.0}

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
    area_disponivel = comprimento_disponivel * largura_disponivel
    restricao_area = 0
    for piscina in piscinas:
        i = piscina["pool_id"]
        restricao_area += (piscina["length"] * piscina["width"]) * variaveis_decisao[i]
    problema += restricao_area <= area_disponivel

    # Resolva o problema
    problema.solve()

    # Imprima os resultados
    print("Status:", LpStatus[problema.status])
    pools_res = []
    for piscina in piscinas:
        i = piscina['pool_id']
        if variaveis_decisao[i].varValue > 0:
            print(f"Selecionado -> Nome: {piscina['pool_name']} | ID: {i}")
            pools_res.append(piscina)
    return pools_res


perform_area_calculation(200, 300, 50000)
