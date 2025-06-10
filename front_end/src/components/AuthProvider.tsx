import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';

// Définition du type d'utilisateur
export interface User {
  user_id: number;
  username: string;
  email: string;
  full_name?: string;
  profile_image_url?: string;
  role: string;
  favorite_genres?: string[];
  created_at?: string;
  last_login?: string;
}

// Interface du contexte d'authentification
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (sessionId: string, userData: User) => void;
  logout: () => Promise<void>;
  updateUserData: (userData: Partial<User>) => void;
}

// Création du contexte avec une valeur par défaut
const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  loading: true,
  login: () => {},
  logout: async () => {},
  updateUserData: () => {},
});

// Hook personnalisé pour utiliser le contexte d'authentification
export const useAuth = () => useContext(AuthContext);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  
  // Fonction pour se connecter - version améliorée avec gestion synchrone
  const login = (sessionId: string, userData: User) => {
    try {
      // Stocker les données dans localStorage
      localStorage.setItem('session_id', sessionId);
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Mettre à jour l'état immédiatement
      setUser(userData);
      
      // Si nous étions en chargement, mettre fin à l'état de chargement
      if (loading) {
        setLoading(false);
      }
      
      console.log('Utilisateur connecté avec succès:', userData.username);
    } catch (error) {
      console.error('Erreur lors de la mise à jour des données de connexion:', error);
    }
  };
  
  // Fonction pour se déconnecter
  const logout = async () => {
    const sessionId = localStorage.getItem('session_id');
    
    if (sessionId) {
      try {
        // Obtenir l'URL de l'API depuis les variables d'environnement
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
        
        await fetch(`${apiUrl}/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ session_id: sessionId })
        });
        
        console.log('Déconnexion effectuée côté serveur');
      } catch (error) {
        console.error('Erreur lors de la déconnexion:', error);
      }
    }
    
    // Supprimer les données de session même si la requête API échoue
    localStorage.removeItem('session_id');
    localStorage.removeItem('user');
    setUser(null);
    console.log('Utilisateur déconnecté localement');
  };
  
  // Fonction pour mettre à jour les données utilisateur
  const updateUserData = (userData: Partial<User>) => {
    if (!user) return;
    
    const updatedUser = { ...user, ...userData };
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setUser(updatedUser);
  };
  
  // Vérifier la validité de la session au chargement et à intervalles réguliers
  useEffect(() => {
    const validateSession = async () => {
      const sessionId = localStorage.getItem('session_id');
      const storedUser = localStorage.getItem('user');
      
      if (!sessionId || !storedUser) {
        setLoading(false);
        return;
      }
      
      try {
        // Définir l'utilisateur immédiatement à partir du localStorage
        // pour éviter le flash de l'interface non authentifiée
        setUser(JSON.parse(storedUser));
        
        // Obtenir l'URL de l'API depuis les variables d'environnement
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
        
        const response = await fetch(`${apiUrl}/auth/validate-session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ session_id: sessionId })
        });
        
        const data = await response.json();
        
        if (response.ok && data.valid) {
          // Mettre à jour avec les données fraîches du serveur
          setUser(data.user);
          console.log('Session validée côté serveur');
        } else {
          // Session invalide, déconnecter l'utilisateur
          localStorage.removeItem('session_id');
          localStorage.removeItem('user');
          setUser(null);
          console.log('Session invalide, déconnexion');
        }
      } catch (error) {
        console.error('Erreur lors de la validation de session:', error);
        // En cas d'erreur réseau, conserver les données locales
        // et on a déjà mis l'utilisateur à partir du localStorage
      } finally {
        setLoading(false);
      }
    };
    
    validateSession();
    
    // Écouter les événements d'authentification pour forcer une revalidation
    const handleAuthStateChanged = () => {
      console.log('Événement auth-state-changed détecté dans AuthProvider');
      validateSession();
    };
    
    // Écouter les changements de localStorage entre les onglets
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === 'session_id' || event.key === 'user') {
        console.log('Changement de localStorage détecté dans AuthProvider:', event.key);
        validateSession();
      }
    };
    
    window.addEventListener('auth-state-changed', handleAuthStateChanged);
    window.addEventListener('storage', handleStorageChange);
    
    // Valider la session toutes les 5 minutes pour maintenir la session active
    const intervalId = setInterval(validateSession, 5 * 60 * 1000);
    
    return () => {
      clearInterval(intervalId);
      window.removeEventListener('auth-state-changed', handleAuthStateChanged);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);
  
  // Valeur du contexte
  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    logout,
    updateUserData
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider; 