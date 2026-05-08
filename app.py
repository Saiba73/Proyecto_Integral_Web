import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from Server.server import agregar_usuario, obtener_usuario_por_email, obtener_perfil_completo, guardar_direccion_db, agregar_usuario

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
            # Comparamos con 'contrasena' (nombre en tu SQL)
            if bcrypt.check_password_hash(usuario['contrasena'], password):
                session['logged_in'] = True
                session['user_id'] = usuario['usuario_id'] # Antes era usuario['id']
                session['user_email'] = usuario['correo']    # Antes era usuario['email']
                session['user_role'] = usuario['tipo_usuario']
                
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error="Contraseña incorrecta.")
        else:
            return render_template('login.html', error="El correo no está registrado.")
            
    return render_template('login.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('correo')
        password = request.form.get('password')
        confirm_password = request.form.get('cpassword')

        # 1. Validar contraseñas iguales
        if password != confirm_password:
            return render_template('registrar.html', error="Las contraseñas no coinciden.")

        # 2. Verificar si el usuario ya existe
        if obtener_usuario_por_email(email):
            return render_template('registrar.html', error="Este correo ya está registrado.")

        # 3. Encriptar contraseña
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # 4. Guardar en DB
        user_id = agregar_usuario(nombre, email, password_hash)

        if user_id:
            return redirect(url_for('login'))
        else:
            return render_template('registrar.html', error="Error interno al crear la cuenta.")

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


@app.route('/perfil')
@login_required
def perfil():
    from Server.server import obtener_perfil_completo
    u_id = session.get('user_id')
    
    usuario, direcciones, pagos = obtener_perfil_completo(u_id)
    
    # Adaptamos los datos para que el HTML no se rompa si falta algo
    return render_template('perfil.html', 
                           usuario=usuario, 
                           direcciones=direcciones, 
                           metodos_pago=pagos,
                           ordenes=[])

@app.route('/api/direccion/<int:id>', methods=['GET'])
@login_required
def api_get_direccion(id):
    # Aquí llamarías a una función en server.py que haga: 
    # SELECT * FROM Direccion WHERE direccion_id = id AND usuario_id = session['user_id']
    # Por ahora devolvemos un ejemplo:
    return jsonify({"calle": "Calle Falsa 123", "ciudad": "Juárez", "cp": "32000", "pais": "México"})

@app.route('/api/direccion/guardar', methods=['POST'])
@login_required
def api_guardar_direccion():
    from Server.server import guardar_direccion_db
    data = request.get_json()
    u_id = session.get('user_id')
    
    exito = guardar_direccion_db(u_id, data, data.get('id'))
    
    if exito:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error"}), 500

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