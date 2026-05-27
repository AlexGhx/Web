from flask import Flask, send_from_directory, request
app = Flask(__name__)
@app.route("/")
def inicio():
    return send_from_directory("", "Principal.html")
@app.route("/Estilo.css")
def estilos():
    return send_from_directory("", "Estilo.css")
@app.route("/Imagenes/Pagina_Principal.png")
def imagen():
    return send_from_directory("", "Imagenes/Pagina_Principal.png")
@app.route("/Imagenes/Polo.png")
def imagen2():
    return send_from_directory("", "Imagenes/Polo.png")
@app.route("/Imagenes/Camisas.png")
def imagen3():
    return send_from_directory("", "Imagenes/Camisas.png")
@app.route("/Imagenes/Chalecos.png")
def imagen4():
    return send_from_directory("", "Imagenes/Chalecos.png")
@app.route("/Imagenes/Clasico.png")
def imagen5():
    return send_from_directory("", "Imagenes/Clasico.png")
@app.route("/Imagenes/Urbano.png")
def imagen6():
    return send_from_directory("", "Imagenes/Urbano.png")
@app.route("/Imagenes/Minimalista.png")
def imagen7():
    return send_from_directory("", "Imagenes/Minimalista.png")
@app.route("/Paginas/Login.html")
def login():
    return send_from_directory("Paginas", "Login.html")
@app.route("/registrar", methods=["POST"])
def registrar():
    usuario = request.form["usuario"]
    correo = request.form["correo"]
    password = request.form["password"]
    confirmar = request.form["confirmar"]
    if usuario == "" or correo == "" or password == "" or confirmar == "":
        return "Complete todos los campos"
    if password != confirmar:
        return "Las contraseñas no coinciden"
    print("Usuario:", usuario)
    print("Correo:", correo)
    print("Contraseña:", password)
    return "Usuario registrado correctamente"
if __name__ == "__main__":
    app.run(debug=True)