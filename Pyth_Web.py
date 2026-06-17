from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3

app = Flask(__name__)
app.secret_key = "Camote123"

import sqlite3
conn = sqlite3.connect('usuarios.db')
conn.execute("INSERT INTO usuarios(usuario, correo, password) VALUES('admin', 'admin@tienda.com', 'admin123')")
conn.commit()
conn.close()

# --- Base de datos ---
def init_db():
    conexion = sqlite3.connect('usuarios.db')
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            correo TEXT,
            password TEXT
        )
    ''')
    conexion.commit()
    conexion.close()

init_db()

# --- Rutas principales ---
@app.route("/")
def inicio():
    return render_template("Principal.html")

@app.route("/tienda")
def tienda():
    return render_template("Tienda.html")

@app.route("/carrito")
def carrito():
    return render_template("Carrito.html")

# --- Autenticación ---
@app.route("/login")
def login():
    return render_template("Login.html")

@app.route("/inicio")
def Inicio_Sesion():
    return render_template("Inicio_Sesion.html")

@app.route("/admin")
def admin():
    if session.get("usuario") != "admin": 
        return redirect(url_for('inicio'))
    return render_template("Admin.html")

@app.route("/conexion")
def Conexion():
    return render_template("Conexion.html", usuario=session.get("usuario"))

@app.route("/registrar", methods=["POST"])
def registrar():
    conexion = sqlite3.connect('usuarios.db')
    cursor = conexion.cursor()
    cursor.execute(
        'INSERT INTO usuarios(usuario, correo, password) VALUES(?,?,?)',
        (request.form['usuario'], request.form['correo'], request.form['password'])
    )
    conexion.commit()
    conexion.close()
    return redirect(url_for('Inicio_Sesion'))

@app.route("/inicio_sesion", methods=["POST"])
def inicio_sesion():
    val_correo = request.form["correo"]
    val_password = request.form["password"]
    conexion = sqlite3.connect('usuarios.db')
    cursor = conexion.cursor()
    cursor.execute(
        'SELECT * FROM usuarios WHERE correo=? AND password=?',
        (val_correo, val_password)
    )
    usuario = cursor.fetchone()
    conexion.close()
    if usuario:
        session["usuario"] = usuario[1]
        return redirect(url_for('Conexion'))
    else:
        return "Correo o contraseña incorrectos"

@app.route("/contacto", methods=["POST"])
def contacto():
    # Aquí se procesaría el mensaje de contacto
    return redirect(url_for('inicio') + '#contacto')

# --- Servir imágenes ---
@app.route("/Imagenes/<path:nombre>")
def imagenes(nombre):
    return send_from_directory("static/Imagenes", nombre)

if __name__ == "__main__":
    app.run(debug=True)
