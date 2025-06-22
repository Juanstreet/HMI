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
                "Voltage_AC_G188_CF", "Current_AC_G01_CF", "Current_AC_G02_CF", "Current_AC_G188_CF"
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

/* Reloj en tiempo real */
function actualizarReloj() {
  const ahora = new Date();
  const horas = ahora.getHours().toString().padStart(2, '0');
  const minutos = ahora.getMinutes().toString().padStart(2, '0');
  document.getElementById('hora-actual').textContent = `${horas}:${minutos}`;
}
setInterval(actualizarReloj, 1000);


