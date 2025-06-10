import * as React from 'react';
import { useState } from 'react';
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
    favorite_genres: []
  });
  const [errors, setErrors] = useState<RegisterError>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [genres, setGenres] = useState<string[]>([]);
  const [showGenreSelect, setShowGenreSelect] = useState<boolean>(false);
  const navigate = useNavigate();

  // Récupérer la liste des genres disponibles
  React.useEffect(() => {
    const fetchGenres = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
        const response = await fetch(`${apiUrl}/books/genres`);
        if (response.ok) {
          const data = await response.json();
          if (Array.isArray(data)) {
            setGenres(data);
          }
        }
      } catch (error) {
        console.error("Erreur lors de la récupération des genres:", error);
      }
    };
    
    fetchGenres();
  }, []);

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

  const handleGenreChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
    setFormData({
      ...formData,
      favorite_genres: selectedOptions
    });
  };

  const toggleGenreSelect = () => {
    setShowGenreSelect(!showGenreSelect);
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
              onClick={toggleGenreSelect}
            >
              {showGenreSelect ? "Masquer les genres" : "Choisir vos genres préférés (optionnel)"}
            </button>
            
            {showGenreSelect && (
              <select
                multiple
                name="favorite_genres"
                id="favorite_genres"
                onChange={handleGenreChange}
                className="genre-select"
              >
                {genres.map(genre => (
                  <option key={genre} value={genre}>
                    {genre}
                  </option>
                ))}
              </select>
            )}
            
            {showGenreSelect && formData.favorite_genres && formData.favorite_genres.length > 0 && (
              <div className="selected-genres">
                <p>Genres sélectionnés:</p>
                <div className="genre-tags">
                  {formData.favorite_genres.map(genre => (
                    <span key={genre} className="genre-tag">
                      {genre}
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