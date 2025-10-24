import './style.css';
import { useDataContext } from '../../contexts/DataContext';

export default function Header() {
  const { refetch, isPolling } = useDataContext();

  const handleRefresh = () => {
    refetch();
  };

  return (
    <header className='header'>
      <div className='logo'>
        <div className='right'>
          <img src='/renaultLogo.svg' alt='Logo Renault'/>
          <h1>Transformation Day</h1>
        </div>
        <div className='header-actions'>
          <button 
            className={`refresh-button ${isPolling ? 'loading' : ''}`}
            onClick={handleRefresh}
            disabled={isPolling}
          >
            {isPolling ? '🔄 Atualizando...' : '🔄 Atualizar'}
          </button>
          <img src='/campoLogo.png' alt='Logo Campo'/>
        </div>
      </div>
    </header>
  );
}