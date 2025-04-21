import '../styles/bookfavintro.css'
import logo from '../logo.png'

const BookFavIntro = () => {
  return (
    <section className="bookfav-intro">
      <div className="intro-logo">
        <img src={logo} alt="BookFav Logo" />
      </div>
      <div className="intro-text-block">
        <h2>Votre bibliothèque personnalisée</h2>
        <p>
          <span className="bookfav-name">BookFav</span> est votre bibliothèque en ligne personnalisée : créez un compte,
          partagez vos goûts et découvrez des recommandations sur mesure.
        </p>
        <p>
          Parcourez notre catalogue enrichi de descriptions et d’avis, et suivez facilement vos lectures passées pour
          toujours trouver votre prochain coup de cœur.
        </p>
      </div>
    </section>
  )
}

export default BookFavIntro
