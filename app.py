import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
# from server.db import

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_de_desarrollo_insegura') 
bcrypt = Bcrypt(app)

def login_required(f):
    """Decorador para restringir el acceso si no hay sesión activa."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            # Si no hay sesión, redirige al login
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Se accede sin login
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/login', metods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/registrar', metods=['GET', 'POST'])
def registrar():

    if request.method == 'POST':
        fname = request.form['nombre']
        lastname = request.form.['correo']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['cpassword']

    if password != confirm_password:
            return render_template('signup.html', error="Error: Las contraseñas no coinciden.")

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    user_id = agregar_usuario(correo, email, password_hash)

    if user_id:
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', error="Error al registrar usuario. El email ya existe.")
            
    return render_template('signup.html')


    return render_template('registrar.html')

@app.route('/ropa', metods=['GET'])
def ropa():
    return render_template('ropa.html')

@app.route('/tazas', metods=['GET'])
def tazas():
    return render_template('tazas.html')

@app.route('/impresiones', metods=['GET'])
def impresiones():
    return render_template('impresiones.html')

@app.route('/carrito', metods=['GET', 'POST'])
def carrito():
    return render_template('carrito.html')
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Requiere login
@app.route('/cambiarContrasena', metods=['GET', 'PUT'])
def cambiar_contrasena():
    return render_template('cambiarContrasena.html')


@app.route('/perfil', metods=['GET', 'POST', 'PUT', 'DELETE'])
def perfil():
    return render_template('perfil.html')

@app.route('/perfilAdmin', metods=['GET', 'POST', 'PUT', 'DELETE'])
def perfil_admin():
    return render_template('perfilAdmin.html')

@app.route('/checkout', metods=['GET', 'POST']) # Corregido el typo
def checkout():
    return render_template('checkout.html')
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)