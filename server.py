import socket
import random 
import threading
import json

host = "0.0.0.0"
port = 7777
banner = """Enter name:"""

user_data = {}
leaderboard = []

def load_user_data():
    global user_data
    try:
        with open("users.json", 'r') as file:
            data = file.read()
            if data:
                user_data = json.loads(data)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def save_user_data():
    with open("users.json", 'w') as file:
        json.dump(user_data, file)
        
def generate_random_int(difficulty):
    if difficulty ==  "easy":
        return random.randint(1,50)
    elif difficulty == "medium":
        return random.randint(1, 100)
    elif difficulty  == "hard":
        return random.randrange(1,500)
        

def handle_client(conn, addr):
    try:
        conn.sendall(banner.encode())
        player_name = conn.recv(1024).decode().strip()
        print(f"Player {player_name} connected.")
        conn.sendall(b"Choose Difficulty level (Easy 1-50, Medium 1-100, Hard 1-500):\n")
        difficulty = conn.recv(1024).decode().strip().lower()
        
        while True:
            guessme = generate_random_int(difficulty)
            conn.sendall(b"Enter your guess:\n")
            tries = 0
            
            while True:
                try:
                    client_input = conn.recv(1024)
                    
                    if not client_input:
                        print(f"Player {player_name} disconnected.")
                        save_user_data()
                        return
                
                    guess = int(client_input.decode().strip())
                    tries += 1
                
                    if guess == guessme:
                        score = 1000 // tries
                        conn.sendall(f"Correct! You Win!\nYour score: {score}\n".encode())
                        user_data[player_name] = {"score": score, "difficulty": difficulty}
                        leaderboard.append({'name': player_name,  'score': score, 'difficulty': difficulty})
                        save_user_data()
                        print(f"Player {player_name} guessed the correct number in {tries} tries!")
                        break
                
                    elif guess > guessme:
                        conn.sendall(b"Lower!\n")
                
                    elif guess < guessme:
                        conn.sendall(b"Higher!\n")
                    
                except ValueError:
                    conn.sendall(b"Invalid input! Please enter a number.\n")
                    
                except ConnectionResetError:
                    print("Connection Reset by Player\n")
                    save_user_data()
                    return

    except ConnectionAbortedError:
        print(f"Client has aborted connection. {player_name} left.")
            
    finally:
         conn.close()
      
def display_leaderboard():
    global leaderboard
    print("\n== Leaderboard ==\n")
    for i, player in enumerate(sorted(leaderboard, key=lambda x: x['score'], reverse=True), start=1):
        print(f"Rank {i}:")
        print(f"Name: {player['name']}")
        print(f"Score: {player['score']}")
        print(f"Difficulty: {player['difficulty']}\n")
    
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)

load_user_data()
print(f"Server is listening on port {port}")

while True:
    print("Waiting for connections...")
    conn, addr = s.accept()
    print(f"New connection from {addr}")
    client_thread = threading.Thread(target=handle_client, args=(conn, addr))
    client_thread.start()
    client_thread.join()
    display_leaderboard()
