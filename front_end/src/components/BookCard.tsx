import * as React from 'react';
import { useState } from 'react';

export interface BookProps {
  isbn: string;
  title: string;
  author: string;
  year: string;
  publisher: string;
  image_url_s: string;
  image_url_m: string;
  image_url_l: string;
}

const BookCard: React.FC<BookProps> = ({ 
  isbn, 
  title, 
  author, 
  year, 
  publisher, 
  image_url_s,
  image_url_m,
  image_url_l 
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
      <div className="book-cover">
        <img 
          src={imageError ? placeholderImage : imageUrls[imageSizeIndex]} 
          alt={`Couverture de ${title}`} 
          onError={handleImageError}
        />
      </div>
      <div className="book-info">
        <h3>{title}</h3>
        <p className="author">par {author}</p>
        <p className="details">
          <span className="year">{year}</span>
          <span className="publisher">{publisher}</span>
        </p>
      </div>
    </div>
  );
};

export default BookCard;
  