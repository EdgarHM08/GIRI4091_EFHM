from flask import Flask, request, jsonify 
import psycopg2
import bcrypt

app = Flask(__name__)

# Conexión a la base de datos
conn = psycopg2.connect(database="laptops", user="postgres", password="linux", host="127.0.0.1", port="5432")
cursor = conn.cursor()

# Ruta para registrar un nuevo usuario
@app.route('/register', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({"message": "Todos los campos son obligatorios"}), 400

    # Encriptar la contraseña y decodificarla para almacenarla como string
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        cursor.execute("INSERT INTO usuarios (email, username, password) VALUES (%s, %s, %s)",
                       (email, username, hashed_password))
        conn.commit()
        return jsonify({"message": "Usuario registrado exitosamente"}), 201
    except psycopg2.Error as e:
        conn.rollback()
        if e.pgcode == '23505':  # Código de error para UNIQUE violation
            return jsonify({"message": "El correo electrónico o nombre de usuario ya existe"}), 409
        else:
            return jsonify({"message": "Error al registrar usuario"}), 500

# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def loginusuario():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"message": "Todos los campos son obligatorios"}), 400

        # Seleccionar los campos 'id' y 'password' del usuario
        cursor.execute("SELECT id, password FROM usuarios WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            return jsonify({"message": "Inicio de sesión exitoso"}), 200
        else:
            return jsonify({"message": "Credenciales incorrectas"}), 401

    except Exception as e:
        print("Error durante el login:", str(e))
        return jsonify({"message": "Ocurrió un error en el servidor"}), 500

# Agregar laptop
@app.route('/laptops', methods=['POST'])
def agregar_laptop():
    try:
        data = request.get_json()

        # Validación para evitar nombres en blanco
        if not data.get('marca') or data['marca'].strip() == "":
            return jsonify({"message": "La marca de la laptop no puede estar en blanco"}), 400

        # Validar otros campos si es necesario
        cursor.execute("INSERT INTO laptops (marca, modelo, precio, procesador, ram, almacenamiento, codigo) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (data['marca'], data['modelo'], data['precio'], data['procesador'], data['ram'], data['almacenamiento'], data['codigo']))
        conn.commit()
        return jsonify({"message": "Laptop agregada exitosamente"}), 201
    except Exception as e:
        conn.rollback()
        print("Error al agregar laptop:", str(e))
        return jsonify({"message": "Error al agregar laptop"}), 500

# Obtener laptops
@app.route('/laptops', methods=['GET'])
def obtener_laptops():
    try:
        cursor.execute("SELECT id, marca, modelo, precio, procesador, ram, almacenamiento, codigo, fecha_creacion FROM laptops")
        laptops = cursor.fetchall()
        return jsonify(laptops), 200
    except Exception as e:
        print("Error al obtener laptops:", str(e))
        return jsonify({"message": "Error al obtener laptops"}), 500

# Obtener una laptop específica por ID
@app.route('/laptops/<int:id>', methods=['GET'])
def obtener_laptop_por_id(id):
    try:
        cursor.execute("SELECT id, marca, modelo, precio, procesador, ram, almacenamiento, codigo, fecha_creacion FROM laptops WHERE id=%s", (id,))
        laptop = cursor.fetchone()
        if laptop:
            return jsonify({
                "id": laptop[0],
                "marca": laptop[1],
                "modelo": laptop[2],
                "precio": laptop[3],
                "procesador": laptop[4],
                "ram": laptop[5],
                "almacenamiento": laptop[6],
                "codigo": laptop[7],
                "fecha_creacion": laptop[8]
            }), 200
        else:
            return jsonify({"message": "Laptop no encontrada"}), 404
    except Exception as e:
        print("Error al obtener laptop por ID:", str(e))
        return jsonify({"message": "Error al obtener laptop"}), 500

# Actualizar laptop
@app.route('/laptops/<int:id>', methods=['PUT'])
def actualizar_laptop(id):
    try:
        data = request.get_json()

        # Verificar que la laptop existe
        cursor.execute("SELECT id FROM laptops WHERE id=%s", (id,))
        laptop = cursor.fetchone()
        if not laptop:
            return jsonify({"message": "Laptop no encontrada"}), 404

        # Validación para evitar campos en blanco al actualizar
        if not data.get('marca') or data['marca'].strip() == "":
            return jsonify({"message": "La marca de la laptop no puede estar en blanco"}), 400
        if not data.get('modelo') or data['modelo'].strip() == "":
            return jsonify({"message": "El modelo no puede estar en blanco"}), 400
        if not data.get('precio'):
            return jsonify({"message": "El precio no puede estar en blanco"}), 400
        if not data.get('procesador') or data['procesador'].strip() == "":
            return jsonify({"message": "El procesador no puede estar en blanco"}), 400
        if not data.get('ram'):
            return jsonify({"message": "La memoria RAM no puede estar en blanco"}), 400
        if not data.get('almacenamiento') or data['almacenamiento'].strip() == "":
            return jsonify({"message": "El almacenamiento no puede estar en blanco"}), 400
        if not data.get('codigo') or data['codigo'].strip() == "":
            return jsonify({"message": "El código no puede estar en blanco"}), 400

        cursor.execute("UPDATE laptops SET marca=%s, modelo=%s, precio=%s, procesador=%s, ram=%s, almacenamiento=%s, codigo=%s WHERE id=%s",
                       (data['marca'], data['modelo'], data['precio'], data['procesador'], data['ram'], data['almacenamiento'], data['codigo'], id))
        conn.commit()
        return jsonify({"message": "Laptop actualizada"}), 200
    except Exception as e:
        conn.rollback()
        print("Error al actualizar laptop:", str(e))
        return jsonify({"message": "Error al actualizar laptop"}), 500

# Eliminar laptop
@app.route('/laptops/<int:id>', methods=['DELETE'])
def eliminar_laptop(id):
    try:
        cursor.execute("SELECT id FROM laptops WHERE id=%s", (id,))
        laptop = cursor.fetchone()
        if not laptop:
            return jsonify({"message": "Laptop no encontrada"}), 404

        cursor.execute("DELETE FROM laptops WHERE id=%s", (id,))
        conn.commit()
        return jsonify({"message": "Laptop eliminada"}), 200
    except Exception as e:
        conn.rollback()
        print("Error al eliminar laptop:", str(e))
        return jsonify({"message": "Error al eliminar laptop"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
