from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
import json
import sqlite3
import base64
import hashlib
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
def init_db():
    conn = sqlite3.connect('database/glory_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT UNIQUE,
            token TEXT,
            glory INTEGER DEFAULT 0,
            clan_id TEXT,
            status TEXT DEFAULT 'inactive',
            bot_status TEXT DEFAULT 'stopped',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clan_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_uid TEXT,
            clan_id TEXT,
            status TEXT DEFAULT 'pending',
            response TEXT,
            response_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS glory_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_uid TEXT,
            glory_earned INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

class GloryBot:
    def __init__(self):
        self.active_bots = {}
        self.bot_threads = {}
    
    def start_bot(self, account_uid, token):
        """Start bot for an account"""
        if account_uid in self.active_bots:
            return {"status": "error", "message": "Bot already running"}
        
        def bot_loop(uid):
            while self.active_bots.get(uid, False):
                try:
                    # Simulate playing and collecting glory
                    glory_earned = self.simulate_play()
                    
                    # Update database
                    conn = sqlite3.connect('database/glory_bot.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE accounts 
                        SET glory = glory + ?, status = 'active'
                        WHERE uid = ?
                    ''', (glory_earned, uid))
                    
                    cursor.execute('''
                        INSERT INTO glory_logs (account_uid, glory_earned)
                        VALUES (?, ?)
                    ''', (uid, glory_earned))
                    
                    conn.commit()
                    conn.close()
                    
                    # Send update via socket
                    socketio.emit('glory_update', {
                        'account_uid': uid,
                        'glory_earned': glory_earned,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    time.sleep(300)  # Wait 5 minutes
                    
                except Exception as e:
                    print(f"Error in bot loop: {e}")
                    time.sleep(60)
        
        self.active_bots[account_uid] = True
        thread = threading.Thread(target=bot_loop, args=(account_uid,))
        thread.daemon = True
        thread.start()
        self.bot_threads[account_uid] = thread
        
        return {"status": "success", "message": "Bot started"}
    
    def stop_bot(self, account_uid):
        """Stop bot for an account"""
        if account_uid in self.active_bots:
            self.active_bots[account_uid] = False
            del self.active_bots[account_uid]
            return {"status": "success", "message": "Bot stopped"}
        return {"status": "error", "message": "Bot not found"}
    
    def simulate_play(self):
        """Simulate playing and return glory earned"""
        import random
        return random.randint(50, 200)

bot_manager = GloryBot()

# API Routes
@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/add_token', methods=['POST'])
def add_token():
    data = request.json
    token = data.get('token')
    clan_id = data.get('clan_id')
    
    if not token:
        return jsonify({"error": "Token required"}), 400
    
    # Generate unique ID
    import hashlib
    uid = hashlib.md5(token.encode()).hexdigest()[:12]
    
    # Save to database
    conn = sqlite3.connect('database/glory_bot.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO accounts (uid, token, clan_id, status)
            VALUES (?, ?, ?, 'active')
        ''', (uid, token, clan_id))
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({
        "status": "success",
        "uid": uid,
        "message": "Token added successfully"
    })

@app.route('/api/accounts')
def get_accounts():
    conn = sqlite3.connect('database/glory_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT uid, glory, clan_id, status, bot_status FROM accounts')
    accounts = cursor.fetchall()
    conn.close()
    
    accounts_list = []
    for acc in accounts:
        accounts_list.append({
            'uid': acc[0],
            'glory': acc[1],
            'clan_id': acc[2],
            'status': acc[3],
            'bot_status': acc[4]
        })
    
    return jsonify(accounts_list)

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    data = request.json
    account_uid = data.get('account_uid')
    
    if not account_uid:
        return jsonify({"error": "Account UID required"}), 400
    
    # Get token from database
    conn = sqlite3.connect('database/glory_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT token FROM accounts WHERE uid = ?', (account_uid,))
    token_result = cursor.fetchone()
    conn.close()
    
    if not token_result:
        return jsonify({"error": "Account not found"}), 404
    
    token = token_result[0]
    result = bot_manager.start_bot(account_uid, token)
    
    return jsonify(result)

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    data = request.json
    account_uid = data.get('account_uid')
    
    if not account_uid:
        return jsonify({"error": "Account UID required"}), 400
    
    result = bot_manager.stop_bot(account_uid)
    return jsonify(result)

@app.route('/api/clan/request', methods=['POST'])
def clan_request():
    data = request.json
    account_uid = data.get('account_uid')
    clan_id = data.get('clan_id')
    
    if not account_uid or not clan_id:
        return jsonify({"error": "Account UID and Clan ID required"}), 400
    
    # Save request to database
    conn = sqlite3.connect('database/glory_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clan_requests (account_uid, clan_id, status)
        VALUES (?, ?, 'pending')
    ''', (account_uid, clan_id))
    conn.commit()
    request_id = cursor.lastrowid
    conn.close()
    
    # Simulate clan response (in real app, this would be actual API call)
    def simulate_response(req_id, acc_uid, cl_id):
        time.sleep(5)  # Wait 5 seconds
        
        import random
        status = random.choice(['accepted', 'rejected'])
        
        conn = sqlite3.connect('database/glory_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE clan_requests 
            SET status = ?, response_time = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, req_id))
        
        if status == 'accepted':
            cursor.execute('UPDATE accounts SET clan_id = ? WHERE uid = ?', 
                          (cl_id, acc_uid))
        
        conn.commit()
        conn.close()
        
        # Send update via socket
        socketio.emit('clan_request_update', {
            'request_id': req_id,
            'account_uid': acc_uid,
            'clan_id': cl_id,
            'status': status
        })
    
    # Start response simulation in background
    threading.Thread(target=simulate_response, args=(request_id, account_uid, clan_id)).start()
    
    return jsonify({
        "status": "success",
        "message": "Clan request sent",
        "request_id": request_id
    })

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('database/glory_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*), SUM(glory) FROM accounts')
    total_accounts, total_glory = cursor.fetchone()
    
    cursor.execute('SELECT COUNT(*) FROM accounts WHERE bot_status = ?', ('running',))
    active_bots = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM clan_requests WHERE status = ?', ('pending',))
    pending_requests = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_accounts': total_accounts or 0,
        'total_glory': total_glory or 0,
        'active_bots': active_bots or 0,
        'pending_requests': pending_requests or 0
    })

# Socket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': 'Connected to Glory Bot Panel'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
