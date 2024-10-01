import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Configuração do Vite para o projeto React
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist', // Diretório de saída para build
    emptyOutDir: true, // Limpar a pasta de saída antes do novo build
  },
});
