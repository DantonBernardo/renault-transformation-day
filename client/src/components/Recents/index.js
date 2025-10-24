import './style.css';
import Loading from '../Loading';
import { useDataContext } from '../../contexts/DataContext';
import { useEffect, useState } from 'react';

export default function Recents() {
  const { groups, loading } = useDataContext();
  const [previousGroups, setPreviousGroups] = useState([]);
  const [newGroups, setNewGroups] = useState([]);

  useEffect(() => {
    if (groups && groups.length > previousGroups.length && previousGroups.length > 0) {
      const newGroupsAdded = groups.slice(0, groups.length - previousGroups.length);
      setNewGroups(newGroupsAdded);
      
      // Remove o destaque após 3 segundos
      setTimeout(() => {
        setNewGroups([]);
      }, 3000);
    }
    setPreviousGroups(groups || []);
  }, [groups, previousGroups.length]);

  if (loading.groups) {
    return <Loading />;
  }

  if (!groups || groups.length === 0) {
    return (
      <div className="recents">
        <h2>Últimos registros</h2>
        <p>Nenhum registro encontrado.</p>
      </div>
    );
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
          {groups.map((group) => {
            const isNew = newGroups.some(ng => ng.id === group.id);
            return (
              <tr key={group.id} className={isNew ? 'new-group' : ''}>
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
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
