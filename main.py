import sqlite3, time,logging, minimalmodbus, pymodbus,pymodbus.client, struct
from easysnmp import Session
from pymodbus.client import ModbusTcpClient
from register import faults_inverter,faults_solar,alarm_CF,register_inverter,register_solar_controler,battery_registers,CF_registers
from alarms import *

# --- Variables globales ---
DB_PATH = '/media/krillbox/HMI/basededatos.db'
logger = logging.getLogger(__name__)  # Logger para este módulo

#Configuracion de la comunicacion con los equipos RTU
try:
    #Inversor Izquierdo
    firts_inverter=minimalmodbus.Instrument("/dev/ttyUSB0",1)
    firts_inverter.serial.baudrate=9600
    #Inversor Derecho
    second_inverter=minimalmodbus.Instrument("/dev/ttyUSB0",2)
    second_inverter.serial.baudrate=9600
    #Controlador Solar
    solar_controler=minimalmodbus.Instrument("/dev/ttyUSB0",3)
    solar_controler.serial.baudrate=9600
    #Configuracion de equpos Modbus TCP/IP
    CF = ModbusTcpClient(host='192.168.1.12', port=8023, retries=1, timeout=1 ) 
    #Configuracion de equpipos SNMP
    battery= Session(hostname="192.168.1.13", community="public",version=2)
except:
    logger.error("No se pudo configurar los equipos")


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
        conn = sqlite3.connect(DB_PATH)
        logger.info("Conexión a la base de datos establecida correctamente.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error al conectar a la base de datos: {e}", exc_info=True)
    return None

def inicializar_db():
    conn = crear_conexion()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='datos'")
            if not cursor.fetchone():
                cursor.execute('''
                CREATE TABLE datos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    current_input_i1 REAL,
                    high_power_output_i1 REAL,
                    low_power_output_i1 REAL,
                    high_apparent_power_i1 REAL,
                    low_apparent_power_i1 REAL,
                    voltage_input_i1 REAL,
                    voltage_output_i1 REAL,
                    frecuency_output_i1 REAL,
                    percentage_load_i1 REAL,
                    current_output_i1 REAL,
                    inv_current_i1 REAL,
                    charging_current_i1 REAL,
                    current_input_i2 REAL,
                    high_power_output_i2 REAL,
                    low_power_output_i2 REAL,
                    high_apparent_power_i2 REAL,
                    low_apparent_power_i2 REAL,
                    voltage_input_i2 REAL,
                    voltage_output_i2 REAL,
                    frecuency_output_i2 REAL,
                    percentage_load_i2 REAL,
                    current_output_i2 REAL,
                    inv_current_i2 REAL,
                    charging_current_i2 REAL,
                    Current_bat REAL,
                    Voltage_bat REAL,
                    soc_bat REAL,
                    soh_bat REAL,
                    Max_capacity_bat REAL,
                    Nominal_capacity_bat REAL,
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
                    Voltage_Bus_DC_CF REAL,
                    Load_Current_CF REAL,
                    Capacity_CF REAL,
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
                    power1_solar REAL
                               )''')

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eventos_sistema'")
                if not cursor.fetchone():
                    cursor.execute('''
                    CREATE TABLE eventos_sistema (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
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
                     ''
                    )''')

                conn.commit()
                logger.info("Tablas 'datos' y 'eventos_sistema' creadas exitosamente.")
            else:
                logger.info("Las tablas ya existen. No se requiere inicialización.")
        except sqlite3.Error as e:
            logger.error(f"Error al inicializar la base de datos: {e}", exc_info=True)
        finally:
            conn.close()
            logger.debug("Conexión a la base de datos cerrada.")

def insertar_datos():
    conn = None
    datos=[]
    alarmas=[]
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
                datos.append(f"({a},inv1)")
            except:
                logger.error("Error al recolectar datos del inversor 1")
        except:
            a="error inv1"
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
                datos.append(f"({b},inv2")
            except:
                logger.error("Error al recolectar los datos del inversor 2")
        except:
            b="error inv2"
            datos.append(b)
            logger.error(f"No se pudo acceder al registro {register_inverter[dato]}")
        

   
    #Bateria
    for i,dato in zip(range(0,len(battery_registers)),battery_registers):
        try:
            e=battery.get(battery_registers[dato]).value
            try:
                e=int(e)
                if e>32768:
                    e=e-65536
                if i==0 or i==1 or i==4 or i==5:
                    e=e*100
                if i>=6 and i<=19:
                    e=e*1000
                datos.append(f"({e}, bat)")
            except:
                e=battery.get(battery_registers[dato]).value
                datos.append(e)
        except:
            e="error bat"
            datos.append(e)
            logger.error(f"No se puedo acceder al registro {battery_registers[dato]}")
        

    #CUADRO DE FUERZA
    for data in CF_registers:
            try:     
                CF.connect()
                d=CF.read_holding_registers(address=CF_registers[data]).registers[0]
                try:    
                    if d>32768:
                        d=d-65536
                    if CF_registers[data]==0 or CF_registers[data]==2001 or CF_registers[data]==2011 or CF_registers[data]==3871:
                        d=d/100
                    if CF_registers[data]==2002 or CF_registers[data]==2005 or CF_registers[data]==2012 or CF_registers[data]==2015 or CF_registers[data]==3875 or CF_registers[data]==3872:
                        d=d/10
                    datos.append(d)
                except:
                    logger.error("Error al recolectar los datos del cuadro de fuerza")
            except:
                d="error CF" 
                datos.append(d) 
                logger.error(f"No se pudo acceder al registro {CF_registers[data]}")   
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
                datos.append(f"({c},solar)")
            except:
                logger.error("Error al recoletasr los datos del controlador solar")
            
        except:
            c="error solar"
            datos.append(c)
            logger.error(f"No ser pudo acceder al registro {register_solar_controler[dato]}")

        

    print(datos)    
#Manejo de Alarmas
    
    MPPTAlarmDecoder.decode_MPPT(alarmas,faults_solar,logger)
    GEAlarmDecoder.CF_decode(alarm_CF,alarmas,logger)
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
    current_input_i1= datos[0]
    high_power_output_i1= datos[1]
    low_power_output_i1= datos[2]
    high_apparent_power_i1= datos[3]
    low_apparent_power_i1= datos[4]
    voltage_input_i1= datos[5]
    voltage_output_i1= datos[6]
    frecuency_output_i1=datos[7]
    percentage_load_i1= datos[8]
    current_output_i1= datos[9]
    inv_current_i1= datos[10]
    charging_current_i1= datos[11]
    #Inversor 2
    current_input_i2= datos[12]
    high_power_output_i2= datos[13]
    low_power_output_i2= datos[14]
    high_apparent_power_i2= datos[15]
    low_apparent_power_i2= datos[16]
    voltage_input_i2= datos[17]
    voltage_output_i2= datos[18]
    frecuency_output_i2= datos[19]
    percentage_load_i2= datos[20]
    current_output_i2= datos[21]
    inv_current_i2= datos[22]
    charging_current_i2= datos[23]
    #Bateria
    Current_bat=datos[24]
    Voltage_bat=datos[25]
    soc_bat=datos[26]
    soh_bat=datos[27]
    Max_capacity_bat=datos[28]
    Nominal_capacity_bat=datos[29]
    Voltage_cell_1_bat=datos[30]
    Voltage_cell_2_bat=datos[31]
    Voltage_cell_3_bat=datos[32]
    Voltage_cell_4_bat=datos[33]
    Voltage_cell_5_bat=datos[34]
    Voltage_cell_6_bat=datos[35]
    Voltage_cell_7_bat=datos[36]
    Voltage_cell_8_bat=datos[37]
    Voltage_cell_9_bat=datos[38]
    Voltage_cell_10_bat=datos[39]
    Voltage_cell_11_bat=datos[40]
    Voltage_cell_12_bat=datos[41]
    Voltage_cell_13_bat=datos[42]
    Voltage_cell_14_bat=datos[43]
    #Cuadro de Fuerza
    Voltage_Bus_DC_CF=datos[44]
    Load_Current_CF=datos[45]
    Capacity_CF=datos[46]
    Output_Current_CF=datos[47]
    Modo_CF=datos[48]
    Temperature_CF=datos[49]
    StatusG01=datos[50]
    Voltaje_Output_G01=datos[51]
    Current_Output_G01=datos[52]
    Voltage_AC_G01=datos[53]
    Current_AC_G01=datos[54]
    StatusG02=datos[55]
    Voltaje_Output_G02=datos[56]
    Current_Output_G02=datos[57]
    Voltage_AC_G02=datos[58]
    Current_AC_G02=datos[59]
    StatusG188=datos[60]
    Voltaje_Output_G188=datos[61]
    Current_Output_G188=datos[62] 
    Voltage_AC_G188=datos[63]
    Current_AC_G188=datos[64]
    #Controlador Solar
    Voltage_PV_solar=datos[65]
    batery_voltage_solar=datos[66]
    Charging_Current_solar=datos[67]
    Output_Voltage_solar=datos[68]
    Load_Current_solar=datos[69]
    Charging_Power_solar=datos[70]
    Load_Power_solar=datos[71]
    power_solar=datos[72]
    power1_solar=datos[73]


    valores = (
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
power1_solar)

    columnas = '''
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
    power1_solar
    '''
    valores1=(alarma1,alarma2,alarma3,alarma4,alarma5,alarma6,alarma7,alarma8,alarma9,alarma10,alarma11,alarma12,alarma13,alarma14,alarma15,alarma16,alarma17,alarma18,alarma19,alarma20,alarma21,alarma22,alarma23,alarma24,alarma25,alarma26,alarma27,alarma28,alarma29,alarma30,alarma31,alarma32,alarma33,alarma34,alarma35,alarma36,alarma37,alarma38,alarma39,alarma40,alarma41,alarma42,alarma43,alarma44,alarma45,alarma46,alarma47,alarma48,alarma49,alarma50,alarma51,alarma52,alarma53,alarma54,alarma55,alarma56,alarma57,alarma58,alarma59,alarma60,alarma61,alarma62,alarma63,alarma64,alarma65,alarma66,alarma67,alarma68,alarma69,alarma70,alarma71,alarma72,alarma73,alarma74,alarma75,alarma76,alarma77,alarma78,alarma79,alarma80,alarma81,alarma82,alarma83,alarma84)

    columnas1="""alarma1,alarma2,alarma3,alarma4,alarma5,alarma6,alarma7,alarma8,alarma9,alarma10,alarma11,alarma12,alarma13,alarma14,alarma15,alarma16,alarma17,alarma18,alarma19,alarma20,alarma21,alarma22,alarma23,alarma24,alarma25,alarma26,alarma27,alarma28,alarma29,alarma30,alarma31,alarma32,alarma33,alarma34,alarma35,alarma36,alarma37,alarma38,alarma39,alarma40,alarma41,alarma42,alarma43,alarma44,alarma45,alarma46,alarma47,alarma48,alarma49,alarma50,alarma51,alarma52,alarma53,alarma54,alarma55,alarma56,alarma57,alarma58,alarma59,alarma60,alarma61,alarma62,alarma63,alarma64,alarma65,alarma66,alarma67,alarma68,alarma69,alarma70,alarma71,alarma72,alarma73,alarma74,alarma75,alarma76,alarma77,alarma78,alarma79,alarma80,alarma81,alarma82,alarma83,alarma84"""
    try:
        placeholders = ', '.join(['?'] * len(valores))
        insert_sql = f"INSERT INTO datos ({columnas}) VALUES ({placeholders})"
        cursor.execute(insert_sql, valores)
        conn.commit()
        logger.info(f"Datos insertados: {valores[:5]}...")  # Log parcial para evitar saturación
        
        #Alarmas
        placeholders = ', '.join(['?'] * len(valores1))
        insert_sql = f"INSERT INTO eventos_sistema ({columnas1}) VALUES ({placeholders})"
        cursor.execute(insert_sql, valores1)
        conn.commit()
        logger.info(f"Datos insertados: {valores[:5]}...")  # Log parcial para evitar saturación
        time.sleep(2)
    except sqlite3.Error as e:
        logger.error(f"Error en la inserción de datos: {e}", exc_info=True)
    except Exception as e:
        logger.critical(f"Error inesperado: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
            logger.info("Conexión a la base de datos cerrada.")

if __name__ == '__main__':
    setup_logging()  # Configura el sistema de logging
    logger.info("Iniciando script de generación de datos aleatorios.")
    inicializar_db()
    while True:
     insertar_datos()