import socket
import ssl
import threading
import time
import json
import base64
import hashlib
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class GloryBot:
    def __init__(self, token, clan_id=None):
        self.token = token
        self.clan_id = clan_id
        self.running = False
        self.socket = None
        self.glory_collected = 0
        
    def start(self):
        """Start the bot"""
        self.running = True
        print(f"Starting bot for token: {self.token[:10]}...")
        
        # Connect to game
        if not self.connect_to_game():
            print("Failed to connect to game")
            return False
        
        # Start glory collection loop
        thread = threading.Thread(target=self.collect_glory_loop)
        thread.daemon = True
        thread.start()
        
        return True
    
    def connect_to_game(self):
        """Connect to game server"""
        try:
            # Parse token
            token_data = self.parse_token(self.token)
            
            # Create SSL connection
            context = ssl.create_default_context()
            self.socket = context.wrap_socket(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                server_hostname='game-server.com'
            )
            
            # Connect (simulated)
            self.socket.connect(('127.0.0.1', 8080))
            
            # Send authentication
            auth_packet = self.create_auth_packet(token_data)
            self.socket.send(auth_packet)
            
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def parse_token(self, token):
        """Parse JWT token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            # Decode payload
            payload = parts[1]
            payload += '=' * ((4 - len(payload) % 4) % 4)
            decoded = base64.urlsafe_b64decode(payload).decode('utf-8')
            
            return json.loads(decoded)
            
        except Exception as e:
            print(f"Token parsing error: {e}")
            return None
    
    def create_auth_packet(self, token_data):
        """Create authentication packet"""
        packet = {
            "type": "auth",
            "token": self.token,
            "timestamp": int(time.time()),
            "version": "1.0"
        }
        
        return json.dumps(packet).encode()
    
    def collect_glory_loop(self):
        """Main glory collection loop"""
        while self.running:
            try:
                # Simulate playing a match
                self.simulate_match()
                
                # Collect glory
                glory = self.collect_glory()
                self.glory_collected += glory
                
                print(f"Collected {glory} glory. Total: {self.glory_collected}")
                
                # Wait before next match
                time.sleep(300)  # 5 minutes
                
            except Exception as e:
                print(f"Error in glory loop: {e}")
                time.sleep(60)
    
    def simulate_match(self):
        """Simulate playing a match"""
        # Send match start packet
        start_packet = {
            "type": "match_start",
            "timestamp": int(time.time())
        }
        
        if self.socket:
            self.socket.send(json.dumps(start_packet).encode())
        
        # Simulate match duration
        time.sleep(30)  # 30 seconds match
        
        # Send match end packet
        end_packet = {
            "type": "match_end",
            "result": "win",
            "glory_earned": 100,
            "timestamp": int(time.time())
        }
        
        if self.socket:
            self.socket.send(json.dumps(end_packet).encode())
    
    def collect_glory(self):
        """Collect glory from match"""
        import random
        return random.randint(50, 150)
    
    def send_clan_request(self):
        """Send clan join request"""
        if not self.clan_id:
            return False
        
        request_packet = {
            "type": "clan_request",
            "clan_id": self.clan_id,
            "timestamp": int(time.time())
        }
        
        if self.socket:
            self.socket.send(json.dumps(request_packet).encode())
        
        return True
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("Bot stopped.")

# Bot Manager for multiple accounts
class BotManager:
    def __init__(self):
        self.bots = {}
        self.threads = {}
    
    def add_bot(self, account_id, token, clan_id=None):
        """Add a new bot"""
        bot = GloryBot(token, clan_id)
        self.bots[account_id] = bot
        return bot
    
    def start_bot(self, account_id):
        """Start a bot"""
        if account_id in self.bots:
            bot = self.bots[account_id]
            return bot.start()
        return False
    
    def stop_bot(self, account_id):
        """Stop a bot"""
        if account_id in self.bots:
            bot = self.bots[account_id]
            bot.stop()
            del self.bots[account_id]
            return True
        return False
    
    def start_all(self):
        """Start all bots"""
        results = {}
        for account_id, bot in self.bots.items():
            results[account_id] = bot.start()
        return results
    
    def stop_all(self):
        """Stop all bots"""
        for account_id, bot in self.bots.items():
            bot.stop()
        self.bots.clear()
        return True

if __name__ == "__main__":
    # Example usage
    manager = BotManager()
    
    # Add sample bot
    bot = manager.add_bot("test_account", "sample_token", "clan_123")
    
    try:
        bot.start()
        time.sleep(60)  # Run for 1 minute
    except KeyboardInterrupt:
        bot.stop()
