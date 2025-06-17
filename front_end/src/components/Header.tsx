import * as React from 'react';
import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import logo from '../logo.png';
import '../styles/Header.css';
import { useAuth } from './AuthProvider';

const Header: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0); // Force le rafraîchissement du composant
  
  // Fonction pour déterminer si un lien est actif
  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };
  
  const handleLogout = async () => {
    await logout();
    setShowUserMenu(false);
    navigate('/login');
  };
  
  const toggleUserMenu = () => {
    setShowUserMenu(!showUserMenu);
  };

  // Forcer le rafraîchissement du Header lorsque le localStorage change
  useEffect(() => {
    // Fonction pour détecter les changements dans le localStorage
    const handleStorageChange = () => {
      setRefreshKey(prevKey => prevKey + 1);
    };

    // Fonction pour détecter les changements d'état d'authentification
    const handleAuthStateChange = () => {
      setRefreshKey(prevKey => prevKey + 1);
      console.log('État d\'authentification mis à jour dans le Header');
    };

    // Écouter les changements de localStorage
    window.addEventListener('storage', handleStorageChange);
    
    // Écouter les événements personnalisés d'authentification
    window.addEventListener('auth-state-changed', handleAuthStateChange);
    
    // Nettoyer les écouteurs d'événements lors du démontage
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth-state-changed', handleAuthStateChange);
    };
  }, []);

  // Vérifier manuellement le localStorage pour s'assurer que l'en-tête est à jour
  useEffect(() => {
    const checkAuthStatus = () => {
      const sessionId = localStorage.getItem('session_id');
      const userJson = localStorage.getItem('user');
      
      // Forcer un rafraîchissement si l'état d'authentification semble désynchronisé
      if ((!!sessionId && !!userJson) !== isAuthenticated) {
        setRefreshKey(prevKey => prevKey + 1);
      }
    };
    
    checkAuthStatus();
  }, [location.pathname, isAuthenticated]); // Vérifier lors des changements de route
  
  return (
    <header className="header" key={refreshKey}>
      <div className="left-logo">
        <img src={logo} alt="BookFav logo" className="logo-img" />
        <span className="logo-text">bookfav</span>
      </div>

      <nav className="nav-links">
        <Link to="/" className={isActive('/')}>
          Accueil
        </Link>
        <Link to="/catalogue" className={isActive('/catalogue')}>
          Catalogue
        </Link>
        {isAuthenticated && (
          <Link to="/dashboard" className={isActive('/dashboard')}>
            Dashboard
          </Link>
        )}
      </nav>
      
      <div className="auth-section">
        {isAuthenticated && user ? (
          <div className="user-menu-container">
            <button 
              className="user-button"
              onClick={toggleUserMenu}
              aria-expanded={showUserMenu}
              aria-haspopup="true"
            >
              {user.profile_image_url ? (
                <img 
                  src={user.profile_image_url} 
                  alt={`Avatar de ${user.username}`} 
                  className="user-avatar"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = 'https://via.placeholder.com/40?text=User';
                  }}
                />
              ) : (
                <div className="user-avatar-placeholder">
                  {user.username.charAt(0).toUpperCase()}
                </div>
              )}
              <span className="user-name">{user.username}</span>
            </button>
            
            {showUserMenu && (
              <div className="user-dropdown">
                <Link 
                  to="/profile" 
                  className="dropdown-item"
                  onClick={() => setShowUserMenu(false)}
                >
                  Mon Profil
                </Link>
                <button 
                  className="dropdown-item logout-item"
                  onClick={handleLogout}
                >
                  Se déconnecter
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="auth-buttons">
            <Link to="/login" className="login-button">
              Connexion
            </Link>
            <Link to="/register" className="register-button">
              S'inscrire
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
