from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

products = []

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "Description": "Description EFHM",
        "id": "1",
        "image": "Nueva imagen",
        "price": "5284",
        "title": "Nuevo producto"
    })

@app.route('/products', methods=['GET'])
def get_products():
    URL = "https://fakestoreapi.com/products"
    products_from_api = requests.get(URL).json()
    return jsonify(products_from_api)

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = get_element(product_id)
    if product is None:
        return jsonify({"error": "Producto NO encontrado"}), 404
    return jsonify(product)

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = get_element(product_id)
    if product is None:
        return jsonify({"error": "Producto NO encontrado"}), 404
    products.remove(product)
    return jsonify({"message": "Producto eliminado exitosamente"}), 200

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = get_element(product_id)
    if product is None:
        return jsonify({"error": "Producto NO encontrado"}), 404

    data = request.get_json()
    product.update(data)
    return jsonify(product), 200

def get_element(product_id):
    URL = "https://fakestoreapi.com/products"
    products = requests.get(URL).json()
    for product in products:
        if product['id'] == product_id:
            return product
    return None

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    product_id = max_id() + 1
    data['id'] = product_id
    products.append(data)
    return jsonify(data), 201

def max_id():
    if not products:
        return 0
    max_id = products[0]['id']
    for product in products:
        if product['id'] > max_id:
            max_id = product['id']
    return max_id

if __name__ == '__main__':
    app.run(port=5001, debug=True)
