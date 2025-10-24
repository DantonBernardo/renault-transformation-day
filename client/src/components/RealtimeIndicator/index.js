import './style.css';

export default function RealtimeIndicator({ isPolling, lastUpdate, sseConnected }) {
  const formatTime = (date) => {
    if (!date) return 'Nunca';
    return date.toLocaleTimeString('pt-BR');
  };

  const getTimeSinceLastUpdate = () => {
    if (!lastUpdate) return null;
    const now = new Date();
    const diffMs = now.getTime() - lastUpdate.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    
    if (diffSeconds < 60) return `${diffSeconds}s atrás`;
    const diffMinutes = Math.floor(diffSeconds / 60);
    if (diffMinutes < 60) return `${diffMinutes}min atrás`;
    const diffHours = Math.floor(diffMinutes / 60);
    return `${diffHours}h atrás`;
  };

  return (
    <div className="realtime-indicator">
      <div className="status-dot">
        <div className={`pulse ${isPolling ? 'active' : ''} ${sseConnected ? 'connected' : 'disconnected'}`}></div>
      </div>
      <div className="status-text">
        <span className="status-label">
          {isPolling ? 'Verificando...' : sseConnected ? 'Tempo Real Ativo' : 'Modo Manual'}
        </span>
        <span className="last-update">
          {lastUpdate ? `Atualizado ${getTimeSinceLastUpdate()}` : 'Aguardando dados...'}
        </span>
        {sseConnected && (
          <span className="sse-status">🟢 Conectado</span>
        )}
      </div>
    </div>
  );
}
