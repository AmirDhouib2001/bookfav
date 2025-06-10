-- Créer les tables pour l'application BookFav

-- Table des livres
CREATE TABLE IF NOT EXISTS books (
    "isbn" VARCHAR(20) PRIMARY KEY,
    "Book-Title" VARCHAR(255) NOT NULL,
    "Book-Author" VARCHAR(255) NOT NULL,
    "Year-Of-Publication" VARCHAR(10),
    "publisher" VARCHAR(255),
    "Image-URL-S" VARCHAR(512),
    "Image-URL-M" VARCHAR(512),
    "Image-URL-L" VARCHAR(512)
);

-- Table des évaluations
CREATE TABLE IF NOT EXISTS ratings (
    "User-ID" INTEGER,
    "isbn" VARCHAR(20),
    "Book-Rating" INTEGER,
    PRIMARY KEY ("User-ID", "isbn")
);

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    "User-ID" INTEGER PRIMARY KEY,
    "Location" VARCHAR(255),
    "Age" INTEGER
);

-- Ajouter quelques livres d'exemple
INSERT INTO books ("isbn", "Book-Title", "Book-Author", "Year-Of-Publication", "publisher", "Image-URL-S", "Image-URL-M", "Image-URL-L")
VALUES
    ('0195153448', 'Classical Mythology', 'Mark P. O. Morford', '2002', 'Oxford University Press', 'http://images.amazon.com/images/P/0195153448.01.THUMBZZZ.jpg', 'http://images.amazon.com/images/P/0195153448.01.MZZZZZZZ.jpg', 'http://images.amazon.com/images/P/0195153448.01.LZZZZZZZ.jpg'),
    ('0002005018', 'Clara Callan', 'Richard Bruce Wright', '2001', 'HarperFlamingo Canada', 'http://images.amazon.com/images/P/0002005018.01.THUMBZZZ.jpg', 'http://images.amazon.com/images/P/0002005018.01.MZZZZZZZ.jpg', 'http://images.amazon.com/images/P/0002005018.01.LZZZZZZZ.jpg'),
    ('0060973129', 'Decision in Normandy', 'Carlo D''Este', '1991', 'HarperPerennial', 'http://images.amazon.com/images/P/0060973129.01.THUMBZZZ.jpg', 'http://images.amazon.com/images/P/0060973129.01.MZZZZZZZ.jpg', 'http://images.amazon.com/images/P/0060973129.01.LZZZZZZZ.jpg'),
    ('0374157065', 'Flu: The Story of the Great Influenza Pandemic of 1918 and the Search for the Virus That Caused It', 'Gina Bari Kolata', '1999', 'Farrar Straus Giroux', 'http://images.amazon.com/images/P/0374157065.01.THUMBZZZ.jpg', 'http://images.amazon.com/images/P/0374157065.01.MZZZZZZZ.jpg', 'http://images.amazon.com/images/P/0374157065.01.LZZZZZZZ.jpg'),
    ('0393045218', 'The Mummies of Urumchi', 'E. J. W. Barber', '1999', 'W. W. Norton &amp; Company', 'http://images.amazon.com/images/P/0393045218.01.THUMBZZZ.jpg', 'http://images.amazon.com/images/P/0393045218.01.MZZZZZZZ.jpg', 'http://images.amazon.com/images/P/0393045218.01.LZZZZZZZ.jpg');

-- Vous pouvez ajouter plus de données d'exemple ici si nécessaire 