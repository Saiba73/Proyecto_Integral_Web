#app.py
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
    eliminar_metodo_pago_db, establecer_pago_predeterminado, establecer_direccion_predeterminada,
    obtener_todos_productos,agregar_producto_db,actualizar_producto_db,eliminar_producto_db,obtener_todas_ordenes,crear_admin_si_no_existe

)

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_de_desarrollo_insegura')
bcrypt = Bcrypt(app)

# Inicializar base de datos
try:
    crear_tablas()
    insertar_productos_iniciales()
    crear_admin_si_no_existe()
    print("Base de datos lista")
except Exception as e:
    print(f"Error con la base de datos: {e}")

def login_required(f):
    """Decorador para restringir el acceso si no hay sesión activa."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador que restringe el acceso solo a usuarios admin."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== RUTAS PÚBLICAS ====================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")

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

@app.route('/api/carrito/agregar', methods=['POST'])
@login_required
def api_agregar_carrito():
    from Server.server import agregar_al_carrito_db
    
    data = request.get_json()
    usuario_id = session.get('user_id')
    
    exito = agregar_al_carrito_db(
        usuario_id=usuario_id,
        producto_id=data.get('producto_id'),
        categoria=data.get('categoria'),
        cantidad=data.get('cantidad', 1),
        talla_tamano=data.get('talla'),
        precio_unitario=data.get('precio')
    )
    
    if exito:
        return jsonify({'status': 'success', 'message': 'Producto agregado al carrito'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Error al agregar'}), 500

@app.route('/api/carrito/obtener', methods=['GET'])
@login_required
def api_obtener_carrito():
    from Server.server import obtener_carrito_con_detalles
    import mysql.connector
    from Server.server import db_config
    
    usuario_id = session.get('user_id')
    items, total = obtener_carrito_con_detalles(usuario_id)
    
    # Agregar color e imagen a cada item
    for item in items:
        if 'Negro' in str(item.get('nombre_producto', '')):
            item['color'] = 'Negro'
        else:
            item['color'] = 'Blanco'
        
        # Asegurar que la ruta de imagen sea correcta
        if item.get('imagen_ruta'):
            # Quitar 'static/' si está al principio
            img_ruta = item['imagen_ruta']
            if img_ruta.startswith('static/'):
                img_ruta = img_ruta[7:]
            item['imagen_ruta'] = img_ruta
    
    return jsonify({'status': 'success', 'items': items, 'total': total})


@app.route('/api/carrito/actualizar/<int:item_id>', methods=['PUT'])
@login_required
def api_actualizar_item_carrito(item_id):
    from Server.server import actualizar_cantidad_item_db
    
    data = request.get_json()
    delta = data.get('delta', 0)
    usuario_id = session.get('user_id')
    
    exito = actualizar_cantidad_item_db(usuario_id, item_id, delta)
    
    if exito:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error'}), 500


@app.route('/api/carrito/eliminar/<int:item_id>', methods=['DELETE'])
@login_required
def api_eliminar_item_carrito(item_id):
    from Server.server import eliminar_item_carrito_db
    
    usuario_id = session.get('user_id')
    exito = eliminar_item_carrito_db(usuario_id, item_id)
    
    if exito:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error'}), 500

@app.route('/producto/<path:producto_id>')
def producto_detalle(producto_id):
    from Server.server import obtener_producto_por_id_con_prefijo, obtener_productos_relacionados
    
    producto = obtener_producto_por_id_con_prefijo(producto_id)
    
    if not producto:
        return redirect(url_for('home'))
    
    relacionados = obtener_productos_relacionados(producto['categoria'], producto['producto_id'])
    
    # Determinar la categoría para el navbar
    categoria_activa = producto['categoria']  # 'ropa', 'tazas' o 'impresiones'
    
    return render_template('producto_detalle.html', 
                           producto=producto, 
                           relacionados=relacionados,
                           categoria_producto=producto['categoria'],
                           categoria_activa=categoria_activa) 

@app.route('/api/carrito/vaciar', methods=['DELETE'])
@login_required
def api_vaciar_carrito():
    from Server.server import vaciar_carrito
    
    usuario_id = session.get('user_id')
    exito = vaciar_carrito(usuario_id)
    
    if exito:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error'}), 500


@app.route('/api/orden/crear', methods=['POST'])
@login_required
def api_crear_orden():
    from Server.server import crear_orden_db
    from Server.server import vaciar_carrito
    
    data = request.get_json()
    usuario_id = session.get('user_id')
    items = data.get('items', [])
    pago_total = data.get('total', 0)
    direccion = data.get('direccion', '')
    
    # Crear lista de productos_ids y cantidades
    productos_ids = [str(item['producto_id']) for item in items]
    cantidades = [str(item['cantidad']) for item in items]
    
    exito = crear_orden_db(
        usuario_id=usuario_id,
        productos_ids=','.join(productos_ids),
        cantidades=','.join(cantidades),
        pago_total=pago_total
    )
    
    if exito:
        # Vaciar carrito después de crear la orden
        vaciar_carrito(usuario_id)
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No se pudo crear la orden'}), 500

# ==================== RUTAS DE PERFIL (requieren login) ====================

@app.route('/perfil')
@login_required
def perfil():
    # Si es admin, redirigir a su panel
    if session.get('user_role') == 'admin':
        return redirect(url_for('perfil_admin'))
    
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

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    return render_template('checkout.html')

@app.route('/perfilAdmin')
@admin_required
def perfil_admin():
    u_id = session.get('user_id')
    usuario, _, _ = obtener_perfil_completo(u_id)
 
    if not usuario:
        return redirect(url_for('home'))
 
    ropa, tazas, impresiones = obtener_todos_productos()
    ordenes = obtener_todas_ordenes()
 
    # Total del inventario (suma de precio × cantidad de todos los productos)
    total = 0
    for p in ropa:
        total += p['precio'] * p['cantidad_disponible']
    for p in tazas:
        total += p['precio'] * p['cantidad_disponible']
    for p in impresiones:
        total += p['precio'] * p['cantidad_disponible']
 
    return render_template(
        'perfilAdmin.html',
        usuario=usuario,
        productos_ropa=ropa,
        productos_tazas=tazas,
        productos_impresiones=impresiones,
        ordenes=ordenes,
        total_inventario=total,
    )
 
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
 
# ── Crear producto ──
@app.route('/admin/producto/nuevo', methods=['POST'])
@admin_required
def admin_nuevo_producto():
    data = request.get_json()
    ok = agregar_producto_db(
        categoria   = data.get('categoria'),
        nombre      = data.get('nombre'),
        diseno      = data.get('diseno', ''),
        tam         = data.get('tam', ''),
        cantidad    = data.get('cantidad', 0),
        precio      = data.get('precio', 0.0),
        imagen_ruta = data.get('imagen_ruta', ''),
    )
    return (jsonify({'status': 'success'}), 200) if ok else (jsonify({'status': 'error'}), 500)
 
 
# ── Editar producto ──
@app.route('/admin/producto/editar/<string:categoria>/<int:producto_id>', methods=['PUT'])
@admin_required
def admin_editar_producto(categoria, producto_id):
    data = request.get_json()
    ok = actualizar_producto_db(
        categoria   = categoria,
        producto_id = producto_id,
        nombre      = data.get('nombre'),
        diseno      = data.get('diseno', ''),
        tam         = data.get('tam', ''),
        cantidad    = data.get('cantidad', 0),
        precio      = data.get('precio', 0.0),
        imagen_ruta = data.get('imagen_ruta', ''),
    )
    return (jsonify({'status': 'success'}), 200) if ok else (jsonify({'status': 'error'}), 500)
 
 
# ── Borrar producto ──
@app.route('/admin/producto/borrar/<string:categoria>/<int:producto_id>', methods=['DELETE'])
@admin_required
def admin_borrar_producto(categoria, producto_id):
    ok = eliminar_producto_db(categoria, producto_id)
    return (jsonify({'status': 'success'}), 200) if ok else (jsonify({'status': 'error'}), 500)



# ==================== INICIO ====================

if __name__ == "__main__":
    app.run(debug=True)