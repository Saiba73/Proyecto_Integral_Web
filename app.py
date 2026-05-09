from dotenv import load_dotenv
import os

# Cargar variables de entorno ANTES de cualquier otra cosa
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from Server.server import (
    agregar_usuario, obtener_perfil_completo, guardar_direccion_db,
    agregar_metodo_pago, obtener_usuario_por_correo,
    crear_tablas, insertar_productos_iniciales,
    obtener_productos_ropa, obtener_productos_tazas, obtener_productos_impresiones,
    eliminar_metodo_pago_db, establecer_pago_predeterminado, establecer_direccion_predeterminada
)

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_de_desarrollo_insegura')
bcrypt = Bcrypt(app)

# Inicializar base de datos
try:
    crear_tablas()
    insertar_productos_iniciales()
    print("✅ Base de datos lista")
except Exception as e:
    print(f"⚠️ Error con la base de datos: {e}")

def login_required(f):
    """Decorador para restringir el acceso si no hay sesión activa."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== RUTAS PÚBLICAS ====================

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

        if password != confirm_password:
            return render_template('registrar.html', error="Las contraseñas no coinciden.")

        if obtener_usuario_por_correo(email):
            return render_template('registrar.html', error="Este correo ya está registrado.")

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = agregar_usuario(nombre, email, password_hash)

        if user_id:
            return redirect(url_for('login'))
        else:
            return render_template('registrar.html', error="Error interno al crear la cuenta.")

    return render_template('registrar.html')

# ==================== RUTAS DE PRODUCTOS ====================

@app.route('/ropa')
def ropa():
    productos = obtener_productos_ropa()
    return render_template('ropa.html', productos=productos)

@app.route('/tazas')
def tazas():
    productos = obtener_productos_tazas()
    return render_template('tazas.html', productos=productos)

@app.route('/impresiones')
def impresiones():
    productos = obtener_productos_impresiones()
    return render_template('impresiones.html', productos=productos)

@app.route('/carrito', methods=['GET', 'POST'])
def carrito():
    return render_template('carrito.html')

@app.route('/producto/<int:producto_id>')
def detalle_producto(producto_id):
    # Por ahora redirige a la página correspondiente
    return redirect(url_for('home'))

# ==================== RUTAS DE PERFIL (requieren login) ====================

@app.route('/perfil')
@login_required
def perfil():
    u_id = session.get('user_id')
    usuario, direcciones, pagos = obtener_perfil_completo(u_id)
    
    if not usuario:
        return redirect(url_for('home'))

    return render_template('perfil.html', 
                           usuario=usuario, 
                           direcciones=direcciones, 
                           metodos_pago=pagos,
                           ordenes=[])

@app.route('/perfil/pago/nuevo', methods=['POST'])
@login_required
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

    exito = agregar_metodo_pago(usuario_id, tipo, titular, ultimos4, vencimiento, predeterminado)

    if exito:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No se pudo guardar en la base de datos'}), 500

@app.route('/perfil/pago/borrar/<int:id>', methods=['POST'])
@login_required
def borrar_pago(id):
    u_id = session.get('user_id')
    if eliminar_metodo_pago_db(id, u_id):
        return redirect(url_for('perfil'))
    return "Error al eliminar", 500

@app.route('/perfil/pago/default/<int:id>', methods=['POST'])
@login_required
def set_pago_default(id):
    u_id = session.get('user_id')
    if establecer_pago_predeterminado(u_id, id):
        return redirect(url_for('perfil'))
    return "Error al actualizar pago", 500

@app.route('/perfil/direccion/default/<int:id>', methods=['POST'])
@login_required
def set_direccion_default(id):
    u_id = session.get('user_id')
    if establecer_direccion_predeterminada(u_id, id):
        return redirect(url_for('perfil'))
    return "Error al actualizar dirección", 500

@app.route('/api/direccion/<int:id>', methods=['GET'])
@login_required
def api_get_direccion(id):
    return jsonify({"calle": "Calle Falsa 123", "ciudad": "Juárez", "cp": "32000", "pais": "México"})

@app.route('/perfil/direccion/nueva', methods=['POST'])
@login_required
def nueva_direccion_perfil():
    data = request.get_json()
    u_id = session.get('user_id')
    
    calle_completa = f"{data.get('calle')} - Col. {data.get('colonia')}"
    ciudad_completa = f"{data.get('alcaldia')}, {data.get('ciudad')}"

    payload = {
        'calle': calle_completa,
        'ciudad': ciudad_completa,
        'cp': data.get('cp'),
        'pais': 'México'
    }
    
    exito = guardar_direccion_db(u_id, payload)
    
    if exito:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 500
    
@app.route('/perfil/direccion/borrar/<int:id>', methods=['POST'])
@login_required
def borrar_direccion(id):
    return redirect(url_for('perfil'))

@app.route('/perfil/direccion/<int:id>', methods=['PUT'])
@login_required
def editar_direccion_perfil(id):
    data = request.get_json()
    u_id = session.get('user_id')
    exito = guardar_direccion_db(u_id, data, id)
    if exito:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 500

@app.route('/perfilAdmin', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def perfil_admin():
    return render_template('perfilAdmin.html')

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    return render_template('checkout.html')

# ==================== INICIO ====================

if __name__ == "__main__":
    app.run(debug=True)