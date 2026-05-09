import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from Server.server import agregar_usuario, obtener_perfil_completo, guardar_direccion_db, agregar_usuario, agregar_metodo_pago, obtener_usuario_por_correo

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
        
        # Usamos la nueva función aquí también
        usuario = obtener_usuario_por_correo(email)
        
        if usuario:
            if bcrypt.check_password_hash(usuario['contrasena'], password):
                session['logged_in'] = True
                session['user_id'] = usuario['usuario_id']
                session['user_email'] = usuario['correo']
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
        if obtener_usuario_por_correo(email):
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
# @app.route('/cambiarContrasena', methods=['GET', 'PUT'])
# @login_required
# def cambiar_contrasena():
#     return render_template('cambiarContrasena.html')


@app.route('/perfil')
@login_required
def perfil():
    # Ya no necesitas el 'from Server.server import...' aquí si ya lo importaste arriba
    u_id = session.get('user_id')
    
    # Obtenemos los datos desde server.py
    usuario, direcciones, pagos = obtener_perfil_completo(u_id)
    
    # Si no se encuentra el usuario, podrías redirigir o mostrar un error
    if not usuario:
        return redirect(url_for('home'))

    return render_template('perfil.html', 
                           usuario=usuario, 
                           direcciones=direcciones, 
                           metodos_pago=pagos,
                           ordenes=[])

# Rutas de pago ------------------------------------------------

@app.route('/perfil/pago/nuevo', methods=['POST'])
def nuevo_pago_perfil():
    if not session.get('logged_in'):
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    usuario_id = session.get('user_id')
    
    tipo = data.get('tipo')
    titular = data.get('titular')
    numero_completo = data.get('numero')
    ultimos4 = numero_completo[-4:] if numero_completo else "0000"
    vencimiento = data.get('vencimiento')
    predeterminado = 1 if data.get('predeterminado') else 0

    # USAMOS LA FUNCIÓN QUE YA SE IMPORTÓ AL INICIO DE APP.PY
    exito = agregar_metodo_pago(usuario_id, tipo, titular, ultimos4, vencimiento, predeterminado)

    if exito:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No se pudo guardar en la base de datos'}), 500

# La función borrar_pago ya la tienes, pero asegúrate que el nombre coincida
@app.route('/perfil/pago/borrar/<int:id>', methods=['POST'])
@login_required
def borrar_pago(id):
    u_id = session.get('user_id')
    # Importamos aquí mismo para asegurar que esté disponible
    from Server.server import eliminar_metodo_pago_db
    
    if eliminar_metodo_pago_db(id, u_id):
        return redirect(url_for('perfil'))
    return "Error al eliminar", 500

@app.route('/perfil/pago/default/<int:id>', methods=['POST'])
@login_required
def set_pago_default(id):
    u_id = session.get('user_id')
    from Server.server import establecer_pago_predeterminado
    if establecer_pago_predeterminado(u_id, id):
        return redirect(url_for('perfil'))
    return "Error al actualizar pago", 500

# Rutas de direccion -------------------------------------------------------------------------
@app.route('/perfil/direccion/default/<int:id>', methods=['POST'])
@login_required
def set_direccion_default(id):
    u_id = session.get('user_id')
    from Server.server import establecer_direccion_predeterminada
    if establecer_direccion_predeterminada(u_id, id):
        return redirect(url_for('perfil'))
    return "Error al actualizar dirección", 500


@app.route('/api/direccion/<int:id>', methods=['GET'])
@login_required
def api_get_direccion(id):
    # Aquí llamarías a una función en server.py que haga: 
    # SELECT * FROM Direccion WHERE direccion_id = id AND usuario_id = session['user_id']
    # Por ahora devolvemos un ejemplo:
    return jsonify({"calle": "Calle Falsa 123", "ciudad": "Juárez", "cp": "32000", "pais": "México"})

@app.route('/perfil/direccion/nueva', methods=['POST'])
@login_required
def nueva_direccion_perfil():
    data = request.get_json()
    u_id = session.get('user_id')
    
    # Concatenamos colonia y alcaldía para no perder información 
    # ya que tu DB parece solo tener 'calle' y 'ciudad'
    calle_completa = f"{data.get('calle')} - Col. {data.get('colonia')}"
    ciudad_completa = f"{data.get('alcaldia')}, {data.get('ciudad')}"

    payload = {
        'calle': calle_completa,
        'ciudad': ciudad_completa,
        'cp': data.get('cp'),
        'pais': 'México'
    }
    
    from Server.server import guardar_direccion_db
    exito = guardar_direccion_db(u_id, payload)
    
    if exito:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 500
    
@app.route('/perfil/direccion/borrar/<int:id>', methods=['POST'])
@login_required
def borrar_direccion(id):
    u_id = session.get('user_id')
    # Aquí llamarías a una función en server.py para hacer el DELETE
    return redirect(url_for('perfil'))

# Ruta para EDITAR (PUT) si decides habilitarla luego
@app.route('/perfil/direccion/<int:id>', methods=['PUT'])
@login_required
def editar_direccion_perfil(id):
    data = request.get_json()
    u_id = session.get('user_id')
    from Server.server import guardar_direccion_db
    exito = guardar_direccion_db(u_id, data, id)
    if exito:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 500

# Administracion de cuentas -------------------------------------------------------------------------------------------------

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