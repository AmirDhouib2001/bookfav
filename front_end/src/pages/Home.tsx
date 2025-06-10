import * as React from 'react';
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import '../styles/Home.css';
import { BookProps } from '../components/BookCard';

const Home: React.FC = () => {
  const [popularBooks, setPopularBooks] = useState<BookProps[]>([]);
  const [newReleases, setNewReleases] = useState<BookProps[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Obtenir l'URL de l'API depuis les variables d'environnement
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

  useEffect(() => {
    const fetchBooks = async () => {
      try {
        setLoading(true);
        // Récupérer les livres populaires
        const popularResponse = await fetch(`${apiUrl}/books/search?per_page=6`);
        if (!popularResponse.ok) {
          throw new Error(`Erreur HTTP: ${popularResponse.status}`);
        }
        const popularData = await popularResponse.json();
        setPopularBooks(popularData.books || []);

        // On réutilise les mêmes livres pour les nouvelles sorties dans cet exemple
        // Dans une vraie application, vous pourriez avoir un endpoint séparé
        setNewReleases(popularData.books || []);

        setLoading(false);
      } catch (err) {
        console.error('Erreur lors du chargement des livres:', err);
        setError('Impossible de charger les livres. Veuillez réessayer plus tard.');
        setLoading(false);
      }
    };

    fetchBooks();
  }, [apiUrl]);

  return (
    <div className="home-container">
      {/* Section Hero avec animation */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Bienvenue sur <span>BookFav</span> 📚
          </h1>
          <p className="hero-subtitle">
            Découvrez, organisez et partagez vos livres préférés. Une bibliothèque numérique adaptée à tous les lecteurs passionnés.
          </p>
          <div className="hero-buttons">
            <Link to="/catalogue" className="primary-btn">
              Découvrir le catalogue
            </Link>
            <Link to="/register" className="secondary-btn">
              Créer un compte
            </Link>
          </div>
        </div>
        <div className="hero-image">
          <img src="https://images.unsplash.com/photo-1507842217343-583bb7270b66?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80" alt="Livres sur une étagère" />
        </div>
      </section>

      {/* Section Fonctionnalités */}
      <section className="features-section">
        <h2 className="section-title">Nos fonctionnalités</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3 className="feature-title">Explorez</h3>
            <p className="feature-desc">
              Parcourez notre vaste catalogue de livres dans tous les genres et découvrez de nouveaux titres.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⭐</div>
            <h3 className="feature-title">Notez</h3>
            <p className="feature-desc">
              Donnez votre avis et attribuez des notes à vos lectures pour les recommander à d'autres.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3 className="feature-title">Organisez</h3>
            <p className="feature-desc">
              Créez des listes personnalisées et gardez une trace de vos livres lus, à lire ou favoris.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🌍</div>
            <h3 className="feature-title">Partagez</h3>
            <p className="feature-desc">
              Partagez vos collections et découvertes avec la communauté de lecteurs.
            </p>
          </div>
        </div>
      </section>

      {/* Section Livres populaires */}
      <section className="books-section">
        <h2 className="section-title">Livres populaires</h2>
        {loading ? (
          <div className="loading-books">Chargement des livres populaires...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : (
          <div className="books-carousel">
            {popularBooks.map((book) => (
              <div key={book.isbn} className="carousel-book">
                <Link to={`/book/${book.isbn}`} className="book-cover-link">
                  <img 
                    src={book.image_url_m || book.image_url_s} 
                    alt={`Couverture de ${book.title}`} 
                    className="book-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = 'https://via.placeholder.com/150x200?text=Pas+d%27image';
                    }}
                  />
                  <div className="book-hover-info">
                    <h4>{book.title}</h4>
                    <p>{book.author}</p>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        )}
        <div className="view-all">
          <Link to="/catalogue" className="view-all-link">
            Voir tous les livres →
          </Link>
        </div>
      </section>

      {/* Section Actualités et événements */}
      <section className="news-section">
        <h2 className="section-title">Actualités littéraires</h2>
        <div className="news-grid">
          <article className="news-card">
            <div className="news-image">
              <img src="https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80" alt="Événement littéraire" />
            </div>
            <div className="news-content">
              <h3>Prix littéraires 2023</h3>
              <p className="news-date">15 juin 2023</p>
              <p className="news-excerpt">
                Découvrez les lauréats des grands prix littéraires de l'année et plongez dans leurs œuvres captivantes.
              </p>
              <a href="#" className="read-more">Lire plus</a>
            </div>
          </article>

          <article className="news-card">
            <div className="news-image">
              <img src="https://images.unsplash.com/photo-1490633874781-1c63cc424610?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80" alt="Club de lecture" />
            </div>
            <div className="news-content">
              <h3>Club de lecture en ligne</h3>
              <p className="news-date">3 juin 2023</p>
              <p className="news-excerpt">
                Rejoignez notre club de lecture virtuel et échangez avec d'autres passionnés sur les romans du moment.
              </p>
              <a href="#" className="read-more">Lire plus</a>
            </div>
          </article>
        </div>
      </section>

      {/* Call to Action */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Rejoignez notre communauté de lecteurs</h2>
          <p>Créez un compte gratuitement et commencez à organiser votre bibliothèque virtuelle dès aujourd'hui.</p>
          <Link to="/register" className="cta-button">
            S'inscrire maintenant
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
  