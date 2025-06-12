import sqlite3, time,logging, minimalmodbus, pymodbus,pymodbus.client, struct
from easysnmp import Session
from register import faults_inverter,faults_solar,alarm_CF,register_inverter,register_solar_controler,battery_registers,CF_registers, alarma
from alarms import *
from pymodbus.client import ModbusTcpClient


import logging
alarmas=[]
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
    CF = pymodbus.client.ModbusTcpClient(host='192.168.1.12', port=502) 
    CF=ModbusTcpClient(host='192.168.1.12', port=502)
    #Configuracion de equpipos SNMP
    battery= Session(hostname="192.168.1.13", community="public",version=2)
except:
    print("Error de conexion con los equipos")


logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # También muestra logs en consola
        ]
)
logger = logging.getLogger(__name__)  # Logger para este módulo

class MPPTAlarmDecoder:
    @staticmethod
    def decode_MPPT(alarmas,solar_controler,faults_solar):
      
        try:
            # Lee el registro del Fault code
            value = solar_controler.read_register(14, 0)

            # Decodifica el valor bit a bit y agrega a la lista
            for bit_position in sorted(faults_solar.keys()):
                fault_desc = faults_solar[bit_position]
                if (value >> (bit_position - 1)) & 1:
                    alarmas.append(fault_desc)
                else:
                    alarmas.append(None)
        except:
            logger.error("Error al leer falla del controlador solar")
                
class GEAlarmDecoder:
    @staticmethod
    def CF_decode(alarm_CF,alarmas,CF):
        try:
            value= CF.read_coils(address=0, count=190).bits
            faults=(1,6,8,9,11,12,17,18,24,25,48,51,57,60,61,62,65,101,105,114,124,132,133,151,152,153,154,156,163,190)
            for i in range(len(value)):
                if i+1 in faults:
                    if value[i]:
                        alarmas.append(alarm_CF.get(value))
                    else:
                        alarmas.append(None)
        except:
            logger.error("Error al leer el registro del CF")
        
class BatteryAlarmDecoder:
    @staticmethod
    def decode_battery(alarmas, battery):
        alarms = {
            ".1.3.6.1.4.1.51232.70.1.30.0": "Alarma de voltaje en celdas",
            ".1.3.6.1.4.1.51232.70.1.31.0": "Alarma de temperatura en celdas"
        }
        try:
            value2=battery.get(".1.3.6.1.4.1.51232.70.1.31.0").value
            for i in range(len(value2)):
                if value2[i]=="0":
                    alarmas.append(None)
                elif value2[i]=="1":
                    alarmas.append(f"Temperatura baja en celda {i+1}")
                elif value2[i]=="2":
                    alarmas.append(f"Temperatura alta en la celda {i+1}")
                elif 128<=int(value2[i])<=239:
                    alarmas.append(None)
                elif value2[i]=='240':
                    alarmas.append(f"Falla desconocida en la celda {i+1}")
           

        except:
            logger.error("Error al leer el registro de la bateria")

class InverterAlarmDecoder:
    @staticmethod
    def decode_inverter(firts_inverter, second_inverter,alarmas, faults_inverter):
        value1=firts_inverter.read_register(40,0,4)


        try:
            value = firts_inverter.read_register(40, 0, functioncode=4) # Función 4 para Input Registers

            for bit_position in sorted(faults_inverter.keys()):
                fault_desc = faults_inverter[bit_position]
                if (value >> (bit_position - 1)) & 1:
                    alarmas.append(fault_desc)
                else:
                    alarmas.append(None)
        except:
            logger.error("Error al recolectar las fallas delos inversores")

if __name__ == '__main__':
    MPPTAlarmDecoder.decode_MPPT(alarmas,solar_controler,faults_solar)
    GEAlarmDecoder.CF_decode(alarm_CF,alarmas,CF)
    BatteryAlarmDecoder.decode_battery(alarmas,battery)
    InverterAlarmDecoder.decode_inverter(firts_inverter,second_inverter,alarmas,faults_inverter)
    numero=0
    for alarma in alarmas:
        numero=numero+1
    print(numero)