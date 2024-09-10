# Utilizar una imagen base más ligera de Alpine
FROM python:3.10-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias, incluido zabbix-sender
RUN apk update && apk add --no-cache zabbix-sender

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
