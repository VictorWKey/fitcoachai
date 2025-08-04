FROM python:3.12-bookworm

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos al contenedor
COPY . /app

# Instala Graphviz y sus bibliotecas de desarrollo
RUN apt-get update && apt-get install -y \
    graphviz \
    graphviz-dev \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]