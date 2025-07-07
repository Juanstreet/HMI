import minimalmodbus, pymodbus,pymodbus.client
from easysnmp import Session
from pymodbus.client import ModbusTcpClient
from register import alarm_CF


alarmas=[]
class MPPTAlarmDecoder:
    @staticmethod
    def decode_MPPT(alarmas,faults_solar,logger):
      
        try:
            # Lee el registro del Fault code
            solar_controler=minimalmodbus.Instrument("/dev/ttyUSB0",3)
            solar_controler.serial.baudrate=9600
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
            for i in range(8):
                alarmas.append("Error MPPT")
                
                
class GEAlarmDecoder:
    @staticmethod
    def CF_decode(alarm_CF, alarmas, logger, client=None):
        faults = (1, 6, 8, 9, 11, 12, 17, 18, 24, 25, 48, 51, 57, 60, 61, 62, 65, 101, 105, 114, 124, 132, 133, 151, 152, 153, 154, 156, 163, 190)
        CF = client if client is not None else ModbusTcpClient(host='192.168.1.12', port=8023)
        try:
            if not CF.connect():
                logger.error("No se pudo conectar al cuadro de fuerza (CF) para alarmas.")
                for _ in range(len(faults)):
                    alarmas.append("Error GEA")
                return
            value = CF.read_coils(address=0, count=190).bits
            for i in range(len(value)):
                if i + 1 in faults:
                    if value[i]:
                        alarmas.append(alarm_CF.get(i + 1))
                    else:
                        alarmas.append(None)
        except Exception as e:
            logger.error(f"Error al leer el registro del CF: {e}")
            for _ in range(len(faults)):
                alarmas.append("Error GEA")
        finally:
            if client is None:
                CF.close()
        
class BatteryAlarmDecoder:
    @staticmethod
    def decode_battery(alarmas,logger):
        alarms = {
            ".1.3.6.1.4.1.51232.70.1.30.0": "Alarma de voltaje en celdas",
            ".1.3.6.1.4.1.51232.70.1.31.0": "Alarma de temperatura en celdas"
        }
        try:
            battery= Session(hostname="192.168.1.13", community="public",version=2)
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
            for i in range(15):
                alarmas.append("Error Bateria")

class InverterAlarmDecoder:
    @staticmethod
    def decode_inverter(alarmas, faults_inverter,logger):
        try:
            #Inversor Izquierdo
            firts_inverter=minimalmodbus.Instrument("/dev/ttyUSB0",1)
            firts_inverter.serial.baudrate=9600
            #Inversor Derecho
            second_inverter=minimalmodbus.Instrument("/dev/ttyUSB0",2)
            second_inverter.serial.baudrate=9600
            value = firts_inverter.read_register(40, 0, functioncode=4) # Función 4 para Input Registers

            for bit_position in sorted(faults_inverter.keys()):
                fault_desc = faults_inverter[bit_position]
                if (value >> (bit_position - 1)) & 1:
                    alarmas.append(fault_desc)
                else:
                    alarmas.append(None)
        except:
            logger.error("Error al recolectar las fallas delos inversores")
            for i in range(31):
                alarmas.append("error inverter")


