from flask import Flask, render_template, jsonify, request, send_file
from flask_caching import Cache
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3
import os
import pandas as pd
import io

app = Flask(__name__)
DB_PATH = '/media/krillbox/HMI/HMI.db'
#DB_PATH = "/home/juan/Downloads/ProyectoIndustrial/HMI.db"

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 10 # segundos
cache = Cache(app)


def crear_conexion():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=15)
        return conn
    except sqlite3.Error as e:
        return None

#------------------------Funciones Principales-----------------------------------------
def convertir_claves_a_string(diccionario):
    return {f"{k[0]:04d}-{k[1]:02d}": v for k, v in diccionario.items()}


def calcular_energia_por_fuente(data):
    # Acumuladores y series a graficar
    energia_red, energia_solar, energia_bateria, energia_carga = [], [], [], []
    tiempos = []
    # Valores acumulados
    acum_red = acum_solar = acum_bat = acum_carga = 0.0
    # Asume que los registros están ordenados cronológicamente (por query_datos)
    for i in range(1, len(data)):
        t0 = datetime.fromisoformat(data[i-1]["fecha_hora"])
        t1 = datetime.fromisoformat(data[i]["fecha_hora"])
        dt_horas = (t1 - t0).total_seconds() / 3600.0 # intervalo en horas
        # Potencias instantáneas (pueden ser None, usa 0 si es así)
        p_red = data[i]["power_red"] or 0
        p_solar = data[i]["Charging_Power_solar"] or 0
        p_bat = data[i]["power_bat"] or 0
        p_carga = data[i]["power_carga"] or 0
        # Energía en el intervalo (Wh)
        e_red = round(p_red * dt_horas,1)
        e_solar = round(p_solar * dt_horas,1)
        e_bat =round( p_bat * dt_horas,1)
        e_carga = round(p_carga * dt_horas,1)
        # Acumula
        acum_red += e_red
        acum_solar += e_solar
        acum_bat += e_bat
        acum_carga += e_carga
        # Guarda para graficar
        tiempos.append(data[i]["fecha_hora"])
        energia_red.append(acum_red)
        energia_solar.append(acum_solar)
        energia_bateria.append(acum_bat)
        energia_carga.append(acum_carga)
    return tiempos, energia_red, energia_solar, energia_bateria, energia_carga

# Función para obtener el último registro
def get_last_row():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datos ORDER BY fecha_hora DESC, id DESC LIMIT 1")
    row = cursor.fetchone()
    suma=0
    conn.close()
    if row:
        celdas=["Voltage_cell_1_bat", "Voltage_cell_2_bat", "Voltage_cell_3_bat", "Voltage_cell_4_bat", "Voltage_cell_5_bat",
                "Voltage_cell_6_bat", "Voltage_cell_7_bat", "Voltage_cell_8_bat", "Voltage_cell_9_bat", "Voltage_cell_10_bat", "Voltage_cell_11_bat",
                "Voltage_cell_12_bat", "Voltage_cell_13_bat", "Voltage_cell_14_bat"]
        row=dict(row)
        power_apparent_carga=row.get("low_apparent_power_i1")+row.get("low_apparent_power_i2")
        fp=round((row.get("power_carga")/power_apparent_carga),1)
        row["power_apparent_carga"]=round(power_apparent_carga,1)
        row["fp"]=fp
        for dato in row:
            if dato in celdas:
                suma=suma+row[dato]
        vol_prom_celda=round(suma/len(celdas),2)
        row["vol_prom_celda"]=vol_prom_celda
        row["voltage_output_i1"] = round(float(row["voltage_output_i1"]), 1) if row.get("voltage_output_i1") is not None else None
        if "power_red" in row and row["power_red"] is not None: 
            row["power_red"] = round(float(row["power_red"]), 1)
        
        return row
    else:
        return {}

#Funcion que calcula la energia acumulada en un rango de tiempo determinado por
# los mismos datos
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

# Funcion que calcula la potencia promedio, la potencia maxima y la energia por mes
# Para calcular los datos por mes de la carga, la energia solar, la red y lo que se desee
def Estadisticas_Mensuales(data):       
    potencias = [r[1] for r in data]
    energia = round(energia_acumulada(data),2)
    pot_max_mensual = max(potencias) if potencias else 0
    pot_prom_mensual = round(sum(potencias)/len(potencias), 2) if potencias else 0
    return (pot_max_mensual, pot_prom_mensual, energia)

#Funcion que calcula la potencia promedio, la potencia maxima y la energia por dia
#Para calcular los datos diarios de la carga, la energia solar, la red y lo que se desee
def estadisticas_por_dia(datos_por_dia, dias=7):
    energias_diarias = {}
    pot_max_diaria = {}
    pot_prom_diaria = {}
    acumulado_diario = {}
    fechas_ordenadas = sorted(datos_por_dia.keys())
    fechas_a_considerar = fechas_ordenadas[-dias:] if dias < len(fechas_ordenadas) else fechas_ordenadas
    acumulado = 0
    for key in fechas_a_considerar:
        datos = datos_por_dia[key]
        potencias = [r[1] for r in datos]
        energia = energia_acumulada(datos)
        energia = round(energia, 2)
        energias_diarias[key] = energia
        pot_max_diaria[key] = max(potencias) if potencias else 0
        pot_prom_diaria[key] = round(sum(potencias)/len(potencias), 2) if potencias else 0
        acumulado += energia
        acumulado_diario[key] = round(acumulado, 2)
    prom_energia_diaria = round(sum(energias_diarias.values()) / len(energias_diarias), 2) if energias_diarias else 0
    return (fechas_a_considerar, energias_diarias, pot_max_diaria, pot_prom_diaria, acumulado_diario, prom_energia_diaria)

#Funcion que obtiene los datos del mes actual
def get_data_month_actual():
    fecha_actual = datetime.now()
    year_month_actual = fecha_actual.strftime('%Y-%m') 
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("""
            SELECT fecha_hora,
                   COALESCE(power_carga, 0) AS power_carga,
                   COALESCE(Charging_Power_solar, 0) AS Charging_Power_solar,
                   COALESCE(power_red, 0) AS power_red,
                   COALESCE(power_bat, 0) AS power_bat
            FROM datos
            WHERE strftime('%Y-%m', fecha_hora) = ?
            ORDER BY fecha_hora ASC
        """, (year_month_actual,))
        
    rows_month_actual = cursor.fetchall()
    conn.close()
    return rows_month_actual

def get_data_month():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT año, mes, energia_carga, energia_solar, energia_red, energia_bat,
               pot_max_carga, pot_prom_carga, pot_max_solar, pot_prom_solar,
               pot_max_red, pot_prom_red, pot_max_bat, pot_prom_bat
        FROM resumen_mensual
        ORDER BY año DESC, mes DESC
        LIMIT 12
    """)
    rows = cursor.fetchall()
    conn.close()
    row=rows[::-1]

    fecha=[]
    energia_carga=[]
    energia_solar=[]
    energia_red=[]
    energia_bat=[]
    pot_max_carga=[]
    pot_prom_carga=[]
    pot_max_solar=[]
    pot_prom_solar=[]
    pot_max_red=[]
    pot_prom_red=[]
    pot_max_bat=[]
    pot_prom_bat=[]

    try:
        response_data={
            "año":0, 
            "mes":0, 
            "energia_carga":0, 
            "energia_solar":0, 
            "energia_red":0, 
            "energia_bat":0,
            "pot_max_carga":0, 
            "pot_prom_carga":0, 
            "pot_max_solar":0, 
            "pot_prom_solar":0,
            "pot_max_red":0, 
            "pot_prom_red":0, 
            "pot_max_bat":0, 
            "pot_prom_bat":0
        }

        meses = [ "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        energia_anual_carga=0
        energia_anual_solar=0
        energia_anual_red=0
        energia_anual_bat=0

        for item in row:
            nombre_mes = meses[item[1] - 1]
            fecha.append(f"{nombre_mes} {item[0]}")

            energia_carga.append(item[2])
            energia_solar.append(item[3])
            energia_red.append(item[4])
            energia_bat.append(item[5])
            pot_max_carga.append(item[6])
            pot_prom_carga.append(item[7])
            pot_max_solar.append(item[8])
            pot_prom_solar.append(item[9])
            pot_max_red.append(item[10])
            pot_prom_red.append(item[11])
            pot_max_bat.append(item[12])
            pot_prom_bat.append(item[13])
            energia_anual_carga+=item[2]
            energia_anual_solar+=item[3]
            energia_anual_red+=item[4]
            energia_anual_bat+=item[5]

        prom_energia_mensual_carga=round(energia_anual_carga/12,1)
        prom_energia_mensual_solar=round(energia_anual_solar/12,1)
        prom_energia_mensual_red=round(energia_anual_red/12,1)
        prom_energia_mensual_bat=round(energia_anual_bat/12,1)

        
        datos = {
            "fecha":fecha,
            "energia_carga":energia_carga,
            "energia_solar":energia_solar,
            "energia_red":energia_red,
            "energia_bat":energia_bat,
            "pot_max_carga":pot_max_carga,
            "pot_prom_carga":pot_prom_carga,
            "pot_max_solar":pot_max_solar,
            "pot_prom_solar":pot_prom_solar,
            "pot_max_red":pot_max_red,
            "pot_prom_red":pot_prom_red,
            "pot_max_bat":pot_max_bat,
            "pot_prom_bat":pot_prom_bat,
            "energia_anual_carga":energia_anual_carga,
            "energia_anual_solar":energia_anual_solar,
            "energia_anual_red":energia_anual_red,
            "energia_anual_bat":energia_anual_bat,
            "prom_energia_mensual_carga":prom_energia_mensual_carga,
            "prom_energia_mensual_solar":prom_energia_mensual_solar,
            "prom_energia_mensual_red":prom_energia_mensual_red,
            "prom_energia_mensual_bat":prom_energia_mensual_bat
        }

        return datos
    except:
        return response_data

def query_datos():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Últimos 100 registros
    query = """
        SELECT fecha_hora,
        voltage_output_i1, frecuency_output_i1, current_output_i1,
        voltage_output_i2, frecuency_output_i2, current_output_i2,
        Current_bat, Voltage_bat, Voltage_Bus_DC_CF, Load_Current_CF,
        Voltage_PV_solar, Charging_Current_solar, Charging_Power_solar,
        power_red, power_carga, voltage_ac, current_carga, current_ac, power_bat
        FROM datos
        ORDER BY fecha_hora DESC
        LIMIT 100
    """
    cursor.execute(query)
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    # Devuelve en orden cronológico
    return data[::-1]

#Funcion para calcular las estadisticas mensuales y diarias necesarias
def calcular_estadisticas():
    rows = get_data_month_actual() # Ahora devuelve lista de diccionarios

    # Agrupa por dia
    datos_carga_diario = defaultdict(list)
    datos_solar_diario = defaultdict(list)
    datos_red_diario = defaultdict(list)
    datos_bat_diario = defaultdict(list)

    datos_carga_mes = []
    datos_solar_mes = []
    datos_red_mes = []
    datos_bat_mes = []

        
    for item in rows: # Iterar sobre diccionarios
        dt_obj = datetime.strptime(item["fecha_hora"], '%Y-%m-%d %H:%M:%S')


        datos_carga_mes.append((dt_obj, item["power_carga"] or 0))
        datos_solar_mes.append((dt_obj, item["Charging_Power_solar"] or 0))
        datos_red_mes.append((dt_obj, item["power_red"] or 0))
        datos_bat_mes.append((dt_obj, item["power_bat"] or 0))

        # Agrupación por día
        key_dia = dt_obj.strftime('%Y-%m-%d')
        datos_carga_diario[key_dia].append((dt_obj, item["power_carga"] or 0))
        datos_solar_diario[key_dia].append((dt_obj, item["Charging_Power_solar"] or 0))
        datos_red_diario[key_dia].append((dt_obj, item["power_red"] or 0))
        datos_bat_diario[key_dia].append((dt_obj, item["power_bat"] or 0))

    # Cálculos carga por día
    (fechas_diarias_carga, energias_diarias_carga_dict, pot_max_diaria_carga,
     pot_prom_diaria_carga, acumulado_diario_carga, prom_energia_diaria_carga) = estadisticas_por_dia(datos_carga_diario, dias=7)

    # Cálculos solar por día
    (fechas_diarias_solar, energias_diarias_solar_dict, pot_max_diaria_solar,
     pot_prom_diaria_solar, acumulado_diario_solar, prom_energia_diaria_solar) = estadisticas_por_dia(datos_solar_diario, dias=7)

    # Cálculos red por día
    (fechas_diarias_red, energias_diarias_red_dict, pot_max_diaria_red,
     pot_prom_diaria_red, acumulado_diario_red, prom_energia_diaria_red) = estadisticas_por_dia(datos_red_diario, dias=7)

    # Caluclos bat por dia
    (fechas_diarias_bat, energias_diarias_bat_dict, pot_max_diaria_bat,
     pot_prom_diaria_bat, acumulado_diario_bat, prom_energia_diaria_bat) = estadisticas_por_dia(datos_bat_diario, dias=7)

    (pot_max_mensual_carga, pot_prom_mensual_carga, energia_carga) = Estadisticas_Mensuales(datos_carga_mes)
    (pot_max_mensual_solar, pot_prom_mensual_solar, energia_solar) = Estadisticas_Mensuales(datos_solar_mes)
    (pot_max_mensual_red, pot_prom_mensual_red, energia_red) = Estadisticas_Mensuales(datos_red_mes)
    (pot_max_mensual_bat, pot_prom_mensual_bat, energia_bat) = Estadisticas_Mensuales(datos_bat_mes)



    # Empaquetar resultados
    return {
        "pot_max_mensual_carga": pot_max_mensual_carga,
        "pot_prom_mensual_carga": pot_prom_mensual_carga,
        "energia_carga": energia_carga,

        "pot_max_mensual_solar": pot_max_mensual_solar,
        "pot_prom_mensual_solar": pot_prom_mensual_solar,
        "energia_solar": energia_solar,

        "pot_max_mensual_red": pot_max_mensual_red,
        "pot_prom_mensual_red": pot_prom_mensual_red,
        "energia_red": energia_red,

        "pot_max_mensual_bat": pot_max_mensual_bat,
        "pot_prom_mensual_bat": pot_prom_mensual_bat,
        "energia_bat": energia_bat,

        "fechas_diarias_carga":fechas_diarias_carga, 
        "energias_diarias_carga_dict":energias_diarias_carga_dict, 
        "pot_max_diaria_carga":pot_max_diaria_carga,
        "pot_prom_diaria_carga":pot_prom_diaria_carga, 
        "acumulado_diario_carga":acumulado_diario_carga, 
        "prom_energia_diaria_carga":prom_energia_diaria_carga,

        "fechas_diarias_solar":fechas_diarias_solar, 
        "energias_diarias_solar_dict":energias_diarias_solar_dict, 
        "pot_max_diaria_solar":pot_max_diaria_solar,
        "pot_prom_diaria_solar":pot_prom_diaria_solar, 
        "acumulado_diario_solar":acumulado_diario_solar, 
        "prom_energia_diaria_solar":prom_energia_diaria_solar,

        "fechas_diarias_red":fechas_diarias_red, 
        "energias_diarias_red_dict":energias_diarias_red_dict, 
        "pot_max_diaria_red":pot_max_diaria_red,
        "pot_prom_diaria_red":pot_prom_diaria_red, 
        "acumulado_diario_red":acumulado_diario_red, 
        "prom_energia_diaria_red":prom_energia_diaria_red,

        "fechas_diarias_bat":fechas_diarias_bat, 
        "energias_diarias_bat_dict":energias_diarias_bat_dict, 
        "pot_max_diaria_bat":pot_max_diaria_bat,
        "pot_prom_diaria_bat":pot_prom_diaria_bat, 
        "acumulado_diario_bat":acumulado_diario_bat, 
        "prom_energia_diaria_bat":prom_energia_diaria_bat

    }
#---------------------------Rutas------------------------------------------------

def calcular_indicadores_alarmas(fecha_inicio, fecha_fin):
    """
    Calcula MTBF, MTTR y Disponibilidad usando los registros de eventos_sistema.
    Considera todas las columnas alarma1...alarma84.
    """
    conn = crear_conexion()
    cursor = conn.cursor()
    alarm_columns = [f"alarma{i}" for i in range(1, 85)]

    query = f"""
        SELECT fecha_hora, {", ".join(alarm_columns)}
        FROM eventos_sistema
        WHERE fecha_hora BETWEEN ? AND ?
        ORDER BY fecha_hora ASC
    """
    cursor.execute(query, (fecha_inicio, fecha_fin))
    rows = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]

    estado_anterior = "None"
    inicio_alarma = None
    lista_mttr = []
    lista_mtbf = []
    tiempo_total = 0
    tiempo_en_falla = 0
    ultima_fin = None

    # Si no hay registros, devuelve ceros
    if not rows:
        return {"mtbf": 0, "mttr": 0, "disponibilidad": 100}

    # Recorrer registros
    for idx, fila in enumerate(rows):
        fecha_hora = datetime.strptime(fila[0], "%Y-%m-%d %H:%M:%S")
        alarmas = fila[1:]
        hay_alarma = any(a and a != "None" for a in alarmas)

        # Detecta cambio de estado
        if estado_anterior == "None" and hay_alarma:
            # Inicio de alarma
            inicio_alarma = fecha_hora
            if ultima_fin:
                lista_mtbf.append((inicio_alarma - ultima_fin).total_seconds())
            estado_anterior = "alarma"
        elif estado_anterior == "alarma" and not hay_alarma:
            # Fin de alarma
            fin_alarma = fecha_hora
            if inicio_alarma:
                duracion = (fin_alarma - inicio_alarma).total_seconds()
                lista_mttr.append(duracion)
                tiempo_en_falla += duracion
                ultima_fin = fin_alarma
            estado_anterior = "None"

        # Para tiempo total
        if idx > 0:
            delta = (fecha_hora - datetime.strptime(rows[idx-1][0], "%Y-%m-%d %H:%M:%S")).total_seconds()
            tiempo_total += delta

    # Si terminó la consulta con alarma activa, calcula hasta el final
    if estado_anterior == "alarma" and inicio_alarma:
        fin_alarma = datetime.strptime(rows[-1][0], "%Y-%m-%d %H:%M:%S")
        duracion = (fin_alarma - inicio_alarma).total_seconds()
        lista_mttr.append(duracion)
        tiempo_en_falla += duracion

    # Convertir segundos a horas
    mtbf = round(sum(lista_mtbf)/len(lista_mtbf)/3600, 2) if lista_mtbf else 0
    mttr = round(sum(lista_mttr)/len(lista_mttr)/3600, 2) if lista_mttr else 0
    disponibilidad = round(100 * (tiempo_total - tiempo_en_falla) / tiempo_total, 2) if tiempo_total > 0 else 100

    conn.close()
    return {
        "mtbf": mtbf,
        "mttr": mttr,
        "disponibilidad": disponibilidad
    }


#-------------------------------------------------------------------------

@app.route("/")
def index():
    registro = get_last_row()
    datos_mensuales= get_data_month()
    estadisticas = calcular_estadisticas()
    now = datetime.now()
    # Obtenemos los valores del mes actual
    datos_mes_actual = {
        # Datos mensuales de la carga
        "mes": f"{now.year}-{now.month:02d}",
        "pot_max_mensual_carga": estadisticas["pot_max_mensual_carga"],
        "pot_prom_mensual_carga": estadisticas["pot_prom_mensual_carga"],
        "energia_carga": estadisticas["energia_carga"],

        "pot_max_mensual_solar": estadisticas["pot_max_mensual_solar"],
        "pot_prom_mensual_solar": estadisticas["pot_prom_mensual_solar"],
        "energia_solar": estadisticas["energia_solar"],

        "pot_max_mensual_red": estadisticas["pot_max_mensual_red"],
        "pot_prom_mensual_red": estadisticas["pot_prom_mensual_red"],
        "energia_red": estadisticas["energia_red"],

        "pot_max_mensual_bat": estadisticas["pot_max_mensual_bat"],
        "pot_prom_mensual_bat": estadisticas["pot_prom_mensual_bat"],
        "energia_bat": estadisticas["energia_bat"]

    }
    datos_diarios={
        #Datos diarios de la carga
        "fechas_diarias_carga":estadisticas["fechas_diarias_carga"], 
        "energias_diarias_carga_dict":estadisticas["energias_diarias_carga_dict"], 
        "pot_max_diaria_carga":estadisticas["pot_max_diaria_carga"],
        "pot_prom_diaria_carga":estadisticas["pot_prom_diaria_carga"], 
        "acumulado_diario_carga":estadisticas["acumulado_diario_carga"], 
        "prom_energia_diaria_carga":int(round(estadisticas["prom_energia_diaria_carga"])),
        # Datos diarios solares
        "fechas_diarias_solar":estadisticas["fechas_diarias_solar"], 
        "energias_diarias_solar_dict":estadisticas["energias_diarias_solar_dict"], 
        "pot_max_diaria_solar":estadisticas["pot_max_diaria_solar"],
        "pot_prom_diaria_solar":estadisticas["pot_prom_diaria_solar"], 
        "acumulado_diario_solar":estadisticas["acumulado_diario_solar"], 
        "prom_energia_diaria_solar":int(round(estadisticas["prom_energia_diaria_solar"])),
        # Datoa diarios de la red
        "fechas_diarias_red":estadisticas["fechas_diarias_red"], 
        "energias_diarias_red_dict":estadisticas["energias_diarias_red_dict"], 
        "pot_max_diaria_red":estadisticas["pot_max_diaria_red"],
        "pot_prom_diaria_red":estadisticas["pot_prom_diaria_red"], 
        "acumulado_diario_red":estadisticas["acumulado_diario_red"], 
        "prom_energia_diaria_red":int(round(estadisticas["prom_energia_diaria_red"])),
        # Datos diarios de la bateria
        "fechas_diarias_bat":estadisticas["fechas_diarias_bat"], 
        "energias_diarias_bat_dict":estadisticas["energias_diarias_bat_dict"], 
        "pot_max_diaria_bat":estadisticas["pot_max_diaria_bat"],
        "pot_prom_diaria_bat":estadisticas["pot_prom_diaria_bat"], 
        "acumulado_diario_bat":estadisticas["acumulado_diario_bat"], 
        "prom_energia_diaria_bat":int(round(estadisticas["prom_energia_diaria_bat"]))

    }

    return render_template("index.html", registro=registro, datos_mes_actual=datos_mes_actual,datos_diarios=datos_diarios, datos_mensuales=datos_mensuales)

@app.route("/ultimo_registro")
def ultimo_registro():
    registro = get_last_row()
    return jsonify(registro)

@app.route('/datos_mensuales')
@cache.cached(timeout=20)
def datos_mensuales():
    datos=get_data_month()
    return jsonify(datos)


@app.route("/datos_graficar")
def datos_graficar():
    try:
        datos_crudos = query_datos()
        
        response_data = {
            'labels': [],
            'voltage_output_i1': [],
            'frecuency_output_i1': [],
            'current_output_i1': [],
            'voltage_output_i2': [],
            'frecuency_output_i2': [],
            'current_output_i2': [],
            'Current_bat': [],
            'Voltage_bat': [],
            'Voltage_Bus_DC_CF': [],
            'Load_Current_CF': [],
            'Voltage_PV_solar': [],
            'Charging_Current_solar': [],
            'Charging_Power_solar': [],
            'power_red': [],
            'power_carga': [],
            'voltage_ac': [],
            'current_carga': [],
            'current_ac': [],
            'power_bat': []
        }

        if datos_crudos:

            (tiempos, energia_red, energia_solar, energia_bateria, energia_carga)=calcular_energia_por_fuente(datos_crudos)

            df = pd.DataFrame(datos_crudos)
            # **Línea corregida:** Convertir la columna 'fecha_hora' a tipo datetime
            df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
            df = df.where(pd.notna(df), None)

            for column in df.columns:
                if column == 'fecha_hora':
                    response_data['labels'] = df[column].dt.strftime('%H:%M:%S').tolist()
                elif column in response_data:
                    response_data[column] = df[column].tolist()
            response_data['tiempos'] = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S") for t in tiempos]
            response_data['energia_red']=energia_red
            response_data['energia_solar']= energia_solar
            response_data['energia_bateria']= energia_bateria
            response_data['energia_carga']= energia_carga

        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error al procesar los datos para el gráfico: {e}")
        return jsonify({}), 500

@app.route("/estadisticas_mes_actual")
@cache.cached(timeout=10)
def estadisticas_mes_actual():
    estadisticas = calcular_estadisticas()
    now = datetime.now()
    datos_mes_actual = {
        "mes": f"{now.year}-{now.month:02d}",
        "pot_max_mensual_carga": estadisticas["pot_max_mensual_carga"],
        "pot_prom_mensual_carga": estadisticas["pot_prom_mensual_carga"],
        "energia_carga": estadisticas["energia_carga"],

        "pot_max_mensual_solar": estadisticas["pot_max_mensual_solar"],
        "pot_prom_mensual_solar": estadisticas["pot_prom_mensual_solar"],
        "energia_solar": estadisticas["energia_solar"],

        "pot_max_mensual_red": estadisticas["pot_max_mensual_red"],
        "pot_prom_mensual_red": estadisticas["pot_prom_mensual_red"],
        "energia_red": estadisticas["energia_red"],

        "pot_max_mensual_bat": estadisticas["pot_max_mensual_bat"],
        "pot_prom_mensual_bat": estadisticas["pot_prom_mensual_bat"],
        "energia_bat": estadisticas["energia_bat"]

    }
    return jsonify(datos_mes_actual)

@app.route("/estadisticas_diarias")
@cache.cached(timeout=10)
def estadisticas_diarias():
    estadisticas = calcular_estadisticas()
    datos_diarios={
        "fechas_a_considerar_carga":estadisticas["fechas_diarias_carga"],
        "energias_diarias_carga":estadisticas["energias_diarias_carga_dict"],
        "pot_max_diaria_carga":estadisticas["pot_max_diaria_carga"],
        "pot_prom_diaria_carga":estadisticas["pot_prom_diaria_carga"],
        "acumulado_diario_carga":estadisticas["acumulado_diario_carga"],
        "prom_energia_diaria_carga":estadisticas["prom_energia_diaria_carga"],

        "fechas_a_considerar_solar":estadisticas["fechas_diarias_solar"],
        "energias_diarias_solar":estadisticas["energias_diarias_solar_dict"],
        "pot_max_diaria_solar":estadisticas["pot_max_diaria_solar"],
        "pot_prom_diaria_solar":estadisticas["pot_prom_diaria_solar"],
        "acumulado_diario_solar":estadisticas["acumulado_diario_solar"],
        "prom_energia_diaria_solar":estadisticas["prom_energia_diaria_solar"],

        "fechas_a_considerar_bat":estadisticas["fechas_diarias_bat"],
        "energias_diarias_bat":estadisticas["energias_diarias_bat_dict"],
        "pot_max_diaria_bat":estadisticas["pot_max_diaria_bat"],
        "pot_prom_diaria_bat":estadisticas["pot_prom_diaria_bat"],
        "acumulado_diario_bat":estadisticas["acumulado_diario_bat"],
        "prom_energia_diaria_bat":estadisticas["prom_energia_diaria_bat"],

        "fechas_a_considerar_red":estadisticas["fechas_diarias_red"],
        "energias_diarias_red":estadisticas["energias_diarias_red_dict"],
        "pot_max_diaria_red":estadisticas["pot_max_diaria_red"],
        "pot_prom_diaria_red":estadisticas["pot_prom_diaria_red"],
        "acumulado_diario_red":estadisticas["acumulado_diario_red"],
        "prom_energia_diaria_red":estadisticas["prom_energia_diaria_red"]
    }
    return jsonify(datos_diarios)



@app.route('/curva_solar')
@cache.cached(timeout=10)
def curva_solar():
    fecha = request.args.get('fecha-curva')
    if not fecha:
        return jsonify({"labels": [], "solar": [], "carga": [], "solar2": []})

    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT fecha_hora, Charging_Power_solar, power_carga, Charging_Current_solar, Voltage_PV_solar
        FROM datos
        WHERE date(fecha_hora) = ?
        ORDER BY fecha_hora ASC
    """
    try:
        df = pd.read_sql_query(query, conn, params=(fecha,))
    except Exception as e:
        conn.close()
        print(f"Error al ejecutar la consulta: {e}")
        return jsonify({"labels": [], "solar": [], "carga": [], "solar2": []})
    finally:
        conn.close()

    if df.empty:
        return jsonify({"labels": [], "solar": [], "carga": [], "solar2": []})

    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
    df.set_index('fecha_hora', inplace=True)

    # Nueva columna: potencia solar calculada
    df['Potencia_Solar2'] = df['Charging_Current_solar'] * df['Voltage_PV_solar']

    # Suavizado: remuestreo a 10 minutos
    df_resample = df.resample('10T').mean().reset_index()

    labels = df_resample['fecha_hora'].dt.strftime('%H:%M').tolist()
    solar = df_resample['Charging_Power_solar'].clip(lower=0).fillna(0).round(2).tolist()
    carga = df_resample['power_carga'].clip(lower=0).fillna(0).round(2).tolist()
    solar2 = df_resample['Potencia_Solar2'].clip(lower=0).fillna(0).round(2).tolist()

    return jsonify({"labels": labels, "solar": solar, "carga": carga, "solar2": solar2})

def parse_datetime_local(dt_str):
    # Convierte 'YYYY-MM-DDTHH:MM' a 'YYYY-MM-DD HH:MM:00'
    if dt_str and 'T' in dt_str:
        return dt_str.replace('T', ' ') + ":00"
    return dt_str

@app.route("/notificaciones", methods=['GET'])
@cache.cached(timeout=30)
def get_alarmas():
    try:
        conn = crear_conexion()
        if not conn:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        
        cursor = conn.cursor()
        
        fecha_inicio_str = request.args.get('start_date')
        fecha_fin_str = request.args.get('end_date')

        # ------- CORRECCION DE FORMATO ---------
        fecha_inicio_str = parse_datetime_local(fecha_inicio_str)
        fecha_fin_str = parse_datetime_local(fecha_fin_str)

        if not fecha_inicio_str or not fecha_fin_str:
            today = datetime.now().strftime('%Y-%m-%d')
            fecha_inicio_str = f"{today} 00:00:00"
            fecha_fin_str = f"{today} 23:59:59"

        #--------------------Consulta de alarmas activas--------------------
        query = "SELECT fecha_hora, "
        alarm_columns = [f"alarma{i}" for i in range(1, 85)]
        query += ", ".join(alarm_columns)
        query += " FROM eventos_sistema WHERE fecha_hora BETWEEN ? AND ? ORDER BY fecha_hora DESC"
        params = [fecha_inicio_str, fecha_fin_str]
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
        
        alarmas_activas = []
        for fila in resultados:
            row_dict = dict(zip(columnas, fila))
            for col_name, value in row_dict.items():
                if col_name.startswith('alarma') and value and value != "None":
                    alarmas_activas.append({
                        "fecha_hora": row_dict['fecha_hora'],
                        "alarma": value,
                        "codigo_alarma": col_name
                    })

        #--------------------Cálculo de MTBF, MTTR y Disponibilidad--------------------
        indicadores = calcular_indicadores_alarmas(fecha_inicio_str, fecha_fin_str)

        conn.close()
        return render_template("notificaciones.html", 
                               alarmas_activas=alarmas_activas,
                               mtbf=indicadores["mtbf"],
                               mttr=indicadores["mttr"],
                               disponibilidad=indicadores["disponibilidad"],
                               fecha_inicio=fecha_inicio_str,
                               fecha_fin=fecha_fin_str)
    except sqlite3.Error as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500


@app.route("/alarmas_activas", methods=["GET"])
@cache.cached(timeout=30)
def api_alarmas_activas():
    try:
        conn = crear_conexion()
        if not conn:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cursor = conn.cursor()

        fecha_inicio_str = request.args.get('start_date')
        fecha_fin_str = request.args.get('end_date')

        # Si no hay fechas, usa el día actual
        if not fecha_inicio_str or not fecha_fin_str:
            today = datetime.now().strftime('%Y-%m-%d')
            fecha_inicio_str = today
            fecha_fin_str = today

        alarm_columns = [f"alarma{i}" for i in range(1, 85)]
        query = "SELECT fecha_hora, " + ", ".join(alarm_columns)
        query += " FROM eventos_sistema WHERE DATE(fecha_hora) BETWEEN ? AND ? ORDER BY fecha_hora DESC"
        params = [fecha_inicio_str, fecha_fin_str]
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        alarmas_activas = []
        for fila in resultados:
            row_dict = dict(zip(columnas, fila))
            for col_name, value in row_dict.items():
                if col_name.startswith('alarma') and value and value != "None":
                    alarmas_activas.append({
                        "fecha_hora": row_dict['fecha_hora'],
                        "alarma": value,
                        "codigo_alarma": col_name
                    })

        # Indicadores también por rango de fecha
        indicadores = calcular_indicadores_alarmas(
            fecha_inicio_str + " 00:00:00", fecha_fin_str + " 23:59:59"
        )

        conn.close()
        return jsonify({
            "alarmas_activas": alarmas_activas,
            "mtbf": indicadores.get("mtbf", 0),
            "mttr": indicadores.get("mttr", 0),
            "disponibilidad": indicadores.get("disponibilidad", 100)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



from flask import send_file
import io

@app.route("/descargar_csv", methods=["GET"])
def descargar_csv():
    tipo = request.args.get('tipo')
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    if tipo in ["datos", "eventos"] and date_start and date_end:
        fecha_inicio = f"{date_start} 00:00:00"
        fecha_fin = f"{date_end} 23:59:59"

    if tipo == "datos" and date_start and date_end:
        query = """
            SELECT * FROM datos WHERE fecha_hora BETWEEN ? AND ? ORDER BY fecha_hora ASC
        """
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
    elif tipo == "eventos" and date_start and date_end:
        query = """
            SELECT * FROM eventos_sistema WHERE fecha_hora BETWEEN ? AND ? ORDER BY fecha_hora ASC
        """
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
    elif tipo == "resumen_mensual":
        query = """
            SELECT * FROM resumen_mensual ORDER BY año DESC, mes DESC LIMIT 12
        """
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
    else:
        return "Tipo de datos o rango de fechas no válido", 400

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    filename = f"{tipo}_datos.csv"
    return send_file(
    io.BytesIO(csv_buffer.getvalue().encode()),
    mimetype='text/csv',
    as_attachment=True,
    download_name=filename  
)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
