from app import app, db, User

with app.app_context():
    # Crée la base de données et les tables
    db.create_all()

    # Vérifie si l'utilisateur existe déjà
    if not User.query.filter_by(username='client').first():
        # Crée un utilisateur
        new_user = User(username='client')
        new_user.set_password('1234')
        db.session.add(new_user)
        db.session.commit()
        print("Utilisateur 'client' créé avec succès.")
    else:
        print("L'utilisateur 'client' existe déjà.")