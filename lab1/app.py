from flask import Flask
import time
import random

app = Flask(__name__)

@app.route('/')
def hello():
    # Introduce artificial delay using exponential distribution
    # random.expovariate(1/0.1) gives a mean delay of 0.1 seconds
    delay = random.expovariate(1/0.1)
    time.sleep(delay)
    return "Hello, World!\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
