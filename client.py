import socket

host = "192.168.0.102"
port = 7777

def Play_Game():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Specify the socket type
    s.connect((host, port))

    data = s.recv(1024)
    print("\n== GuessingGameV2 ==\n")
    print(data.decode().strip())

    while True:
        user_input = input("Input: ").strip()
        s.sendall(user_input.encode())
        
        print()
        reply = s.recv(1024).decode().strip()
        
        if "Correct" in reply:
            print(reply)
            s.close()  
            return
        
        print(reply)

while True:
    Play_Game()
    repeat = input("\nWant to play another round? (y/n): ").strip().lower()
    if repeat != 'y':
        break
