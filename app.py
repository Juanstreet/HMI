from flask import Flask, render_template, jsonify
from collections import defaultdict
from datetime import datetime
import sqlite3

app = Flask(__name__)
DB_PATH = '/media/juan/HMI/HMI.db'

# Función para obtener el último registro
def get_last_row():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datos ORDER BY fecha_hora DESC, id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    else:
        return {}

def get_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Intentar traer power_red, si no existe, poner 0
    try:
        cursor.execute("""
            SELECT fecha_hora,
                   COALESCE(low_power_output_i1, 0), 
                   COALESCE(low_power_output_i2, 0), 
                   COALESCE(Charging_Power_solar, 0),
                   COALESCE(power_red, 0)
            FROM datos
            ORDER BY fecha_hora ASC
        """)
    except sqlite3.OperationalError:
        cursor.execute("""
            SELECT fecha_hora,
                   COALESCE(low_power_output_i1, 0), 
                   COALESCE(low_power_output_i2, 0), 
                   COALESCE(Charging_Power_solar, 0),
                   0 as power_red
            FROM datos
            ORDER BY fecha_hora ASC
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def energia_acumulada(datos):
    if len(datos) < 2:
        return 0
    energia = 0
    for i in range(len(datos) - 1):
        dt1, pot1 = datos[i]
        dt2, _ = datos[i+1]
        delta_horas = (dt2 - dt1).total_seconds() / 3600.0
        energia += pot1 * delta_horas
    return energia

def calcular_estadisticas():
    rows = get_data()

    # Agrupar por mes para cada flujo
    datos_carga_mes = defaultdict(list)
    datos_solar_mes = defaultdict(list)
    datos_red_mes = defaultdict(list)

    for fecha_str, low1, low2, solar, red in rows:
        dt = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
        key_mes = (dt.year, dt.month)
        pot_carga = (low1 or 0) + (low2 or 0)
        pot_solar = solar or 0
        pot_red = red or 0

        datos_carga_mes[key_mes].append((dt, pot_carga))
        datos_solar_mes[key_mes].append((dt, pot_solar))
        datos_red_mes[key_mes].append((dt, pot_red))

    # Estadísticas genéricas por mes
    def estadisticas_por_mes(datos_por_mes):
        energias_mensuales = {}
        pot_max_mensual = {}
        pot_prom_mensual = {}
        acumulado_mensual = {}
        meses_ordenados = sorted(datos_por_mes.keys())
        acumulado = 0
        for key in meses_ordenados:
            datos = datos_por_mes[key]
            potencias = [r[1] for r in datos]
            energia = energia_acumulada(datos)
            energia = round(energia, 2)
            energias_mensuales[key] = energia
            pot_max_mensual[key] = max(potencias) if potencias else 0
            pot_prom_mensual[key] = round(sum(potencias)/len(potencias), 2) if potencias else 0
            acumulado += energia
            acumulado_mensual[key] = round(acumulado, 2)
        prom_energia_mensual = round(sum(energias_mensuales.values()) / len(energias_mensuales), 2) if energias_mensuales else 0
        return (meses_ordenados, energias_mensuales, pot_max_mensual, pot_prom_mensual, acumulado_mensual, prom_energia_mensual)

    # Cálculos carga
    (meses_carga, energias_mensuales_carga, pot_max_mensual_carga,
     pot_prom_mensual_carga, acumulado_mensual_carga, prom_energia_mensual_carga) = estadisticas_por_mes(datos_carga_mes)

    # Cálculos solar
    (meses_solar, energias_mensuales_solar, pot_max_mensual_solar,
     pot_prom_mensual_solar, acumulado_mensual_solar, prom_energia_mensual_solar) = estadisticas_por_mes(datos_solar_mes)

    # Cálculos red
    (meses_red, energias_mensuales_red, pot_max_mensual_red,
     pot_prom_mensual_red, acumulado_mensual_red, prom_energia_mensual_red) = estadisticas_por_mes(datos_red_mes)

    # Empaquetar resultados
    return {
        "meses_carga": meses_carga,
        "energias_mensuales_carga": energias_mensuales_carga,
        "pot_max_mensual_carga": pot_max_mensual_carga,
        "pot_prom_mensual_carga": pot_prom_mensual_carga,
        "acumulado_mensual_carga": acumulado_mensual_carga,
        "prom_energia_mensual_carga": prom_energia_mensual_carga,
        "meses_solar": meses_solar,
        "energias_mensuales_solar": energias_mensuales_solar,
        "pot_max_mensual_solar": pot_max_mensual_solar,
        "pot_prom_mensual_solar": pot_prom_mensual_solar,
        "acumulado_mensual_solar": acumulado_mensual_solar,
        "prom_energia_mensual_solar": prom_energia_mensual_solar,
        "meses_red": meses_red,
        "energias_mensuales_red": energias_mensuales_red,
        "pot_max_mensual_red": pot_max_mensual_red,
        "pot_prom_mensual_red": pot_prom_mensual_red,
        "acumulado_mensual_red": acumulado_mensual_red,
        "prom_energia_mensual_red": prom_energia_mensual_red
    }

@app.route("/")
def index():
    registro = get_last_row()
    estadisticas = calcular_estadisticas()
    now = datetime.now()
    mes_actual_key = (now.year, now.month)
    # Obtenemos los valores del mes actual
    datos_mes_actual = {
        "mes": f"{now.year}-{now.month:02d}",
        "energia_carga": estadisticas["energias_mensuales_carga"].get(mes_actual_key, 0),
        "pot_max_carga": estadisticas["pot_max_mensual_carga"].get(mes_actual_key, 0),
        "pot_prom_carga": estadisticas["pot_prom_mensual_carga"].get(mes_actual_key, 0),
        "acumulado_carga": estadisticas["acumulado_mensual_carga"].get(mes_actual_key, 0),

        "energia_solar": estadisticas["energias_mensuales_solar"].get(mes_actual_key, 0),
        "pot_max_solar": estadisticas["pot_max_mensual_solar"].get(mes_actual_key, 0),
        "pot_prom_solar": estadisticas["pot_prom_mensual_solar"].get(mes_actual_key, 0),
        "acumulado_solar": estadisticas["acumulado_mensual_solar"].get(mes_actual_key, 0),

        "energia_red": estadisticas["energias_mensuales_red"].get(mes_actual_key, 0),
        "pot_max_red": estadisticas["pot_max_mensual_red"].get(mes_actual_key, 0),
        "pot_prom_red": estadisticas["pot_prom_mensual_red"].get(mes_actual_key, 0),
        "acumulado_red": estadisticas["acumulado_mensual_red"].get(mes_actual_key, 0),
    }
    return render_template("index.html", registro=registro, datos_mes_actual=datos_mes_actual)

@app.route("/ultimo_registro")
def ultimo_registro():
    registro = get_last_row()
    return jsonify(registro)

@app.route("/estadisticas_mes_actual")
def estadisticas_mes_actual():
    estadisticas = calcular_estadisticas()
    now = datetime.now()
    mes_actual_key = (now.year, now.month)
    datos_mes_actual = {
        "mes": f"{now.year}-{now.month:02d}",
        "energia_carga": estadisticas["energias_mensuales_carga"].get(mes_actual_key, 0),
        "pot_max_carga": estadisticas["pot_max_mensual_carga"].get(mes_actual_key, 0),
        "pot_prom_carga": estadisticas["pot_prom_mensual_carga"].get(mes_actual_key, 0),
        "acumulado_carga": estadisticas["acumulado_mensual_carga"].get(mes_actual_key, 0),

        "energia_solar": estadisticas["energias_mensuales_solar"].get(mes_actual_key, 0),
        "pot_max_solar": estadisticas["pot_max_mensual_solar"].get(mes_actual_key, 0),
        "pot_prom_solar": estadisticas["pot_prom_mensual_solar"].get(mes_actual_key, 0),
        "acumulado_solar": estadisticas["acumulado_mensual_solar"].get(mes_actual_key, 0),

        "energia_red": estadisticas["energias_mensuales_red"].get(mes_actual_key, 0),
        "pot_max_red": estadisticas["pot_max_mensual_red"].get(mes_actual_key, 0),
        "pot_prom_red": estadisticas["pot_prom_mensual_red"].get(mes_actual_key, 0),
        "acumulado_red": estadisticas["acumulado_mensual_red"].get(mes_actual_key, 0),
    }
    return jsonify(datos_mes_actual)

if __name__ == "__main__":
    app.run(debug=True)