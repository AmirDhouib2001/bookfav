import { Link } from 'react-router-dom'
import logo from '../logo.png'
import '../styles/dashboard.css'

function Header() {
  return (
    <header className="header">
      <div className="left-logo">
        <img src={logo} alt="BookFav logo" className="logo-img" />
        <span className="logo-text">bookfav</span>
      </div>

      <nav className="nav-links">
        <Link to="/catalogue">Catalogue</Link>
        <Link to="/account">Mon compte</Link>
      </nav>
    </header>
  )
}

export default Header
