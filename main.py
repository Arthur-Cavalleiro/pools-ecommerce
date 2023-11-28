from flask import Flask, render_template, request, redirect
from functions import perform_area_calculation
import requests
import json

app = Flask(__name__)

pools = []
poolsPerArea = []


@app.route('/')
def menu_page():
    return render_template('Menu.html', conteudo='teste')


@app.route('/calculo')
def calculation_page():
    return render_template('Calc.html', pools=pools)


@app.route('/getPoolsPerArea', methods=['POST'])
def calculate_pools():
    comprimento = request.form.get('comprimento')
    largura = request.form.get('largura')
    orcamento = request.form.get('orcamento')

    calculated_pools = perform_area_calculation(comprimento, largura, orcamento)

    return redirect('/calculo')


app.run(debug=True)
