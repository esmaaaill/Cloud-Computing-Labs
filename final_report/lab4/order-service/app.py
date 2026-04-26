from flask import Flask, jsonify, request
import requests
import os
import time

app = Flask(__name__)

PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://localhost:5001')

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    if not data or 'product_id' not in data:
        return jsonify({"error": "Missing product_id"}), 400
    
    product_id = data['product_id']
    
    # Retry logic and timeout for calling product-service
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}", timeout=2)
            if response.status_code == 200:
                product_data = response.json()
                return jsonify({
                    "message": "Order created successfully",
                    "order": {
                        "product": product_data,
                        "status": "confirmed"
                    }
                }), 201
            elif response.status_code == 404:
                return jsonify({"error": "Product not found"}), 404
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(1) # wait before retry
                continue
            else:
                return jsonify({
                    "error": "Product service unavailable",
                    "details": str(e)
                }), 503
                
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
