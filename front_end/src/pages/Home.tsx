import * as React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import '../styles/Home.css';

const Home: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="home-container">
      <section className="hero-section">
        <div className="hero-content">
        <h1 className="hero-title">
            Bienvenue {isAuthenticated && user ? `${user.username}` : ''} sur <span>BookFav</span>
        </h1>
        <p className="hero-subtitle">
            Votre bibliothèque personnelle dans le cloud. Découvrez, organisez et partagez vos lectures préférées.
          </p>
          {isAuthenticated ? (
            <div className="hero-buttons">
              <Link to="/catalogue" className="primary-btn">
                Explorer le catalogue
              </Link>
              <Link to="/profile" className="secondary-btn">
                Mon profil
              </Link>
            </div>
          ) : (
            <div className="hero-buttons">
              <Link to="/catalogue" className="primary-btn">
                Explorer le catalogue
              </Link>
              <Link to="/login" className="secondary-btn">
                Se connecter
        </Link>
            </div>
          )}
        </div>
        <div className="hero-image">
          <div className="book-stack">
            <div className="book book-1"></div>
            <div className="book book-2"></div>
            <div className="book book-3"></div>
          </div>
        </div>
      </section>

      <section className="features-section">
        <h2 className="section-title">Pourquoi choisir BookFav ?</h2>
        <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">🔍</div>
            <h3 className="feature-title">Recherche avancée</h3>
            <p className="feature-desc">
              Trouvez facilement des livres par titre, auteur, genre ou description grâce à notre moteur de recherche puissant.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3 className="feature-title">Bibliothèque personnalisée</h3>
          <p className="feature-desc">
              Créez votre collection personnelle et organisez vos lectures selon vos préférences.
          </p>
        </div>

        <div className="feature-card">
            <div className="feature-icon">💬</div>
            <h3 className="feature-title">Détails complets</h3>
          <p className="feature-desc">
              Accédez à des informations détaillées sur chaque livre, incluant les descriptions, genres et plus encore.
          </p>
        </div>

        <div className="feature-card">
            <div className="feature-icon">⭐</div>
            <h3 className="feature-title">Recommandations</h3>
          <p className="feature-desc">
              Recevez des suggestions de lectures basées sur vos genres préférés et vos habitudes de lecture.
            </p>
          </div>
        </div>
      </section>

      <section className="popular-section">
        <h2 className="section-title">Comment ça fonctionne</h2>
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h3 className="step-title">Créez un compte</h3>
            <p className="step-desc">Inscrivez-vous gratuitement et configurez votre profil personnel.</p>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <h3 className="step-title">Explorez le catalogue</h3>
            <p className="step-desc">Parcourez notre vaste collection de livres dans tous les genres.</p>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <h3 className="step-title">Marquez vos favoris</h3>
            <p className="step-desc">Ajoutez des livres à votre collection personnelle et notez-les.</p>
          </div>
          <div className="step">
            <div className="step-number">4</div>
            <h3 className="step-title">Recevez des recommandations</h3>
            <p className="step-desc">Découvrez de nouveaux livres adaptés à vos préférences de lecture.</p>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <h2 className="cta-title">Prêt à commencer votre voyage littéraire ?</h2>
        <p className="cta-subtitle">Rejoignez notre communauté de passionnés de lecture dès aujourd'hui.</p>
        {isAuthenticated ? (
          <Link to="/catalogue" className="cta-button">
            Explorer le catalogue
          </Link>
        ) : (
          <Link to="/register" className="cta-button">
            S'inscrire gratuitement
          </Link>
        )}
      </section>
    </div>
  );
};

export default Home;
  