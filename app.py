import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from Server.server import agregar_usuario, obtener_usuario_por_email

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        usuario = obtener_usuario_por_email(email)
        
        if usuario:
            if bcrypt.check_password_hash(usuario['password_hash'], password):
                session['logged_in'] = True
                session['user_id'] = usuario['id']
                session['user_email'] = usuario['email']
                
                # 3. Redirigir al Home Protegido
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error="Contraseña o email incorrectos.")
        else:
            return render_template('login.html', error="Contraseña o email incorrectos.")
            
    # Muestra el formulario GET
    return render_template('login.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['correo']
        password = request.form['password']
        confirm_password = request.form['cpassword']

        if password != confirm_password:
            return render_template('signup.html', error="Error: Las contraseñas no coinciden.")

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        user_id = agregar_usuario(nombre, email, password_hash)

        if user_id:
                return redirect(url_for('login'))
        else:
            return render_template('registrar.html', error="Error al registrar usuario. El email ya existe.")
    
    return render_template('registrar.html')

@app.route('/ropa', methods=['GET'])
def ropa():
    return render_template('ropa.html')

@app.route('/tazas', methods=['GET'])
def tazas():
    return render_template('tazas.html')

@app.route('/impresiones', methods=['GET'])
def impresiones():
    return render_template('impresiones.html')

@app.route('/carrito', methods=['GET', 'POST'])
def carrito():
    return render_template('carrito.html')
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Requiere login
@app.route('/cambiarContrasena', methods=['GET', 'PUT'])
@login_required
def cambiar_contrasena():
    return render_template('cambiarContrasena.html')


@app.route('/perfil', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def perfil():
    return render_template('perfil.html')

@app.route('/perfilAdmin', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def perfil_admin():
    return render_template('perfilAdmin.html')

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    return render_template('checkout.html')
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)