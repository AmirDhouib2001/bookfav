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
  genre?: string;
  description?: string;
}

interface SearchFilters {
  q: string;
  title: string;
  author: string;
  genre: string;
  description: string;
}

const Catalogue: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [genres, setGenres] = useState<string[]>([]);
  const [filters, setFilters] = useState<SearchFilters>({
    q: '',
    title: '',
    author: '',
    genre: '',
    description: ''
  });

  // Obtenir l'URL de l'API depuis les variables d'environnement ou utiliser une valeur par défaut
  const configuredApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
  
  // URLs de secours à essayer en cas d'échec
  const fallbackUrls = [
    configuredApiUrl,
    'http://localhost:5001/api',
    'http://127.0.0.1:5001/api'
  ];

  // Fonction pour construire l'URL avec les filtres
  const buildUrl = (baseUrl: string, page: number, filters: SearchFilters) => {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('per_page', '12');
    
    if (filters.q) params.append('q', filters.q);
    if (filters.title) params.append('title', filters.title);
    if (filters.author) params.append('author', filters.author);
    if (filters.genre) params.append('genre', filters.genre);
    if (filters.description) params.append('description', filters.description);
    
    return `${baseUrl}/books/search?${params.toString()}`;
  };

  // Fonction pour récupérer les livres
  const fetchBooks = async (page: number, useFilters = false) => {
    setLoading(true);
    let successfulFetch = false;
    let lastError = null;
    
    // Essayer chaque URL jusqu'à ce qu'une fonctionne
    for (const apiUrl of fallbackUrls) {
      if (successfulFetch) break;
      
      try {
        // Déterminer l'URL en fonction de si des filtres sont utilisés
        const url = useFilters 
          ? buildUrl(apiUrl, page, filters)
          : `${apiUrl}/books?page=${page}&per_page=12`;
        
        console.log(`Tentative de récupération des livres depuis: ${url}`);
        
        const response = await fetch(url);
        console.log(`Statut de la réponse (${url}):`, response.status);
        
        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`Données reçues de ${url}:`, data);
        
        if (data.books && Array.isArray(data.books)) {
          setBooks(data.books);
          setTotalPages(data.pages || 1);
          setError(null);
          successfulFetch = true;
          console.log(`✅ Connexion réussie à ${apiUrl}`);
        } else if (data.error) {
          console.error(`Erreur reçue du serveur (${url}):`, data.error);
          lastError = `Erreur du serveur: ${data.error}`;
        } else {
          console.error(`Format de données incorrect (${url}):`, data);
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

  // Charger les genres disponibles
  const fetchGenres = async () => {
    try {
      for (const apiUrl of fallbackUrls) {
        try {
          const response = await fetch(`${apiUrl}/books/genres`);
          if (response.ok) {
            const data = await response.json();
            if (Array.isArray(data)) {
              setGenres(data);
              break;
            }
          }
        } catch (err) {
          console.error(`Erreur lors du chargement des genres depuis ${apiUrl}:`, err);
        }
      }
    } catch (err) {
      console.error("Erreur lors du chargement des genres:", err);
    }
  };

  // Effet initial pour charger les livres et les genres
  useEffect(() => {
    fetchBooks(currentPage);
    fetchGenres();
  }, []);

  // Effet pour recharger les livres lorsque la page change
  useEffect(() => {
    // Si des filtres sont actifs, utiliser la recherche avancée
    const hasActiveFilters = Object.values(filters).some(value => value !== '');
    fetchBooks(currentPage, hasActiveFilters);
  }, [currentPage]);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  // Gérer les changements dans les filtres
  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Appliquer les filtres de recherche
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1); // Réinitialiser à la première page lors d'une nouvelle recherche
    fetchBooks(1, true);
  };

  // Réinitialiser les filtres
  const handleReset = () => {
    setFilters({
      q: '',
      title: '',
      author: '',
      genre: '',
      description: ''
    });
    setCurrentPage(1);
    fetchBooks(1, false);
  };

  return (
    <div className="catalogue-container">
      <h1>Catalogue de livres</h1>
      
      <div className="search-section">
        <div className="search-controls">
          <button 
            className="toggle-filters-btn" 
            onClick={() => setShowFilters(!showFilters)}
          >
            {showFilters ? 'Masquer les filtres' : 'Afficher les filtres avancés'}
          </button>
          
          <div className="quick-search">
            <input 
              type="text" 
              name="q" 
              value={filters.q} 
              onChange={handleFilterChange}
              placeholder="Recherche rapide..."
            />
            <button onClick={handleSearch}>Rechercher</button>
          </div>
        </div>
        
        {showFilters && (
          <form className="advanced-search-form" onSubmit={handleSearch}>
            <div className="filters-grid">
              <div className="filter-group">
                <label htmlFor="title">Titre</label>
                <input 
                  type="text" 
                  id="title" 
                  name="title" 
                  value={filters.title} 
                  onChange={handleFilterChange}
                  placeholder="Recherche par titre"
                />
              </div>
              
              <div className="filter-group">
                <label htmlFor="author">Auteur</label>
                <input 
                  type="text" 
                  id="author" 
                  name="author" 
                  value={filters.author} 
                  onChange={handleFilterChange}
                  placeholder="Recherche par auteur"
                />
              </div>
              
              <div className="filter-group">
                <label htmlFor="genre">Genre</label>
                <select 
                  id="genre" 
                  name="genre" 
                  value={filters.genre} 
                  onChange={handleFilterChange}
                >
                  <option value="">Tous les genres</option>
                  {genres.map(genre => (
                    <option key={genre} value={genre}>{genre}</option>
                  ))}
                </select>
              </div>
              
              <div className="filter-group">
                <label htmlFor="description">Description</label>
                <input 
                  type="text" 
                  id="description" 
                  name="description" 
                  value={filters.description} 
                  onChange={handleFilterChange}
                  placeholder="Mots dans la description"
                />
              </div>
            </div>
            
            <div className="filter-actions">
              <button type="submit" className="apply-filters-btn">Appliquer les filtres</button>
              <button type="button" className="reset-filters-btn" onClick={handleReset}>Réinitialiser</button>
            </div>
          </form>
        )}
      </div>
      
      {loading ? (
        <div className="loading">Chargement des livres...</div>
      ) : error ? (
        <div className="error">{error} <pre>Vérifiez la console pour plus de détails.</pre></div>
      ) : books.length === 0 ? (
        <div className="no-books">Aucun livre ne correspond à votre recherche.</div>
      ) : (
        <>
          <div className="search-results-info">
            {filters.q || filters.title || filters.author || filters.genre || filters.description ? (
              <p>Résultats de la recherche : {books.length} livre(s) trouvé(s) sur un total de {totalPages * 12}</p>
            ) : null}
          </div>
          
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
                genre={book.genre}
                description={book.description}
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
        </>
      )}
    </div>
  );
};

export default Catalogue;
  