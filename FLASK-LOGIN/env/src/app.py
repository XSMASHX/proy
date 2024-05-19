from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from config import config

# Modelos
from modelos.ModelUser import ModelUser

# Entities:
from modelos.entities.User import User

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db = MySQL(app)
login_manager_app = LoginManager(app)
login_manager_app.login_view = 'login'  # Redirige a la página de login si no está autenticado

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user is not None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Invalid password...")
                return render_template('auth/login.html')
        else:
            flash("User not found...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')
    
@app.route('/layout')
@login_required
def layout():
    return render_template('layout.html')

    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

# En la vista de habitaciones, convierte la tupla de habitación en un diccionario antes de pasarla a la plantilla
@app.route('/habitaciones')
@login_required
def habitaciones():
    tipo = request.args.get('tipo')
    estado = request.args.get('estado')
    metodo_pago = request.args.get('metodo_pago')
    
    query = "SELECT * FROM habitaciones WHERE 1=1"
    filters = []

    if tipo:
        query += " AND tipo = %s"
        filters.append(tipo)
    
    if estado:
        query += " AND estado = %s"
        filters.append(estado)

    if metodo_pago:
        query += " AND metodo_pago = %s"
        filters.append(metodo_pago)
    
    cursor = db.connection.cursor()
    cursor.execute(query, filters)
    habitaciones = cursor.fetchall()

    habitaciones_dicts = []
    for habitacion in habitaciones:
        habitacion_dict = {
            'id': habitacion[0],
            'nombre': habitacion[1],
            'tipo': habitacion[2],
            'estado': habitacion[3],
            'imagen': habitacion[4],
            'tiempo_reservacion': habitacion[5],
            'metodo_pago': habitacion[6]
        }
        habitaciones_dicts.append(habitacion_dict)

    return render_template('habitaciones.html', habitaciones=habitaciones_dicts)




@app.route('/habitacion/<int:id>', methods=['GET', 'POST'])
@login_required
def habitacion_detalle(id):
    cursor = db.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        estado = request.form['estado']
        tiempo_reservacion = request.form['tiempo_reservacion']
        precio = request.form['precio']
        metodo_pago = request.form['metodo_pago']
        numero_personas = request.form['numero_personas']
        id_orden = request.form['id_orden']
        estado_pago = request.form['estado_pago']

        cursor.execute("""
            UPDATE habitaciones SET nombre=%s, tipo=%s, estado=%s, tiempo_reservacion=%s, 
            precio=%s, metodo_pago=%s, numero_personas=%s, id_orden=%s, estado_pago=%s 
            WHERE id=%s
        """, (nombre, tipo, estado, tiempo_reservacion, precio, metodo_pago, numero_personas, id_orden, estado_pago, id))
        db.connection.commit()

    cursor.execute("SELECT * FROM habitaciones WHERE id = %s", (id,))
    habitacion = cursor.fetchone()

    if habitacion:
        habitacion_dict = {
            'id': habitacion[0],
            'nombre': habitacion[1],
            'tipo': habitacion[2],
            'estado': habitacion[3],
            'imagen': habitacion[4],
            'tiempo_reservacion': habitacion[5],
            'precio': habitacion[6],
            'metodo_pago': habitacion[7],
            'numero_personas': habitacion[8],
            'id_orden': habitacion[9],
            'estado_pago': habitacion[10]
        }
    else:
        habitacion_dict = None

    return render_template('habitacion_detalle.html', habitacion=habitacion_dict)



@app.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    cursor = db.connection.cursor()
    if request.method == 'POST':
        if 'eliminar' in request.form:
            id_habitacion = request.form['id']
            cursor.execute("DELETE FROM habitaciones WHERE id = %s", (id_habitacion,))
            db.connection.commit()
        elif 'agregar' in request.form:
            nombre = request.form['nombre']
            tipo = request.form['tipo']
            estado = request.form['estado']
            imagen = request.form['imagen']
            tiempo_reservacion = request.form['tiempo_reservacion']
            cursor.execute("INSERT INTO habitaciones (nombre, tipo, estado, imagen, tiempo_reservacion) VALUES (%s, %s, %s, %s, %s)", 
                        (nombre, tipo, estado, imagen, tiempo_reservacion))
            db.connection.commit()
    cursor.execute("SELECT id, nombre, tipo, estado, imagen, tiempo_reservacion FROM habitaciones")
    habitaciones = cursor.fetchall()
    return render_template('configuracion.html', habitaciones=habitaciones)



@app.route('/historial')
@login_required
def historial():
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM ordenes WHERE estado='solvente'")
    ordenes = cursor.fetchall()

    # Verifica los datos obtenidos
    print(ordenes)  # Esta línea te permitirá ver los datos en la consola

    # Convertir las tuplas de órdenes en una lista de diccionarios
    ordenes_dicts = []
    for orden in ordenes:
        orden_dict = {
            'id': orden[0],
            'habitacion_id': orden[1],
            'usuario_id': orden[2],
            'estado': orden[3]
        }
        ordenes_dicts.append(orden_dict)

    return render_template('historial.html', ordenes=ordenes_dicts)


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run(debug=True)
