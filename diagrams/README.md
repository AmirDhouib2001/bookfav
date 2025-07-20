# 📊 Diagrammes Draw.io - Projet BookFav

Ce dossier contient tous les diagrammes techniques du projet BookFav au format Draw.io, correspondant aux schémas décrits dans le rapport technique.

## 📋 Liste des Diagrammes

### 1. **01_schema_relationnel.drawio**
- **Description :** Schéma relationnel de la base de données PostgreSQL
- **Contenu :** Tables `auth_users`, `books`, `user_book_ratings` avec relations
- **Utilisation :** Comprendre la structure des données et les relations

### 2. **02_architecture_globale.drawio**
- **Description :** Architecture générale du système à 3 niveaux
- **Contenu :** Frontend (React), Backend (Flask), Base de données (PostgreSQL)
- **Utilisation :** Vue d'ensemble de l'architecture technique

### 3. **03_workflow_global.drawio**
- **Description :** Workflow global du traitement des données
- **Contenu :** Du clic utilisateur jusqu'à l'affichage des recommandations
- **Utilisation :** Comprendre le flux de données complet

### 4. **04_workflow_collaborative_filtering.drawio**
- **Description :** Pipeline détaillé du système Collaborative Filtering
- **Contenu :** Matrix Factorization + MLP, entraînement, prédictions
- **Utilisation :** Comprendre le fonctionnement du système CF

### 5. **05_workflow_content_based.drawio**
- **Description :** Pipeline du système Content-Based Filtering
- **Contenu :** TF-IDF, similarité cosinus, recommandations
- **Utilisation :** Comprendre le système de recommandation par contenu

### 6. **06_workflow_reentrainement.drawio**
- **Description :** Processus de réentraînement asynchrone
- **Contenu :** Déclencheurs, validation, déploiement des modèles
- **Utilisation :** Comprendre la mise à jour des modèles

### 7. **07_metriques_performances.drawio**
- **Description :** Métriques et performances du système
- **Contenu :** KPIs, benchmarks, satisfaction utilisateur
- **Utilisation :** Évaluer les performances du système

### 8. **08_architecture_cloud.drawio**
- **Description :** Architecture cloud AWS du système
- **Contenu :** AWS Amplify (frontend), Elastic Beanstalk (backend), RDS (base de données)
- **Services :** CloudFront, S3, Route 53, Load Balancer, CloudWatch
- **Utilisation :** Comprendre le déploiement cloud et la scalabilité

## 🚀 Comment Utiliser les Fichiers

### Ouvrir dans Draw.io
1. Aller sur [app.diagrams.net](https://app.diagrams.net)
2. Cliquer sur "Open Existing Diagram"
3. Sélectionner le fichier `.drawio` souhaité
4. Le diagramme s'ouvre automatiquement

### Modifier les Diagrammes
- **Couleurs :** Cliquer sur un élément → panneau de droite → changer les couleurs
- **Texte :** Double-cliquer sur un élément pour éditer le texte
- **Formes :** Utiliser la palette de gauche pour ajouter des éléments
- **Connexions :** Glisser depuis un élément vers un autre pour créer des flèches

### Exporter les Diagrammes
- **PNG/JPG :** File → Export as → PNG/JPEG
- **PDF :** File → Export as → PDF
- **SVG :** File → Export as → SVG (pour intégration web)

## 📐 Conventions Visuelles

### Codes Couleur
- **🔵 Bleu :** Composants Frontend (React)
- **🟡 Jaune :** Composants Backend (Flask)
- **🟢 Vert :** Base de données et stockage
- **🟠 Orange :** Processus et workflows
- **🟣 Violet :** Services et APIs
- **🔴 Rouge :** Alertes et erreurs

### Formes Standard
- **Rectangles :** Composants et services
- **Losanges :** Points de décision
- **Cercles :** Étapes numérotées
- **Flèches :** Flux de données
- **Containers :** Groupes logiques

## 🔧 Personnalisation

### Adapter pour Votre Projet
1. **Modifier les noms :** Remplacer "BookFav" par votre nom de projet
2. **Ajuster les métriques :** Mettre à jour les chiffres avec vos données
3. **Personnaliser les couleurs :** Adapter au thème de votre organisation
4. **Ajouter des éléments :** Intégrer vos spécificités techniques

### Créer de Nouveaux Diagrammes
1. **Duplicquer un fichier existant** comme base
2. **Modifier le contenu** selon vos besoins
3. **Respecter les conventions** visuelles établies
4. **Ajouter à ce README** pour documenter

## 📚 Ressources Complémentaires

### Documentation Draw.io
- [Guide officiel Draw.io](https://www.diagrams.net/doc/)
- [Tutoriels vidéo](https://www.youtube.com/c/drawio)
- [Templates et exemples](https://www.diagrams.net/example-diagrams)

### Bonnes Pratiques
- **Simplicité :** Éviter la surcharge d'informations
- **Cohérence :** Utiliser les mêmes conventions partout
- **Lisibilité :** Texte suffisamment grand et contrasté
- **Mise à jour :** Synchroniser avec l'évolution du code

## 🤝 Contribution

### Modifier un Diagramme
1. Ouvrir le fichier dans Draw.io
2. Effectuer les modifications
3. Sauvegarder au format `.drawio`
4. Documenter les changements

### Proposer de Nouveaux Diagrammes
1. Identifier le besoin
2. Créer le diagramme
3. Respecter les conventions
4. Ajouter à la documentation

## 📞 Support

Pour toute question concernant les diagrammes :
- Consulter la documentation Draw.io
- Vérifier les conventions dans ce README
- Proposer des améliorations via les issues

---

*Dernière mise à jour : 2024*
*Version des diagrammes : 1.0* 