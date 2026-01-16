import sqlite3, time,logging, minimalmodbus, pymodbus,pymodbus.client, struct, datetime, math
from easysnmp import Session
from pymodbus.client import ModbusTcpClient
from register import faults_inverter,faults_solar,alarm_CF,register_inverter,register_solar_controler,battery_registers,CF_registers
from alarms import *
from app import energia_acumulada
from collections import defaultdict

# --- Variables globales ---
#DB_PATH = '/media/krillbox/HMI/HMI.db'
DB_PATH = "/home/krillbox/Descargas/HMI.db"
logger = logging.getLogger(__name__)  # Logger para este módulo

#Configuracion de la comunicacion con los equipos RTU
try:
    #Inversor Izquierdo
    firts_inverter=minimalmodbus.Instrument("/dev/ttyUSB0",1)
    firts_inverter.serial.baudrate=9600
except:
    logger.error("No se pudo configurar el inversor izquierdo")
try:
    #Inversor Derecho
    second_inverter=minimalmodbus.Instrument("/dev/ttyUSB0",2)
    second_inverter.serial.baudrate=9600
except:
    logger.error("No se pudo configurar el inversor derecho")
try:
    #Controlador Solar
    solar_controler=minimalmodbus.Instrument("/dev/ttyUSB0",3)
    solar_controler.serial.baudrate=9600
except:
    logger.error("No se pudo configurar controlador solar")
try:
    #Configuracion de equpos Modbus TCP/IP
    CF = ModbusTcpClient(host='192.168.1.12', port=8023, retries=1, timeout=2 ) 
except:
    logger.error("No se pudo configurar el cuadro de fuerza")
try:
    #Configuracion de equpipos SNMP
    battery= Session(hostname="192.168.1.13", community="public",version=2)
except:
    logger.error("No se pudo configurar la bateria")

def Estadisticas_Mensuales(data):       
    potencias = [r[1] for r in data]
    energia = round(energia_acumulada(data),2)
    pot_max_mensual = max(potencias) if potencias else 0
    pot_prom_mensual = round(sum(potencias)/len(potencias), 2) if potencias else 0
    return (pot_max_mensual, pot_prom_mensual, energia, potencias)

def guardar_resumen_mensual(year, month):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Verifica si ya existe el resumen para ese mes
    cursor.execute("SELECT COUNT(*) FROM resumen_mensual WHERE año=? AND mes=?", (year, month))
    if cursor.fetchone()[0]:
        conn.close()
        print(f"Resumen mensual para {year}-{month:02d} ya existe.")
        return

    # Trae los datos crudos del mes
    cursor.execute("""
        SELECT fecha_hora,
               COALESCE(power_carga, 0) AS power_carga,
               COALESCE(Charging_Power_solar, 0) AS Charging_Power_solar,
               COALESCE(power_red, 0) AS power_red,
               COALESCE(power_bat, 0) AS power_bat
        FROM datos
        WHERE strftime('%Y', fecha_hora) = ? AND strftime('%m', fecha_hora) = ?
        ORDER BY fecha_hora ASC
    """, (str(year), f"{month:02d}"))
    rows = cursor.fetchall()

    datos_carga_mes = []
    datos_solar_mes = []
    datos_red_mes = []
    datos_bat_mes = []

    for item in rows:
        dt_obj = datetime.datetime.strptime(item["fecha_hora"], '%Y-%m-%d %H:%M:%S')
        datos_carga_mes.append((dt_obj, item["power_carga"] or 0))
        datos_solar_mes.append((dt_obj, item["Charging_Power_solar"] or 0))
        datos_red_mes.append((dt_obj, item["power_red"] or 0))
        datos_bat_mes.append((dt_obj, item["power_bat"] or 0))

    pot_max_mensual_carga, pot_prom_mensual_carga, energia_carga = Estadisticas_Mensuales(datos_carga_mes)
    pot_max_mensual_solar, pot_prom_mensual_solar, energia_solar = Estadisticas_Mensuales(datos_solar_mes)
    pot_max_mensual_red, pot_prom_mensual_red, energia_red = Estadisticas_Mensuales(datos_red_mes)
    pot_max_mensual_bat, pot_prom_mensual_bat, energia_bat = Estadisticas_Mensuales(datos_bat_mes)

    cursor.execute("""
        INSERT INTO resumen_mensual (
            año, mes,
            energia_carga, energia_solar, energia_red, energia_bat,
            pot_max_carga, pot_prom_carga, pot_max_solar, pot_prom_solar,
            pot_max_red, pot_prom_red, pot_max_bat, pot_prom_bat
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        year, month,
        energia_carga, energia_solar, energia_red, energia_bat,
        pot_max_mensual_carga, pot_prom_mensual_carga, pot_max_mensual_solar, pot_prom_mensual_solar,
        pot_max_mensual_red, pot_prom_mensual_red, pot_max_mensual_bat, pot_prom_mensual_bat
    ))
    conn.commit()
    conn.close()
    print(f"Resumen mensual guardado para {year}-{month:02d}.")


def setup_logging():
    # Configuración básica
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # También muestra logs en consola
        ]
    )
"""# --- Configuración del logging ---

    # Directorio para logs (si no existe, se crea)
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Archivo de log principal
    log_file = os.path.join(log_dir, "app.log")"""


# --- Funciones principales ---
def crear_conexion():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=15)
        logger.info("Conexión a la base de datos establecida correctamente.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error al conectar a la base de datos: {e}", exc_info=True)
        return None


def fetch_last_event(conn):
    cursor = conn.cursor()
    alarm_cols = [f"alarma{i}" for i in range(1, 85)]
    cols = ", ".join(["id", "fecha_hora"] + alarm_cols)
    cursor.execute(f"SELECT {cols} FROM eventos_sistema ORDER BY fecha_hora DESC, id DESC LIMIT 1")
    row = cursor.fetchone()
    if not row:
        return None
    columns = ["id", "fecha_hora"] + alarm_cols
    return dict(zip(columns, row))


def normalize_alarm_value(v):

    if v is None:
        return None
    s = str(v).strip()
    if s == "" or s.lower() == "none":
        return None
    return s


def should_insert_event(conn, new_alarm_values):
    last = fetch_last_event(conn)
    if last is None:
        return True  

    for i in range(1, 85):
        key = f"alarma{i}"
        new_val = normalize_alarm_value(new_alarm_values.get(key))
        last_val = normalize_alarm_value(last.get(key))
        if new_val != last_val:
            return True 
    return False  

def inicializar_db():
    try: 
        with sqlite3.connect(DB_PATH, timeout=15) as conn:
            conn.execute('PRAGMA journal_mode=WAL;')
            cursor = conn.cursor()
            
            # Verificar y crear tabla 'datos'
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='datos'")
            if not cursor.fetchone():
                cursor.execute('''
                    CREATE TABLE datos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha_hora DATETIME,
                        current_input_i1 REAL,
                        high_power_output_i1 REAL,
                        low_power_output_i1 INTEGER,
                        high_apparent_power_i1 REAL,
                        low_apparent_power_i1 INTEGER,
                        voltage_input_i1 REAL,
                        voltage_output_i1 REAL,
                        frecuency_output_i1 REAL,
                        percentage_load_i1 REAL,
                        current_output_i1 REAL,
                        inv_current_i1 REAL,
                        charging_current_i1 REAL,
                        current_input_i2 REAL,
                        high_power_output_i2 REAL,
                        low_power_output_i2 INTEGER,
                        high_apparent_power_i2 REAL,
                        low_apparent_power_i2 INTEGER,
                        voltage_input_i2 REAL,
                        voltage_output_i2 REAL,
                        frecuency_output_i2 REAL,
                        percentage_load_i2 REAL,
                        current_output_i2 REAL,
                        inv_current_i2 REAL,
                        charging_current_i2 REAL,
                        Current_bat REAL,
                        Voltage_bat REAL,
                        soc_bat INTEGER,
                        soh_bat INTEGER,
                        Max_capacity_bat INTEGER,
                        Nominal_capacity_bat INTEGER,
                        Voltage_cell_1_bat REAL,
                        Voltage_cell_2_bat REAL,
                        Voltage_cell_3_bat REAL,
                        Voltage_cell_4_bat REAL,
                        Voltage_cell_5_bat REAL,
                        Voltage_cell_6_bat REAL,
                        Voltage_cell_7_bat REAL,
                        Voltage_cell_8_bat REAL,
                        Voltage_cell_9_bat REAL,
                        Voltage_cell_10_bat REAL,
                        Voltage_cell_11_bat REAL,
                        Voltage_cell_12_bat REAL,
                        Voltage_cell_13_bat REAL,
                        Voltage_cell_14_bat REAL,
                        ciclos_bat REAL,
                        Temperatura REAL,
                        Voltage_Bus_DC_CF REAL,
                        Load_Current_CF REAL,
                        Capacity_CF INTEGER,
                        Output_Current_CF REAL,
                        Modo_CF REAL,
                        Temperature_CF REAL,
                        StatusG01 REAL,
                        Voltaje_Output_G01 REAL,
                        Current_Output_G01 REAL,
                        Voltage_AC_G01 REAL,
                        Current_AC_G01 REAL,
                        StatusG02 REAL,
                        Voltaje_Output_G02 REAL,
                        Current_Output_G02 REAL,
                        Voltage_AC_G02 REAL,
                        Current_AC_G02 REAL,
                        StatusG188 REAL,
                        Voltaje_Output_G188 REAL,
                        Current_Output_G188 REAL,
                        Voltage_AC_G188 REAL,
                        Current_AC_G188 REAL,
                        Voltage_PV_solar REAL,
                        batery_voltage_solar REAL,
                        Charging_Current_solar REAL,
                        Output_Voltage_solar REAL,
                        Load_Current_solar REAL,
                        Charging_Power_solar REAL,
                        Load_Power_solar REAL,
                        power_solar REAL,
                        power1_solar REAL,
                        autonomia_total TEXT,
                        autonomia_bat TEXT,
                        power_red REAL,
                        power_carga REAL,
                        voltage_ac REAL,
                        current_carga REAL,
                        current_ac REAL,
                        current_inp_inv REAL,
                        power_bat REAL
                    )
                ''')
                logger.info("Tabla 'datos' creada exitosamente.")
            
            # Verificar y crear tabla 'eventos_sistema'
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eventos_sistema'")
            if not cursor.fetchone():
                cursor.execute('''
                    CREATE TABLE eventos_sistema (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha_hora DATETIME,
                        alarma1 TEXT,
                        alarma2 TEXT,
                        alarma3 TEXT,
                        alarma4 TEXT,
                        alarma5 TEXT,
                        alarma6 TEXT,
                        alarma7 TEXT,
                        alarma8 TEXT,
                        alarma9 TEXT,
                        alarma10 TEXT,
                        alarma11 TEXT,
                        alarma12 TEXT,
                        alarma13 TEXT,
                        alarma14 TEXT,
                        alarma15 TEXT,
                        alarma16 TEXT,
                        alarma17 TEXT,
                        alarma18 TEXT,
                        alarma19 TEXT,
                        alarma20 TEXT,
                        alarma21 TEXT,
                        alarma22 TEXT,
                        alarma23 TEXT,
                        alarma24 TEXT,
                        alarma25 TEXT,
                        alarma26 TEXT,
                        alarma27 TEXT,
                        alarma28 TEXT,
                        alarma29 TEXT,
                        alarma30 TEXT,
                        alarma31 TEXT,
                        alarma32 TEXT,
                        alarma33 TEXT,
                        alarma34 TEXT,
                        alarma35 TEXT,
                        alarma36 TEXT,
                        alarma37 TEXT,
                        alarma38 TEXT,
                        alarma39 TEXT,
                        alarma40 TEXT,
                        alarma41 TEXT,
                        alarma42 TEXT,
                        alarma43 TEXT,
                        alarma44 TEXT,
                        alarma45 TEXT,
                        alarma46 TEXT,
                        alarma47 TEXT,
                        alarma48 TEXT,
                        alarma49 TEXT,
                        alarma50 TEXT,
                        alarma51 TEXT,
                        alarma52 TEXT,
                        alarma53 TEXT,
                        alarma54 TEXT,
                        alarma55 TEXT,
                        alarma56 TEXT,
                        alarma57 TEXT,
                        alarma58 TEXT,
                        alarma59 TEXT,
                        alarma60 TEXT,
                        alarma61 TEXT,
                        alarma62 TEXT,
                        alarma63 TEXT,
                        alarma64 TEXT,
                        alarma65 TEXT,
                        alarma66 TEXT,
                        alarma67 TEXT,
                        alarma68 TEXT,
                        alarma69 TEXT,
                        alarma70 TEXT,
                        alarma71 TEXT,
                        alarma72 TEXT,
                        alarma73 TEXT,
                        alarma74 TEXT,
                        alarma75 TEXT,
                        alarma76 TEXT,
                        alarma77 TEXT,
                        alarma78 TEXT,
                        alarma79 TEXT,
                        alarma80 TEXT,
                        alarma81 TEXT,
                        alarma82 TEXT,
                        alarma83 TEXT,
                        alarma84 TEXT                        
                    )
                ''')
                logger.info("Tabla 'eventos_sistema' creada exitosamente.")
            
            # Verificar y crear tabla 'resumen_mensual'
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resumen_mensual'")
            if not cursor.fetchone():
                cursor.execute('''
                    CREATE TABLE resumen_mensual (
                        año INTEGER,
                        mes INTEGER,
                        energia_carga REAL,
                        energia_solar REAL,
                        energia_red REAL,
                        energia_bat REAL,
                        pot_max_carga REAL,
                        pot_prom_carga REAL,
                        pot_max_solar REAL,
                        pot_prom_solar REAL,
                        pot_max_red REAL,
                        pot_prom_red REAL,
                        pot_max_bat REAL,
                        pot_prom_bat REAL,
                        PRIMARY KEY (año, mes)
                    )
                ''')
                logger.info("Tabla 'resumen_mensual' creada exitosamente.")
            
            # Crear índice si no existe
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_eventos_fecha_hora ON eventos_sistema(fecha_hora)")
                conn.commit()
                logger.info("Índice idx_eventos_fecha_hora creado o ya existente.")
            except sqlite3.Error as e:
                logger.warning(f"No se pudo crear índice idx_eventos_fecha_hora: {e}")
            
            conn.commit()
            logger.info("Base de datos inicializada correctamente.")
            
    except sqlite3.Error as e:
        logger.error(f"Error al inicializar la base de datos: {e}", exc_info=True)
        # Imprimir error en consola también para depuración
        print(f"Error SQLite: {e}")
    except Exception as e:
        logger.error(f"Error inesperado al inicializar la base de datos: {e}", exc_info=True)
        print(f"Error inesperado: {e}")

def tabla_existe(nombre_tabla):
    try:
        with sqlite3.connect(DB_PATH, timeout=15) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nombre_tabla,))
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Error al verificar la existencia de la tabla {nombre_tabla}: {e}")
        return False

def insertar_datos():
    conn = None
    datos=[]
    alarmas=[]
    fecha_hora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        conn = crear_conexion()
        if conn is None:
            logger.critical("No se pudo establecer conexión con la base de datos. Terminando ejecución.")
            return
        cursor = conn.cursor()
        logger.info("Iniciando inserción de datos...")
    except:
        logger.error("No se pudo iniciar la insercion de datos (sin conexion con la base de datos)")

        
       
    #Insercion de Datos
    #INVERSOR 1
    for dato in register_inverter: 
        try:
            a=firts_inverter.read_register(register_inverter[dato],0,4)
            try:
                if a>32768:
                    a=a-65536
                if register_inverter[dato]==17 or register_inverter[dato]==23:
                    a = a * 0.01
                if register_inverter[dato]==83:
                    a = a
                else:
                    a=a*0.1
                datos.append(a)
            except:
                logger.error("Error al recolectar datos del inversor 1")
        except:
            a=0
            datos.append(a)
            logger.error(f"No se pudo acceder al registro {register_inverter[dato]}")
        
    
    #INVERSOR 2
    for dato in register_inverter: 
        try:
            b=second_inverter.read_register(register_inverter[dato],0,4)
            
            try:
                if b>32768:
                    b=b-65536
                if register_inverter[dato]==17 or register_inverter[dato]==23:
                    b = b * 0.01
                if register_inverter[dato]==83:
                    b = b
                else:
                    b=b*0.1
                datos.append(b)
            except:
                logger.error("Error al recolectar los datos del inversor 2")
        except:
            b=0
            datos.append(b)
            logger.error(f"No se pudo acceder al registro {register_inverter[dato]}")
        
   
    #Bateria
    for i,dato in zip(range(0,len(battery_registers)),battery_registers):
        try:
            e=battery.get(battery_registers[dato]).value
            try:
                e=float(e)
                datos.append(e)
            except:
                e=battery.get(battery_registers[dato]).value
                datos.append(e)
        except:
            e=0
            datos.append(e)
            logger.error(f"No se puedo acceder al registro {battery_registers[dato]}")

    #CUADRO DE FUERZA
    try:
        if not CF.connect():
            logger.error("No se pudo conectar al Cuadro de Fuerza (CF) por Modbus TCP/IP.")
            # Agrega ceros por cada registro esperado del cuadro de fuerza
            for _ in CF_registers:
                datos.append(0)
        else:
            for data in CF_registers:
                try:
                    result = CF.read_holding_registers(address=CF_registers[data], count=1)
                    d = result.registers[0]
                    try:
                        if d > 32768:
                            d = d - 65536
                        if CF_registers[data] in [0, 2001, 2011, 3871]:
                            d = d / 100
                        if CF_registers[data] in [2002, 2005, 2012, 2015, 3875, 3872]:
                            d = d / 10
                        datos.append(d)
                    except Exception as e:
                        logger.error(f"Error al procesar el dato del cuadro de fuerza: {e}")
                except Exception as e:
                    d = 0
                    datos.append(d)
                    logger.error(f"No se pudo acceder al registro {CF_registers[data]}: {e}")
    finally:
        CF.close() 
       
    
    #CONTROLADOR SOLAR
    for dato in register_solar_controler: 
        try:
            c=solar_controler.read_register(register_solar_controler[dato],0,3)
            try:
                if register_solar_controler[dato]==6 or register_solar_controler[dato]==1 or register_solar_controler[dato]==2 or register_solar_controler[dato]==3 or register_solar_controler[dato]==4:
                    c=c*0.1
                if register_solar_controler[dato]==526:
                    register1=solar_controler.read_register(526,0,3)
                    register2=solar_controler.read_register(527,0,3)
                    bytes=struct.pack(">HH", register1, register2)

                    c=struct.unpack("<f", bytes)[0]
                datos.append(c)
            except:
                logger.error("Error al recoletasr los datos del controlador solar")
            
        except:
            c=0
            datos.append(c)
            logger.error(f"No ser pudo acceder al registro {register_solar_controler[dato]}")

        

    #Manejo de Alarmas
    
    MPPTAlarmDecoder.decode_MPPT(alarmas,faults_solar,logger)
    # CF
    CF.connect()
    GEAlarmDecoder.CF_decode(alarm_CF, alarmas, logger, client=CF)
    CF.close()
    BatteryAlarmDecoder.decode_battery(alarmas,logger)
    InverterAlarmDecoder.decode_inverter(alarmas,faults_inverter,logger)
                                         
    #MPPT
    alarma1=alarmas[0]
    alarma2=alarmas[1]
    alarma3=alarmas[2]
    alarma4=alarmas[3]
    alarma5=alarmas[4]
    alarma6=alarmas[5]
    alarma7=alarmas[6]
    alarma8=alarmas[7]
    alarma9=alarmas[8]
    #CF
    alarma10=alarmas[9]
    alarma11=alarmas[10]
    alarma12=alarmas[11]
    alarma13=alarmas[12]
    alarma14=alarmas[13]
    alarma15=alarmas[14]
    alarma16=alarmas[15]
    alarma17=alarmas[16]
    alarma18=alarmas[17]
    alarma19=alarmas[18]
    alarma20=alarmas[19]
    alarma21=alarmas[20]
    alarma22=alarmas[21]
    alarma23=alarmas[22]
    alarma24=alarmas[23]
    alarma25=alarmas[24]
    alarma26=alarmas[25]
    alarma27=alarmas[26]
    alarma28=alarmas[27]
    alarma29=alarmas[28]
    alarma30=alarmas[29]
    alarma31=alarmas[30]
    alarma32=alarmas[31]
    alarma33=alarmas[32]
    alarma34=alarmas[33]
    alarma35=alarmas[34]
    alarma36=alarmas[35]
    alarma37=alarmas[36]
    alarma38=alarmas[37]
    alarma39=alarmas[38]
    #Battery
    alarma40=alarmas[39]
    alarma41=alarmas[40]
    alarma42=alarmas[41]
    alarma43=alarmas[42]
    alarma44=alarmas[43]
    alarma45=alarmas[44]
    alarma46=alarmas[45]
    alarma47=alarmas[46]
    alarma48=alarmas[47]
    alarma49=alarmas[48]
    alarma50=alarmas[49]
    alarma51=alarmas[50]
    alarma52=alarmas[51]
    alarma53=alarmas[52]
    alarma54=alarmas[53]
    alarma55=alarmas[54]
    #Inverter
    alarma56=alarmas[55]
    alarma57=alarmas[56]
    alarma58=alarmas[57]
    alarma59=alarmas[58]
    alarma60=alarmas[59]
    alarma61=alarmas[60]
    alarma62=alarmas[61]
    alarma63=alarmas[62]
    alarma64=alarmas[63]
    alarma65=alarmas[64]
    alarma66=alarmas[65]
    alarma67=alarmas[66]
    alarma68=alarmas[67]
    alarma69=alarmas[68]
    alarma70=alarmas[69]
    alarma71=alarmas[70]
    alarma72=alarmas[71]
    alarma73=alarmas[72]
    alarma74=alarmas[73]
    alarma75=alarmas[74]
    alarma76=alarmas[75]
    alarma77=alarmas[76]
    alarma78=alarmas[77]
    alarma79=alarmas[78]
    alarma80=alarmas[79]
    alarma81=alarmas[80]
    alarma82=alarmas[81]
    alarma83=alarmas[82]
    alarma84=alarmas[83]
 
#Inversor 1
    current_input_i1= round(datos[0],1)
    high_power_output_i1= round(datos[1],1)
    low_power_output_i1= round(datos[2],1)
    high_apparent_power_i1= round(datos[3],1)
    low_apparent_power_i1= round((datos[4]),1)
    voltage_input_i1= round(datos[5]*10,1)
    voltage_output_i1= round(datos[6],1)
    frecuency_output_i1=round(datos[7]*10,2)
    percentage_load_i1= round(datos[8])
    current_output_i1= round(datos[9],1)
    inv_current_i1= round(datos[10],1)
    charging_current_i1= round(datos[11],1)
    #Inversor 2
    current_input_i2= round(datos[12],1)
    high_power_output_i2= round(datos[13],1)
    low_power_output_i2= round((datos[14]),1)
    high_apparent_power_i2= round(datos[15],1)
    low_apparent_power_i2= round(datos[16],1)
    voltage_input_i2= round(datos[17]*10,1)
    voltage_output_i2= round(datos[18],1)
    frecuency_output_i2= round(datos[19]*10,2)
    percentage_load_i2= round(datos[20])
    current_output_i2= round(datos[21],1)
    inv_current_i2= round(datos[22],1)
    charging_current_i2= round(datos[23],1)
    #Bateria
    Current_bat=round(datos[24],1)
    Voltage_bat=round(datos[25],1)
    soc_bat=int(round(datos[26]))
    soh_bat=int(round(datos[27]))
    Max_capacity_bat=int(round(datos[28]/100))
    Nominal_capacity_bat=int(round(datos[29]/100))
    Voltage_cell_1_bat=round(datos[30],1)
    Voltage_cell_2_bat=round(datos[31],1)
    Voltage_cell_3_bat=round(datos[32],1)
    Voltage_cell_4_bat=round(datos[33],1)
    Voltage_cell_5_bat=round(datos[34],1)
    Voltage_cell_6_bat=round(datos[35],1)
    Voltage_cell_7_bat=round(datos[36],1)
    Voltage_cell_8_bat=round(datos[37],1)
    Voltage_cell_9_bat=round(datos[38],1)
    Voltage_cell_10_bat=round(datos[39],1)
    Voltage_cell_11_bat=round(datos[40],1)
    Voltage_cell_12_bat=round(datos[41],1)
    Voltage_cell_13_bat=round(datos[42],1)
    Voltage_cell_14_bat=round(datos[43],1)
    ciclos_bat=round(datos[44])
    Temperatura=round(datos[45],1)
    #Cuadro de Fuerza
    Voltage_Bus_DC_CF=round(datos[46],1)
    Load_Current_CF=round(datos[47],1)
    Capacity_CF=round(datos[48])
    Output_Current_CF=round(datos[49],1)
    Modo_CF=datos[50]
    Temperature_CF=int(datos[51])
    StatusG01=datos[52]
    Voltaje_Output_G01=round((datos[53]/100),1)
    Current_Output_G01=round((datos[54])/10,1)
    Voltage_AC_G01=round(datos[55],1)
    Current_AC_G01=round((datos[56]/10),1)
    StatusG02=datos[57]
    Voltaje_Output_G02=round((datos[58]/100),1)
    Current_Output_G02=round((datos[59]/10),1)
    Voltage_AC_G02=round(datos[60],1)
    Current_AC_G02=round((datos[61]/10),1)
    StatusG188=datos[62]
    Voltaje_Output_G188=round((datos[63]/100),1)
    Current_Output_G188=round((datos[64]/10),1) 
    Voltage_AC_G188=round(datos[65],1)
    Current_AC_G188=round((datos[66]/10),1)
    #Controlador Solar
    Voltage_PV_solar=round(datos[67],1)
    batery_voltage_solar=round(datos[68],1)
    Charging_Current_solar=round(datos[69],1)
    Output_Voltage_solar=round(datos[70],1)
    Load_Current_solar=round(datos[71],1)
    Charging_Power_solar=int(round(datos[72]))
    Load_Power_solar=round(datos[73],1)
    power_solar=round(datos[74],1)
    power1_solar=round(datos[75],1)


    try:
        autonomia_total=round((48*100*(soc_bat/100))/(low_power_output_i1+low_power_output_i2-Charging_Power_solar),1)
        autonomia_bat=round((4800*(soh_bat/100)*(soc_bat/100))/(low_power_output_i1+low_power_output_i2),1)
    except:
        autonomia_total="∞"
        autonomia_bat="∞"

    

    power_red=round(((Current_Output_G01+Current_Output_G02+Current_Output_G188)*Voltaje_Output_G188)/0.9)

    if power_red<0:
        power_red=0

    power_carga=round(low_power_output_i1+low_power_output_i2+120)
    voltage_ac=round((Voltage_AC_G188),1)
           
    try:
        current_carga=round((power_carga/voltage_output_i1),1)
    except:
        current_carga=0
    try:
        current_ac=round((power_red/Voltage_AC_G01),1)
    except:
        current_ac=0
       
    if Current_bat>0:
        current_inp_inv=round(Charging_Current_solar+Current_Output_G01+Current_Output_G02+Current_AC_G188+Current_bat,1)
    else:
        current_inp_inv=round(Charging_Current_solar+Current_Output_G01+Current_Output_G02+Current_Output_G188,1)
    power_bat=round(Voltage_bat*Current_bat,1)

    valores = (
        fecha_hora,
        current_input_i1,
        high_power_output_i1,
        low_power_output_i1,
        high_apparent_power_i1,
        low_apparent_power_i1,
        voltage_input_i1,
        voltage_output_i1,
        frecuency_output_i1,
        percentage_load_i1,
        current_output_i1,
        inv_current_i1,
        charging_current_i1,
        current_input_i2,
        high_power_output_i2,
        low_power_output_i2,
        high_apparent_power_i2,
        low_apparent_power_i2,
        voltage_input_i2,
        voltage_output_i2,
        frecuency_output_i2,
        percentage_load_i2,
        current_output_i2,
        inv_current_i2,
        charging_current_i2,
        Current_bat,
        Voltage_bat,
        soc_bat,
        soh_bat,
        Max_capacity_bat,
        Nominal_capacity_bat,
        Voltage_cell_1_bat,
        Voltage_cell_2_bat,
        Voltage_cell_3_bat,
        Voltage_cell_4_bat,
        Voltage_cell_5_bat,
        Voltage_cell_6_bat,
        Voltage_cell_7_bat,
        Voltage_cell_8_bat,
        Voltage_cell_9_bat,
        Voltage_cell_10_bat,
        Voltage_cell_11_bat,
        Voltage_cell_12_bat,
        Voltage_cell_13_bat,
        Voltage_cell_14_bat,
        ciclos_bat,
        Temperatura,
        Voltage_Bus_DC_CF,
        Load_Current_CF,
        Capacity_CF,
        Output_Current_CF,
        Modo_CF,
        Temperature_CF,
        StatusG01,
        Voltaje_Output_G01,
        Current_Output_G01,
        Voltage_AC_G01,
        Current_AC_G01,
        StatusG02,
        Voltaje_Output_G02,
        Current_Output_G02,
        Voltage_AC_G02,
        Current_AC_G02,
        StatusG188,
        Voltaje_Output_G188,
        Current_Output_G188,
        Voltage_AC_G188,
        Current_AC_G188,
        Voltage_PV_solar,
        batery_voltage_solar,
        Charging_Current_solar,
        Output_Voltage_solar,
        Load_Current_solar,
        Charging_Power_solar,
        Load_Power_solar,
        power_solar,
        power1_solar,
        autonomia_total,
        autonomia_bat,
        power_red,
        power_carga,
        voltage_ac,
        current_carga,
        current_ac,
        current_inp_inv,
        power_bat)

    columnas = '''
    fecha_hora,
    current_input_i1,
    high_power_output_i1,
    low_power_output_i1,
    high_apparent_power_i1,
    low_apparent_power_i1,
    voltage_input_i1,
    voltage_output_i1,
    frecuency_output_i1,
    percentage_load_i1,
    current_output_i1,
    inv_current_i1,
    charging_current_i1,
    current_input_i2,
    high_power_output_i2,
    low_power_output_i2,
    high_apparent_power_i2,
    low_apparent_power_i2,
    voltage_input_i2,
    voltage_output_i2,
    frecuency_output_i2,
    percentage_load_i2,
    current_output_i2,
    inv_current_i2,
    charging_current_i2,
    Current_bat,
    Voltage_bat,
    soc_bat,
    soh_bat,
    Max_capacity_bat,
    Nominal_capacity_bat,
    Voltage_cell_1_bat,
    Voltage_cell_2_bat,
    Voltage_cell_3_bat,
    Voltage_cell_4_bat,
    Voltage_cell_5_bat,
    Voltage_cell_6_bat,
    Voltage_cell_7_bat,
    Voltage_cell_8_bat,
    Voltage_cell_9_bat,
    Voltage_cell_10_bat,
    Voltage_cell_11_bat,
    Voltage_cell_12_bat,
    Voltage_cell_13_bat,
    Voltage_cell_14_bat,
    ciclos_bat,
    Temperatura,
    Voltage_Bus_DC_CF,
    Load_Current_CF,
    Capacity_CF,
    Output_Current_CF,
    Modo_CF,
    Temperature_CF,
    StatusG01,
    Voltaje_Output_G01,
    Current_Output_G01,
    Voltage_AC_G01,
    Current_AC_G01,
    StatusG02,
    Voltaje_Output_G02,
    Current_Output_G02,
    Voltage_AC_G02,
    Current_AC_G02,
    StatusG188,
    Voltaje_Output_G188,
    Current_Output_G188,
    Voltage_AC_G188,
    Current_AC_G188,
    Voltage_PV_solar,
    batery_voltage_solar,
    Charging_Current_solar,
    Output_Voltage_solar,
    Load_Current_solar,
    Charging_Power_solar,
    Load_Power_solar,
    power_solar,
    power1_solar,
    autonomia_total,
    autonomia_bat,
    power_red,
    power_carga,
    voltage_ac,
    current_carga,
    current_ac,
    current_inp_inv,
    power_bat
      '''
    valores1=(fecha_hora, alarma1,alarma2,alarma3,alarma4,alarma5,alarma6,alarma7,alarma8,alarma9,alarma10,alarma11,alarma12,alarma13,alarma14,alarma15,alarma16,alarma17,alarma18,alarma19,alarma20,alarma21,alarma22,alarma23,alarma24,alarma25,alarma26,alarma27,alarma28,alarma29,alarma30,alarma31,alarma32,alarma33,alarma34,alarma35,alarma36,alarma37,alarma38,alarma39,alarma40,alarma41,alarma42,alarma43,alarma44,alarma45,alarma46,alarma47,alarma48,alarma49,alarma50,alarma51,alarma52,alarma53,alarma54,alarma55,alarma56,alarma57,alarma58,alarma59,alarma60,alarma61,alarma62,alarma63,alarma64,alarma65,alarma66,alarma67,alarma68,alarma69,alarma70,alarma71,alarma72,alarma73,alarma74,alarma75,alarma76,alarma77,alarma78,alarma79,alarma80,alarma81,alarma82,alarma83,alarma84)

    columnas1="""fecha_hora, alarma1,alarma2,alarma3,alarma4,alarma5,alarma6,alarma7,alarma8,alarma9,alarma10,alarma11,alarma12,alarma13,alarma14,alarma15,alarma16,alarma17,alarma18,alarma19,alarma20,alarma21,alarma22,alarma23,alarma24,alarma25,alarma26,alarma27,alarma28,alarma29,alarma30,alarma31,alarma32,alarma33,alarma34,alarma35,alarma36,alarma37,alarma38,alarma39,alarma40,alarma41,alarma42,alarma43,alarma44,alarma45,alarma46,alarma47,alarma48,alarma49,alarma50,alarma51,alarma52,alarma53,alarma54,alarma55,alarma56,alarma57,alarma58,alarma59,alarma60,alarma61,alarma62,alarma63,alarma64,alarma65,alarma66,alarma67,alarma68,alarma69,alarma70,alarma71,alarma72,alarma73,alarma74,alarma75,alarma76,alarma77,alarma78,alarma79,alarma80,alarma81,alarma82,alarma83,alarma84"""
   
    try:
        # Verifica que existan las tablas antes de insertar
        if not tabla_existe("datos") or not tabla_existe("eventos_sistema") or not tabla_existe("resumen_mensual")  :
            logger.warning("Tablas no existentes, intentando inicializar la base de datos.")
            inicializar_db()
        with sqlite3.connect(DB_PATH, timeout=15) as conn:
            conn.execute('PRAGMA journal_mode=WAL;')
            cursor = conn.cursor()

            placeholders = ', '.join(['?'] * len(valores))
            insert_sql = f"INSERT INTO datos ({columnas}) VALUES ({placeholders})"
            cursor.execute(insert_sql, valores)
            logger.info(f"Datos insertados: {valores[:5]}...")  # Log parcial para evitar saturación
            
        
            new_alarm_values = {f"alarma{i}": alarmas[i-1] for i in range(1, 85)}

            try:
                if should_insert_event(conn, new_alarm_values):

                    placeholders1 = ', '.join(['?'] * len(valores1))
                    insert_sql = f"INSERT INTO eventos_sistema ({columnas1}) VALUES ({placeholders1})"
                    cursor.execute(insert_sql, valores1)
                    conn.commit()
                    logger.info("Evento inserción: nuevo estado detectado, se insertó nuevo registro en eventos_sistema.")
                else:
                   
                    last = fetch_last_event(conn)
                    if last:
                        cursor.execute("UPDATE eventos_sistema SET fecha_hora = ? WHERE id = ?", (fecha_hora, last['id']))
                        conn.commit()
                        logger.debug("Evento repetido: actualizado fecha_hora del último registro en eventos_sistema.")
            except Exception as e:
                logger.error(f"Error al decidir insertar/actualizar evento: {e}", exc_info=True)

    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            logger.warning("La base de datos está bloqueada, reintentando en el siguiente ciclo.")
        else:
            logger.error(f"Error operativo de la base de datos: {e}")
    except sqlite3.Error as e:
        logger.error(f"Error general de la base de datos: {e}")
    except Exception as e:
        logger.critical(f"Error inesperado: {e}")
   
   

if __name__ == '__main__':
    setup_logging()
    ultimo_mes_guardado = datetime.datetime.now().month
    while True:
        try:
            now = datetime.datetime.now()
            # Si cambió el mes, guarda el resumen del mes anterior
            if now.month != ultimo_mes_guardado:
                # Calcula el mes y año anterior
                if now.month == 1:
                    prev_year = now.year - 1
                    prev_month = 12
                else:
                    prev_year = now.year
                    prev_month = now.month - 1
                guardar_resumen_mensual(prev_year, prev_month)
                ultimo_mes_guardado = now.month

            insertar_datos()
        except Exception as e:
            logger.critical(f"Error inesperado en el ciclo principal: {e}", exc_info=True)
        time.sleep(5)
