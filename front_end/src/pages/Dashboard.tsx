import React, { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthProvider';
import BookScrollSection from '../components/BookScrollSection';
import '../styles/dashboard.css';

interface Book {
  isbn: string;
  title: string;
  author: string;
  year: string;
  publisher: string;
  image_url_s: string;
  image_url_m: string;
  image_url_l: string;
  genre?: string;
  description?: string;
  similarity_score?: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [contentRecommendations, setContentRecommendations] = useState<Book[]>([]);
  const [collaborativeRecommendations, setCollaborativeRecommendations] = useState<Book[]>([]);
  const [contentLoading, setContentLoading] = useState(true);
  const [collaborativeLoading, setCollaborativeLoading] = useState(true);
  const [contentError, setContentError] = useState<string | null>(null);
  const [collaborativeError, setCollaborativeError] = useState<string | null>(null);

  const fetchContentRecommendations = async () => {
      try {
      setContentLoading(true);
      setContentError(null);
        
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
        const sessionId = localStorage.getItem('session_id');
        
        const headers: HeadersInit = {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        };
        
        // Ajouter l'ID de session si disponible
        if (sessionId) {
          headers['X-Session-ID'] = sessionId;
        }
        
        const response = await fetch(`${apiUrl}/books/recommendations`, {
          method: 'GET',
          headers: headers,
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
      setContentRecommendations(data);
        
      } catch (err) {
      console.error('Erreur détaillée (content-based):', err);
      setContentError(err instanceof Error ? err.message : 'Une erreur est survenue');
      } finally {
      setContentLoading(false);
      }
    };

  const fetchCollaborativeRecommendations = async () => {
    try {
      setCollaborativeLoading(true);
      setCollaborativeError(null);
      
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
      const sessionId = localStorage.getItem('session_id');
      
      if (!sessionId) {
        console.log('Pas de session, aucune recommandation collaborative');
        setCollaborativeRecommendations([]);
        return;
      }
      
      const headers: HeadersInit = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Session-ID': sessionId
      };
      
      const response = await fetch(`${apiUrl}/recommendations/collaborative`, {
        method: 'GET',
        headers: headers,
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      const data = await response.json();
      setCollaborativeRecommendations(data.recommendations || []);
      
    } catch (err) {
      console.error('Erreur détaillée (collaborative):', err);
      setCollaborativeError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setCollaborativeLoading(false);
    }
  };

  useEffect(() => {
    fetchContentRecommendations();
    fetchCollaborativeRecommendations();
  }, []);

  // Afficher le loading si l'une des deux sections est en cours de chargement
  if (contentLoading || collaborativeLoading) {
    return (
      <div className="dashboard">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Chargement des recommandations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Section Content-Based */}
      <div className="scroll-section">
        <h2 className="section-title">
          {user?.favorite_genres?.length || user?.favorite_authors?.length 
            ? "Recommandations basées sur vos préférences" 
            : "Sélection populaire"
          }
        </h2>
        
        {contentError ? (
          <div className="error-message">
            <h3>Erreur</h3>
            <p>{contentError}</p>
            <p className="error-help">
              Une erreur s'est produite lors du chargement des recommandations content-based.
            </p>
          </div>
        ) : contentRecommendations.length > 0 ? (
          <BookScrollSection 
            title={user?.favorite_genres?.length || user?.favorite_authors?.length 
              ? "Basé sur vos préférences" 
              : "Livres populaires"
            }
            books={contentRecommendations}
          />
        ) : (
          <div className="no-recommendations">
            <p>
              Aucune recommandation basée sur vos préférences disponible pour le moment.
            </p>
            <p className="recommendation-help">
              {!user?.favorite_genres?.length && !user?.favorite_authors?.length 
                ? "Ajoutez des genres et des auteurs que vous aimez dans votre profil pour obtenir des recommandations personnalisées."
                : "Nous travaillons à améliorer nos recommandations. Revenez bientôt !"
              }
            </p>
          </div>
        )}
      </div>

      {/* Section Collaborative Filtering */}
      <div className="scroll-section">
        <h2 className="section-title">
          Recommandations collaborative filtering
        </h2>
        
        {collaborativeError ? (
          <div className="error-message">
            <h3>Erreur</h3>
            <p>{collaborativeError}</p>
            <p className="error-help">
              Une erreur s'est produite lors du chargement des recommandations collaborative.
            </p>
          </div>
        ) : collaborativeRecommendations.length > 0 ? (
          <BookScrollSection 
            title="Basé sur les utilisateurs similaires"
            books={collaborativeRecommendations}
          />
        ) : (
          <div className="no-recommendations">
            <p>
              Aucune recommandation collaborative disponible pour le moment.
            </p>
            <p className="recommendation-help">
              Notez plus de livres pour obtenir des recommandations basées sur les utilisateurs similaires.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
