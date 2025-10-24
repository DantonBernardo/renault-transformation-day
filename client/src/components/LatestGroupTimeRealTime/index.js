import './style.css';
import { useEffect, useRef, useState } from "react";
import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from "chart.js";
import { useApiPolling } from '../../hooks/useApiCache';

// registra apenas o necessário pro gráfico de linha
Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

export default function LatestGroupTimeRealTime() {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const { data, loading, error } = useApiPolling(`${process.env.REACT_APP_API_URL}latest-group-times`, {}, 10000); // Atualiza a cada 10 segundos

  const chartData = useMemo(() => {
    if (!data || data.length === 0) {
      return {
        labels: [],
        datasets: [{
          label: "Tempo do grupo (s)",
          data: [],
          borderColor: "rgb(75, 192, 192)",
          backgroundColor: "rgba(75, 192, 192, 0.3)",
          tension: 0.2,
          pointRadius: 5,
          pointHoverRadius: 8,
          fill: false,
        }],
      };
    }

    const labels = data.map((g) => `#${g.id}`);
    const times = data.map((g) => g.group_time);
    
    return {
      labels,
      datasets: [
        {
          label: "Tempo do grupo (s)",
          data: times,
          borderColor: "rgb(75, 192, 192)",
          backgroundColor: "rgba(75, 192, 192, 0.3)",
          tension: 0.2,
          pointRadius: 5,
          pointHoverRadius: 8,
          fill: false,
        },
      ],
    };
  }, [data]);

  const chartConfig = useMemo(() => ({
    type: "line",
    data: chartData,
    options: {
      responsive: true,
      plugins: {
        legend: { position: "top" },
      },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: "Tempo (s)" } },
        x: { title: { display: true, text: "Grupo" } },
      },
      animation: {
        duration: 1000, // Animação suave para atualizações
        easing: 'easeInOutQuart'
      }
    },
  }), [chartData]);

  useEffect(() => {
    if (!loading && chartRef.current && data) {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }

      const ctx = chartRef.current.getContext("2d");
      chartInstanceRef.current = new Chart(ctx, chartConfig);
    }

    return () => chartInstanceRef.current?.destroy();
  }, [loading, chartConfig, data]);

  return (
    <div className="latest-group-time">
      <h2 className="chart-title">Tempos de grupo recentes (Tempo Real)</h2>
      <div className="chart-container">
        <canvas ref={chartRef} width={400} height={400}></canvas>
      </div>
      {loading && <p className="loading-indicator">Atualizando dados...</p>}
    </div>
  );
}
