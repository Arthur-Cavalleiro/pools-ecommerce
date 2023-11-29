from flask import Flask, render_template, request, redirect
from functions import perform_area_calculation, request_pool_data

app = Flask(__name__)

pools = []
poolsPerArea = []


@app.route('/')
def menu_page():
    pools.clear()

    resultados = request_pool_data()

    for pool in resultados:
        pools.append(pool)

    return render_template('Menu.html', pools=pools)


@app.route('/calculo')
def calculation_page():
    return render_template('Calc.html', poolsPerArea=poolsPerArea)


@app.route('/getPoolsPerArea', methods=['POST'])
def calculate_pools():
    poolsPerArea.clear()

    comprimento = float(request.form.get('comprimento'))
    largura = float(request.form.get('largura'))
    orcamento = float(request.form.get('orcamento'))

    resultados = perform_area_calculation(comprimento, largura, orcamento)

    for pool in resultados:
        poolsPerArea.append(pool)

    return redirect('/calculo')


app.run(debug=True)
