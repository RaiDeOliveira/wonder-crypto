import numpy as np
import pandas as pd
from fastapi import FastAPI
from tensorflow.keras.models import load_model
import yfinance as yf

# Inicialização do FastAPI
app = FastAPI()

# Carrega o modelo previamente salvo
model = load_model('meu_modelo_rnn.h5')

# Definir um valor de limite para variações logarítmicas para evitar explosão
VARIATION_LIMIT = 0.1  # Limitar variações logarítmicas para +/-10%

# Rota para predição dos próximos 7 dias
@app.get("/predict-next-week")
def predict_next_7_days():
    # Passo 1: Coletar os dados mais recentes do Bitcoin (por exemplo, dos últimos 50 dias)
    btc_data = yf.download("BTC-USD", start="2024-08-01", end="2024-09-29")

    # Considera a coluna de fechamento ajustado como base
    close_prices = btc_data['Close'].values

    # Passo 2: Transformação para série estacionária (aplicar log e a primeira diferença)
    # Aplicar logaritmo natural nos preços de fechamento
    log_prices = np.log(close_prices)

    # Calcular a primeira diferença dos preços logaritmizados
    log_diff = np.diff(log_prices)

    # Seleciona os últimos 50 valores transformados para alimentar o modelo
    last_50_days = log_diff[-50:]  # Pegando os últimos 50 dias (input para o modelo)
    last_50_days_scaled = last_50_days.reshape(1, len(last_50_days), 1)  # Reshape para (1, 50, 1)

    # Lista para armazenar as previsões dos próximos 7 dias (série estacionária)
    predictions_log_diff = []

    # Passo 3: Fazer predição dos próximos 7 dias
    for _ in range(20):
        # Realiza a predição do próximo dia (variação em log)
        predicted_log_diff = model.predict(last_50_days_scaled)

        # Limitar a variação prevista para evitar explosão de valores
        if abs(predicted_log_diff) > VARIATION_LIMIT:
            predicted_log_diff = np.clip(predicted_log_diff, -VARIATION_LIMIT, VARIATION_LIMIT)

        # Ajusta o valor previsto para ter as mesmas dimensões do array de entrada
        predicted_log_diff_reshaped = np.reshape(predicted_log_diff, (1, 1, 1))

        # Adiciona a predição à lista (converte para tipo float)
        predictions_log_diff.append(float(predicted_log_diff))

        # Atualiza o array com a predição, removendo o primeiro valor e adicionando a nova previsão
        last_50_days_scaled = np.append(last_50_days_scaled[:, 1:, :], predicted_log_diff_reshaped, axis=1)

    # Passo 4: Reverter as transformações para obter valores de preços reais
    # Para reverter a transformação, precisamos do último valor original antes da transformação
    last_real_log_price = log_prices[-1]  # Último valor em log antes da transformação

    # Inverter a série estacionária (cálculo cumulativo)
    # Usar np.cumsum para adicionar a primeira predição e depois acumular as previsões
    cumulative_log_price = np.cumsum([last_real_log_price] + predictions_log_diff)

    # Inversão do logaritmo (aplicar exponenciação)
    predicted_prices = np.exp(cumulative_log_price)

    # Passo 5: Retornar as previsões desnormalizadas como um dicionário
    return {"next_7_days_predictions": predicted_prices.tolist()}
