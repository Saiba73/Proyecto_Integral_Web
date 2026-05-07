import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
# from server.db import

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_de_desarrollo_insegura') 
bcrypt = Bcrypt(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/login')
def about():
    return render_template('login.html')

@app.route('/cambiarContrasena')
def about():
    return render_template('cambiarContrasena.html')

    @app.route('/registrar')
def about():
    return render_template('registrar.html')

@app.route('/ropa')
def about():
    return render_template('ropa.html')

@app.route('/tazas')
def about():
    return render_template('tazas.html')

@app.route('/impresiones')
def about():
    return render_template('impresiones.html')

@app.route('/perfil')
def about():
    return render_template('perfil.html')

@app.route('/perfilAdmin')
def about():
    return render_template('perfilAdmin.html')

@app.route('/carrito')
def about():
    return render_template('carrito.html')

@app.route('/cehckout')
def about():
    return render_template('checkout.html')

if __name__ == "__main__":
    app.run(debug=True)