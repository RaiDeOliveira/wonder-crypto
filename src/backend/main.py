import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
import yfinance as yf
from fastapi.middleware.cors import CORSMiddleware
from minio import Minio
import io  # Biblioteca para lidar com fluxos de I/O
from datetime import datetime, timedelta  # Importação adicional para lidar com datas

# Inicialização do FastAPI
app = FastAPI()

# Configurações de CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Substitua pelo URL do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o cliente do MinIO
minio_client = Minio(
    "minio:9000",  # Serviço MinIO no mesmo network
    access_key="admin",
    secret_key="password",
    secure=False  # HTTPS não é necessário para desenvolvimento local
)

# Nome do bucket para armazenamento
bucket_name = "meu-bucket"

# Função para garantir que o bucket exista
def ensure_bucket_exists(bucket_name: str):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' criado com sucesso.")
    else:
        print(f"Bucket '{bucket_name}' já existe.")

# Garante que o bucket seja criado durante a inicialização do app
ensure_bucket_exists(bucket_name)

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Garante que o bucket exista antes de fazer upload
        ensure_bucket_exists(bucket_name)

        # Ler o conteúdo do arquivo e calcular o tamanho
        contents = await file.read()
        file_size = len(contents)

        # Upload do arquivo para o bucket
        result = minio_client.put_object(
            bucket_name,
            file.filename,
            io.BytesIO(contents),  # Enviar o conteúdo do arquivo lido
            length=file_size,
            content_type=file.content_type
        )
        return JSONResponse(content={"filename": file.filename, "bucket": bucket_name}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Carrega o modelo previamente salvo
model = load_model('meu_modelo_rnn.h5')

# Definir um valor de limite para variações logarítmicas para evitar explosão
VARIATION_LIMIT = 0.0025  # Limitar variações logarítmicas para +/-0,25%

# Rota para predição dos próximos 7 dias
@app.get("/predict-next-week")
def predict_next_7_days():
    # Passo 1: Coletar os dados mais recentes do Bitcoin (por exemplo, dos últimos 50 dias)
    end_date = datetime.now().strftime('%Y-%m-%d')  # Data final é o dia atual
    start_date = (datetime.now() - timedelta(days=50)).strftime('%Y-%m-%d')  # Data inicial é 50 dias atrás

    btc_data = yf.download("BTC-USD", start=start_date, end=end_date)

    # Considera a coluna de fechamento ajustado como base
    close_prices = btc_data['Close'].values

    # Passo 2: Transformação para série estacionária (aplicar log e a primeira diferença)
    log_prices = np.log(close_prices)

    # Calcular a primeira diferença dos preços logaritmizados
    log_diff = np.diff(log_prices)

    # Seleciona os últimos 50 valores transformados para alimentar o modelo
    last_50_days = log_diff[-50:]  # Pegando os últimos 50 dias (input para o modelo)
    last_50_days_scaled = last_50_days.reshape(1, len(last_50_days), 1)  # Reshape para (1, 50, 1)

    # Inicialize last_real_log_price com o último preço logarítmico
    last_real_log_price = log_prices[-1]  # Último valor logarítmico antes da transformação

    # Lista para armazenar as previsões dos próximos 7 dias (série estacionária)
    predictions_log_diff = []

    # Passo 3: Fazer predição dos próximos 7 dias
    for _ in range(7):
        # Realiza a predição do próximo dia (variação em log)
        predicted_log_diff = model.predict(last_50_days_scaled)

        # Limitar a variação prevista para evitar explosão de valores
        predicted_log_diff = np.clip(predicted_log_diff, -VARIATION_LIMIT, VARIATION_LIMIT)

        # Adiciona a predição à lista
        predictions_log_diff.append(float(predicted_log_diff))

        # Atualiza o último log com a predição
        last_real_log_price += predicted_log_diff  # Aqui, agora a variável está inicializada

        # Atualiza o array com a predição, remodelando corretamente para ter 3 dimensões
        last_50_days_scaled = np.append(last_50_days_scaled[:, 1:, :], predicted_log_diff.reshape(1, 1, 1), axis=1)

    # Passo 4: Reverter as transformações para obter valores de preços reais
    cumulative_log_price = last_real_log_price + np.cumsum(predictions_log_diff)

    # Inversão do logaritmo (aplicar exponenciação)
    predicted_prices = np.exp(cumulative_log_price)

    # Retornar os valores preditos junto com os últimos 7 valores reais
    last_7_real_prices = close_prices[-7:].tolist()

    return {
        "last_7_days_real_prices": last_7_real_prices,  # Últimos 7 valores reais
        "next_7_days_predictions": predicted_prices.tolist()  # Próximos 7 dias previstos
    }

@app.get("/get-last-7-days-prices")
def get_last_7_days_prices():
    # Coletar os dados dos últimos 7 dias
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    btc_data = yf.download("BTC-USD", start=start_date, end=end_date)
    close_prices = btc_data['Close'].values

    return {"last_7_days_prices": close_prices.tolist()}
