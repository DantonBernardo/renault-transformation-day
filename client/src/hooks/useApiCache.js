import { useState, useEffect, useCallback, useRef } from 'react';

// Cache simples em memória
const cache = new Map();
const CACHE_DURATION = 30000; // 30 segundos

export function useApiCache(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const fetchData = useCallback(async () => {
    // Cancela requisição anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Verifica cache primeiro
    const cacheKey = `${url}_${JSON.stringify(options)}`;
    const cached = cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      setData(cached.data);
      setLoading(false);
      setError(null);
      return;
    }

    // Cria novo AbortController
    abortControllerRef.current = new AbortController();

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(url, {
        ...options,
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Salva no cache
      cache.set(cacheKey, {
        data: result,
        timestamp: Date.now()
      });

      setData(result);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err);
        console.error('Erro na requisição:', err);
      }
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  useEffect(() => {
    fetchData();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData]);

  const refetch = useCallback(() => {
    // Remove do cache para forçar nova requisição
    const cacheKey = `${url}_${JSON.stringify(options)}`;
    cache.delete(cacheKey);
    fetchData();
  }, [fetchData, url, options]);

  return { data, loading, error, refetch };
}

// Hook para polling automático
export function useApiPolling(url, options = {}, interval = 5000) {
  const { data, loading, error, refetch } = useApiCache(url, options);
  const intervalRef = useRef(null);

  useEffect(() => {
    intervalRef.current = setInterval(refetch, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [refetch, interval]);

  return { data, loading, error, refetch };
}
