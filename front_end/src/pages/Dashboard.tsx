import React, { useState, useEffect } from 'react';
import { useAuth } from '../components/AuthProvider';
import BookScrollSection from '../components/BookScrollSection';
import '../styles/dashboard.css';
import BookFavIntro from '../components/BookFavIntro';

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
  const [recommendations, setRecommendations] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);
        
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
        setRecommendations(data);
        
      } catch (err) {
        console.error('Erreur détaillée:', err);
        setError(err instanceof Error ? err.message : 'Une erreur est survenue');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Chargement des recommandations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="error-message">
          <h3>Erreur</h3>
          <p>{error}</p>
          <p className="error-help">
            Une erreur s'est produite lors du chargement des recommandations. Veuillez réessayer plus tard.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <BookFavIntro />
      
      <div className="scroll-section">
        <h2 className="section-title">
          {user?.favorite_genres?.length || user?.favorite_authors?.length 
            ? "Recommandations personnalisées" 
            : "Sélection populaire"
          }
        </h2>
        {recommendations.length > 0 ? (
          <BookScrollSection 
            title={user?.favorite_genres?.length || user?.favorite_authors?.length 
              ? "Basé sur vos préférences" 
              : "Livres populaires"
            }
            books={recommendations}
          />
        ) : (
          <div className="no-recommendations">
            <p>
              Aucune recommandation disponible pour le moment.
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
    </div>
  );
};

export default Dashboard;
