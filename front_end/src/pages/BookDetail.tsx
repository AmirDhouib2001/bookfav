import * as React from 'react';
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { BookProps } from '../components/BookCard';
import StarRating from '../components/StarRating';
import '../styles/BookDetail.css';

interface BookRatingStats {
  isbn: string;
  book_title: string;
  stats: {
    total_ratings: number;
    average_rating: number;
    five_stars: number;
    four_stars: number;
    three_stars: number;
    two_stars: number;
    one_star: number;
  };
  recent_reviews: Array<{
    id: number;
    rating: number;
    review: string;
    created_at: string;
    user: {
      username: string;
      full_name: string;
    };
  }>;
}

const BookDetail: React.FC = () => {
  const { isbn } = useParams<{ isbn: string }>();
  const [book, setBook] = useState<BookProps | null>(null);
  const [ratingStats, setRatingStats] = useState<BookRatingStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [imageError, setImageError] = useState<boolean>(false);
  
  // Obtenir l'URL de l'API depuis les variables d'environnement
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
  
  // Image de remplacement en cas d'erreur
  const placeholderImage = 'https://via.placeholder.com/300x400?text=Pas+d%27image';

  useEffect(() => {
    const fetchBookDetails = async () => {
      try {
        setLoading(true);
        
        // Récupérer les détails du livre
        const bookResponse = await fetch(`${apiUrl}/books/isbn/${isbn}`);
        if (!bookResponse.ok) {
          throw new Error(`Erreur HTTP: ${bookResponse.status}`);
        }
        const bookData = await bookResponse.json();
        setBook(bookData);
        
        // Récupérer les statistiques de notation
        try {
          const ratingsResponse = await fetch(`${apiUrl}/ratings/book/${isbn}`);
          if (ratingsResponse.ok) {
            const ratingsData = await ratingsResponse.json();
            setRatingStats(ratingsData);
          }
        } catch (ratingsError) {
          console.log('Pas de données de notation disponibles:', ratingsError);
        }
        
      } catch (err) {
        setError(`Erreur lors du chargement des détails du livre: ${err}`);
        console.error('Erreur:', err);
      } finally {
        setLoading(false);
      }
    };
    
    if (isbn) {
      fetchBookDetails();
    }
  }, [isbn, apiUrl]);

  const handleRatingChange = () => {
    // Recharger les statistiques après qu'un utilisateur ait noté
    if (isbn) {
      fetch(`${apiUrl}/ratings/book/${isbn}`)
        .then(response => response.json())
        .then(data => setRatingStats(data))
        .catch(error => console.log('Erreur lors du rechargement des stats:', error));
    }
  };

  const renderRatingDistribution = () => {
    if (!ratingStats || ratingStats.stats.total_ratings === 0) return null;

    const { stats } = ratingStats;
    const total = stats.total_ratings;

    return (
      <div className="rating-distribution">
        <h3>Répartition des notes</h3>
        {[5, 4, 3, 2, 1].map(star => {
          const count = stats[`${star === 1 ? 'one' : star === 2 ? 'two' : star === 3 ? 'three' : star === 4 ? 'four' : 'five'}_star${star !== 1 ? 's' : ''}`];
          const percentage = total > 0 ? (count / total) * 100 : 0;
          
          return (
            <div key={star} className="rating-bar">
              <span className="star-label">{star} ⭐</span>
              <div className="bar-container">
                <div 
                  className="bar-fill" 
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
              <span className="rating-count">({count})</span>
            </div>
          );
        })}
      </div>
    );
  };

  if (loading) return <div className="loading">Chargement des détails du livre...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!book) return <div className="not-found">Livre non trouvé</div>;

  return (
    <div className="book-detail-container">
      <div className="book-detail-header">
        <Link to="/catalogue" className="back-link">← Retour au catalogue</Link>
        <h1>{book.title}</h1>
      </div>
      
      <div className="book-detail-content">
        <div className="book-detail-cover">
          <img 
            src={imageError ? placeholderImage : book.image_url_l || book.image_url_m || book.image_url_s} 
            alt={`Couverture de ${book.title}`} 
            onError={() => setImageError(true)}
          />
        </div>
        
        <div className="book-detail-info">
          <p className="author"><strong>Auteur:</strong> {book.author}</p>
          <p className="publisher"><strong>Éditeur:</strong> {book.publisher}</p>
          <p className="year"><strong>Année de publication:</strong> {book.year}</p>
          {book.genre && <p className="genre"><strong>Genre:</strong> {book.genre}</p>}
          <p className="isbn"><strong>ISBN:</strong> {book.isbn}</p>
          
          {/* Section de notation */}
          <div className="book-rating-section">
            <h3>Noter ce livre</h3>
            <StarRating 
              isbn={book.isbn}
              showReviewInput={true}
              size="large"
              onRatingChange={handleRatingChange}
            />
          </div>
          
          {/* Statistiques de notation */}
          {ratingStats && ratingStats.stats.total_ratings > 0 && (
            <div className="rating-stats-section">
              <h3>Notes et avis</h3>
              <div className="rating-overview">
                <div className="average-rating">
                  <span className="rating-number">{ratingStats.stats.average_rating.toFixed(1)}</span>
                  <div className="rating-stars">
                    <StarRating 
                      isbn={book.isbn}
                      readonly={true}
                      initialRating={Math.round(ratingStats.stats.average_rating)}
                      size="medium"
                    />
                  </div>
                  <span className="total-ratings">
                    Basé sur {ratingStats.stats.total_ratings} avis
                  </span>
                </div>
                {renderRatingDistribution()}
              </div>
            </div>
          )}
          
          {book.description && (
            <div className="description">
              <h3>Description:</h3>
              <p>{book.description}</p>
            </div>
          )}
          
          {!book.description && (
            <div className="no-description">
              <p>Aucune description disponible pour ce livre.</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Section des commentaires récents */}
      {ratingStats && ratingStats.recent_reviews.length > 0 && (
        <div className="recent-reviews-section">
          <h3>Commentaires récents</h3>
          <div className="reviews-list">
            {ratingStats.recent_reviews.map(review => (
              <div key={review.id} className="review-item">
                <div className="review-header">
                  <div className="reviewer-info">
                    <strong>{review.user.full_name || review.user.username}</strong>
                    <StarRating 
                      isbn={book.isbn}
                      readonly={true}
                      initialRating={review.rating}
                      size="small"
                    />
                  </div>
                  <span className="review-date">
                    {new Date(review.created_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>
                <p className="review-text">{review.review}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default BookDetail; 