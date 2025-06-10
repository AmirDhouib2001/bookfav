import * as React from 'react';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import '../styles/Auth.css';

interface LoginFormData {
  username: string;
  password: string;
}

interface LoginError {
  username?: string;
  password?: string;
  general?: string;
}

const Login: React.FC = () => {
  const { login } = useAuth();
  const [formData, setFormData] = useState<LoginFormData>({
    username: '',
    password: ''
  });
  const [errors, setErrors] = useState<LoginError>({});
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Effacer l'erreur lorsque l'utilisateur commence à taper
    if (errors[name as keyof LoginError]) {
      setErrors({
        ...errors,
        [name]: undefined
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: LoginError = {};
    
    if (!formData.username.trim()) {
      newErrors.username = "Le nom d'utilisateur est requis";
    }
    
    if (!formData.password) {
      newErrors.password = "Le mot de passe est requis";
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
      // Obtenir l'URL de l'API depuis les variables d'environnement
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
      
      const response = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        setErrors({
          general: data.error || 'Une erreur est survenue lors de la connexion'
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
      console.error('Erreur lors de la connexion:', error);
      setErrors({
        general: 'Une erreur de connexion est survenue. Veuillez réessayer.'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Connexion</h2>
        
        {errors.general && (
          <div className="auth-error-message">
            {errors.general}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Nom d'utilisateur</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Entrez votre nom d'utilisateur"
              className={errors.username ? 'error' : ''}
            />
            {errors.username && <div className="field-error">{errors.username}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Mot de passe</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Entrez votre mot de passe"
              className={errors.password ? 'error' : ''}
            />
            {errors.password && <div className="field-error">{errors.password}</div>}
          </div>
          
          <div className="form-actions">
            <button 
              type="submit" 
              className="auth-button" 
              disabled={loading}
            >
              {loading ? 'Connexion en cours...' : 'Se connecter'}
            </button>
          </div>
        </form>
        
        <div className="auth-footer">
          <p>Vous n'avez pas de compte ? <Link to="/register">Créer un compte</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Login; 