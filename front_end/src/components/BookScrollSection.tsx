import BookCard from './BookCard'
import '../styles/dashboard.css'

type Book = {
  title: string
  image: string
  author: string
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
        {books.map((book, index) => (
          <BookCard key={index} book={book} showActions={showActions} />
        ))}
      </div>
    </div>
  )
}

export default BookScrollSection
