import * as React from 'react';
import { useState, useEffect } from 'react';
import BookCard, { BookProps } from '../components/BookCard';
import '../styles/Catalogue.css';

interface Book {
  isbn: string;
  title: string;
  author: string;
  year: string;
  publisher: string;
  image_url_s: string;
  image_url_m: string;
  image_url_l: string;
}

const Catalogue: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Obtenir l'URL de l'API depuis les variables d'environnement ou utiliser une valeur par défaut
  const configuredApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
  
  // URLs de secours à essayer en cas d'échec
  const fallbackUrls = [
    configuredApiUrl,
    'http://localhost:5001/api',
    'http://127.0.0.1:5001/api'
  ];

  useEffect(() => {
    const fetchBooksWithFallback = async () => {
      setLoading(true);
      let successfulFetch = false;
      let lastError = null;
      
      // Essayer chaque URL jusqu'à ce qu'une fonctionne
      for (const apiUrl of fallbackUrls) {
        if (successfulFetch) break;
        
        try {
          console.log(`Tentative de récupération des livres depuis: ${apiUrl}/books?page=${currentPage}&per_page=12`);
          
          const response = await fetch(`${apiUrl}/books?page=${currentPage}&per_page=12`);
          console.log(`Statut de la réponse (${apiUrl}):`, response.status);
          
          if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
          }
          
          const data = await response.json();
          console.log(`Données reçues de ${apiUrl}:`, data);
          
          if (data.books && Array.isArray(data.books)) {
            setBooks(data.books);
            setTotalPages(data.pages || 1);
            setError(null);
            successfulFetch = true;
            console.log(`✅ Connexion réussie à ${apiUrl}`);
          } else if (data.error) {
            console.error(`Erreur reçue du serveur (${apiUrl}):`, data.error);
            lastError = `Erreur du serveur: ${data.error}`;
          } else {
            console.error(`Format de données incorrect (${apiUrl}):`, data);
            lastError = "Format de données incorrect reçu du serveur";
          }
        } catch (err) {
          console.error(`Erreur lors du chargement des livres depuis ${apiUrl}:`, err);
          lastError = `Impossible de se connecter à ${apiUrl}`;
        }
      }
      
      if (!successfulFetch) {
        setError(`Impossible de charger les livres. ${lastError}`);
      }
      
      setLoading(false);
    };

    fetchBooksWithFallback();
  }, [currentPage]);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  if (loading) return <div className="loading">Chargement des livres...</div>;
  if (error) return <div className="error">{error} <pre>Vérifiez la console pour plus de détails.</pre></div>;
  if (books.length === 0) return <div className="no-books">Aucun livre disponible pour le moment.</div>;

  return (
    <div className="catalogue-container">
      <h1>Catalogue de livres</h1>
      
      <div className="books-grid">
        {books.map((book: Book) => (
          <BookCard
            key={book.isbn}
            isbn={book.isbn}
            title={book.title}
            author={book.author}
            year={book.year}
            publisher={book.publisher}
            image_url_s={book.image_url_s}
            image_url_m={book.image_url_m}
            image_url_l={book.image_url_l}
          />
        ))}
      </div>
      
      {totalPages > 1 && (
        <div className="pagination">
          <button 
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Précédent
          </button>
          
          <span>Page {currentPage} sur {totalPages}</span>
          
          <button 
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Suivant
          </button>
        </div>
      )}
    </div>
  );
};

export default Catalogue;
  