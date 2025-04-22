FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Installer les types React manquants
RUN npm install --save-dev @types/react @types/react-dom @types/react-router-dom

# Build l'application pour la production
# CMD ["npm", "run", "build"]

# Ou pour le développement avec hot-reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 