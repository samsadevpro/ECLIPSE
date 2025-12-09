📸 Aperçu

![image alt](https://github.com/samsadevpro/ECLIPSE/blob/d74616b72327dcad07418b97ec8b1b33f9cd2b39/Connexion.png)
![image alt](https://github.com/samsadevpro/ECLIPSE/blob/d74616b72327dcad07418b97ec8b1b33f9cd2b39/Acceuil.png)

✨ Fonctionnalités

🔐 Sécurité

Chiffrement AES-256 GCM

Hachage du mot de passe maître (SHA-256)

Dérivation de clé sécurisée (PBKDF2 – 200 000 itérations)

Coffre-fort enregistré dans vault.dat (fichier chiffré)

🖥️ Interface utilisateur

Interface moderne grâce à ttkbootstrap

Ajout d'un site avec :

nom du site

identifiant

mot de passe

Suppression d’un site

Visualisation des identifiants

Déconnexion

Modification du mot de passe maître

🧑‍💻 Pour les développeurs

Code en Python 3

Totalement autonome (aucune base de données)

Fichier unique pour la portabilité

Facile à modifier & améliorer

📦 Installation
1. Cloner le projet
   
   git clone https://github.com/<ton_nom>/<password-manager>.git
   
   cd password-manager

2. Installer les dépendances

pip install pycryptodome ttkbootstrap

3. Lancer le programme

python password_manager.py

🧪 Première utilisation

Au lancement, l’application demande de créer un mot de passe maître.

Celui-ci est haché et stocké dans master.key.

Un fichier chiffré vault.dat est créé pour stocker vos mots de passe.

🔧 Outils utilisées

| Technologie / Lib | Utilisation         |
| ----------------- | ------------------- |
| **Python 3**      | Langage principal   |
| **Tkinter**       | Interface graphique |
| **ttkbootstrap**  | Style moderne       |
| **PyCryptodome**  | AES, PBKDF2         |
| **hashlib**       | SHA-256             |


🛡️ Sécurité

🔒 Chiffrement

Les informations sensibles sont chiffrées avec :

AES-GCM (256 bits)

PBKDF2 pour dérivation avec sel unique à chaque chiffrement

📁 Fichiers générés

| Fichier      | Description                                     |
| ------------ | ----------------------------------------------- |
| `master.key` | Hachage SHA-256 du mot de passe maître          |
| `vault.dat`  | Coffre chiffré contenant tous les mots de passe |

📜 Exemple de structure des données chiffrées

Côté développeur, le vault ressemble à ceci avant chiffrement :

{
  "google.com": {
    "user": "mail@gmail.com",
    "password": "123456"
  },
  "github.com": {
    "user": "username",
    "password": "abcdef"
  }
}

Après chiffrement, il devient un paquet AES en base64 :

{
  "salt": "AAECAwQFBgcICQoLDA0ODw==",
  "nonce": "ZDExa2ZsaWprbWtqaA==",
  "tag": "bWFnbmlmaXF1ZQ==",
  "ciphertext": "8sv52Ze..."
}


📌 Améliorations possibles

Générateur automatique de mots de passe

Recherche dans la liste des sites

Export / import du vault

Synchronisation cloud (Dropbox / Google Drive)

Version mobile (Kivy) ou web (Flask)

📝 Licence

Ce projet est sous licence MIT, vous pouvez l'utiliser librement.

👤 Auteur

Samsa

📧 Email samsadevpro@gmail.com

🔗 GitHub : https://github.com/samsadevpro



