from bottle import Bottle, request, response
from prometheus_client import start_http_server, Counter, generate_latest, CONTENT_TYPE_LATEST
import threading

# Inicializar el contador de requests
heavywork_requests = Counter('heavywork_requests_total', 'Total number of requests to /heavywork')

app = Bottle()

@app.post('/heavywork')
def heavywork():
    # Incrementar el contador para la ruta /heavywork
    heavywork_requests.inc()
    response.status = 202
    return {"message": "Heavy work started"}

@app.post('/lightwork')
def lightwork():
    return {"message": "Light work done"}

@app.get('/metrics')
def metrics():
    # Exponer las métricas en formato Prometheus
    response.content_type = CONTENT_TYPE_LATEST
    return generate_latest()

def run_metrics_server():
    # Iniciar el servidor HTTP para Prometheus en el puerto 8000
    start_http_server(8000)

if __name__ == "__main__":
    # Iniciar el servidor de métricas en un hilo separado
    metrics_thread = threading.Thread(target=run_metrics_server)
    metrics_thread.start()

    # Iniciar la aplicación Bottle en el puerto 8080
    app.run(host="0.0.0.0", port=8080)