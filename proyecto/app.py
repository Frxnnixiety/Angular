from flask import Flask, render_template, request, redirect, url_for
import json
import os
import requests
from datetime import datetime

app = Flask(__name__)

# API Key de Twelve Data
API_KEY = "3dcf6e034ade478b8848b8848b8848b9e3b0"
DATA_FILE = "data.json"

# Lista de acciones principales de tu tablero fijo
ACCIONES_MONITOREO = ["AAPL", "AMZN", "GOOGL", "IBM", "META", "NVDA", "TSLA"]

# Diccionario de respaldo inmediato por si los créditos de la API gratuita se agotan temporalmente
PRECIOS_RESPALDO = {
    "AAPL": 195.50, "AMZN": 245.98, "GOOGL": 369.26, 
    "IBM": 287.60, "META": 312.10, "NVDA": 40.00, "TSLA": 248.30
}

def init_db():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"portfolios": {}}, f, indent=4)

def read_db():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_db(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# --- LOGICA DE PETICIONES A LA API ---

def buscar_simbolo(nombre):
    nombre_limpio = nombre.strip().upper()
    if nombre_limpio in PRECIOS_RESPALDO:
        return nombre_limpio
        
    url = f"https://api.twelvedata.com/symbol_search?symbol={nombre_limpio}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=5).json()
        if "data" in response and len(response["data"]) > 0:
            return response["data"][0]["symbol"].upper()
    except Exception:
        pass
    return nombre_limpio

def obtener_precio_actual(simbolo):
    simbolo_limpio = simbolo.strip().upper()
    url = f"https://api.twelvedata.com/price?symbol={simbolo_limpio}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=5).json()
        # Verificar si la API contestó con el precio directamente
        if "price" in response:
            return float(response["price"])
        # Si arroja un mensaje de error por exceso de llamadas (rate limit)
        elif "code" in response or "message" in response:
            print(f"[API Alert] Límite excedido o error para {simbolo_limpio}. Usando respaldo.")
    except Exception as e:
        print(f"[Network Error] No se pudo conectar a la API: {e}")
    
    # Retorna el precio del catálogo de respaldo si la API falla
    return PRECIOS_RESPALDO.get(simbolo_limpio, 150.00)

# --- RUTAS ---

@app.route('/')
def index():
    db = read_db()
    portfolios = db["portfolios"]
    total_consolidado = 0.0
    
    for p_name, p_data in portfolios.items():
        ganancia_portafolio = 0.0
        for tx in p_data["transacciones"]:
            precio_actual = obtener_precio_actual(tx["simbolo"])
            ganancia_portafolio += (precio_actual - tx["precio_operacion"]) * tx["cantidad"]
        
        p_data["rendimiento"] = round(ganancia_portafolio, 2)
        total_consolidado += ganancia_portafolio

    return render_template('portafolios.html', portfolios=portfolios, total_consolidado=round(total_consolidado, 2))

# NUEVA RUTA: Apartado para ver todas las acciones y sus precios actuales
@app.route('/mercado')
def mercado():
    lista_precios = []
    for simbolo in ACCIONES_MONITOREO:
        precio = obtener_precio_actual(simbolo)
        lista_precios.append({
            "simbolo": simbolo,
            "precio": precio
        })
    return render_template('mercado.html', lista_precios=lista_precios)

@app.route('/agregar_portafolio', methods=['POST'])
def agregar_portafolio():
    nombre = request.form.get('nombre_portafolio').strip()
    if nombre:
        db = read_db()
        if nombre not in db["portfolios"]:
            db["portfolios"][nombre] = {
                "fecha_creacion": datetime.now().strftime("%d/%m/%Y"),
                "transacciones": [],
                "rendimiento": 0.0
            }
            write_db(db)
    return redirect(url_for('index'))

@app.route('/eliminar_portafolio/<nombre>')
def eliminar_portafolio(nombre):
    db = read_db()
    if nombre in db["portfolios"]:
        del db["portfolios"][nombre]
        write_db(db)
    return redirect(url_for('index'))

@app.route('/cotizar', methods=['GET', 'POST'])
def cotizar():
    resultado = None
    if request.method == 'POST':
        busqueda = request.form.get('busqueda').upper()
        simbolo = buscar_simbolo(busqueda)
        precio = obtener_precio_actual(simbolo)
        resultado = {"simbolo": simbolo, "precio": precio}
    return render_template('cotizar.html', resultado=resultado)

@app.route('/comprar', methods=['GET', 'POST'])
def comprar():
    db = read_db()
    portfolios = db["portfolios"]
    
    if request.method == 'POST':
        p_nombre = request.form.get('portafolio')
        busqueda = request.form.get('simbolo').upper()
        cantidad = int(request.form.get('cantidad'))
        
        simbolo = buscar_simbolo(busqueda)
        precio = obtener_precio_actual(simbolo)
        
        if p_nombre in portfolios:
            nueva_tx = {
                "simbolo": simbolo,
                "cantidad": cantidad, 
                "precio_operacion": precio,
                "tipo": "compra",
                "fecha": datetime.now().strftime("%d/%m/%Y")
            }
            db["portfolios"][p_nombre]["transacciones"].append(nueva_tx)
            write_db(db)
            return redirect(url_for('index'))
            
    return render_template('comprar.html', portfolios=portfolios)

@app.route('/vender', methods=['GET', 'POST'])
def vender():
    db = read_db()
    portfolios = db["portfolios"]
    
    if request.method == 'POST':
        p_nombre = request.form.get('portafolio')
        busqueda = request.form.get('simbolo').upper()
        cantidad_vender = int(request.form.get('cantidad'))
        
        simbolo = buscar_simbolo(busqueda)
        precio_actual = obtener_precio_actual(simbolo)
        
        if p_nombre in portfolios:
            nueva_tx = {
                "simbolo": simbolo,
                "cantidad": -cantidad_vender,
                "precio_operacion": precio_actual, 
                "tipo": "venta",
                "fecha": datetime.now().strftime("%d/%m/%Y")
            }
            db["portfolios"][p_nombre]["transacciones"].append(nueva_tx)
            write_db(db)
            return redirect(url_for('index'))
                
    return render_template('vender.html', portfolios=portfolios)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)