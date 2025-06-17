import BookCard from './BookCard'
import '../styles/dashboard.css'

interface Book {
  isbn: string;
  title: string;
  author: string;
  year: string;
  publisher: string;
  image_url_s: string;
  image_url_m: string;
  image_url_l: string;
  genre?: string;
  description?: string;
}

type Props = {
  title: string
  books: Book[]
  showActions?: boolean
}

const BookScrollSection = ({ title, books, showActions }: Props) => {
  return (
    <div className="scroll-section">
      <h2 className="section-title">{title}</h2>
      <div className="scroll-container">
        {books.map((book) => (
          <BookCard 
            key={book.isbn} 
            isbn={book.isbn}
            title={book.title}
            author={book.author}
            year={book.year}
            publisher={book.publisher}
            image_url_s={book.image_url_s}
            image_url_m={book.image_url_m}
            image_url_l={book.image_url_l}
            genre={book.genre}
            description={book.description}
          />
        ))}
      </div>
    </div>
  )
}

export default BookScrollSection
