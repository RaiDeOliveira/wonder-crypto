# Imagem base com Python 3.11
FROM python:3.11-slim

# Definindo o diretório de trabalho
WORKDIR /app

# Instalando dependências do sistema necessárias para o TensorFlow e outras bibliotecas
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiando o requirements.txt para instalar as dependências Python
COPY requirements.txt .

# Instalando as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiando o código da aplicação
COPY . .

# Expondo a porta da API
EXPOSE 8000

# Comando para iniciar o servidor FastAPI com Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
