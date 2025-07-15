let charts = {};
let originalScales = {};

function saveOriginalScales(chartId) {
    if (!charts[chartId]) return;
    const chart = charts[chartId];
    if (!originalScales[chartId]) originalScales[chartId] = {};
    ['y-volt','y-corr'].forEach(axis => {
        const scale = chart.scales[axis];
        if (scale) {
            originalScales[chartId][axis] = { min: scale.min, max: scale.max };
        }
    });
}

function zoomYAxis(chartId, axisId, factor) {
    const chart = charts[chartId];
    if (!chart) return;
    const scale = chart.scales[axisId];
    if (!scale) return;
    if (!originalScales[chartId] || !originalScales[chartId][axisId]) {
        saveOriginalScales(chartId);
    }
    let min = scale.min;
    let max = scale.max;
    let range = max - min;
    let center = (max + min) / 2;
    let newRange = range * factor;
    chart.options.scales[axisId].min = center - newRange / 2;
    chart.options.scales[axisId].max = center + newRange / 2;
    chart.update();
}

function setZoomMode(chartId, mode) {
    if (charts[chartId]) {
        charts[chartId].options.plugins.zoom.zoom.mode = mode;
        charts[chartId].options.plugins.zoom.pan.mode = mode;
        charts[chartId].update();
    }
}

function resetZoom(chartId) {
    if (charts[chartId]) {
        charts[chartId].resetZoom();
        if(originalScales[chartId]) {
            ['y-volt','y-corr'].forEach(axis => {
                if (originalScales[chartId][axis]) {
                    charts[chartId].options.scales[axis].min = originalScales[chartId][axis].min;
                    charts[chartId].options.scales[axis].max = originalScales[chartId][axis].max;
                }
            });
            charts[chartId].update();
        }
    }
}

function autoUpdateChart(id, endpoint, chartType, dataCallback, options, interval=30000) {
    const ctx = document.getElementById(id).getContext('2d');
    async function fetchAndUpdate() {
        const res = await fetch(endpoint + '?_=' + new Date().getTime());
        const data = await res.json();
        const chartData = dataCallback(data);
        if (charts[id]) {
            charts[id].data = chartData.data;
            charts[id].update();
        } else {
            charts[id] = new Chart(ctx, {
                type: chartType,
                data: chartData.data,
                options: options
            });
            setTimeout(() => saveOriginalScales(id), 500);
        }
    }
    fetchAndUpdate();
    setInterval(fetchAndUpdate, interval);
}

// --- Red eléctrica (Variables Electricas)---
autoUpdateChart(
    'redElectrica',
    '/api/red-electrica',
    'line',
    data => ({
        data: {
            labels: data.map(d=>d.fecha_hora),
            datasets: [
                {
                    label: 'Tensión (V)',
                    data: data.map(d=>d.voltage_ac),
                    borderColor: 'rgb(0, 191, 255)',
                    backgroundColor: 'rgba(0,191,255,0.12)',
                    borderWidth: 2,
                    tension: 0.4,
                    yAxisID: 'y-volt'
                },
                {
                    label: 'Corriente (A)',
                    data: data.map(d=>d.current_carga),
                    borderColor: "rgb(57, 255, 20)",
                    backgroundColor: 'rgba(57,255,20,0.09)',
                    borderWidth: 2,
                    tension: 0.4,
                    yAxisID: 'y-corr'
                }
            ]
        }
    }),
    {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        stacked: false,
        plugins: {
            legend: { position: 'top', label:{color:"#fff"} },
            zoom: {
                zoom: {
                    wheel: { enabled: true },
                    pinch: { enabled: true },
                    mode: 'y'
                },
                pan: {
                    enabled: true,
                    mode: 'y'
                }
            }
        },
        scales: {
            x: {
                title: {display: true, 
                text: 'Fecha y hora' },
                ticks: { color: "#fff" }, 
                grid: { color: "rgb(32, 40, 53)" }
            },
            'y-volt': {
                type: 'linear',
                display: true,
                position: 'left',
                title: {display: true, text: 'Tensión (V)', 
                color: "rgb(0, 191, 255)"},
                beginAtZero: true,
                ticks: { color: "rgb(0, 191, 255)" },
                grid: { color: "rgb(38,49,66)" }
            },
            'y-corr': {
                type: 'linear',
                display: true,
                position: 'right',
                title: {display: true, text: 'Corriente (A)', 
                color:"rgb(57, 255, 20)"},
                ticks: { color: "rgb(57, 255, 20)" }
            }
        }
    }
);

// --- Carga (Variables Elecricas)---
autoUpdateChart(
    'chartcarga',
    '/api/carga',
    'line',
    data => ({
        data: {
            labels: data.map(d=>d.fecha_hora),
            datasets: [
                {
                    label: 'Tensión (V)',
                    data: data.map(d=>d.voltage),
                    yAxisID: 'y-volt',
                    borderColor: '#00bfff',
                    backgroundColor: 'rgba(0,191,255,0.12)',
                    borderWidth: 2
                },
                {
                    label: 'Corriente (A)',
                    data: data.map(d=>d.current),
                    borderColor: '#39ff14',
                    backgroundColor: 'rgba(57,255,20,0.09)',
                    borderWidth: 2,
                    yAxisID: 'y-corr'
                }
            ]
        }
    }),
    {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        stacked: false,
        plugins: {
            legend: { position: 'top' },
            zoom: {
                zoom: {
                    wheel: { enabled: true },
                    pinch: { enabled: true },
                    mode: 'y'
                },
                pan: {
                    enabled: true,
                    mode: 'y'
                }
            }
        },
        scales: {
            x: {
                title: {display: true, text: 'Fecha y hora'},
                ticks: { color: "#fff" }, 
                grid: { color: "#32445A" }
            },
            'y-volt': {
                type: 'linear',
                display: true,
                position: 'left',
                title: {display: true, text: 'Tensión (V)', color: "#00bfff" },
                ticks: { color: "#00bfff" },
                grid: { color: "#263142" }
            },
            'y-corr': {
                type: 'linear',
                display: true,
                position: 'right',
                title: {display: true, text: 'Corriente (A)', color: "#39ff14" },
                ticks: { color: "#39ff14" },
                grid: {drawOnChartArea: false}
            }
        }
    }
);
 // --Carga Mensual--
autoUpdateChart(
    'chartcargamensual',
    '/api/energia-mensual-carga',
    'bar',
    data => ({
        data: {
            labels: data.labels,
            datasets: [{
                label: 'kWh',
                data: data.valores,
                backgroundColor: 'rgba(19,224,200,0.6)',
                borderColor: '#13e0c8',
                borderWidth: 1
            }]
        }
    })
);

// --- Solar (Variables Electricas) ---
autoUpdateChart(
    'solarLinea',
    '/api/solar-linea',
    'line',
    data => ({
        data: {
            labels: data.map(d=>d.fecha_hora),
            datasets: [
                {
                    label: 'Tensión Solar (V)',
                    data: data.map(d=>d.voltage),
                    borderColor:'orange',
                    yAxisID: 'y-volt'
                },
                {
                    label: 'Corriente Solar (A)',
                    data: data.map(d=>d.current),
                    borderColor:'brown',
                    yAxisID: 'y-corr'
                }
            ]
        }
    }),
    {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        stacked: false,
        plugins: {
            legend: { position: 'top' },
            zoom: {
                zoom: {
                    wheel: { enabled: true },
                    pinch: { enabled: true },
                    mode: 'y'
                },
                pan: {
                    enabled: true,
                    mode: 'y'
                }
            }
        },
        scales: {
            x: {
                title: {display: true, text: 'Fecha y hora'},
                ticks: { color: "#fff" }, 
                grid: { color: "#32445A" }
            },
            'y-volt': {
                type: 'linear',
                display: true,
                position: 'left',
                title: {display: true, text: 'Tensión Solar (V)', color: "#00bfff" },
                ticks: { color: "#00bfff" },
                grid: { color: "#263142" }
            },
            'y-corr': {
                type: 'linear',
                display: true,
                position: 'right',
                title: {display: true, text: 'Corriente Solar (A)', color: "#39ff14" },
                ticks: { color: "#39ff14" },
                grid: {drawOnChartArea: false}
            }
        }
    }
);

// --- Curva Solar del día ---
let curvaSolarChart;

function completarHoras5min(data) {
    // Crea todos los intervalos de 5 minutos del día
    let horas = [];
    for(let h=0; h<24; h++) {
        for(let m=0; m<60; m+=5) {
            horas.push(`${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}`);
        }
    }
    // Llena los datos con potencia (0 si no hay datos)
    let potenciaPorHora = {};
    data.forEach(d => { potenciaPorHora[d.hora] = d.potencia; });
    return horas.map(h => ({hora: h, potencia: potenciaPorHora[h] || 0}));
}

function actualizarCurvaSolar() {
    const fecha = document.getElementById('solarFecha').value;
    let endpoint = '/api/solar-curva';
    if (fecha) endpoint += '?fecha=' + fecha;
    fetch(endpoint)
        .then(res => res.json())
        .then(data => {
            data = completarHoras5min(data); // Para mostrar todos los intervalos aunque no haya datos
            const labels = data.map(d => d.hora);
            const valores = data.map(d => d.potencia);
            if (curvaSolarChart) {
                curvaSolarChart.data.labels = labels;
                curvaSolarChart.data.datasets[0].data = valores;
                curvaSolarChart.update();
            } else {
                const ctx = document.getElementById('curvaSolar').getContext('2d');
                curvaSolarChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Potencia Solar (W)',
                            data: valores,
                            borderColor: 'orange',
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { 
                                title: { display: true, text: 'Hora del día' },
                                ticks: { color: "#fff" }, 
                                grid: { color: "#32445A" }
                            },
                            y: { 
                                title: { display: true, text: 'Potencia (W)', color: "#39ff14" },
                                ticks: { color: "#39ff14" },
                                grid: {drawOnChartArea: false}
                            }
                        }
                    }
                });
            }
        });
}

document.addEventListener('DOMContentLoaded', () => {
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('solarFecha').value = hoy;
    actualizarCurvaSolar();
});