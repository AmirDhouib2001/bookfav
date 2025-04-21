import BookScrollSection from '../components/BookScrollSection'
import '../styles/dashboard.css'
import BookFavIntro from '../components/BookFavIntro'


const Dashboard = () => {
  const recommendations = Array.from({ length: 10 }).map((_, i) => ({
    title: `Livre ${i + 1}`,
    image: `https://picsum.photos/200/300?random=${i + 2}`,
    author: `Auteur ${i + 1}`
  }))

  const alreadyRead = Array.from({ length: 6 }).map((_, i) => ({
    title: `Lecture ${i + 1}`,
    image: `https://picsum.photos/200/300?random=${i + 12}`,
    author: `Auteur ${i + 10}`
  }))

  return (
    <div className="dashboard">
        <BookFavIntro />
        <BookScrollSection title="Nos suggestions du moment" books={recommendations} />
        <BookScrollSection title="Mes lectures passées" books={alreadyRead} showActions />
    
    </div>
  )
}

export default Dashboard
