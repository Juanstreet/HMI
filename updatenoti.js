document.addEventListener('DOMContentLoaded', () => {
    const ctxBarConsMensualRed = document.getElementById('BarConsMensualRed').getContext('2d');
    const ctxBarConsMensualSolar = document.getElementById('BarConsMensualSolar').getContext('2d');
    const ctxBarConsMensualDias = document.getElementById('BarConsMensualDias').getContext('2d');
    const ctxBarSolarMensualDias = document.getElementById("BarSolarMensualDias").getContext("2d");
    const ctxVoltageCurrentCarga2 = document.getElementById("VoltageCurrentCarga2").getContext("2d");
    const ctxBarConsMensual = document.getElementById("BarConsMensual").getContext("2d");


    // Inicializa los campos con el día actual
    const today = new Date().toISOString().slice(0, 10);
    document.getElementById('start_date').value = today;
    document.getElementById('end_date').value = today;

    // Actualiza la tabla de alarmas activas según las fechas seleccionadas (o día actual si no hay selección)
    function actualizarTablaAlarmas(startDate = "", endDate = "") {
        // Si no hay fechas, usa el día actual
        if (!startDate) startDate = today;
        if (!endDate) endDate = today;
        let url = `/alarmas_activas?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const tbody = document.getElementById('alarmas-tbody');
                tbody.innerHTML = "";
                const alarmas = data.alarmas_activas || [];
                if (alarmas.length === 0 || data.error) {
                    tbody.innerHTML = '<tr><td colspan="3">No hay alarmas activas en el periodo seleccionado.</td></tr>';
                } else {
                    alarmas.forEach(a => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${a.fecha_hora}</td>
                            <td>${a.codigo_alarma}</td>
                            <td>${a.alarma}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
            })
            .catch(e => {
                const tbody = document.getElementById('alarmas-tbody');
                tbody.innerHTML = '<tr><td colspan="3">Error al obtener alarmas</td></tr>';
            });
    }

    // Evento para el formulario
    document.getElementById('filtro-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        actualizarTablaAlarmas(startDate, endDate);
    });

    // Inicializa la tabla al cargar (día actual)
    actualizarTablaAlarmas(today, today);


    function actualizarDatos() {
        fetch('/ultimo_registro')
            .then(response => response.json())
            .then(data => {
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
                "current_ac","current_inp_inv", "power_bat","ciclos_bat"
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
    };



    const VoltageCurrentCarga2 = new Chart(ctxVoltageCurrentCarga2, {
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
                borderColor: 'rgba(255, 99, 132, 1)',
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
                    }
                },
                'voltage-axis': {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Tensión (V)'
                    }
                },
                'current-axis': {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Corriente (A)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    }
                }
            },
            plugins: {
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

    //Grafico de barras del consumo mensual
    const BarConsMensual = new Chart(ctxBarConsMensual, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Energia consumida (KWh)',
                data: [],
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

// Grafica de barras de la energia consumida de la red
    const BarConsMensualRed = new Chart(ctxBarConsMensualRed, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Energia consumida (KWh)',
                data: [],
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

// Grafica de barras de la energia consumida de la red
    const BarConsMensualSolar = new Chart(ctxBarConsMensualSolar, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Energia consumida (KWh)',
                data: [],
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

//  Grafica de barras de la energia consumida en los 7 ultimos dias
    const BarConsMensualDias = new Chart(ctxBarConsMensualDias, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Energia consumida (KWh)',
                data: [],
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
                        color:"#00bfff"
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

    const BarSolarMensualDias = new Chart(ctxBarSolarMensualDias, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Energia Solar (KWh)',
                data: [],
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
//-----------------------------------------------------------------------------------------------------

//Funciones para las graficas 
    function graficardatos_graficar() {
        fetch('/datos_graficar', {cache: "no-store"})
            .then(response => response.json())
            .then(data => {
                //Voltaje y corriente de la carga 2
                VoltageCurrentCarga2.data.labels = data.labels.slice();
                VoltageCurrentCarga2.data.datasets[0].data = data.voltage_output_i2.slice();
                VoltageCurrentCarga2.data.datasets[1].data = data.current_output_i2.slice();
                VoltageCurrentCarga2.update("none");
            })
            .catch(error => console.error('Error al obtener datos /datos_graficar:', error));
    }


    function graficarestadisticas_mensuales(){
        fetch("/datos_mensuales", {cache:"no-store"})
        .then(response => response.json())
        .then(data => {
            // Energia consumidaporla carga mensual
            BarConsMensual.data.labels = data.fecha.slice();
            BarConsMensual.data.datasets[0].data = data.energia_carga;
            BarConsMensual.update("none");

            // Energia consumida de la red mensual
            BarConsMensualRed.data.labels = data.fecha.slice();
            BarConsMensualRed.data.datasets[0].data = data.energia_red;
            BarConsMensualRed.update("none");

            BarConsMensualSolar.data.labels = data.fecha.slice();
            BarConsMensualSolar.data.datasets[0].data = data.energia_solar;
            BarConsMensualSolar.update("none");
        })
        .catch(error => console.error('Error al obtener datos de consumo mensual:', error));
    }


    function graficarestadisticas_diarias(){
        fetch("/estadisticas_diarias", {cache:"no-store"})
        .then(response => response.json())
        .then(data => {
            // Graficar consumo en 7 dias
            BarConsMensualDias.data.labels = data.fechas_a_considerar_carga.slice();
            BarConsMensualDias.data.datasets[0].data = data.fechas_a_considerar_carga.map(
                dia => data.energias_diarias_carga[dia]
            );
            BarConsMensualDias.update("none");

            // Graficar energia solar en los ultimos 7 dias
            BarSolarMensualDias.data.labels = data.fechas_a_considerar_carga.slice();
            BarSolarMensualDias.data.datasets[0].data = data.fechas_a_considerar_carga.map(
                dia => data.energias_diarias_solar[dia]
            );
            BarSolarMensualDias.update("none");
            
        })
        .catch(error => console.error('Error al obtener datos de consumo diario:', error));
    }   



    graficardatos_graficar();
    graficarestadisticas_mensuales();
    graficarestadisticas_diarias()
    actualizarDatos();

    setInterval(graficardatos_graficar, 10000);
    setInterval(graficarestadisticas_mensuales,60000);
    setInterval(graficarestadisticas_diarias,60000);
    setInterval(actualizarDatos,10000);
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
