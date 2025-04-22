import * as React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Home.css';

const Home: React.FC = () => {
  return (
    <div className="home-container">
      <section className="hero-section">
        <h1 className="hero-title">
          Bienvenue sur <span>BookFav</span> 📚
        </h1>
        <p className="hero-subtitle">
          Découvrez, organisez et partagez vos livres préférés. Une bibliothèque numérique adaptée à tous les lecteurs passionnés.
        </p>
        <Link to="/catalogue" className="get-started-btn">
          Découvrir le catalogue
        </Link>
      </section>

      <section className="features-section">
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
      </section>
    </div>
  );
};

export default Home;
  