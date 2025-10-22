import './style.css';

export default function Header() {
  return (
    <header className='header'>
      <div className='logo'>
        <div className='right'>
          <img src='/renaultLogo.svg' alt='Logo Renault'/>
          <h1>Transformation Day</h1>
        </div>
        <img src='/campoLogo.png' alt='Logo Renault'/>
      </div>
    </header>
  );
}