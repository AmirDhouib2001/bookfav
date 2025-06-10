import * as React from 'react';
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { BookProps } from '../components/BookCard';
import '../styles/BookDetail.css';

const BookDetail: React.FC = () => {
  const { isbn } = useParams<{ isbn: string }>();
  const [book, setBook] = useState<BookProps | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [imageError, setImageError] = useState<boolean>(false);
  
  // Obtenir l'URL de l'API depuis les variables d'environnement
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
  
  // Image de remplacement en cas d'erreur
  const placeholderImage = 'https://via.placeholder.com/300x400?text=Pas+d%27image';

  useEffect(() => {
    const fetchBookDetails = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${apiUrl}/books/isbn/${isbn}`);
        
        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        setBook(data);
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
    </div>
  );
};

export default BookDetail; 