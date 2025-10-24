import Header from './components/Header';
import Recents from './components/Recents';
import Charts from './components/Charts';
import Notifications from './components/Notifications';
import RealtimeIndicator from './components/RealtimeIndicator';
import RealtimeNotifications from './components/RealtimeNotifications';
import { DataProvider, useDataContext } from './contexts/DataContext';

function AppContent() {
  const { isPolling, lastUpdate } = useDataContext();

  return (
    <div className='App'>
      <Header />
      <RealtimeIndicator isPolling={isPolling} lastUpdate={lastUpdate} />
      <Notifications />
      <Charts />
      <Recents />
      <RealtimeNotifications />
    </div>
  );
}

export default function App() {
  return (
    <DataProvider>
      <AppContent />
    </DataProvider>
  );
};