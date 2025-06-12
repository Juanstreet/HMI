from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = "/media/krillbox/HMI/basededatos.db"

# Función para obtener el último registro
def get_last_row():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datos ORDER BY fecha_hora DESC, id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    else:
        return {}

# Ruta principal
@app.route("/")
def index():
    registro = get_last_row()
    return render_template("index.html", registro=registro)

# Ruta para AJAX que devuelve el último registro como JSON
@app.route("/ultimo_registro")
def ultimo_registro():
    registro = get_last_row()
    return jsonify(registro)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)