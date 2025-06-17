import * as React from 'react';
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import '../styles/Auth.css';

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  full_name?: string;
  favorite_genres?: string[];
  favorite_authors?: string[];
}

interface RegisterError {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

const Register: React.FC = () => {
  const { login } = useAuth();
  const [formData, setFormData] = useState<RegisterFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    favorite_genres: [],
    favorite_authors: []
  });
  const [errors, setErrors] = useState<RegisterError>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [genres, setGenres] = useState<string[]>([]);
  const [authors, setAuthors] = useState<string[]>([]);
  const [filteredGenres, setFilteredGenres] = useState<string[]>([]);
  const [filteredAuthors, setFilteredAuthors] = useState<string[]>([]);
  const [genreSearch, setGenreSearch] = useState<string>('');
  const [authorSearch, setAuthorSearch] = useState<string>('');
  const [showGenres, setShowGenres] = useState<boolean>(false);
  const [showAuthors, setShowAuthors] = useState<boolean>(false);
  const navigate = useNavigate();

  // Récupérer la liste des genres disponibles
  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
        const response = await fetch(`${apiUrl}/books/genres`);
        if (response.ok) {
          const data = await response.json();
          if (Array.isArray(data)) {
            setGenres(data);
            setFilteredGenres(data);
          }
        }
      } catch (error) {
        console.error("Erreur lors de la récupération des genres:", error);
      }
    };
    
    fetchGenres();
  }, []);

  // Récupérer la liste des auteurs disponibles
  useEffect(() => {
    const fetchAuthors = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
        const response = await fetch(`${apiUrl}/books/authors`);
        if (response.ok) {
          const data = await response.json();
          if (Array.isArray(data)) {
            setAuthors(data);
            setFilteredAuthors(data);
          }
        }
      } catch (error) {
        console.error("Erreur lors de la récupération des auteurs:", error);
      }
    };
    
    fetchAuthors();
  }, []);

  // Filtrer les genres en fonction de la recherche
  useEffect(() => {
    if (!genreSearch.trim()) {
      setFilteredGenres(genres);
    } else {
      const filtered = genres.filter(genre => 
        genre.toLowerCase().includes(genreSearch.toLowerCase())
      );
      setFilteredGenres(filtered);
    }
  }, [genreSearch, genres]);

  // Filtrer les auteurs en fonction de la recherche
  useEffect(() => {
    if (!authorSearch.trim()) {
      setFilteredAuthors(authors);
    } else {
      const filtered = authors.filter(author => 
        author.toLowerCase().includes(authorSearch.toLowerCase())
      );
      setFilteredAuthors(filtered);
    }
  }, [authorSearch, authors]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Effacer l'erreur lorsque l'utilisateur commence à taper
    if (errors[name as keyof RegisterError]) {
      setErrors({
        ...errors,
        [name]: undefined
      });
    }
  };

  const handleGenreSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setGenreSearch(e.target.value);
  };

  const handleAuthorSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAuthorSearch(e.target.value);
  };

  const handleGenreChange = (genre: string) => {
    const currentGenres = [...(formData.favorite_genres || [])];
    const genreIndex = currentGenres.indexOf(genre);
    
    if (genreIndex === -1) {
      // Ajouter le genre s'il n'est pas déjà sélectionné
      currentGenres.push(genre);
    } else {
      // Retirer le genre s'il est déjà sélectionné
      currentGenres.splice(genreIndex, 1);
    }
    
    setFormData({
      ...formData,
      favorite_genres: currentGenres
    });
  };

  const handleAuthorChange = (author: string) => {
    const currentAuthors = [...(formData.favorite_authors || [])];
    const authorIndex = currentAuthors.indexOf(author);
    
    if (authorIndex === -1) {
      // Ajouter l'auteur s'il n'est pas déjà sélectionné
      currentAuthors.push(author);
    } else {
      // Retirer l'auteur s'il est déjà sélectionné
      currentAuthors.splice(authorIndex, 1);
    }
    
    setFormData({
      ...formData,
      favorite_authors: currentAuthors
    });
  };

  const toggleGenres = () => {
    setShowGenres(!showGenres);
    if (!showGenres) {
      // Réinitialiser la recherche lors de l'ouverture
      setGenreSearch('');
      setFilteredGenres(genres);
    }
  };

  const toggleAuthors = () => {
    setShowAuthors(!showAuthors);
    if (!showAuthors) {
      // Réinitialiser la recherche lors de l'ouverture
      setAuthorSearch('');
      setFilteredAuthors(authors);
    }
  };

  const validate = (): boolean => {
    const newErrors: RegisterError = {};
    
    if (!formData.username.trim()) {
      newErrors.username = "Le nom d'utilisateur est requis";
    } else if (formData.username.length < 3) {
      newErrors.username = "Le nom d'utilisateur doit contenir au moins 3 caractères";
    }
    
    if (!formData.email.trim()) {
      newErrors.email = "L'adresse email est requise";
    } else {
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (!emailRegex.test(formData.email)) {
        newErrors.email = "Veuillez entrer une adresse email valide";
      }
    }
    
    if (!formData.password) {
      newErrors.password = "Le mot de passe est requis";
    } else if (formData.password.length < 8) {
      newErrors.password = "Le mot de passe doit contenir au moins 8 caractères";
    } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = "Le mot de passe doit contenir au moins une lettre et un chiffre";
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Les mots de passe ne correspondent pas";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }
    
    setLoading(true);
    
    try {
      // Exclure confirmPassword avant d'envoyer au serveur
      const { confirmPassword, ...submitData } = formData;
      
      // Obtenir l'URL de l'API depuis les variables d'environnement
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
      
      const response = await fetch(`${apiUrl}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(submitData)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        setErrors({
          general: data.error || "Une erreur est survenue lors de l'inscription"
        });
        return;
      }
      
      // Utiliser la fonction login du contexte d'authentification
      login(data.session_id, data.user);
      
      // Déclencher un événement pour signaler le changement d'authentification
      // Cet événement sera capté par le Header pour forcer son rafraîchissement
      window.dispatchEvent(new Event('auth-state-changed'));
      
      // Pour s'assurer que le localStorage est synchronisé entre les onglets
      window.dispatchEvent(new Event('storage'));
      
      // Redirection vers la page d'accueil
      navigate('/');
      
    } catch (error) {
      console.error("Erreur lors de l'inscription:", error);
      setErrors({
        general: "Une erreur de connexion est survenue. Veuillez réessayer."
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card register-card">
        <h2>Créer un compte</h2>
        
        {errors.general && (
          <div className="auth-error-message">
            {errors.general}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Nom d'utilisateur*</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choisissez un nom d'utilisateur"
              className={errors.username ? 'error' : ''}
            />
            {errors.username && <div className="field-error">{errors.username}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Adresse email*</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Entrez votre adresse email"
              className={errors.email ? 'error' : ''}
            />
            {errors.email && <div className="field-error">{errors.email}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Mot de passe*</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Créez un mot de passe"
              className={errors.password ? 'error' : ''}
            />
            {errors.password && <div className="field-error">{errors.password}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmer le mot de passe*</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirmez votre mot de passe"
              className={errors.confirmPassword ? 'error' : ''}
            />
            {errors.confirmPassword && <div className="field-error">{errors.confirmPassword}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="full_name">Nom complet (optionnel)</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name || ''}
              onChange={handleChange}
              placeholder="Entrez votre nom complet"
            />
          </div>
          
          <div className="form-group genre-group">
            <button 
              type="button" 
              className="toggle-genres-btn"
              onClick={toggleGenres}
            >
              {showGenres 
                ? "Masquer les genres" 
                : `Choisir vos genres préférés (${genres.length} disponibles)`}
            </button>
            
            {showGenres && (
              <>
                <input
                  type="text"
                  className="search-input"
                  placeholder="Rechercher un genre..."
                  value={genreSearch}
                  onChange={handleGenreSearch}
                />
                <div className="checkbox-container">
                  {filteredGenres.length > 0 ? (
                    filteredGenres.map(genre => (
                      <div key={genre} className="checkbox-item">
                        <input
                          type="checkbox"
                          id={`genre-${genre}`}
                          checked={formData.favorite_genres?.includes(genre) || false}
                          onChange={() => handleGenreChange(genre)}
                        />
                        <label htmlFor={`genre-${genre}`}>{genre}</label>
                      </div>
                    ))
                  ) : (
                    <p className="no-results">Aucun genre trouvé pour "{genreSearch}"</p>
                  )}
                </div>
              </>
            )}
            
            {showGenres && formData.favorite_genres && formData.favorite_genres.length > 0 && (
              <div className="selected-genres">
                <p>Genres sélectionnés ({formData.favorite_genres.length}):</p>
                <div className="genre-tags">
                  {formData.favorite_genres.map(genre => (
                    <span key={genre} className="genre-tag" onClick={() => handleGenreChange(genre)}>
                      {genre} ✕
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <div className="form-group author-group">
            <button 
              type="button" 
              className="toggle-authors-btn"
              onClick={toggleAuthors}
            >
              {showAuthors 
                ? "Masquer les auteurs" 
                : `Choisir vos auteurs préférés (${authors.length} disponibles)`}
            </button>
            
            {showAuthors && (
              <>
                <input
                  type="text"
                  className="search-input"
                  placeholder="Rechercher un auteur..."
                  value={authorSearch}
                  onChange={handleAuthorSearch}
                />
                <div className="search-info">Liste des auteurs disponibles</div>
                <div className="checkbox-container">
                  {filteredAuthors.length > 0 ? (
                    filteredAuthors.map(author => (
                      <div key={author} className="checkbox-item">
                        <input
                          type="checkbox"
                          id={`author-${author}`}
                          checked={formData.favorite_authors?.includes(author) || false}
                          onChange={() => handleAuthorChange(author)}
                        />
                        <label htmlFor={`author-${author}`}>{author}</label>
                      </div>
                    ))
                  ) : (
                    <p className="no-results">Aucun auteur trouvé pour "{authorSearch}"</p>
                  )}
                </div>
              </>
            )}
            
            {showAuthors && formData.favorite_authors && formData.favorite_authors.length > 0 && (
              <div className="selected-authors">
                <p>Auteurs sélectionnés ({formData.favorite_authors.length}):</p>
                <div className="author-tags">
                  {formData.favorite_authors.map(author => (
                    <span key={author} className="author-tag" onClick={() => handleAuthorChange(author)}>
                      {author} ✕
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <div className="form-actions">
            <button 
              type="submit" 
              className="auth-button" 
              disabled={loading}
            >
              {loading ? "Inscription en cours..." : "Créer mon compte"}
            </button>
          </div>
        </form>
        
        <div className="auth-footer">
          <p>Vous avez déjà un compte ? <Link to="/login">Se connecter</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Register; 