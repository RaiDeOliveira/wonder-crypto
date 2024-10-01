import React, { useState } from 'react';
import axios from 'axios';
import "./fileUpload.css"; // Certifique-se de que este caminho está correto

function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage("Por favor, selecione um arquivo antes de fazer upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:8000/upload-file/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setMessage(`Upload bem-sucedido: ${response.data.message}`);
    } catch (error) {
      setMessage("Erro ao fazer upload do arquivo. Por favor, tente novamente.");
      console.error("Erro ao fazer upload:", error);
    }
  };

  return (
    <div className='file-upload'>
      <h2>Upload de Arquivo .h5</h2>
      <input type="file" accept=".h5" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file}>
        Upload
      </button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default FileUpload;
