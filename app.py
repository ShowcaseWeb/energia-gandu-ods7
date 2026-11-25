import json, os, math
from datetime import datetime
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "gandu.json")

def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)

IRRADIANCIA = 4.84
TARIFA = 0.878
FATOR = 0.80
FIO_B = {2023: 0.15, 2024: 0.30, 2025: 0.45, 2026: 0.60, 2027: 0.75, 2028: 0.90, 2029: 1.00}

def calcular(consumo, placa=550):
    if not math.isfinite(consumo) or not 0 < consumo <= 100000:
        return None
    ger_kwp = IRRADIANCIA * 30 * FATOR
    kwp = consumo / ger_kwp
    n = math.ceil(kwp * 1000 / placa)
    inv = n * 1750
    eco_bruta = consumo * TARIFA * 0.90
    fio_medio = FIO_B[2026]
    eco_liq = eco_bruta * (1 - fio_medio * 0.30)
    pb = inv / eco_liq if eco_liq > 0 else 0
    ger = n * (placa/1000) * ger_kwp
    co2 = ger * 12 * 0.0817
    return {"kwp": round(n * placa / 1000,2), "placas": n, "investimento": round(inv,2),
            "economia_mensal": round(eco_liq,2), "economia_anual": round(eco_liq*12,2),
            "payback_meses": round(pb,1), "payback_anos": round(pb/12,1),
            "geracao_mensal": round(ger,0), "co2_evitado_ano": round(co2,1),
            "fio_b": "60% (2026)", "tarifa": TARIFA}

def comparar_cenarios(consumo):
    cenarios = []
    for ano, fio in FIO_B.items():
        ger_kwp = IRRADIANCIA * 30 * FATOR
        kwp = consumo / ger_kwp
        n = math.ceil(kwp * 1000 / 550)
        inv = n * 1750
        eco_bruta = consumo * TARIFA * 0.90
        eco_liq = eco_bruta * (1 - fio * 0.30)
        pb = inv / eco_liq if eco_liq > 0 else 0
        cenarios.append({"ano": ano, "fio_b": f"{int(fio*100)}%", "economia_mensal": round(eco_liq,2),
                         "payback_anos": round(pb/12,1)})
    return cenarios

@app.context_processor
def g():
    return {"ano": 2026, "dt": datetime.now().strftime("%d/%m/%Y")}

@app.route("/")
def home():
    d = load()
    return render_template("home.html", d=d)

@app.route("/gandu")
def gandu():
    d = load()
    return render_template("gandu.html", d=d)

@app.route("/energia")
def energia():
    d = load()
    return render_template("energia.html", d=d)

@app.route("/simulador", methods=["GET", "POST"])
def simulador():
    d = load()
    calc = None
    cenarios = None
    consumo = None
    if request.method == "POST":
        try:
            consumo = float(request.form.get("consumo", 0))
            calc = calcular(consumo)
            cenarios = comparar_cenarios(consumo) if calc else None
        except (ValueError, TypeError, OverflowError):
            calc = None
    return render_template("simulador.html", d=d, calc=calc, cenarios=cenarios, consumo=consumo)

@app.route("/relatos")
def relatos():
    d = load()
    tipo = request.args.get("tipo", "todos")
    relatos = d["relatos"]
    if tipo != "todos":
        relatos = [r for r in relatos if r["tipo"] == tipo]
    return render_template("relatos.html", d=d, relatos=relatos, tipo=tipo)

@app.route("/lei")
def lei():
    d = load()
    return render_template("lei.html", d=d)

@app.route("/api/simular")
def api_simular():
    try:
        consumo = float(request.args.get("consumo", 0))
        calc = calcular(consumo)
        if calc is None:
            return jsonify({"erro": "Consumo deve estar entre 0 e 100000 kWh"}), 400
        return jsonify({"calculo": calc, "cenarios": comparar_cenarios(consumo)})
    except (ValueError, TypeError, OverflowError):
        return jsonify({"erro": "invalido"}), 400

@app.route("/api/gandu")
def api_gandu():
    return jsonify(load())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("GANDU_PORT", "5077")), debug=False)