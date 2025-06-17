import * as React from 'react';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import StarRating from './StarRating';

export interface BookProps {
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
  rating_stats?: {
    total_ratings: number;
    average_rating: number;
  };
}

const BookCard: React.FC<BookProps> = ({ 
  isbn, 
  title, 
  author, 
  year, 
  publisher, 
  image_url_s,
  image_url_m,
  image_url_l,
  genre,
  description,
  rating_stats
}) => {
  const [imageError, setImageError] = useState(false);
  const [imageSizeIndex, setImageSizeIndex] = useState(1); // 0=S, 1=M, 2=L
  
  // Tableau des URLs d'images dans l'ordre des tailles
  const imageUrls = [image_url_s, image_url_m, image_url_l];
  
  // Image de remplacement en cas d'erreur
  const placeholderImage = 'https://via.placeholder.com/150x200?text=Pas+d%27image';
  
  // Gérer les erreurs de chargement d'image en essayant différentes tailles
  const handleImageError = () => {
    if (imageSizeIndex < imageUrls.length - 1) {
      // Essayer la taille suivante
      setImageSizeIndex(imageSizeIndex + 1);
    } else {
      // Si toutes les tailles ont échoué, utiliser l'image de remplacement
      setImageError(true);
    }
  };
  
  return (
    <div className="book-card">
      <Link to={`/book/${isbn}`} className="book-link">
        <div className="book-cover">
          <img 
            src={imageError ? placeholderImage : imageUrls[imageSizeIndex]} 
            alt={`Couverture de ${title}`} 
            onError={handleImageError}
          />
        </div>
        <div className="book-info">
          <h4>{title}</h4>
          <p className="author">{author}</p>
          {genre && <span className="genre">{genre}</span>}
          <p className="year">{year}</p>
          <p className="publisher">{publisher}</p>
          
          {/* Affichage de la note moyenne si disponible */}
          {rating_stats && rating_stats.total_ratings > 0 && (
            <div className="book-rating-info">
              <StarRating 
                isbn={isbn}
                readonly={true}
                initialRating={Math.round(rating_stats.average_rating)}
                size="small"
              />
              <span className="rating-count">
                ({rating_stats.total_ratings} avis)
              </span>
            </div>
          )}
        </div>
      </Link>
      
      {/* Section interactive de notation (en dehors du Link) */}
      <div className="book-rating-section">
        <StarRating 
          isbn={isbn}
          showReviewInput={true}
          size="small"
        />
      </div>
    </div>
  );
};

export default BookCard;
  