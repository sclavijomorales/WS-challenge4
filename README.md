# Whitestack Challenge 4

Se utilizo minikube como infra para realizar el challenge

- Se habilito el addons de metrics-server
- Se desplego [kube-prometheus](https://github.com/prometheus-operator/kube-prometheus)


## Punto 1 - Adaptar la aplicación web

**Clonar el repo del challenge**

```bash
git clone https://github.com/whitestack/ws-challenge-4.git
```

**Agregar contador en app.py** 

<details>
<summary>app.py</summary>

```python
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

```
</details>

**Agregar prometheus_client en requerimientos** 

<details>

<summary>requirements.txt</summary>

```txt
bottle==0.12.19
prometheus_client==0.14.1
```

</details>


## Punto 2 - Desplegar la aplicación

- **Editar el Dockerfile**

<details>

<summary>Dockerfile</summary>

```Dockerfile
# Usa una imagen base de Python
FROM python:3.9-slim

# Permite que los mensajes de log aparezcan inmediatamente en los logs de Knative
ENV PYTHONUNBUFFERED True

# Define el directorio de la aplicación en el contenedor
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copia el código local al contenedor
COPY . .

# Instala las dependencias de producción
RUN pip install --no-cache-dir -r requirements.txt

# Exponer los puertos necesarios
EXPOSE 8080
EXPOSE 8000

# Comando para iniciar la aplicación Bottle y el servidor de métricas
CMD ["python", "app.py"]
```

</details>

- **Crear la imagen docker** 

- **Subir la imagen a dockerhub**

- **Crear el helm chart**

- **Crear namespace apps**
```bash
kubectl apply -f namespace-apps.yaml
```
- **Crear role en apps**
```bash
kubectl apply -f role-apps.yaml
```
- **Crear rolebindig en apps**
```bash
kubectl apply -f rolebinding-apps.yaml
```
- **Instalar la app con Helm**
```bash
helm install sc-app sc-app-chart-0.1.0.tgz --namespace apps
```

## Punto 3 - Crear ServiceMonitor para obtención de métricas

<details>

<summary>service-monitor.yaml</summary>

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: sc-app-srv-mon
  namespace: apps
spec:
  endpoints:
  - interval: 30s
    port: metrics
    path: /metrics
  selector:
    matchLabels:
      app: app-sc

```

</details>


```bash
kubectl apply -f service-monitor.yaml
```

## Punto 4 -Instalar y configurar Prometheus Adapter

<details>

<summary>values-adapter.yaml</summary>

```yaml
prometheus:
  url: http://prometheus-operated.monitoring.svc
  port: 9090
 
rules:
   default: false
   custom:
   - seriesQuery: 'heavywork_requests_total'
     resources:
       template: <<.Resource>>
     name:
       matches: "heavywork_requests_total"
       as: "heavywork_requests_total"
     metricsQuery: sum(rate(<<.Series>>{<<.LabelMatchers>>}[1m])) by (<<.GroupBy>>)

```
</details>

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install -f values-adapter.yaml prometheus-adapter prometheus-community/prometheus-adapter --namespace apps
 
```

## Punto 5 - Crear HPA

<details>

<summary>hpa-apps.yaml</summary>

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sc-apps-hpa
  namespace: apps
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-sc-sc-app
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Object
    object:
      metric:
        name: heavywork_requests_total
      describedObject:
        apiVersion: v1
        kind: Service
        name: app-sc-sc-app
      target:
        type: Value
        value: "10" # Umbral de 10 peticiones por segundo

```
</details>

```bash
kubectl apply -f hpa-apps.yaml
```

## Punto 6 - Generar carga y analizar

Realizamos un Port forward para poder realizar consultas a la app desde la misma maquina.

```bash
kubectl -n apps port-forward svc/app-sc-sc-app 8080
```
Ejecutamos el script para generar carga

```bash
python3 generate_load.py localhost 8080 /heavywork
```





