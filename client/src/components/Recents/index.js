import './style.css';
import { useState, useEffect } from 'react';
import Loading from '../Loading';

export default function Recents() {
  const [loading, setLoading] = useState(true);
  const [recents, setRecents] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/groups', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        const data = await response.json();
        setRecents(data);
      } catch (error) {
        console.error('Erro ao buscar dados:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="recents">
      <h2>Últimos registros</h2>

      <table className="recents-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tempo do Grupo (s)</th>
            <th>Data</th>
            <th>Detalhes dos Cubos</th>
          </tr>
        </thead>
        <tbody>
          {recents.map((group) => (
            <tr key={group.id}>
              <td>#{group.id}</td>
              <td>{group.group_time.toFixed(2)}</td>
              <td>{new Date(group.created_at).toLocaleString()}</td>
              <td>
                <table className="inner-table">
                  <thead>
                    <tr>
                      <th>Cor</th>
                      <th>Face</th>
                      <th>Tempo Individual (s)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.cubes.map((cube) => (
                      <tr key={cube.id}>
                        <td data-color={cube.color}>{cube.color}</td>
                        <td>{cube.face}</td>
                        <td>{cube.individual_time.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
