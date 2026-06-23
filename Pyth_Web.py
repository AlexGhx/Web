from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "Camote123"

UPLOAD_FOLDER = os.path.join('static', 'Uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            categoria TEXT,
            descripcion TEXT,
            precio REAL,
            imagen TEXT
        )
    ''')
    # Agrega columnas faltantes si la tabla ya existía sin ellas
    columnas_extra = [
        ('stock',  'ALTER TABLE productos ADD COLUMN stock INTEGER DEFAULT 0'),
        ('estado', 'ALTER TABLE productos ADD COLUMN estado TEXT DEFAULT "Activo"'),
        ('imagen', 'ALTER TABLE productos ADD COLUMN imagen TEXT DEFAULT ""'),
    ]
    cursor.execute("PRAGMA table_info(productos)")
    columnas_existentes = {row[1] for row in cursor.fetchall()}
    for col, sql in columnas_extra:
        if col not in columnas_existentes:
            cursor.execute(sql)
    # Insertar productos por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos_default = [
            ('Polo Clásico Blanco',  'Polo',        'Polo básico de algodón premium, ideal para el día a día.',         59.90, 50, 'Activo', 'Polo.png'),
            ('Polo Urbano Negro',    'Polo',        'Corte moderno con detalle en mangas, perfecto para el streetwear.',64.90, 35, 'Activo', 'Polo.png'),
            ('Polo Minimalista Gris','Polo',        'Simple y elegante, perfecto para cualquier combinación.',          54.90, 40, 'Activo', 'Polo.png'),
            ('Camisa Denim Azul',    'Camisa',      'Mezclilla con acabados premium para un look casual sofisticado.',  89.90, 25, 'Activo', 'Camisas.png'),
            ('Camisa Lino Blanca',   'Camisa',      'Ligera y fresca, ideal para el verano y ocasiones formales.',      79.90, 30, 'Activo', 'Camisas.png'),
            ('Camisa Urbana Oversize','Camisa',     'Corte oversize inspirado en el streetwear contemporáneo.',         95.90, 20, 'Activo', 'Camisas.png'),
            ('Chaleco Urbano Gris',  'Chaleco',     'Chaleco acolchado perfecto para días fríos con estilo.',           79.90, 15, 'Activo', 'Chalecos.png'),
            ('Chaleco Clásico Beige','Chaleco',     'Elegante y versátil para toda ocasión y estación.',                85.90, 18, 'Activo', 'Chalecos.png'),
            ('Look Clásico Premium', 'Clasico',     'Conjunto clásico de alta calidad para ocasiones especiales.',     120.00, 10, 'Activo', 'Clasico.png'),
            ('Outfit Urbano Completo','Urbano',     'Conjunto urbano moderno para un look total en la ciudad.',        110.00, 12, 'Activo', 'Urbano.png'),
            ('Set Minimalista',      'Minimalista', 'Conjunto minimalista con prendas de líneas puras y colores neutros.',99.90, 20, 'Activo', 'Minimalista.png'),
        ]
        cursor.executemany(
            'INSERT INTO productos(nombre, categoria, descripcion, precio, stock, estado, imagen) VALUES(?,?,?,?,?,?,?)',
            productos_default
        )
    cursor.execute("SELECT * FROM usuarios WHERE correo='admin@tienda.com'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios(usuario, correo, password) VALUES(?,?,?)",
            ('admin', 'admin@tienda.com', 'admin123')
        )
    conexion.commit()
    conexion.close()

init_db()

def get_imagen_url(imagen):
    if not imagen:
        return '/static/Imagenes/Polo.png'
    if imagen.startswith('/'):
        return imagen
    # Imágenes por defecto viven en /static/Imagenes/
    default_imgs = {'Polo.png','Camisas.png','Chalecos.png','Clasico.png','Urbano.png','Minimalista.png','Pagina_Principal.png'}
    if imagen in default_imgs:
        return '/static/Imagenes/' + imagen
    # Imágenes subidas por el admin viven en /static/Uploads/
    return '/static/Uploads/' + imagen

# Hacemos get_imagen_url disponible en templates
app.jinja_env.globals['get_imagen_url'] = get_imagen_url

# --- Rutas principales ---
@app.route("/")
def inicio():
    return render_template("Principal.html", usuario=session.get("usuario"))

@app.route("/tienda")
def tienda():
    conexion = sqlite3.connect('usuarios.db')
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos WHERE estado='Activo' ORDER BY id DESC")
    productos = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    return render_template("Tienda.html", usuario=session.get("usuario"), productos=productos)

@app.route("/carrito")
def carrito():
    return render_template("Carrito.html", usuario=session.get("usuario"))

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
    conexion = sqlite3.connect('usuarios.db')
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos ORDER BY id DESC")
    productos = [dict(row) for row in cursor.fetchall()]
    conexion.close()
    from flask import request as req
    ok = req.args.get('ok')
    mensaje = f'Producto "{ok}" agregado exitosamente.' if ok else None
    return render_template("Admin.html", usuario=session.get("usuario"), productos=productos, mensaje=mensaje)

@app.route("/admin/agregar", methods=["POST"])
def admin_agregar():
    if session.get("usuario") != "admin":
        return redirect(url_for('inicio'))
    
    nombre = request.form.get('nombre', '').strip()
    categoria = request.form.get('categoria', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    precio = request.form.get('precio', 0)
    stock = request.form.get('stock', 0)
    estado = request.form.get('estado', 'Activo')
    
    imagen_nombre = ''
    if 'imagen' in request.files:
        file = request.files['imagen']
        if file and file.filename:
            imagen_nombre = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, imagen_nombre))
    
    conexion = sqlite3.connect('usuarios.db')
    cursor = conexion.cursor()
    cursor.execute(
        'INSERT INTO productos(nombre, categoria, descripcion, precio, stock, estado, imagen) VALUES(?,?,?,?,?,?,?)',
        (nombre, categoria, descripcion, float(precio), int(stock) if stock else 0, estado, imagen_nombre)
    )
    conexion.commit()
    conexion.close()
    
    # Re-render admin with success message
    from flask import flash
    return redirect(url_for('admin') + f'?ok={nombre}')

@app.route("/admin/editar/<int:prod_id>", methods=["POST"])
def admin_editar(prod_id):
    if session.get("usuario") != "admin":
        return redirect(url_for('inicio'))
    nombre = request.form.get('nombre', '').strip()
    categoria = request.form.get('categoria', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    precio = request.form.get('precio', 0)
    stock = request.form.get('stock', 0)
    estado = request.form.get('estado', 'Activo')
    conexion = sqlite3.connect('usuarios.db')
    cursor = conexion.cursor()
    cursor.execute(
        'UPDATE productos SET nombre=?, categoria=?, descripcion=?, precio=?, stock=?, estado=? WHERE id=?',
        (nombre, categoria, descripcion, float(precio), int(stock) if stock else 0, estado, prod_id)
    )
    conexion.commit()
    conexion.close()
    return redirect(url_for('admin'))

@app.route("/admin/eliminar/<int:prod_id>", methods=["POST"])
def admin_eliminar(prod_id):
    if session.get("usuario") != "admin":
        return redirect(url_for('inicio'))
    conexion = sqlite3.connect('usuarios.db')
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (prod_id,))
    conexion.commit()
    conexion.close()
    return redirect(url_for('admin'))

@app.route("/conexion")
def Conexion():
    if not session.get("usuario"):
        return redirect(url_for('Inicio_Sesion'))
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

@app.route("/cerrar_sesion")
def cerrar_sesion():
    session.clear()
    return redirect(url_for('inicio'))

@app.route("/contacto", methods=["POST"])
def contacto():
    return redirect(url_for('inicio') + '#contacto')

# --- Servir imágenes ---
@app.route("/Imagenes/<path:nombre>")
def imagenes(nombre):
    return send_from_directory("static/Imagenes", nombre)

if __name__ == "__main__":
    app.run(debug=True)
