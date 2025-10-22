import './style.css';
import { useEffect, useRef } from "react";
import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from "chart.js";

// registra apenas o necessário pro gráfico de linha
Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

export default function LatestGroupTime() {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);

  const fetchData = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/latest-group-times");
      const data = await res.json();
      return data;
    } catch (err) {
      console.error("Erro ao buscar dados:", err);
      return [];
    }
  };

  useEffect(() => {
    const loadChart = async () => {
      const groups = await fetchData();
      const labels = groups.map((g) => `#${g.id}`);
      const times = groups.map((g) => g.group_time);

      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }

      const ctx = chartRef.current.getContext("2d");
      chartInstanceRef.current = new Chart(ctx, {
        type: "line",
        data: {
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
        },
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
      });
    };

    loadChart();
    return () => chartInstanceRef.current?.destroy();
  }, []);

  return (
    <div className="latest-group-time">
      <h2 className="chart-title">Tempos de grupo recentes</h2>
      <div className="chart-container">
        <canvas ref={chartRef} width={400} height={400}></canvas>
      </div>
    </div>
  );
}
