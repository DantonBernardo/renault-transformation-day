import './style.css';
import { useEffect, useState } from 'react';
import { useDataContext } from '../../contexts/DataContext';

export default function RealtimeNotifications() {
  const { groups, lastUpdate, isPolling } = useDataContext();
  const [previousCount, setPreviousCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [lastNotificationTime, setLastNotificationTime] = useState(null);

  useEffect(() => {
    // Só mostra notificação se:
    // 1. Há grupos
    // 2. O número de grupos aumentou
    // 3. Não estamos no carregamento inicial (previousCount > 0)
    // 4. Não mostrou notificação muito recentemente (evita spam)
    if (groups && groups.length > previousCount && previousCount > 0) {
      const now = new Date();
      const timeSinceLastNotification = lastNotificationTime 
        ? now.getTime() - lastNotificationTime.getTime() 
        : Infinity;

      // Só mostra notificação se passou pelo menos 2 segundos da última
      if (timeSinceLastNotification > 2000) {
        const newGroups = groups.slice(0, groups.length - previousCount);
        const newNotifications = newGroups.map(group => ({
          id: `group-${group.id}-${Date.now()}`,
          message: `Novo grupo #${group.id} adicionado! Tempo: ${group.group_time.toFixed(2)}s`,
          timestamp: new Date(),
          type: 'success'
        }));
        
        setNotifications(prev => [...newNotifications, ...prev].slice(0, 3)); // Máximo 3 notificações
        setLastNotificationTime(now);
      }
    }
    
    if (groups) {
      setPreviousCount(groups.length);
    }
  }, [groups, previousCount, lastNotificationTime]);

  useEffect(() => {
    // Remove notificações antigas após 4 segundos
    if (notifications.length > 0) {
      const timer = setTimeout(() => {
        setNotifications(prev => prev.slice(0, -1));
      }, 4000);

      return () => clearTimeout(timer);
    }
  }, [notifications]);

  // Não mostra notificações se não há nenhuma
  if (notifications.length === 0) return null;

  return (
    <div className="realtime-notifications">
      {notifications.map(notification => (
        <div 
          key={notification.id} 
          className={`notification ${notification.type}`}
        >
          <div className="notification-content">
            <span className="notification-message">{notification.message}</span>
            <span className="notification-time">
              {notification.timestamp.toLocaleTimeString('pt-BR')}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
