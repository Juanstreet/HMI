document.getElementById("descarga-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const tipo = document.getElementById("tipo").value;
    let date_start = document.getElementById("date_start").value;
    let date_end = document.getElementById("date_end").value;

    // Si es resumen mensual, no enviar fechas
    let url = `/descargar_csv?tipo=${encodeURIComponent(tipo)}`;
    if (tipo !== "resumen_mensual") {
        // Valida fechas
        if (!date_start || !date_end) {
            alert("Por favor selecciona el rango de fechas.");
            return;
        }
        // Se envía como YYYY-MM-DD, backend ajusta hora
        url += `&date_start=${encodeURIComponent(date_start)}&date_end=${encodeURIComponent(date_end)}`;
    }

    window.location.href = url;
});

// Oculta campos de fecha si selecciona resumen mensual
document.getElementById("tipo").addEventListener("change", function() {
    const fechasFields = document.getElementById("fechas-fields");
    if (this.value === "resumen_mensual") {
        fechasFields.style.display = "none";
    } else {
        fechasFields.style.display = "block";
    }
});