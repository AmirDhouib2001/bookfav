import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthProvider';
import '../styles/StarRating.css';

interface StarRatingProps {
  isbn: string;
  readonly?: boolean;
  initialRating?: number;
  onRatingChange?: (rating: number, review?: string) => void;
  showReviewInput?: boolean;
  size?: 'small' | 'medium' | 'large';
}

interface RatingData {
  id: number;
  rating: number;
  review?: string;
}

const StarRating: React.FC<StarRatingProps> = ({
  isbn,
  readonly = false,
  initialRating = 0,
  onRatingChange,
  showReviewInput = false,
  size = 'medium'
}) => {
  const [rating, setRating] = useState<number>(initialRating);
  const [hoverRating, setHoverRating] = useState<number>(0);
  const [review, setReview] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [userRating, setUserRating] = useState<RatingData | null>(null);
  const [showReviewModal, setShowReviewModal] = useState<boolean>(false);
  const { user, sessionId } = useAuth();

  useEffect(() => {
    if (user && sessionId && !readonly) {
      fetchUserRating();
    }
  }, [isbn, user, sessionId]);

  const fetchUserRating = async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/ratings/user/book/${isbn}`, {
        headers: {
          'X-Session-ID': sessionId || '',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.has_rating) {
          setUserRating(data.rating);
          setRating(data.rating.rating);
          setReview(data.rating.review || '');
        }
      }
    } catch (error) {
      console.error('Erreur lors de la récupération de la note utilisateur:', error);
    }
  };

  const handleStarClick = (starRating: number) => {
    if (readonly || !user) return;
    
    if (starRating === rating) {
      // Si on clique sur la même étoile, on peut la désélectionner
      setRating(0);
    } else {
      setRating(starRating);
    }

    if (showReviewInput) {
      setShowReviewModal(true);
    } else {
      submitRating(starRating, '');
    }
  };

  const submitRating = async (newRating: number, newReview: string = '') => {
    console.log('=== DÉBUT submitRating ===');
    console.log('Paramètres reçus:', { newRating, newReview, isbn });
    console.log('État actuel:', { user, sessionId, isSubmitting });

    if (!user || !sessionId) {
      console.error('❌ Utilisateur non connecté ou session manquante:', { user: !!user, sessionId: !!sessionId });
      alert('Vous devez être connecté pour noter un livre');
      return;
    }

    if (newRating < 1 || newRating > 5) {
      console.error('❌ Note invalide:', newRating);
      alert('La note doit être entre 1 et 5 étoiles');
      return;
    }

    console.log('✅ Validation OK, début de la soumission...');
    setIsSubmitting(true);
    
    try {
      const requestBody = {
        isbn,
        rating: newRating,
        review: newReview
      };
      
      console.log('📤 Envoi de la requête:', {
        url: 'http://localhost:5001/api/ratings/rate',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: requestBody
      });

      const response = await fetch('http://localhost:5001/api/ratings/rate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify(requestBody)
      });

      console.log('📥 Réponse reçue:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries())
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Succès - Données reçues:', data);
        
        setUserRating(data.rating);
        if (onRatingChange) {
          console.log('🔄 Appel de onRatingChange');
          onRatingChange(newRating, newReview);
        }
        
        console.log('🚪 Fermeture de la modal');
        setShowReviewModal(false);
      } else {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          errorData = { error: 'Erreur inconnue du serveur' };
        }
        console.error('❌ Erreur du serveur:', { status: response.status, data: errorData });
        alert(`Erreur du serveur: ${errorData.error || 'Erreur inconnue'}`);
        setShowReviewModal(false);
      }
    } catch (error) {
      console.error('❌ Erreur réseau ou autre:', error);
      alert(`Erreur de connexion: ${error.message || 'Erreur inconnue'}`);
      setShowReviewModal(false);
    } finally {
      console.log('🏁 Fin de submitRating, setIsSubmitting(false)');
      setIsSubmitting(false);
    }
    
    console.log('=== FIN submitRating ===');
  };

  const handleReviewSubmit = () => {
    console.log('handleReviewSubmit appelé avec:', { rating, review, isbn, user, sessionId });
    if (rating === 0) {
      alert('Veuillez sélectionner une note avant d\'envoyer');
      return;
    }
    submitRating(rating, review);
  };

  const handleModalOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      setShowReviewModal(false);
    }
  };

  const renderStars = () => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      const isFilled = i <= (hoverRating || rating);
      stars.push(
        <span
          key={i}
          className={`star ${size} ${isFilled ? 'filled' : 'empty'} ${!readonly && user ? 'interactive' : ''}`}
          onClick={() => handleStarClick(i)}
          onMouseEnter={() => !readonly && user && setHoverRating(i)}
          onMouseLeave={() => !readonly && user && setHoverRating(0)}
          title={!readonly && user ? `Noter ${i} étoile${i > 1 ? 's' : ''}` : ''}
        >
          ★
        </span>
      );
    }
    return stars;
  };

  return (
    <div className="star-rating-container">
      <div className="star-rating">
        <div className="stars-container">
          {renderStars()}
        </div>
        {!readonly && user && (
          <span className="rating-text">
            {hoverRating ? `${hoverRating}/5` : rating ? `${rating}/5` : 'Noter ce livre'}
          </span>
        )}
        {!user && !readonly && (
          <span className="rating-text">Connectez-vous pour noter</span>
        )}
      </div>

      {userRating && userRating.review && (
        <div className="user-review">
          <p><strong>Votre commentaire:</strong> {userRating.review}</p>
        </div>
      )}

      {/* Modal pour ajouter un commentaire */}
      {showReviewModal && (
        <div className="review-modal-overlay" onClick={handleModalOverlayClick}>
          <div className="review-modal">
            <h3>Noter ce livre ({rating}/5)</h3>
            <div className="modal-stars">
              {renderStars()}
            </div>
            <textarea
              value={review}
              onChange={(e) => setReview(e.target.value)}
              placeholder="Ajoutez un commentaire (optionnel)..."
              rows={4}
              className="review-textarea"
            />
            <div className="modal-buttons">
              <button
                type="button"
                onClick={(e) => {
                  console.log('🔘 Clic sur le bouton Envoyer détecté');
                  e.preventDefault();
                  e.stopPropagation();
                  handleReviewSubmit();
                }}
                disabled={isSubmitting || rating === 0}
                className="submit-btn"
              >
                {isSubmitting ? 'Envoi...' : 'Envoyer la note'}
              </button>
              <button
                type="button"
                onClick={(e) => {
                  console.log('🔘 Clic sur le bouton Annuler détecté');
                  e.preventDefault();
                  e.stopPropagation();
                  setShowReviewModal(false);
                }}
                className="cancel-btn"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StarRating; 