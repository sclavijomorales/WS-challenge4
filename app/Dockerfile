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