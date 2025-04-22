import * as React from 'react';
import { Link, useLocation } from 'react-router-dom';
import logo from '../logo.png';
import '../styles/Header.css';

const Header: React.FC = () => {
  const location = useLocation();
  
  // Fonction pour déterminer si un lien est actif
  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };
  
  return (
    <header className="header">
      <div className="left-logo">
        <img src={logo} alt="BookFav logo" className="logo-img" />
        <span className="logo-text">bookfav</span>
      </div>

      <nav className="nav-links">
        <Link to="/" className={isActive('/')}>
          Accueil
        </Link>
        <Link to="/catalogue" className={isActive('/catalogue')}>
          Catalogue
        </Link>
        <Link to="/dashboard" className={isActive('/dashboard')}>
          Dashboard
        </Link>
      </nav>
    </header>
  );
};

export default Header;
