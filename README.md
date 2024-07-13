## Comandos utilies

Exportar variable de ambiente

```bash
export KUBECONFIG="/root/challenge4/access.yaml"
```

Listar servicios

```bash
kubectl get services -n challenger-006
```
------------------

## Despliegue

**Clonar el repo del challenge**

```bash
git clone https://github.com/whitestack/ws-challenge-4.git
```

**Agregar contador en app.py** 

```bash
from bottle import Bottle, request, response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import REGISTRY
import time

app = Bottle()

# Define un contador para las solicitudes a /heavywork
requests_counter = Counter('requests_total', 'Total number of requests', ['path'])

@app.post('/heavywork')
def heavywork():
    response.status = 202
    # Incrementa el contador de solicitudes para /heavywork
    requests_counter.labels(path='/heavywork').inc()
    return {"message": "Heavy work started"}

@app.post('/lightwork')
def lightwork():
    return {"message": "Light work done"}

@app.route('/metrics')
def metrics():
    # Exponer las métricas para Prometheus
    return generate_latest(REGISTRY), {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

```

**Crear la imagen docker** 

```bash
docker build -t mi-app:latest .
```









