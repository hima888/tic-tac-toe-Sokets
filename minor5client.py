
import socket
import sys
import threading
import time

# Packet codes
SERVER_FULL = 'F'
GAME_INFO = ' '
GAME_END = 'V'
REGISTER = 'R'

# Packet constants
BUFLEN = 512

# Board constants
NULL_CHAR = ' '
BOARD_ROWS = 3
BOARD_COLS = 3
MAX_PLAYERS = 2

if len(sys.argv) <= 2:
    print("usage: client <hostname> <PORT NUMBER>")
    sys.exit()

EXIT_CODES = {
     SERVER_FULL : "Server is full! Try again later",
     GAME_END : "Thank you for playing!"
}

DISPLAY = {
    'X': 'X',
    'O': 'O',
     NULL_CHAR: ' '
}

GAME_OVER = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (sys.argv[1], int(sys.argv[2]))

def display_game(game_info):
    # this function handles displaying the game
    game_info = list(game_info)

    for i in range(len(game_info)):
        game_info[i] = DISPLAY[game_info[i]]
    
    print("board\n")
    print("  1|2|3")
    print("+"*9)
    print("A|" + game_info[0] + "|" + game_info[1]  + "|" + game_info[2] + "|")
    print("+"*9)
    print("B|" + game_info[3] + "|" + game_info[4]  + "|" + game_info[5] + "|") 
    print("+"*9)
    print("C|" + game_info[6] + "|" + game_info[7]  + "|" + game_info[8] + "|")
    print("+"*9)


def display_thread():
    # this function handles display
    global GAME_OVER
    while not GAME_OVER:
        response, _ = sock.recvfrom( BUFLEN)
        if response[0] ==  GAME_INFO:
            display_game(response[1:])
        elif response in EXIT_CODES:
            print(EXIT_CODES[response])
            GAME_OVER = True
        else:
            print(response)

def user_thread():
    # this function handles user input
    while not GAME_OVER:
        message = raw_input()
        if message =="?":
            print("? -Display this help\nR -Resign\nMove<R><C> -Move where <R> is a row A, B or C and <C> is a column 1,2 or 3\nExample Moves: MA1 MC3 MB1\n")
        else:
            sock.sendto(message, server_address)

def launch_game():
    
    # this function launches the game
    user = threading.Thread(target=user_thread)
    display = threading.Thread(target=display_thread)
    user.daemon = True
    display.daemon = True
    user.start()
    display.start()
    while not GAME_OVER:
        time.sleep(1)


# intilazation func to start the client 
def initialize():
    print("Connecting to server...")
    sock.sendto( REGISTER, server_address)

initialize()
launch_game()
