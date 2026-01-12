#!/bin/bash

echo "=== Instalador Automático HMI - UNIMET ==="
echo "=== Versión 1.1 - Incluye correcciones de dependencias ==="

# 1. Actualizar sistema e instalar dependencias del sistema
echo "[1/7] Actualizando sistema e instalando dependencias del sistema..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# NOTA: Instalar libsnmp-dev antes de las dependencias Python (requerido para easysnmp)
echo "Instalando libsnmp-dev (requerido para easysnmp)..."
sudo apt install -y libsnmp-dev

# 2. Clonar repositorio
echo "[2/7] Clonando repositorio HMI..."
cd ~
if [ -d "HMI" ]; then
    echo "La carpeta HMI ya existe. ¿Desea sobrescribir? (s/n)"
    read respuesta
    if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
        rm -rf HMI
        git clone https://github.com/Juanstreet/HMI.git
    else
        echo "Usando carpeta HMI existente."
    fi
else
    git clone https://github.com/Juanstreet/HMI.git
fi

# 3. Crear entorno virtual
echo "[3/7] Creando entorno virtual..."
cd ~/HMI
if [ -d "hmi_env" ]; then
    echo "El entorno virtual ya existe. ¿Recrearlo? (s/n)"
    read respuesta
    if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
        rm -rf hmi_env
        python3 -m venv hmi_env
    fi
else
    python3 -m venv hmi_env
fi

# 4. Activar entorno virtual e instalar dependencias de Python
echo "[4/7] Instalando librerías de Python..."
source hmi_env/bin/activate

# NOTA: Primero actualizar pip, setuptools y wheel para evitar problemas con Flask
echo "Actualizando pip, setuptools y wheel..."
pip install --upgrade pip setuptools wheel

# Instalar librerías necesarias (sin duplicados según el manual)
echo "Instalando dependencias Python..."
pip install minimalmodbus easysnmp flask flask-caching pymodbus pandas

# Verificar instalación de Flask (según nota del manual)
if ! pip show Flask &> /dev/null; then
    echo "Reintentando instalación de Flask..."
    pip install Flask
fi

# 5. Configurar base de datos
echo "[5/7] Configurando base de datos..."
echo "Por favor, ingrese la ruta completa para la base de datos (ejemplo: /home/$USER/HMI/HMI.db):"
echo "Presione Enter para usar la ruta por defecto (/home/$USER/HMI/HMI.db)"
read db_path

if [ -z "$db_path" ]; then
    db_path="/home/$USER/HMI/HMI.db"
    echo "Usando ruta por defecto: $db_path"
else
    echo "Usando ruta personalizada: $db_path"
fi

# Crear directorio si no existe
db_dir=$(dirname "$db_path")
mkdir -p "$db_dir"

# Reemplazar DB_PATH en main.py y app.py si existen
if [ -f "main.py" ]; then
    sed -i "s|DB_PATH = .*|DB_PATH = '$db_path'|g" main.py
    echo "Configurado DB_PATH en main.py"
fi

if [ -f "app.py" ]; then
    sed -i "s|DB_PATH = .*|DB_PATH = '$db_path'|g" app.py
    echo "Configurado DB_PATH en app.py"
fi

# 6. Configurar servicios systemd
echo "[6/7] Configurando servicios systemd..."

# Obtener nombre de usuario actual
CURRENT_USER=$(whoami)

# Servicio hmi_data.service (sistema)
echo "Creando servicio hmi_data.service..."
sudo tee /etc/systemd/system/hmi_data.service <<EOF
[Unit]
Description=Servicio de Recolección de Datos HMI
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=/home/$CURRENT_USER/HMI
Environment=PATH=/home/$CURRENT_USER/HMI/hmi_env/bin
ExecStart=/home/$CURRENT_USER/HMI/hmi_env/bin/python /home/$CURRENT_USER/HMI/main.py
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=hmi_data

[Install]
WantedBy=multi-user.target
EOF

# Servicio hmi-web.service (usuario)
echo "Creando servicio hmi-web.service..."
mkdir -p ~/.config/systemd/user/

tee ~/.config/systemd/user/hmi-web.service <<EOF
[Unit]
Description=Servidor Web HMI
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/$CURRENT_USER/HMI
Environment=PATH=/home/$CURRENT_USER/HMI/hmi_env/bin
ExecStart=/home/$CURRENT_USER/HMI/hmi_env/bin/python /home/$CURRENT_USER/HMI/app.py
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=hmi_web

[Install]
WantedBy=default.target
EOF

# 7. Habilitar e iniciar servicios
echo "[7/7] Habilitando e iniciando servicios..."

# Servicio del sistema (hmi_data)
echo "Configurando hmi_data.service..."
sudo systemctl daemon-reload
sudo systemctl enable hmi_data.service
sudo systemctl start hmi_data.service

# Servicio de usuario (hmi-web)
echo "Configurando hmi-web.service..."
# Habilitar persistencia de sesión
sudo loginctl enable-linger $CURRENT_USER
systemctl --user daemon-reload
systemctl --user enable hmi-web.service
systemctl --user start hmi-web.service

echo ""
echo "=== INSTALACIÓN COMPLETADA ==="
echo "==============================="
echo "Servicios configurados:"
echo "  • hmi_data.service  (sistema) - RECOLECCIÓN DE DATOS"
echo "  • hmi-web.service   (usuario) - SERVIDOR WEB"
echo ""
echo "Para verificar el estado de los servicios:"
echo "  sudo systemctl status hmi_data.service"
echo "  systemctl --user status hmi-web.service"
echo ""
echo "Acceso a la interfaz web:"
echo "  Desde la Raspberry: http://localhost:5000"
echo "  Desde otro dispositivo: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Comandos útiles:"
echo "  Reiniciar servicios: sudo systemctl restart hmi_data.service"
echo "                    systemctl --user restart hmi-web.service"
echo "  Ver logs: sudo journalctl -u hmi_data.service -f"
echo "          journalctl --user -u hmi-web.service -f"
echo ""