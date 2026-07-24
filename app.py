from flask import Flask, request, jsonify
import oracledb
import os

app = Flask(__name__)

# Infos de connexion Oracle (utilise la chaîne DSN sans Wallet si mTLS est désactivé)
DB_USER = "ADMIN"
DB_PASSWORD = "TonMotDePasseOracle" # Ton MDP de BDD
DB_DSN = "votre_dsn_oracle" # Trouvable sur Oracle Cloud dans Database Connection

def get_db_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, permission FROM users WHERE username = :1 AND password_hash = :2",
            [username, password]
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            return jsonify({"success": True, "username": row[0], "permission": row[1]}), 200
        else:
            return jsonify({"success": False, "error": "Identifiants incorrects"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users/create', methods=['POST'])
def create_user():
    data = request.json or {}
    if data.get('admin_permission') != 3:
        return jsonify({"success": False, "error": "Permission insuffisante"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, permission) VALUES (:1, :2, :3)",
            [data.get('username'), data.get('password'), data.get('permission')]
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Utilisateur créé !"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)