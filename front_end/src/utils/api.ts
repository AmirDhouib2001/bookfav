/**
 * Configuration centralisée de l'URL de l'API
 * Utilise la variable d'environnement VITE_API_URL définie dans docker-compose.yml
 */
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

/**
 * Fonction utilitaire pour construire des URLs d'API
 */
export const buildApiUrl = (endpoint: string): string => {
  // Supprime le slash initial si présent pour éviter les doubles slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_URL}/${cleanEndpoint}`;
};

console.log('🔗 API URL configurée:', API_URL); 