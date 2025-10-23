import './style.css';
import { useEffect, useRef, useMemo } from "react";
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from "chart.js";
import Loading from '../Loading';
import { useDataContext } from '../../contexts/DataContext';

// registra os componentes necessários pro gráfico de barras
Chart.register(BarController, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const COLORS = ["WHITE", "RED", "ORANGE", "BLUE", "YELLOW", "GREEN"];
const LABELS = ["White", "Red", "Orange", "Blue", "Yellow", "Green"];

export default function AvgColor() {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const { averages, loading } = useDataContext();

  const dataValues = useMemo(() => {
    if (!averages) return COLORS.map(() => 0);
    return COLORS.map(color => averages[color] || 0);
  }, [averages]);

  const chartConfig = useMemo(() => ({
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
  }), [dataValues]);

  useEffect(() => {
    if (!loading.averages && chartRef.current && averages) {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }

      const ctx = chartRef.current.getContext("2d");
      chartInstanceRef.current = new Chart(ctx, chartConfig);
    }

    return () => chartInstanceRef.current?.destroy();
  }, [loading.averages, chartConfig, averages]);

  if (loading.averages) return <Loading />;

  return (
    <div className="avgColor">
      <h2 className="chart-title">Tempo médio por cor</h2>
      <div className="chart-container">
        <canvas ref={chartRef} width={400} height={400}></canvas>
      </div>
    </div>
  );
}
