import './style.css';
import { useEffect, useRef, useMemo } from "react";
import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from "chart.js";
import { useDataContext } from '../../contexts/DataContext';

// registra apenas o necessário pro gráfico de linha
Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

export default function LatestGroupTime() {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const { latestTimes, loading } = useDataContext();

  const chartData = useMemo(() => {
    if (!latestTimes || latestTimes.length === 0) {
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

    const labels = latestTimes.map((g) => `#${g.id}`);
    const times = latestTimes.map((g) => g.group_time);
    
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
  }, [latestTimes]);

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
    },
  }), [chartData]);

  useEffect(() => {
    if (!loading.latestTimes && chartRef.current && latestTimes) {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }

      const ctx = chartRef.current.getContext("2d");
      chartInstanceRef.current = new Chart(ctx, chartConfig);
    }

    return () => chartInstanceRef.current?.destroy();
  }, [loading.latestTimes, chartConfig, latestTimes]);

  return (
    <div className="latest-group-time">
      <h2 className="chart-title">Tempos de grupo recentes</h2>
      <div className="chart-container">
        <canvas ref={chartRef} />
      </div>
    </div>
  );
}
