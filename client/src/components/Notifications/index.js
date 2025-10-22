import { useEffect, useState } from "react";
import "./style.css";
import Loading from '../Loading';

export default function NotificationsTable() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/notifications");
        const data = await res.json();
        setNotifications(data);
      } catch (err) {
        console.error("Erro ao buscar notificações:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, []);

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="notifications-container">
      <h2 className="notifications-title">Notificações de Grupos</h2>
      <table>
        <thead>
          <tr>
            <th>ID do Grupo</th>
            <th>Tempo do Grupo</th>
            <th>Status</th>
            <th>Razão</th>
          </tr>
        </thead>
        <tbody>
          {notifications.map((n) => (
            <tr key={n.group_id}>
              <td>#{n.group_id}</td>
              <td>{n.group_time.toFixed(2)}s</td>
              <td className={n.type === "high_time" ? "late" : "early"}>
                {n.type === "high_time" ? "Atrasado" : "Adiantado"}
              </td>
              <td>
                <strong className="cube-color">{n.cube.color}</strong> 
                <div>
                  {n.type === "high_time" ? '+' : '-'} {n.cube.diff.toFixed(2)}s
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
