from flask import Flask, jsonify

app = Flask(__name__)

catalog = {
    "1": {"name": "Laptop", "price": 999.99},
    "2": {"name": "Smartphone", "price": 499.99},
    "3": {"name": "Headphones", "price": 199.99}
}

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/products/<product_id>')
def get_product(product_id):
    product = catalog.get(product_id)
    if product:
        return jsonify(product), 200
    return jsonify({"error": "Product not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
