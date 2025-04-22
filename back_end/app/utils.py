import csv
import os
from .models import Book
from app import db

def load_books_from_csv(limit=100, force_reload=False):
    """
    Charge les livres depuis le fichier CSV dans la base de données.
    Limite le nombre de livres chargés selon le paramètre limit.
    
    Args:
        limit (int): Nombre maximum de livres à charger
        force_reload (bool): Si True, recharge les livres même s'il en existe déjà
    """
    # Essayer plusieurs chemins possibles pour le fichier CSV
    possible_paths = [
        # Chemin relatif au dossier de l'application
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'books_utf8_clean.csv'),
        # Chemin dans le conteneur Docker avec volume monté
        '/app/data/books_utf8_clean.csv',
        # Chemin absolu pour le développement local
        '/home/dhouib/Bureau/Amir/ESGI/PA/bookfav/data/books_utf8_clean.csv'
    ]
    
    # Trouver le premier chemin valide
    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            print(f"Trouvé le fichier CSV à: {csv_path}")
            break
    
    # Si aucun chemin n'est valide
    if csv_path is None:
        print(f"ERREUR: Le fichier CSV n'existe dans aucun des chemins suivants: {', '.join(possible_paths)}")
        return 0
    
    # Vérifier si des livres existent déjà dans la base
    try:
        existing_count = Book.query.count()
        if existing_count > 0 and not force_reload:
            print(f"La base de données contient déjà {existing_count} livres. Aucun chargement nécessaire.")
            return existing_count
    except Exception as e:
        print(f"Erreur lors de la vérification des livres existants: {e}")
        # En cas d'erreur, supposons qu'il n'y a pas de livres
        existing_count = 0
    
    # Si force_reload est True et qu'il y a des livres, les supprimer d'abord
    if force_reload and existing_count > 0:
        try:
            print("Suppression des livres existants...")
            Book.query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la suppression des livres existants: {e}")
            return 0
    
    count = 0
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            print(f"Lecture du fichier CSV: {csv_path}")
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader)  # Ignorer l'en-tête
            
            for row in csv_reader:
                if count >= limit:
                    break
                
                # Si la ligne n'a pas assez de colonnes, l'ignorer
                if len(row) < 8:
                    print(f"Ligne ignorée (pas assez de colonnes): {row}")
                    continue
                
                try:
                    isbn = row[0].strip('"')
                    title = row[1].strip('"')
                    author = row[2].strip('"')
                    year = row[3].strip('"')
                    publisher = row[4].strip('"')
                    image_url_s = row[5].strip('"')
                    image_url_m = row[6].strip('"')
                    image_url_l = row[7].strip('"')
                    
                    # Créer un nouveau livre
                    book = Book(
                        isbn=isbn,
                        title=title,
                        author=author,
                        year=year,
                        publisher=publisher,
                        image_url_s=image_url_s,
                        image_url_m=image_url_m,
                        image_url_l=image_url_l
                    )
                    
                    db.session.add(book)
                    count += 1
                    
                    # Commit par lots pour éviter de surcharger la mémoire
                    if count % 10 == 0:
                        db.session.commit()
                        print(f"Progression: {count} livres chargés...")
                
                except Exception as e:
                    print(f"Erreur avec la ligne {count+1}: {e}")
                    continue
            
            # Commit final
            db.session.commit()
            print(f"Chargement terminé: {count} livres ajoutés à la base de données.")
            return count
            
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors du chargement des livres: {e}")
        return 0 