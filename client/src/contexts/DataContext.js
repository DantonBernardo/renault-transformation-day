import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useSSE } from '../hooks/useSSE';

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
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState({
    groups: true,
    averages: true,
    latestTimes: true,
    notifications: true
  });
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isPolling, setIsPolling] = useState(false);
  const [lastGroupCount, setLastGroupCount] = useState(0);
  const [sseEnabled, setSseEnabled] = useState(true);

  const fetchGroups = useCallback(async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}groups`);
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
      const response = await fetch(`${process.env.REACT_APP_API_URL}averages-all-colors`);
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
      const response = await fetch(`${process.env.REACT_APP_API_URL}latest-group-times`);
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

  const fetchNotifications = useCallback(async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/notifications');
      const data = await response.json();
      
      // Compara se as notificações mudaram OU se é o primeiro carregamento
      const currentNotifications = JSON.stringify(notifications.map(n => ({ group_id: n.group_id, type: n.type })));
      const newNotifications = JSON.stringify(data.map(n => ({ group_id: n.group_id, type: n.type })));
      
      if (currentNotifications !== newNotifications || notifications.length === 0) {
        console.log('Notificações atualizadas:', {
          previousCount: notifications.length,
          newCount: data.length,
          isFirstLoad: notifications.length === 0
        });
        setNotifications(data);
        setLoading(prev => ({ ...prev, notifications: false }));
        return { data, hasChanges: true };
      }
      
      return { data, hasChanges: false };
    } catch (error) {
      console.error('Erro ao buscar notificações:', error);
      setLoading(prev => ({ ...prev, notifications: false }));
      return { data: [], hasChanges: false };
    }
  }, [notifications]);

  const fetchAllData = useCallback(async () => {
    setIsPolling(true);
    try {
      const [groupsResult, averagesResult, timesResult, notificationsResult] = await Promise.all([
        fetchGroups(),
        fetchAverages(),
        fetchLatestTimes(),
        fetchNotifications()
      ]);

      // Sempre atualiza lastUpdate na primeira execução ou quando há mudanças
      const isFirstLoad = !lastUpdate;
      if (isFirstLoad || groupsResult.hasChanges || averagesResult.hasChanges || timesResult.hasChanges || notificationsResult.hasChanges) {
        setLastUpdate(new Date());
        console.log('Dados atualizados:', {
          firstLoad: isFirstLoad,
          groups: groupsResult.hasChanges,
          averages: averagesResult.hasChanges,
          times: timesResult.hasChanges,
          notifications: notificationsResult.hasChanges
        });
      }
    } catch (error) {
      console.error('Erro ao buscar todos os dados:', error);
    } finally {
      setIsPolling(false);
    }
  }, [fetchGroups, fetchAverages, fetchLatestTimes, fetchNotifications, lastUpdate]);

  // Função para processar dados recebidos via SSE
  const handleSSEData = useCallback((data) => {
    console.log('Dados recebidos via SSE:', data);
    
    if (data.groups) {
      setGroups(data.groups);
      setLastGroupCount(data.groups.length);
    }
    
    if (data.averages) {
      setAverages(data.averages);
    }
    
    if (data.latestTimes) {
      setLatestTimes(data.latestTimes);
    }
    
    if (data.notifications) {
      setNotifications(data.notifications);
    }
    
    // Atualiza loading states
    setLoading({
      groups: false,
      averages: false,
      latestTimes: false,
      notifications: false
    });
    
    // Atualiza timestamp
    setLastUpdate(new Date());
  }, []);

  // Função para lidar com erros do SSE
  const handleSSEError = useCallback((error) => {
    console.error('Erro na conexão SSE:', error);
    // Pode implementar fallback para polling aqui se necessário
  }, []);

  // Configuração do SSE
  const { isConnected: sseConnected } = useSSE(
    'http://127.0.0.1:8000/sse',
    handleSSEData,
    handleSSEError,
    sseEnabled
  );

  // Carrega dados iniciais apenas uma vez
  useEffect(() => {
    fetchAllData();
  }, []);

  const value = {
    groups,
    averages,
    latestTimes,
    notifications,
    loading,
    lastUpdate,
    isPolling,
    sseConnected,
    sseEnabled,
    setSseEnabled,
    refetch: fetchAllData
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};
