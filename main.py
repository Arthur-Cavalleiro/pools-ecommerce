from flask import Flask, render_template, request, redirect
import requests
import json

app = Flask(__name__)

pools = []
poolsPerArea = []

@app.route('/')
def menuPage():
  return render_template('Menu.html', conteudo='teste')

@app.route('/calculo')
def showPage():
  return render_template('Calc.html', pools=pools)

@app.route('/getPoolsPerArea', methods=['POST'])
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



  return redirect('/calculo')

app.run(debug=True)
