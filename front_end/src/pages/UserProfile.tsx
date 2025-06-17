import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, User } from '../components/AuthProvider';
import '../styles/Profile.css';

interface ProfileFormData {
  full_name?: string;
  profile_image_url?: string;
  favorite_genres?: string[];
  favorite_authors?: string[];
  current_password?: string;
  new_password?: string;
  confirm_new_password?: string;
}

interface ProfileErrors {
  full_name?: string;
  profile_image_url?: string;
  favorite_genres?: string;
  favorite_authors?: string;
  current_password?: string;
  new_password?: string;
  confirm_new_password?: string;
  general?: string;
}

const UserProfile: React.FC = () => {
  const { user, isAuthenticated, loading, logout, updateUserData } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState<ProfileFormData>({
    full_name: '',
    profile_image_url: '',
    favorite_genres: [],
    favorite_authors: [],
    current_password: '',
    new_password: '',
    confirm_new_password: ''
  });
  const [errors, setErrors] = useState<ProfileErrors>({});
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [changingPassword, setChangingPassword] = useState<boolean>(false);
  const [updateSuccess, setUpdateSuccess] = useState<boolean>(false);
  const [genres, setGenres] = useState<string[]>([]);
  const [authors, setAuthors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [genreSearch, setGenreSearch] = useState<string>('');
  const [authorSearch, setAuthorSearch] = useState<string>('');
  const [filteredGenres, setFilteredGenres] = useState<string[]>([]);
  const [filteredAuthors, setFilteredAuthors] = useState<string[]>([]);

  // Rediriger vers la page de connexion si l'utilisateur n'est pas authentifié
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, loading, navigate]);

  // Initialiser le formulaire avec les données utilisateur actuelles
  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        profile_image_url: user.profile_image_url || '',
        favorite_genres: user.favorite_genres || [],
        favorite_authors: user.favorite_authors || [],
        current_password: '',
        new_password: '',
        confirm_new_password: ''
      });
    }
  }, [user]);

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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Effacer l'erreur lorsque l'utilisateur commence à taper
    if (errors[name as keyof ProfileErrors]) {
      setErrors({
        ...errors,
        [name]: undefined
      });
    }
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

  const handleGenreSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setGenreSearch(e.target.value);
  };

  const handleAuthorSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAuthorSearch(e.target.value);
  };

  const validate = (): boolean => {
    const newErrors: ProfileErrors = {};
    
    // Validation uniquement si on change le mot de passe
    if (changingPassword) {
      if (!formData.current_password) {
        newErrors.current_password = "Le mot de passe actuel est requis";
      }
      
      if (!formData.new_password) {
        newErrors.new_password = "Le nouveau mot de passe est requis";
      } else if (formData.new_password.length < 8) {
        newErrors.new_password = "Le mot de passe doit contenir au moins 8 caractères";
      } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.new_password)) {
        newErrors.new_password = "Le mot de passe doit contenir au moins une lettre et un chiffre";
      }
      
      if (formData.new_password !== formData.confirm_new_password) {
        newErrors.confirm_new_password = "Les mots de passe ne correspondent pas";
      }
    }
    
    // Validation de l'URL de l'image si fournie
    if (formData.profile_image_url && !isValidURL(formData.profile_image_url)) {
      newErrors.profile_image_url = "Veuillez entrer une URL valide";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const isValidURL = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch (e) {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }
    
    setIsLoading(true);
    setUpdateSuccess(false);
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';
      const sessionId = localStorage.getItem('session_id');
      
      if (!sessionId) {
        throw new Error("Session non trouvée");
      }
      
      const updateData: ProfileFormData = {
        full_name: formData.full_name,
        profile_image_url: formData.profile_image_url,
        favorite_genres: formData.favorite_genres,
        favorite_authors: formData.favorite_authors
      };
      
      // Ajouter les données de mot de passe si on change le mot de passe
      if (changingPassword && formData.current_password && formData.new_password) {
        updateData.current_password = formData.current_password;
        updateData.new_password = formData.new_password;
      }
      
      const response = await fetch(`${apiUrl}/auth/update-profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify(updateData)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        setErrors({
          general: data.error || "Une erreur est survenue lors de la mise à jour du profil"
        });
        return;
      }
      
      // Mettre à jour les données utilisateur dans le contexte
      updateUserData(data.user);
      
      // Réinitialiser les champs de mot de passe
      setFormData({
        ...formData,
        current_password: '',
        new_password: '',
        confirm_new_password: ''
      });
      
      setChangingPassword(false);
      setUpdateSuccess(true);
      setIsEditing(false);
      
      // Masquer le message de succès après 3 secondes
      setTimeout(() => {
        setUpdateSuccess(false);
      }, 3000);
      
    } catch (error) {
      console.error("Erreur lors de la mise à jour du profil:", error);
      setErrors({
        general: "Une erreur de connexion est survenue. Veuillez réessayer."
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading || !user) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Chargement du profil...</p>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h1>Mon Profil</h1>
        <button 
          onClick={handleLogout} 
          className="logout-button"
        >
          Se déconnecter
        </button>
      </div>
      
      {errors.general && (
        <div className="profile-error-message">
          {errors.general}
        </div>
      )}
      
      {updateSuccess && (
        <div className="profile-success-message">
          Profil mis à jour avec succès !
        </div>
      )}
      
      <div className="profile-card">
        <div className="profile-info">
          <div className="profile-image-container">
            {formData.profile_image_url ? (
              <img 
                src={formData.profile_image_url} 
                alt={`Avatar de ${user.username}`}
                className="profile-image"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = 'https://via.placeholder.com/150?text=Avatar';
                }}
              />
            ) : (
              <div className="profile-image-placeholder">
                {user.username.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          
          <div className="user-details">
            <h2>{user.username}</h2>
            <p className="user-email">{user.email}</p>
            {!isEditing && (
              <>
                {user.full_name && <p><strong>Nom complet:</strong> {user.full_name}</p>}
                <p><strong>Membre depuis:</strong> {new Date(user.created_at || '').toLocaleDateString()}</p>
                {user.favorite_genres && user.favorite_genres.length > 0 && (
                  <div className="user-genres">
                    <p><strong>Genres préférés:</strong></p>
                    <div className="genre-tags">
                      {user.favorite_genres.map(genre => (
                        <span key={genre} className="genre-tag">
                          {genre}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {user.favorite_authors && user.favorite_authors.length > 0 && (
                  <div className="user-authors">
                    <p><strong>Auteurs préférés:</strong></p>
                    <div className="author-tags">
                      {user.favorite_authors.map(author => (
                        <span key={author} className="author-tag">
                          {author}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
        
        {!isEditing ? (
          <button 
            onClick={() => setIsEditing(true)} 
            className="edit-profile-btn"
          >
            Modifier mon profil
          </button>
        ) : (
          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-group">
              <label htmlFor="full_name">Nom complet</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name || ''}
                onChange={handleChange}
                placeholder="Entrez votre nom complet"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="profile_image_url">URL de l'image de profil</label>
              <input
                type="text"
                id="profile_image_url"
                name="profile_image_url"
                value={formData.profile_image_url || ''}
                onChange={handleChange}
                placeholder="https://example.com/avatar.jpg"
                className={errors.profile_image_url ? 'error' : ''}
              />
              {errors.profile_image_url && <div className="field-error">{errors.profile_image_url}</div>}
            </div>
            
            <div className="form-group">
              <label htmlFor="favorite_genres">Genres préférés</label>
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
              {formData.favorite_genres && formData.favorite_genres.length > 0 && (
                <div className="selected-items">
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
            
            <div className="form-group">
              <label htmlFor="favorite_authors">Auteurs préférés</label>
              <input
                type="text"
                className="search-input"
                placeholder="Rechercher un auteur..."
                value={authorSearch}
                onChange={handleAuthorSearch}
              />
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
              {formData.favorite_authors && formData.favorite_authors.length > 0 && (
                <div className="selected-items">
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
            
            <div className="password-section">
              <div className="password-header">
                <h3>Changement de mot de passe</h3>
                <button 
                  type="button" 
                  className="toggle-password-btn"
                  onClick={() => setChangingPassword(!changingPassword)}
                >
                  {changingPassword ? "Annuler" : "Changer mon mot de passe"}
                </button>
              </div>
              
              {changingPassword && (
                <div className="password-fields">
                  <div className="form-group">
                    <label htmlFor="current_password">Mot de passe actuel</label>
                    <input
                      type="password"
                      id="current_password"
                      name="current_password"
                      value={formData.current_password || ''}
                      onChange={handleChange}
                      placeholder="Entrez votre mot de passe actuel"
                      className={errors.current_password ? 'error' : ''}
                    />
                    {errors.current_password && <div className="field-error">{errors.current_password}</div>}
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="new_password">Nouveau mot de passe</label>
                    <input
                      type="password"
                      id="new_password"
                      name="new_password"
                      value={formData.new_password || ''}
                      onChange={handleChange}
                      placeholder="Entrez votre nouveau mot de passe"
                      className={errors.new_password ? 'error' : ''}
                    />
                    {errors.new_password && <div className="field-error">{errors.new_password}</div>}
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="confirm_new_password">Confirmer le nouveau mot de passe</label>
                    <input
                      type="password"
                      id="confirm_new_password"
                      name="confirm_new_password"
                      value={formData.confirm_new_password || ''}
                      onChange={handleChange}
                      placeholder="Confirmez votre nouveau mot de passe"
                      className={errors.confirm_new_password ? 'error' : ''}
                    />
                    {errors.confirm_new_password && <div className="field-error">{errors.confirm_new_password}</div>}
                  </div>
                </div>
              )}
            </div>
            
            <div className="form-actions">
              <button 
                type="button" 
                onClick={() => setIsEditing(false)} 
                className="cancel-button"
                disabled={isLoading}
              >
                Annuler
              </button>
              <button 
                type="submit" 
                className="save-button" 
                disabled={isLoading}
              >
                {isLoading ? "Enregistrement..." : "Enregistrer les modifications"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default UserProfile; 