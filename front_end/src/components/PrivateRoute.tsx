import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthProvider';

interface PrivateRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ 
  children, 
  redirectTo = '/login' 
}) => {
  const { isAuthenticated, loading } = useAuth();

  // Si l'authentification est en cours de vérification, afficher un indicateur de chargement
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Vérification de la session...</p>
      </div>
    );
  }

  // Si l'utilisateur n'est pas authentifié, rediriger vers la page de connexion
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  // Si l'utilisateur est authentifié, afficher le contenu protégé
  return <>{children}</>;
};

export default PrivateRoute; 