import Header from './components/Header';
import Recents from './components/Recents';
import Charts from './components/Charts';
import Notifications from './components/Notifications';

export default function App() {
  return (
    <div className='App'>
      <Header />
      <Notifications />
      <Charts />
      <Recents />
    </div>
  );
};