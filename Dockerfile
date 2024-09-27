# Utilizar una imagen base ligera de Debian
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias, incluido zabbix-sender
RUN apt-get update && apt-get install -y --no-install-recommends zabbix-sender

# Copiar el archivo de requisitos y el código de la aplicación
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto que utiliza la aplicación (ajusta según tu configuración)
EXPOSE 8080

# Establecer el comando predeterminado para ejecutar la aplicación
CMD ["python", "app.py"]
