# Utilizar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requisitos y el código de la aplicación
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Copiar el archivo .env
COPY .env .env

# Instalar la biblioteca para manejar archivos .env si no está ya incluida
RUN pip install python-dotenv

# Exponer el puerto que utiliza la aplicación (ajusta según tu configuración)
EXPOSE 8080

# Establecer las variables de entorno cargadas desde el archivo .env
CMD ["python", "-m", "dotenv", "run", "--", "python", "app.py"]
