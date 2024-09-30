# Imagem base com Node.js para o build do frontend
FROM node:18 AS build

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando os arquivos package.json e package-lock.json para instalar dependências
COPY package*.json ./

# Instalando as dependências
RUN npm install

# Copiando todo o código para a imagem
COPY . .

# Build do frontend para produção
RUN npm run build

# Servindo o conteúdo estático
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
