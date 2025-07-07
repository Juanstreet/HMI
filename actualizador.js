function actualizarDatos() {
    fetch('/ultimo_registro')
        .then(response => response.json())
        .then(data => {
            const campos = [
                "current_input_i1", "high_power_output_i1", "low_power_output_i1", "high_apparent_power_i1", "low_apparent_power_i1",
                "voltage_input_i1", "voltage_output_i1", "frecuency_output_i1", "percentage_load_i1", "current_output_i1",
                "inv_current_i1", "charging_current_i1", "current_input_i2", "high_power_output_i2", "low_power_output_i2",
                "high_apparent_power_i2", "low_apparent_power_i2", "voltage_input_i2", "voltage_output_i2", "frecuency_output_i2",
                "percentage_load_i2", "current_output_i2", "inv_current_i2", "charging_current_i2", "Current_bat", "Voltage_bat",
                "soc_bat", "soh_bat", "Max_capacity_bat", "Nominal_capacity_bat", "Voltage_cell_1_bat", "Voltage_cell_2_bat",
                "Voltage_cell_3_bat", "Voltage_cell_4_bat", "Voltage_cell_5_bat", "Voltage_cell_6_bat", "Voltage_cell_7_bat",
                "Voltage_cell_8_bat", "Voltage_cell_9_bat", "Voltage_cell_10_bat", "Voltage_cell_11_bat", "Voltage_cell_12_bat",
                "Voltage_cell_13_bat", "Voltage_cell_14_bat", "Voltage_PV", "batery_voltage", "Charging_Current", "Output_Voltage",
                "Load_Current", "Charging_Power", "Load_Power", "power", "power1", "Voltage_Bus_DC_CF", "current_CF", "Capt_CF",
                "Output_Current_CF", "Modo_CF", "Temperature_CF", "StatusG01_CF", "Voltage_AC_G01_CF", "Voltage_AC_G02_CF",
                "Voltage_AC_G188_CF", "Current_AC_G01_CF", "Current_AC_G02_CF", "Current_AC_G188_CF","autonomia_total","autonomia_bat","power_red","power_carga","voltage_ac","current_carga","current_ac","current_inp_inv","power_bat"
            ];
            campos.forEach(function(campo) {
                const el = document.getElementById(campo);
                if (el && data.hasOwnProperty(campo)) {
                    el.textContent = data[campo];
                }
            });
            const registroJson = document.getElementById('registro_json');
            if (registroJson) {
                registroJson.textContent = JSON.stringify(data, null, 2);
            }
        });
}
setInterval(actualizarDatos, 1000);

/* Actualiza las estadísticas del mes actual */
function actualizarEstadisticasMesActual() {
    fetch('/estadisticas_mes_actual')
        .then(response => response.json())
        .then(data => {
            if (!data) return;
            // Carga
            if (document.getElementById('mes')) {
                document.getElementById('mes').textContent = data.mes || '';
            }
            if (document.getElementById('energia_carga')) {
                document.getElementById('energia_carga').textContent = data.energia_carga || 0;
            }
            if (document.getElementById('pot_max_carga')) {
                document.getElementById('pot_max_carga').textContent = data.pot_max_carga || 0;
            }
            if (document.getElementById('pot_prom_carga')) {
                document.getElementById('pot_prom_carga').textContent = data.pot_prom_carga || 0;
            }
            if (document.getElementById('acumulado_carga')) {
                document.getElementById('acumulado_carga').textContent = data.acumulado_carga || 0;
            }
            // Solar
            if (document.getElementById('energia_solar')) {
                document.getElementById('energia_solar').textContent = data.energia_solar || 0;
            }
            if (document.getElementById('pot_max_solar')) {
                document.getElementById('pot_max_solar').textContent = data.pot_max_solar || 0;
            }
            if (document.getElementById('pot_prom_solar')) {
                document.getElementById('pot_prom_solar').textContent = data.pot_prom_solar || 0;
            }
            if (document.getElementById('acumulado_solar')) {
                document.getElementById('acumulado_solar').textContent = data.acumulado_solar || 0;
            }
            // Red
            if (document.getElementById('energia_red')) {
                document.getElementById('energia_red').textContent = data.energia_red || 0;
            }
            if (document.getElementById('pot_max_red')) {
                document.getElementById('pot_max_red').textContent = data.pot_max_red || 0;
            }
            if (document.getElementById('pot_prom_red')) {
                document.getElementById('pot_prom_red').textContent = data.pot_prom_red || 0;
            }
            if (document.getElementById('acumulado_red')) {
                document.getElementById('acumulado_red').textContent = data.acumulado_red || 0;
            }
        });
}
setInterval(actualizarEstadisticasMesActual, 10000); // Cada 10 segundos

/* Reloj en tiempo real */
function actualizarReloj() {
  const ahora = new Date();
  const horas = ahora.getHours().toString().padStart(2, '0');
  const minutos = ahora.getMinutes().toString().padStart(2, '0');
  document.getElementById('hora-actual').textContent = `${horas}:${minutos}`;
}
setInterval(actualizarReloj, 1000);

// Llama a las funciones una vez al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    actualizarDatos();
    actualizarEstadisticasMesActual();
    actualizarReloj();
});