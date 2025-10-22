import './style.css';
import { useEffect, useRef, useState } from "react";
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from "chart.js";
import Loading from '../Loading';

// registra os componentes necessários pro gráfico de barras
Chart.register(BarController, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const COLORS = ["WHITE", "RED", "ORANGE", "BLUE", "YELLOW", "GREEN"];
const LABELS = ["White", "Red", "Orange", "Blue", "Yellow", "Green"];

export default function AvgColor() {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    const promises = COLORS.map(async (color) => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/average/${color}`);
        const data = await res.json();
        return data.average_individual_time || 0;
      } catch (err) {
        console.error(err);
        return 0;
      } finally {
        setLoading(false);
      }
    });
    return await Promise.all(promises);
  };

  useEffect(() => {
    const loadChart = async () => {
      const dataValues = await fetchData();

      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }

      const ctx = chartRef.current.getContext("2d");
      chartInstanceRef.current = new Chart(ctx, {
        type: "bar",
        data: {
          labels: LABELS,
          datasets: [
            {
              label: "Tempo médio (s)",
              data: dataValues,
              backgroundColor: [
                "rgba(244, 240, 240, 0.7)",
                "rgba(255, 0, 0, 0.7)",
                "rgba(255, 165, 0, 0.7)",
                "rgba(0, 0, 255, 0.7)",
                "rgba(255, 255, 0, 0.7)",
                "rgba(0, 255, 0, 0.7)"
              ],
              borderWidth: 1
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
          },
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      });
    };

    loadChart();

    return () => chartInstanceRef.current?.destroy();
  }, []);

  if (loading) return <Loading />;

  return (
    <div className="avgColor">
      <h2 className="chart-title">Tempo médio por cor</h2>
      <div className="chart-container">
        <canvas ref={chartRef} width={400} height={400}></canvas>
      </div>
    </div>
  );
}
