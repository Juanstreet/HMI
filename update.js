document.addEventListener('DOMContentLoaded', () => {
    // Referencias a los elementos del DOM
    const fechaInput = document.getElementById('fecha-curva');
    const btnGraficar = document.getElementById('btn-graficar');
    const ctxSolar = document.getElementById('curvaSolarChart').getContext('2d');
    // const ctxSolar2 = document.getElementById('curvaSolarChart2').getContext('2d');
    const ctxBarEnerRedSolar = document.getElementById('BarEnerRedSolar').getContext('2d');
    const ctxVoltageCurrent = document.getElementById('voltageCurrentChartSolar').getContext('2d');
    const ctxVoltageCurrentRed = document.getElementById('VoltageCurrentRed').getContext('2d');
    const ctxVoltageCurrentCarga = document.getElementById('VoltageCurrentCarga').getContext('2d');
    const ctxEnergiaCargaSolar = document.getElementById('EnergiaCargaSolar').getContext('2d');
    const ctxVoltageCurrentMPPT = document.getElementById("VoltageCurrentMPPT").getContext("2d");
    const ctxVoltageCurrentBat = document.getElementById("VoltageCurrentBat").getContext("2d");
    const ctxPowerBat = document.getElementById("PowerBat").getContext("2d");
    const ctxPowerRed = document.getElementById("PowerRed").getContext("2d");
    const ctxPowerCarga = document.getElementById("PowerCarga").getContext("2d");

    

    // const ctxFrecuenciaRed = document.getElementById('FrecuenciaRed').getContext('2d');

    

    // Referencias a los botones de zoom
    const zoomInSolarBtn = document.getElementById('zoom-in-solar');
    const zoomOutSolarBtn = document.getElementById('zoom-out-solar');
    const zoomInCargaBtn = document.getElementById('zoom-in-carga');
    const zoomOutCargaBtn = document.getElementById('zoom-out-carga');

    const zoomFactor = 1.2;


    function actualizarIconosDinamicos(valores) {
        // Mapea cada icono con el valor correspondiente
        const iconos = [
            {id: "icon-red", valor: valores.current_ac },
            {id: "circle-red", valor:valores.current_ac},
            {id: "flecha-red", valor: valores.current_ac},
            {id: "red-on",valor: valores.voltage_ac},
            {id: "red-off",valor: valores.voltage_ac},

            { id: "icon-solar", valor: valores.Charging_Current_solar },
            {id: "circle-solar", valor: valores.Charging_Current_solar},
            {id: "flecha-solar", valor: valores.Charging_Current_solar},
            {id: "solar-on", valor: valores.Charging_Current_solar},

            { id: "icon-bat", valor: valores.Current_bat },
            {id: "circle-bateria", valor: valores.Current_bat},
            {id: "flecha-bat", valor: valores.Current_bat},
            {id: "bat-dis", valor: valores.Current_bat},
            {id: "bat-char", valor: valores.Current_bat},
            {id: "bat-off", valor: valores.Current_bat},

            {id: "icon-carga", valor: valores.current_carga },
            {id: "circle-carga", valor: valores.current_carga},
            {id: "flecha-carga", valor: valores.current_carga},
            {id: "car-on", valor: valores.current_carga},
            {id: "car-off", valor: valores.current_carga}

        ];
       
        iconos.forEach(icono => {
            const el = document.getElementById(icono.id);
            if (!el) return;

            // Elimina clases anteriores
            el.classList.remove("icon-off", "icon-on", "flecha-green", "flecha-off", "icon-green","condition-off", "flecha-dis");

            // Valida y convierte a número
            const v = Number(icono.valor);
            // Aplica el color según el rango que tú definas
            if (icono.id === "icon-red" || icono.id === "icon-solar" || icono.id === "icon-carga" || icono.id === "circle-red" || icono.id === "circle-solar" || icono.id === "circle-carga"){
                if (v === 0 || v < 0) {
                el.classList.add("icon-off");
                } 
                else if (v > 0) {
                    el.classList.add("icon-on");
                } 
            }
//----------------------------Flechas-----------------------------------------
            else if (icono.id === "flecha-carga" || icono.id === "flecha-red" || icono.id === "flecha-solar"){
                if (v === 0 || v < 0) {
                el.classList.add("flecha-off");
                } 
            }
            else if (icono.id === "flecha-bat"){
                if (v === 0) {
                el.classList.add("flecha-off");
                } 
                else if (v > 0) {
                    el.classList.add("flecha-green");
                }
                else if (v < 0) {
                    el.classList.add("flecha-dis");
                } 
            }
//----------------------------------------------------------------------------

            else if (icono.id === "icon-bat"|| icono.id === "circle-bateria" ){
                if (v === 0){
                    el.classList.add("icon-off")
                }
                else if (v > 0){
                    el.classList.add("icon-green")
                }
                else if (v < 0){
                    el.classList.add("icon-off")
                }
            }

            else if (icono.id=="red-on"||icono.id=="solar-on" ||icono.id=="car-on"){
                if (v < 0 || v ===0){
                    el.classList.add("condition-off")
                }
            }

            else if (icono.id=="red-off"|| icono.id=="car-off"){
                if (v > 0){
                    el.classList.add("condition-off")
                }

            }        
            
            else if (icono.id=='bat-dis'){
                if (v > 0){
                    el.classList.add('condition-off')
                }
                else if (v ===0){
                    el.classList.add("condition-off")
                }
            }

            else if (icono.id=='bat-char'){
                if (v < 0){
                    el.classList.add('condition-off')
                }
                else if (v ===0){
                    el.classList.add("condition-off")
                }
            }

            else if (icono.id=='bat-off'){
                if (v > 0 || v < 0){
                    el.classList.add('condition-off')
                }
            }

    })
    }

    function actualizarDatos() {
        fetch('/ultimo_registro')
            .then(response => response.json())
            .then(data => {
                actualizarIconosDinamicos(data);
                const campos = [
                "current_input_i1", "high_power_output_i1", "low_power_output_i1", "high_apparent_power_i1", 
                "low_apparent_power_i1", "voltage_input_i1", "voltage_output_i1", "frecuency_output_i1", 
                "percentage_load_i1", "current_output_i1", "inv_current_i1", "charging_current_i1",
                "current_input_i2", "high_power_output_i2", "low_power_output_i2", "high_apparent_power_i2",
                "low_apparent_power_i2", "voltage_input_i2", "voltage_output_i2", "frecuency_output_i2",
                "percentage_load_i2", "current_output_i2", "inv_current_i2", "charging_current_i2",
                "Current_bat", "Voltage_bat", "soc_bat", "soh_bat",
                "Max_capacity_bat", "Nominal_capacity_bat", "Voltage_cell_1_bat", "Voltage_cell_2_bat",
                "Voltage_cell_3_bat", "Voltage_cell_4_bat", "Voltage_cell_5_bat", "Voltage_cell_6_bat",
                "Voltage_cell_7_bat", "Voltage_cell_8_bat", "Voltage_cell_9_bat", "Voltage_cell_10_bat",
                "Voltage_cell_11_bat", "Voltage_cell_12_bat", "Voltage_cell_13_bat", "Voltage_cell_14_bat",
                "Voltage_Bus_DC_CF", "Load_Current_CF", "Capacity_CF", "Output_Current_CF",
                "Modo_CF", "Temperature_CF", "StatusG01", "Voltaje_Output_G01",
                "Current_Output_G01", "Voltage_AC_G01", "Current_AC_G01", "StatusG02",
                "Voltaje_Output_G02", "Current_Output_G02", "Voltage_AC_G02", "Current_AC_G02",
                "StatusG188", "Voltaje_Output_G188", "Current_Output_G188", "Voltage_AC_G188",
                "Current_AC_G188", "Voltage_PV_solar", "batery_voltage_solar", "Charging_Current_solar",
                "Output_Voltage_solar", "Load_Current_solar", "Charging_Power_solar", "Load_Power_solar",
                "power_solar", "power1_solar", "autonomia_total", "autonomia_bat", 
                "power_red", "power_carga", "voltage_ac", "current_carga",
                "current_ac","current_inp_inv", "power_bat","ciclos_bat","power_apparent_carga","fp"
                ];
                campos.forEach(function(campo) {
                    // Busca TODOS los elementos con la clase igual al nombre del campo
                    document.querySelectorAll('.' + campo).forEach(function(el) {
                        if (data.hasOwnProperty(campo)) {
                            el.textContent = data[campo];
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Error al obtener los datos:', error);
                // Opcional: mostrar un mensaje de error en la interfaz de usuario
            });
    }

    function actualizarDatosMensuales() {
        fetch('/estadisticas_mes_actual')
            .then(response => response.json())
            .then(data => {
                const campos = [
                "mes","energias_mensuales_carga","pot_max_mensual_carga","pot_prom_mensual_carga",
                "acumulado_mensual_carga","prom_energia_mensual_carga","meses_solar","energias_mensuales_solar",
                "pot_max_mensual_solar","pot_prom_mensual_solar","acumulado_mensual_solar","prom_energia_mensual_solar",
                "meses_red","energias_mensuales_red","pot_max_mensual_red","pot_prom_mensual_red",
                "acumulado_mensual_red","prom_energia_mensual_red","energias_mensuales_bat","pot_max_mensual_bat",
                "pot_prom_mensual_bat","acumulado_mensual_bat","prom_energia_mensual_bat", "energia_bat","pot_max_bat",
                "pot_prom_bat", "acumulado_bat","energia_anual_carga", "energia_anual_solar", "energia_anual_red","energia_anual_bat"
                ];
                campos.forEach(function(campo) {
                    // Busca TODOS los elementos con la clase igual al nombre del campo
                    document.querySelectorAll('.' + campo).forEach(function(el) {
                        if (data.hasOwnProperty(campo)) {
                            el.textContent = data[campo];
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Error al obtener los datos:', error);
                // Opcional: mostrar un mensaje de error en la interfaz de usuario
            });
    }

    function actualizarDatosDiarios() {
        fetch('/estadisticas_diarias')
            .then(response => response.json())
            .then(data => {
                const campos = [
                    "fechas_a_considerar_carga","energias_diarias_carga","pot_max_diaria_carga","pot_prom_diaria_carga",
                    "acumulado_diario_carga","prom_energia_diaria_carga","fechas_a_considerar_solar","energias_diarias_solar",
                    "pot_max_diaria_solar","pot_prom_diaria_solar","acumulado_diario_solar","prom_energia_diaria_solar",
                    "fechas_a_considerar_red","energias_diarias_red","pot_max_diaria_red","pot_prom_diaria_red",
                    "acumulado_diario_red","prom_energia_diaria_red", "energias_diarias_bat_dict","pot_max_diaria_bat",
                    "pot_prom_diaria_bat","acumulado_diario_bat","prom_energia_diaria_bat"
                ];
                campos.forEach(function(campo) {
                    // Busca TODOS los elementos con la clase igual al nombre del campo
                    document.querySelectorAll('.' + campo).forEach(function(el) {
                        if (data.hasOwnProperty(campo)) {
                            el.textContent = data[campo];
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Error al obtener los datos:', error);
                // Opcional: mostrar un mensaje de error en la interfaz de usuario
            });
    }


    
    
    // Gráfico de la curva solar1
    const curvaChart = new Chart(ctxSolar, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Potencia Solar',
                data: [],
                borderColor: '#00bfff',
                backgroundColor: 'rgba(0,191,255,0.12)',
                borderWidth: 2,
                tension: 0.4,
                yAxisID: 'solar-axis',
                pointRadius: 0
            },
            {
                label: 'Potencia de Carga',
                data: [],
                borderColor: '#39ff14',
                backgroundColor: 'rgba(57,255,20,0.09)',
                borderWidth: 2,
                tension: 0.4,
                yAxisID: 'carga-axis',
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,   
                        pointStyle: 'line',    
                        boxWidth: 60,
                        boxHeight: 30,
                        color: "#fff"
                    }
                },
                
                tooltip: { mode: 'index', intersect: false },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'x', // Permite pan solo en el eje horizontal
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x', // Permite zoom solo en el eje horizontal
                    }
                }
            },
            scales: {
                x: { 
                    ticks: { color: "#fff" }, 
                    grid: { color: "#32445A" } 
                },
                'solar-axis': {
                    tbeginAtZero: true,
                    title: { display: true, text: 'Potencia Solar (W)', color: "#00bfff" },
                    ticks: { color: "#00bfff" },
                    grid: { color: "#263142" }
                },
                'carga-axis': {
                    beginAtZero: true,
                    position: 'right',
                    title: { display: true, text: 'Potencia de la Carga (W)', color: "#39ff14" },
                    ticks: { color: "#39ff14" },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });

     // Gráfico de la curva solar2
    // const curvaChart2 = new Chart(ctxSolar2, {
    //     type: 'line',
    //     data: {
    //         labels: [],
    //         datasets: [{
    //             label: 'Potencia Solar',
    //             data: [],
    //             borderColor: '#00bfff',
    //             backgroundColor: 'rgba(0,191,255,0.12)',
    //             borderWidth: 2,
    //             tension: 0.4,
    //             yAxisID: 'solar-axis',
    //             pointRadius: 0
    //         },
    //         {
    //             label: 'Potencia de Carga',
    //             data: [],
    //             borderColor: '#39ff14',
    //             backgroundColor: 'rgba(57,255,20,0.09)',
    //             borderWidth: 2,
    //             tension: 0.4,
    //             yAxisID: 'carga-axis',
    //             pointRadius: 0
    //         }]
    //     },
    //     options: {
    //         responsive: true,
    //         maintainAspectRatio: false,
    //         plugins: {
    //             legend: {
    //                 labels: {
    //                     usePointStyle: true,   
    //                     pointStyle: 'line',    
    //                     boxWidth: 60,
    //                     boxHeight: 30,
    //                     color: "#fff"
    //                 }
    //             },
    //             tooltip: { mode: 'index', intersect: false },
    //             zoom: {
    //                 pan: {
    //                     enabled: true,
    //                     mode: 'x', // Permite pan solo en el eje horizontal
    //                 },
    //                 zoom: {
    //                     wheel: {
    //                         enabled: true,
    //                     },
    //                     pinch: {
    //                         enabled: true
    //                     },
    //                     mode: 'x', // Permite zoom solo en el eje horizontal
    //                 }
    //             }
    //         },
    //         scales: {
    //             x: { 
    //                 ticks: { color: "#fff" }, 
    //                 grid: { color: "#32445A" } 
    //             },
    //             'solar-axis': {
    //                 tbeginAtZero: true,
    //                 title: { display: true, text: 'Potencia Solar (W)', color: "#00bfff" },
    //                 ticks: { color: "#00bfff" },
    //                 grid: { color: "#263142" }
    //             },
    //             'carga-axis': {
    //                 beginAtZero: true,
    //                 position: 'right',
    //                 title: { display: true, text: 'Potencia de la Carga (W)', color: "#39ff14" },
    //                 ticks: { color: "#39ff14" },
    //                 grid: { drawOnChartArea: false }
    //             }
    //         }
    //     }
    // });


    // Gráfico de variables solares 
    const voltageCurrentChartSolar = new Chart(ctxVoltageCurrent, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Tensión Solar (V)',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                yAxisID: 'voltage-axis',
                tension: 0.4,
                pointRadius: 0
            },
            {
                label: 'Corriente Solar (A)',
                data: [],
                borderColor: "#39ff14",
                borderWidth: 2,
                yAxisID: 'current-axis',
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Hora',
                    },
                    ticks: { color: "#fff" }, 
                    grid: { color: "#32445A" } 
                },
                'voltage-axis': {
                    tbeginAtZero: true,
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Tensión (V)',
                        color:"#00bfff"
                    },
                    ticks: { color: "#00bfff" },
                    grid: { color: "#263142" }
                },
                'current-axis': {
                    beginAtZero: true,
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Corriente (A)',
                        color:"#39ff14"
                    },
                    ticks: { color: "#39ff14" },
                    grid: { drawOnChartArea: false }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,   
                        pointStyle: 'line',    
                        boxWidth: 60,
                        boxHeight: 30,
                        color: "#fff"
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'x', // Permite pan solo en el eje horizontal
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x', // Permite zoom solo en el eje horizontal
                    }
                }
            }
        }
    });

    // Gráfico de variables red
    const VoltageCurrentRed = new Chart(ctxVoltageCurrentRed, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Tensión (V)',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                yAxisID: 'voltage-axis',
                tension: 0.4,
                pointRadius: 0
            },
            {
                label: 'Corriente (A)',
                data: [],
                borderColor: "#39ff14",
                borderWidth: 2,
                yAxisID: 'current-axis',
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Hora'
                    },
                    ticks: { color: "#fff" }, 
                    grid: { color: "#32445A" } 
                },
                'voltage-axis': {
                    tbeginAtZero: true,
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Tensión (V)',
                        color:"#00bfff"
                    },
                    ticks: { color: "#00bfff" },
                    grid: { color: "#263142" }
                },
                'current-axis': {
                    beginAtZero: true,
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Corriente (A)',
                        color:"#39ff14"
                    },
                    ticks: { color: "#39ff14" },
                    grid: { drawOnChartArea: false }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,   
                        pointStyle: 'line',    
                        boxWidth: 60,
                        boxHeight: 30,
                        color: "#fff"
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'x', // Permite pan solo en el eje horizontal
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x', // Permite zoom solo en el eje horizontal
                    }
                }
            }
        }
    });

    const VoltageCurrentCarga = new Chart(ctxVoltageCurrentCarga, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Tensión Solar (V)',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                yAxisID: 'voltage-axis',
                tension: 0.4,
                pointRadius: 0
            },
            {
                label: 'Corriente Solar (A)',
                data: [],
                borderColor: "#39ff14",
                borderWidth: 2,
                yAxisID: 'current-axis',
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Hora'
                    },
                    ticks: { color: "#fff" }, 
                    grid: { color: "#32445A" } 
                },
                'voltage-axis': {
                    tbeginAtZero: true,
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Tensión (V)',
                        color:"#00bfff"
                    },
                    ticks: { color: "#00bfff" },
                    grid: { color: "#263142" }
                },
                'current-axis': {
                    beginAtZero: true,
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Corriente (A)',
                        color:"#39ff14"
                    },
                    ticks: { color: "#39ff14" },
                    grid: { drawOnChartArea: false }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,   
                        pointStyle: 'line',    
                        boxWidth: 60,
                        boxHeight: 30,
                        color: "#fff"
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'x', // Permite pan solo en el eje horizontal
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x', // Permite zoom solo en el eje horizontal
                    }
                }
            }
        }
    });

    const VoltageCurrentBat = new Chart(ctxVoltageCurrentBat, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Tensión Solar (V)',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                yAxisID: 'voltage-axis',
                tension: 0.4,
                pointRadius: 0
            },
            {
                label: 'Corriente Solar (A)',
                data: [],
                borderColor: "#39ff14",
                borderWidth: 2,
                yAxisID: 'current-axis',
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Hora'
                    },
                    ticks: { color: "#fff" }, 
                    grid: { color: "#32445A" }
                },
                'voltage-axis': {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Tensión (V)',
                        color:"#00bfff"
                    },
                    ticks: { color: "#00bfff" },
                    grid: { color: "#263142" },
                    tbeginAtZero: true

                },
                'current-axis': {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Corriente (A)',
                        color:"#39ff14"
                    },
                    ticks: { color: "#39ff14" },
                    grid: { drawOnChartArea: false },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,   
                        pointStyle: 'line',    
                        boxWidth: 60,
                        boxHeight: 30,
                        color: "#fff"
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'x', // Permite pan solo en el eje horizontal
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x', // Permite zoom solo en el eje horizontal
                    }
                }
            }
        }
    });

    const EnergiaCargaSolar = new Chart(ctxEnergiaCargaSolar, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Energia de la Carga (KWh)',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                yAxisID: 'KWH-axis',
                tension: 0.4,
                pointRadius: 0
            },
           ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Mes'
                    },
                    ticks: { color: "#fff" }, 
                    grid: { color: "#32445A" } 
                },
                'KWH-axis': {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Energia (KWh)',
                        color: "#00bfff"
                    },
                    ticks: { color: "#00bfff" },
                    grid: { color: "#263142" }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,   
                        pointStyle: 'line',    
                        boxWidth: 60,
                        boxHeight: 30,
                        color: "#fff"
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'x', // Permite pan solo en el eje horizontal
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x', // Permite zoom solo en el eje horizontal
                    }
                }
            }
        }
    });



    // const FrecuenciaRed = new Chart(ctxFrecuenciaRed, {
    //     type: 'line',
    //     data: {
    //         labels: [],
    //         datasets: [{
    //             label: 'Frecuencia de la red (Hz)',
    //             data: [],
    //             borderColor: 'rgba(54, 162, 235, 1)',
    //             borderWidth: 2,
    //             yAxisID: 'voltage-axis',
    //             tension: 0.4,
    //             pointRadius: 0
    //         },
    //         {
    //             label: 'Frecuencia de salida (Hz)',
    //             data: [],
    //             borderColor: "#39ff14",
    //             borderWidth: 2,
    //             yAxisID: 'current-axis',
    //             tension: 0.4,
    //             pointRadius: 0
    //         }]
    //     },
    //     options: {
    //         responsive: true,
    //         maintainAspectRatio: false,
    //         scales: {
    //             x: {
    //                 display: true,
    //                 title: {
    //                     display: true,
    //                     text: 'Hora'
    //                 },
    //                 ticks: { color: "#fff" }, 
    //                 grid: { color: "#32445A"}
    //             },
    //             'voltage-axis': {
    //                 type: 'linear',
    //                 position: 'left',
    //                 title: {
    //                     display: true,
    //                     text: 'Frecuencia de la red (Hz)',
    //                     color:"#00bfff"
    //                 },
    //                 beginAtZero: true,
    //                 ticks: { color: "#00bfff" },
    //                 grid: { color: "#263142" }
    //             },
    //             'current-axis': {
    //                 type: 'linear',
    //                 position: 'right',
    //                 title: {
    //                     display: true,
    //                     text: 'Frecuencia de salida (Hz)',
    //                     color: "#39ff14"
    //                 },
    //                 beginAtZero: true,
    //                 ticks: { color: "#39ff14" },
    //                 grid: { drawOnChartArea: false} 
    //             }
    //         },
    //         plugins: {
    //             legend: {
    //                 labels: {
    //                     usePointStyle: true,   
    //                     pointStyle: 'line',    
    //                     boxWidth: 60,
    //                     boxHeight: 30,
    //                     color: "#fff"
    //                 }
    //             },
    //             zoom: {
    //                 pan: {
    //                     enabled: true,
    //                     mode: 'x', // Permite pan solo en el eje horizontal
    //                 },
    //                 zoom: {
    //                     wheel: {
    //                         enabled: true,
    //                     },
    //                     pinch: {
    //                         enabled: true
    //                     },
    //                     mode: 'x', // Permite zoom solo en el eje horizontal
    //                 }
    //             }
    //         }
    //     }
    // });

    const VoltageCurrentMPPT = new Chart(ctxVoltageCurrentMPPT, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Corriente (A)',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                yAxisID: 'current-axis',
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Tensión (V)',
                        color:"#00bfff"
                    },
                    ticks: { color: "#fff" }, 
                    grid: { color: "#32445A" } 
                },
                'current-axis': {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Corriente (A)',
                        color:"#00bfff"
                    },
                    beginAtZero: true,
                    ticks: { color: "#00bfff" },
                    grid: { color: "#263142" }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,   
                        pointStyle: 'line',    
                        boxWidth: 60,
                        boxHeight: 30,
                        color: "#fff"
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'x', // Permite pan solo en el eje horizontal
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x', // Permite zoom solo en el eje horizontal
                    }
                }
            }
        }
    });

    const PowerBat = new Chart(ctxPowerBat, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Potencia',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                yAxisID: 'potencia-axis',
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Tiempo'
                    },
                    ticks: { color: "#fff" }, 
                    grid: { color: "#32445A" }
                },
                'potencia-axis': {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Potencia (W)',
                        color: "#00bfff"
                    },
                    ticks: { color: "#00bfff" },
                    grid: { color: "#263142" },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,   
                        pointStyle: 'line',    
                        boxWidth: 60,
                        boxHeight: 30,
                        color: "#fff"
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'x', // Permite pan solo en el eje horizontal
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x', // Permite zoom solo en el eje horizontal
                    }
                }
            }
        }
    });

    const PowerRed = new Chart(ctxPowerRed, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Potencia',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                yAxisID: 'potencia-axis',
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Tiempo'
                    },
                    ticks: { color: "#fff" }, 
                    grid: { color: "#32445A" } 
                },
                'potencia-axis': {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Potencia (W)',
                        color: "#00bfff"
                    },
                    beginAtZero: true,
                    ticks: { color: "#00bfff" },
                    grid: { color: "#263142" }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,   
                        pointStyle: 'line',    
                        boxWidth: 60,
                        boxHeight: 30,
                        color: "#fff"
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'x', // Permite pan solo en el eje horizontal
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x', // Permite zoom solo en el eje horizontal
                    }
                }
            }
        }
    });

    const PowerCarga = new Chart(ctxPowerCarga, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Potencia',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                yAxisID: 'potencia-axis',
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Tiempo'
                    },
                    ticks: { color: "#fff" }, 
                    grid: { color: "#32445A" } 
                },
                'potencia-axis': {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Potencia (W)',
                        color:"#00bfff"
                    },
                    beginAtZero: true,
                    ticks: { color: "#00bfff" },
                    grid: { color: "#263142" }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,   
                        pointStyle: 'line',    
                        boxWidth: 60,
                        boxHeight: 30,
                        color: "#fff"
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'x', // Permite pan solo en el eje horizontal
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x', // Permite zoom solo en el eje horizontal
                    }
                }
            }
        }
    });


    //Grafico de barras de la energia mensual de la red y solar
    const BarEnerRedSolar = new Chart(ctxBarEnerRedSolar, {
    type: 'bar',
    data: {
        labels: [], // Ejemplo: ['Enero', 'Febrero', ...]
        datasets: [
            {
                label: 'Energia de la red (Wh)',
                data: [], // Array de datos de la red
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                yAxisID: 'WH-axis',
            },
            {
                label: 'Energia solar (Wh)',
                data: [], // Array de datos de energía solar
                backgroundColor: 'rgba(57, 255, 20, 0.5)',
                borderColor: "rgba(57, 255, 20, 1)",
                borderWidth: 2,
                yAxisID: 'WH-axis',
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Mes'
                },
                ticks: { color: "#fff" }, 
                grid: { color: "#32445A" }
            },
            'WH-axis': {
                type: 'linear',
                position: 'left',
                title: {
                    display: true,
                    text: 'Energia (Wh)',
                    color:"#00bfff"
                },
                beginAtZero: true,
                ticks: { color: "#00bfff" },
                grid: { color: "#263142" }
            }
        },
        plugins: {
            legend: {
                labels: {
                    usePointStyle: true,
                    pointStyle: 'rect', // Para barras es mejor rect
                    boxWidth: 60,
                    boxHeight: 30,
                    color: "#fff"
                }
            },
            zoom: {
                pan: { enabled: true, mode: 'x' },
                zoom: {
                    wheel: { enabled: true },
                    pinch: { enabled: true },
                    mode: 'x',
                }
            }
        }
    }
    });



// Grafica de barras de la energia consumida de la red
    // const BarConsMensualSolar = new Chart(ctxBarConsMensualSolar, {
    //     type: 'bar',
    //     data: {
    //         labels: [],
    //         datasets: [{
    //             label: 'Energia consumida (Wh)',
    //             data: [],
    //             borderColor: 'rgba(54, 162, 235, 1)',
    //             borderWidth: 2,
    //             yAxisID: 'WH-axis',
    //             tension: 0.4,
    //             pointRadius: 0
    //         },
    //        ]
    //     },
    //     options: {
    //         responsive: true,
    //         maintainAspectRatio: false,
    //         scales: {
    //             x: {
    //                 display: true,
    //                 title: {
    //                     display: true,
    //                     text: 'Mes'
    //                 },
    //                 ticks: { color: "#fff" }, 
    //                 grid: { color: "#32445A" }
    //             },
    //             'WH-axis': {
    //                 type: 'linear',
    //                 position: 'left',
    //                 title: {
    //                     display: true,
    //                     text: 'Energia (Wh)',
    //                     color:"#00bfff"
    //                 },
    //                 beginAtZero: true,
    //                 ticks: { color: "#00bfff" },
    //                 grid: { color: "#263142" }
    //             }
    //         },
    //         plugins: {
    //             legend: {
    //                 labels: {
    //                     usePointStyle: true,   
    //                     pointStyle: 'line',    
    //                     boxWidth: 60,
    //                     boxHeight: 30,
    //                     color: "#fff"
    //                 }
    //             },
    //             zoom: {
    //                 pan: {
    //                     enabled: true,
    //                     mode: 'x', // Permite pan solo en el eje horizontal
    //                 },
    //                 zoom: {
    //                     wheel: {
    //                         enabled: true,
    //                     },
    //                     pinch: {
    //                         enabled: true
    //                     },
    //                     mode: 'x', // Permite zoom solo en el eje horizontal
    //                 }
    //             }
    //         }
    //     }
    // });

//-----------------------------------------------------------------------------------------------------

//Funciones para las graficas 

    function graficarCurvaSolar() {
        const fecha = fechaInput.value;
        if (fecha) {
            fetch(`/curva_solar?fecha-curva=${fecha}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    //Curva solar 1
                    curvaChart.data.labels = data.labels;
                    curvaChart.data.datasets[0].data = data.solar;
                    curvaChart.data.datasets[1].data = data.carga;
                    curvaChart.update("none");
                    //Curva solar 2
                    // curvaChart2.data.labels = data.labels;
                    // curvaChart2.data.datasets[0].data = data.solar2;
                    // curvaChart2.data.datasets[1].data = data.carga;
                    // curvaChart2.update("none");
                })
                .catch(error => console.error('Error al obtener datos de la curva solar:', error));
        }
    }

    function graficardatos_graficar() {
        fetch('/datos_graficar', {cache: "no-store"})
            .then(response => response.json())
            .then(data => {

                // Voltaje y corriente solar
                voltageCurrentChartSolar.data.labels = data.labels.slice();
                voltageCurrentChartSolar.data.datasets[0].data = data.Voltage_PV_solar.slice();
                voltageCurrentChartSolar.data.datasets[1].data = data.Charging_Current_solar.slice();
                voltageCurrentChartSolar.update("none");
                // Voltaje y corriente de la red
                VoltageCurrentRed.data.labels = data.labels.slice();
                VoltageCurrentRed.data.datasets[0].data = data.voltage_ac.slice();
                VoltageCurrentRed.data.datasets[1].data = data.current_ac.slice();
                VoltageCurrentRed.update("none");
                // Voltaje y corriente de la carga
                VoltageCurrentCarga.data.labels = data.labels.slice();
                VoltageCurrentCarga.data.datasets[0].data = data.voltage_output_i1.slice();
                VoltageCurrentCarga.data.datasets[1].data = data.current_output_i1.slice();
                VoltageCurrentCarga.update("none");
            
                // Voltaje y Corriente de la bateria
                VoltageCurrentBat.data.labels = data.labels.slice();
                VoltageCurrentBat.data.datasets[0].data = data.Voltage_bat.slice();
                VoltageCurrentBat.data.datasets[1].data = data.Current_bat.slice();
                VoltageCurrentBat.update("none");
                // Potencia de la bateria
                PowerBat.data.labels = data.labels.slice();
                PowerBat.data.datasets[0].data = data.power_bat.slice();
                PowerBat.update("none");
                // Potencia de la red
                PowerRed.data.labels = data.labels.slice();
                PowerRed.data.datasets[0].data = data.power_red.slice();
                PowerRed.update("none");
                //Potencia de la carga
                PowerCarga.data.labels = data.labels.slice();
                PowerCarga.data.datasets[0].data = data.power_carga.slice();
                PowerCarga.update("none");
                
                // MPPT
                VoltageCurrentMPPT.data.labels = data.Voltage_PV_solar.slice();
                VoltageCurrentMPPT.data.datasets[0].data = data.Charging_Current_solar.slice();
                VoltageCurrentMPPT.update("none");
                // Frecuencia de la red
                // FrecuenciaRed.data.labels = data.labels.slice();
                // FrecuenciaRed.data.datasets[0].data = data.voltage_output_i2.slice();
                // FrecuenciaRed.data.datasets[1].data = data.current_carga.slice();
                // FrecuenciaRed.update("none");
               
            })
            .catch(error => console.error('Error al obtener datos /datos_graficar:', error));
    }



    function graficarestadisticas_diarias(){
        fetch("/estadisticas_diarias", {cache:"no-store"})
        .then(response => response.json())
        .then(data => {
            
        })
        .catch(error => console.error('Error al obtener datos de consumo diario:', error));
    }   


    function graficarestadisticas_mensuales(){
        fetch("/datos_mensuales", {cache:"no-store"})
        .then(response => response.json())
        .then(data => {
            BarEnerRedSolar.data.labels = data.fecha.slice();
            BarEnerRedSolar.data.datasets[0].data = data.energia_red; 
            BarEnerRedSolar.data.datasets[1].data = data.energia_solar;
            BarEnerRedSolar.update("none");

            // Energia de la carga y solar
            EnergiaCargaSolar.data.labels =data.fecha.slice();
            EnergiaCargaSolar.data.datasets[0].data =data.energia_carga.slice();
            EnergiaCargaSolar.update("none");
        })
        .catch(error => console.error('Error al obtener datos de consumo mensual:', error));
    }


    // ---- CORRECCIÓN DE BOTONES DE ZOOM ----
    function zoomAxis(chart, axisId, factor, tipo) {
        const axis = chart.options.scales[axisId];
        let currentMax = axis.max;
        // Si no hay max definido, lo ajustamos al máximo del dataset correspondiente
        if (typeof currentMax === "undefined" || currentMax === null) {
            let datasetIndex = 0;
            if (axisId === "carga-axis") datasetIndex = 1;
            if (axisId === "current-axis") datasetIndex = 1;
            const datos = chart.data.datasets[datasetIndex].data;
            currentMax = Math.max(...datos);
            if (!isFinite(currentMax) || currentMax === 0) currentMax = 10;
            axis.max = currentMax;
        }
        // Ajusta el máximo del eje según el tipo de zoom (in/out)
        if (tipo === "in") axis.max = axis.max / factor;
        else axis.max = axis.max * factor;
        chart.update("none");
    }

    // Botones de zoom para curva solar
    zoomInSolarBtn.addEventListener('click', () => { zoomAxis(curvaChart, 'solar-axis', zoomFactor, "in"); });
    zoomOutSolarBtn.addEventListener('click', () => { zoomAxis(curvaChart, 'solar-axis', zoomFactor, "out"); });
    zoomInCargaBtn.addEventListener('click', () => { zoomAxis(curvaChart, 'carga-axis', zoomFactor, "in"); });
    zoomOutCargaBtn.addEventListener('click', () => { zoomAxis(curvaChart, 'carga-axis', zoomFactor, "out"); });


    // Listeners para cambio de fecha y botón
    fechaInput.addEventListener('change', graficarCurvaSolar);
    btnGraficar.addEventListener('click', graficarCurvaSolar);

    // Carga las gráficas del día actual al inicio
    const today = new Date().toISOString().slice(0, 10);
    fechaInput.value = today;
    graficarCurvaSolar();
    graficardatos_graficar();
    graficarestadisticas_diarias()
    actualizarDatos();
    actualizarDatosMensuales();
    actualizarDatosDiarios();
    graficarestadisticas_mensuales();

    // Actualización automática de las gráficas cada 5 segundos
    setInterval(() => {
        const today = new Date().toISOString().slice(0, 10);
        if (fechaInput.value === today) {
            graficarCurvaSolar();
        }
    }, 10000);

    setInterval(graficardatos_graficar, 10000);
    setInterval(graficarestadisticas_diarias,60000);
    setInterval(actualizarDatos,5000);
    setInterval(actualizarDatosMensuales, 10000);
    setInterval(actualizarDatosDiarios, 60000);
    setInterval(graficarestadisticas_mensuales,100000);
});

function actualizarReloj() {
    const ahora = new Date();

    // Obtener la fecha
    const dia = ahora.getDate().toString().padStart(2, '0');
    const mes = (ahora.getMonth() + 1).toString().padStart(2, '0');
    const año = ahora.getFullYear();

    // Obtener la hora
    const horas = ahora.getHours().toString().padStart(2, '0');
    const minutos = ahora.getMinutes().toString().padStart(2, '0');
    const segundos = ahora.getSeconds().toString().padStart(2, '0');

    // Construir las cadenas para la fecha y la hora
    const fechaTexto = `${dia}/${mes}/${año}`;
    const horaTexto = `${horas}:${minutos}:${segundos}`;

    // Actualizar todos los elementos con la clase 'reloj'
    const relojes = document.querySelectorAll('.reloj');
    relojes.forEach(el => el.textContent = horaTexto);

    // Actualizar todos los elementos con la clase 'fecha'
    const fechas = document.querySelectorAll('.fecha');
    fechas.forEach(el => el.textContent = fechaTexto);
}

// Para que el reloj se actualice cada segundo:
setInterval(actualizarReloj, 1000);

// También puedes llamarla una vez al cargar la página
actualizarReloj();
