import './App.css';
import BaseButton from './components/baseButton/baseButton';
import FileUpload from './components/fileUpload/fileUpload';

function App() {
  return (
    <div className='app'>
      <div className='paddingDiv'>
        <h1 className='title'>Wonder Crypto</h1>
        <br></br>
        <BaseButton />
        <br></br>
        <FileUpload /> {/* Componente de upload de arquivos */}
      </div>
    </div>
  );
}

export default App;
