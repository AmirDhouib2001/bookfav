type Book = {
    title: string
    image: string
    author: string
  }
  
  type Props = {
    book: Book
    showActions?: boolean
  }
  
  const BookCard = ({ book, showActions = false }: Props) => {
    return (
      <div className="book-card">
        <img src={book.image} alt={book.title} />
        <h4>{book.title}</h4>
        <p>{book.author}</p>
        {showActions && (
          <div className="actions">
            <button>👍</button>
            <button>⭐</button>
            <button>💬</button>
          </div>
        )}
      </div>
    )
  }
  
  export default BookCard
  