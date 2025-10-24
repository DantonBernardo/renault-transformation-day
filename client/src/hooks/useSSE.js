import { useEffect, useRef, useState } from 'react';

/**
 * Hook para gerenciar Server-Sent Events
 * @param {string} url - URL do endpoint SSE
 * @param {function} onMessage - Callback para quando receber mensagem
 * @param {function} onError - Callback para quando houver erro
 * @param {boolean} enabled - Se a conexão deve estar ativa
 */
export function useSSE(url, onMessage, onError, enabled = true) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const eventSourceRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = () => {
    if (!enabled || eventSourceRef.current) return;

    try {
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('SSE conectado');
        setIsConnected(true);
        reconnectAttempts.current = 0;
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          if (onMessage) onMessage(data);
        } catch (error) {
          console.error('Erro ao processar mensagem SSE:', error);
        }
      };

      eventSource.addEventListener('data-update', (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          if (onMessage) onMessage(data);
        } catch (error) {
          console.error('Erro ao processar atualização de dados:', error);
        }
      });

      eventSource.addEventListener('heartbeat', (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Heartbeat SSE:', data.timestamp);
        } catch (error) {
          console.error('Erro ao processar heartbeat:', error);
        }
      });

      eventSource.onerror = (error) => {
        console.error('Erro na conexão SSE:', error);
        setIsConnected(false);
        
        if (onError) onError(error);
        
        // Reconexão automática com backoff exponencial
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.pow(2, reconnectAttempts.current) * 1000; // 1s, 2s, 4s, 8s, 16s
          console.log(`Tentando reconectar em ${delay}ms (tentativa ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            disconnect();
            connect();
          }, delay);
        } else {
          console.error('Máximo de tentativas de reconexão atingido');
        }
      };

    } catch (error) {
      console.error('Erro ao criar conexão SSE:', error);
      if (onError) onError(error);
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
      console.log('SSE desconectado');
    }
  };

  useEffect(() => {
    if (enabled) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, url]);

  return {
    isConnected,
    lastMessage,
    connect,
    disconnect
  };
}
