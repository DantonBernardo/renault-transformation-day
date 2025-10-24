import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const DataContext = createContext();

export const useDataContext = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useDataContext deve ser usado dentro de DataProvider');
  }
  return context;
};

export const DataProvider = ({ children }) => {
  const [groups, setGroups] = useState([]);
  const [averages, setAverages] = useState({});
  const [latestTimes, setLatestTimes] = useState([]);
  const [loading, setLoading] = useState({
    groups: true,
    averages: true,
    latestTimes: true
  });
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isPolling, setIsPolling] = useState(false);
  const [lastGroupCount, setLastGroupCount] = useState(0);

  const fetchGroups = useCallback(async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/groups');
      const data = await response.json();
      
      // Compara dados mais detalhadamente
      const currentGroups = JSON.stringify(groups.map(g => ({ id: g.id, group_time: g.group_time })));
      const newGroups = JSON.stringify(data.map(g => ({ id: g.id, group_time: g.group_time })));
      
      // Só atualiza se houve mudança nos dados OU se é o primeiro carregamento
      if (currentGroups !== newGroups || groups.length === 0) {
        console.log('Grupos atualizados:', {
          previousCount: groups.length,
          newCount: data.length,
          isFirstLoad: groups.length === 0
        });
        setGroups(data);
        setLastGroupCount(data.length);
        setLoading(prev => ({ ...prev, groups: false }));
        return { data, hasChanges: true };
      }
      
      return { data, hasChanges: false };
    } catch (error) {
      console.error('Erro ao buscar grupos:', error);
      setLoading(prev => ({ ...prev, groups: false }));
      return { data: [], hasChanges: false };
    }
  }, [groups]);

  const fetchAverages = useCallback(async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/averages-all-colors');
      const data = await response.json();
      
      // Compara se as médias mudaram OU se é o primeiro carregamento
      const currentAverages = JSON.stringify(averages);
      const newAverages = JSON.stringify(data);
      
      if (currentAverages !== newAverages || Object.keys(averages).length === 0) {
        setAverages(data);
        setLoading(prev => ({ ...prev, averages: false }));
        return { data, hasChanges: true };
      }
      
      return { data, hasChanges: false };
    } catch (error) {
      console.error('Erro ao buscar médias:', error);
      setLoading(prev => ({ ...prev, averages: false }));
      return { data: {}, hasChanges: false };
    }
  }, [averages]);

  const fetchLatestTimes = useCallback(async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/latest-group-times');
      const data = await response.json();
      
      // Compara dados mais detalhadamente
      const currentTimes = JSON.stringify(latestTimes.map(t => ({ id: t.id, group_time: t.group_time })));
      const newTimes = JSON.stringify(data.map(t => ({ id: t.id, group_time: t.group_time })));
      
      // Só atualiza se houve mudança nos dados OU se é o primeiro carregamento
      if (currentTimes !== newTimes || latestTimes.length === 0) {
        console.log('Tempos recentes atualizados:', {
          previousCount: latestTimes.length,
          newCount: data.length,
          isFirstLoad: latestTimes.length === 0
        });
        setLatestTimes(data);
        setLoading(prev => ({ ...prev, latestTimes: false }));
        return { data, hasChanges: true };
      }
      
      return { data, hasChanges: false };
    } catch (error) {
      console.error('Erro ao buscar tempos recentes:', error);
      setLoading(prev => ({ ...prev, latestTimes: false }));
      return { data: [], hasChanges: false };
    }
  }, [latestTimes]);

  const fetchAllData = useCallback(async () => {
    setIsPolling(true);
    try {
      const [groupsResult, averagesResult, timesResult] = await Promise.all([
        fetchGroups(),
        fetchAverages(),
        fetchLatestTimes()
      ]);

      // Sempre atualiza lastUpdate na primeira execução ou quando há mudanças
      const isFirstLoad = !lastUpdate;
      if (isFirstLoad || groupsResult.hasChanges || averagesResult.hasChanges || timesResult.hasChanges) {
        setLastUpdate(new Date());
        console.log('Dados atualizados:', {
          firstLoad: isFirstLoad,
          groups: groupsResult.hasChanges,
          averages: averagesResult.hasChanges,
          times: timesResult.hasChanges
        });
      }
    } catch (error) {
      console.error('Erro ao buscar todos os dados:', error);
    } finally {
      setIsPolling(false);
    }
  }, [fetchGroups, fetchAverages, fetchLatestTimes, lastUpdate]);

  // Polling mais inteligente - verifica a cada 5 segundos
  useEffect(() => {
    // Carrega dados iniciais
    fetchAllData();

    // Configura polling com intervalo maior
    const interval = setInterval(fetchAllData, 5000); // 5 segundos

    return () => clearInterval(interval);
  }, [fetchAllData]);

  const value = {
    groups,
    averages,
    latestTimes,
    loading,
    lastUpdate,
    isPolling,
    refetch: fetchAllData
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};
