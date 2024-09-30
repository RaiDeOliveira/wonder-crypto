import numpy as np
import pandas as pd
from fastapi import FastAPI
from tensorflow.keras.models import load_model
import yfinance as yf
from fastapi.middleware.cors import CORSMiddleware

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

# Carrega o modelo previamente salvo
model = load_model('meu_modelo_rnn.h5')

# Definir um valor de limite para variações logarítmicas para evitar explosão
VARIATION_LIMIT = 0.05  # Limitar variações logarítmicas para +/-5%

# Rota para predição dos próximos 7 dias
@app.get("/predict-next-week")
def predict_next_7_days():
    # Passo 1: Coletar os dados mais recentes do Bitcoin (por exemplo, dos últimos 50 dias)
    btc_data = yf.download("BTC-USD", start="2024-08-01", end="2024-09-29")

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
    btc_data = yf.download("BTC-USD", start="2024-09-22", end="2024-09-29")  # Ajuste as datas conforme necessário
    close_prices = btc_data['Close'].values

    return {"last_7_days_prices": close_prices.tolist()}
