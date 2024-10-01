# Usar a imagem base do Node.js para build do frontend
FROM node:18 AS build

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos de dependência do projeto
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar o restante dos arquivos do projeto para a imagem
COPY . .

# Rodar o build do Vite para produção
RUN npm run build

# Usar uma imagem do Nginx para servir o frontend
FROM nginx:alpine

# Copiar o build do Vite para o diretório de conteúdo estático do Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Expor a porta 80 para o Nginx
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]
