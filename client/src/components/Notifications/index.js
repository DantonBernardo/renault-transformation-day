import "./style.css";
import Loading from '../Loading';
import { useDataContext } from '../../contexts/DataContext';

export default function NotificationsTable() {
  const { notifications, loading } = useDataContext();

  if (loading.notifications) {
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
