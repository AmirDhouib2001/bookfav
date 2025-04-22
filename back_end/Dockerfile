FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances nécessaires pour PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Variables d'environnement
ENV FLASK_APP=app
ENV FLASK_ENV=development
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Exposer le port
EXPOSE 5000

# Démarrer l'application avec plus de logs
CMD ["flask", "run", "--host=0.0.0.0", "--debug"]
