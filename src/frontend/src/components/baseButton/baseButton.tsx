import { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2'; // Importar o componente Line para o gráfico
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import "./baseButton.css";

// Registrar os componentes necessários do Chart.js
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

function BaseButton() {
  // Estado para armazenar os dados do gráfico
  const [chartData, setChartData] = useState<any>(null);

  // Função para buscar os dados do backend
  const handleButtonClick = async () => {
    try {
      // Fazer uma requisição GET para a rota do FastAPI que gera as predições
      const response = await axios.get("http://localhost:8000/predict-next-week/");

      // Capturar os dados de resposta: últimas 7 reais e predições
      const predictions = response.data.next_7_days_predictions[0]; // Acessar o primeiro elemento do array
      const last7RealValues = response.data.last_7_days_real_prices;  // Puxar os dados reais dos últimos 7 dias

      // Obter a data atual
      const today = new Date();
      
      // Combinar os rótulos para os últimos 7 dias e os próximos 7 dias
      const labels = Array.from({ length: last7RealValues.length + predictions.length }, (_, i) => {
        const date = new Date(today);
        date.setDate(today.getDate() - (7 - i)); // Calcular a data correta
        return date.toISOString().split('T')[0]; // Formatar como "ano-mês-dia"
      });

      // Preencher valores `null` para o gráfico real antes das previsões
      const realValuesWithNulls = [...last7RealValues, ...Array(predictions.length).fill(null)];
      // Preencher `null` para o gráfico previsto antes dos valores previstos
      const predictedValuesWithNulls = [...Array(last7RealValues.length).fill(null), ...predictions];

      // Atualizar o estado com os novos dados
      setChartData({
        labels: labels,
        datasets: [
          {
            label: "Preço Real do Bitcoin (USD)",
            data: realValuesWithNulls, // Usar dados reais com `null` após o último valor real
            fill: false,
            borderColor: "rgb(75, 192, 192)", // Cor para os dados reais
            tension: 0.1,
          },
          {
            label: "Preço Previsto do Bitcoin (USD)",
            data: predictedValuesWithNulls, // Usar `null` antes do início das previsões
            fill: false,
            borderColor: "rgb(255, 99, 132)", // Cor para os dados previstos
            tension: 0.1,
            borderDash: [5, 5], // Linha pontilhada para diferenciar previsões
          },
        ],
      });
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
    }
  };

  return (
    <div>
      {/* Botão para buscar e exibir os dados */}
      <button onClick={handleButtonClick}>
        Previsão para BITCOIN
      </button>

      {/* Renderizar o gráfico se os dados estiverem presentes */}
      {chartData && (
        <div style={{ marginTop: "20px", width: "480px", height: "480px" }}> {/* Aumentar a altura do gráfico */}
          <Line 
            data={chartData} 
            options={{ 
              responsive: true, 
              maintainAspectRatio: false, // Para que a altura definida seja respeitada
              plugins: { 
                legend: { position: "top" } 
              } 
            }} 
          />
        </div>
      )}
    </div>
  );
}

export default BaseButton;
