from bottle import Bottle, request, response
import time
from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter

app = Bottle()

# Defino contador
requests_counter = Counter('requests_total', 'Total number of requests', ['path'])

@app.post('/heavywork')
def heavywork():
    response.status = 202
    # Incremento contador
    requests_counter.labels(path='/heavywork').inc()
    return {"message": "Heavy work started"}


@app.post('/lightwork')
def lightwork():
    return {"message": "Light work done"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
