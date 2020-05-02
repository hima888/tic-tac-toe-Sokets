import socket
import sys
import random

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


if len(sys.argv) < 2:
    print("usage:  <PORT NUMBER>")
    sys.exit()

# Constants
TURN_ERROR = "It isn't your turn right now."
INPUT_ERROR = ("Invalid Move\n"
"Move should be M<R><C> with no spaces\n"
"Example: MA1 or MB3\n")
WAIT_MSG = "You are player X. Waiting on player O to connect \n"

ROLE_PROMPT = "You are playing as: %s\n"
MOVE_PROMPT = "Your Turn \n"
VALID_ROWS = {
    'A': 0,
    'B': 1,
    'C': 2
}
VALID_COLS = {
    '1': 0,
    '2': 1,
    '3': 2
}
SYMBOLS = [
    'X',
    'O'
]

class Board(object):
    def __init__(self):
        self.ROLE = {}
        self.PLAYERS = []
        self.PLAY_PTR = 0
        self.NUM_PLAYERS = 0
        self.GAME_BOARD = [
            [ NULL_CHAR] *  BOARD_COLS
            for _ in range( BOARD_ROWS)
        ]
        self.LINES = self.generate_lines()
        self.MOVES_LEFT = self.move_set()

    def move_set(self):
        moves = set()
        for row in VALID_ROWS.keys():
            for col in VALID_COLS.keys():
                moves.add("M"+row + col)
        return moves

    def generate_lines(self):
        lines = []

        # rows and cols
        for row in range( BOARD_ROWS):
            temp_rows = []
            temp_cols = []
            for col in range( BOARD_COLS):
                temp_rows.append((row, col))
                temp_cols.append((col, row))
            lines.append(temp_rows)
            lines.append(temp_cols)

        # diagonals
        diag_a = []
        diag_b = []
        for row in range( BOARD_ROWS):
            diag_a.append((row, row))
            diag_b.append(( BOARD_ROWS - row - 1, row))
        lines.append(diag_a)
        lines.append(diag_b)

        return lines

    def add_player(self, player_id):
        self.ROLE[player_id] = SYMBOLS[self.NUM_PLAYERS]
        self.PLAYERS.append(player_id)
        self.NUM_PLAYERS += 1

BOARD = Board()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', int(sys.argv[1]))

print('Network Server Starting')

sock.bind(server_address)

def send_to_address(message, address):
    '''send msg btween server and clients '''
    if address !=  "AI":
        sock.sendto(message, address)
        # print(BOARD.ROLE[address]+">")


def broadcast(message):
    '''to broadcast msg to all users connected with server'''
    for address in BOARD.PLAYERS:
        send_to_address(message, address)

def is_valid_move(move):
    #return the rest of valid moves 
    return(len(move) <= 3 and
           move in BOARD.MOVES_LEFT and
           move[0]=='M' and
           move[1] in VALID_ROWS and
           move[2] in VALID_COLS)

def reset():
    '''reset the all game'''
    global BOARD
    BOARD = Board()

def increment_play_order():
    '''keep tracking of clients order'''
    BOARD.PLAY_PTR += 1
    if BOARD.PLAY_PTR >= len(BOARD.PLAYERS):

        BOARD.PLAY_PTR = 0

def await_players():
    print("Waiting on Clients..")
    #waiting clients to connect 
    while BOARD.NUM_PLAYERS <  MAX_PLAYERS:
        data, address = sock.recvfrom( BUFLEN)
        if address not in BOARD.ROLE:
            BOARD.add_player(address)

        else:
            #server full check and user inputs warinings
            send_to_address(INPUT_ERROR, address)
            print(INPUT_ERROR , address)
            # send_to_address(WAIT_MSG, address)
        print(BOARD.ROLE[address]+"< Connected")    
        broadcast_state(address)


def broadcast_state(address):
    '''transmiting the game states between clients'''
    if BOARD.NUM_PLAYERS <  MAX_PLAYERS:
        message = WAIT_MSG
        broadcast(message )
        print(BOARD.ROLE[address]+">"+WAIT_MSG)


def drawmapS(game_info1):
    '''draw the board in the server side'''
    print("board")
    print("  1|2|3")
    print("+"*9)
    print("A|" + game_info1[1] + "|" + game_info1[2]  + "|" + game_info1[3] + "|")
    print("+"*9)
    print("B|" + game_info1[4] + "|" + game_info1[5]  + "|" + game_info1[6] + "|") 
    print("+"*9)
    print("C|" + game_info1[7] + "|" + game_info1[8]  + "|" + game_info1[9] + "|")
    print("+"*9)

# is user try to resign ?!
def checkresign(move,address):
    if move =="R":
        if BOARD.ROLE[address]=="X":
            # send_to_address( "you lose", address)
            broadcast("player O win")
            print("player O win")
        else:
            broadcast("player X win")
            print("player X win")
        m="%s is resigned"
        broadcast(m% BOARD.ROLE[address])
        broadcast( GAME_END)
        print("Game Ended")
        sys.exit()
    else:
        return False

def broadcast_game():
    game_state = [ GAME_INFO]
    for row in range(len(BOARD.GAME_BOARD)):
        for col in range(len(BOARD.GAME_BOARD)):
            game_state.append(BOARD.GAME_BOARD[row][col])
    broadcast(''.join(game_state))
    drawmapS(game_state)


def is_winning_set(char_set):
    '''combination od=f moves which led to win the game'''
    return ( NULL_CHAR not in char_set and
            len(char_set) == 1)

def get_winner():
    '''winner announcing fuction ''' 
    for line in BOARD.LINES:
        temp = set()
        for row, col in line:
            temp.add(BOARD.GAME_BOARD[row][col])
        if is_winning_set(temp):
            return "%s won!" %temp.pop()
            
    #game is tie no body won 
    if not BOARD.MOVES_LEFT:
        return "Tie Game\n"

    return None

def launch_game():
    '''this func starts the game between 2 clients'''
    # broadcast("\nGame on!\n")
    for address in BOARD.PLAYERS:
        message = ROLE_PROMPT % BOARD.ROLE[address]
        send_to_address(message, address)
        if BOARD.ROLE[address]=="O":
            print(BOARD.ROLE[address]+">"+message)

        # print(BOARD.PLAYERS)
    manage_board()

def prompt_player(address):
    message = (MOVE_PROMPT) 
    send_to_address(message, address)
    print(BOARD.ROLE[address]+">"+message)

#set of all moves in the game 
def set_board_at(move, value):
    row = VALID_ROWS[move[1]]
    col = VALID_COLS[move[2]]
    BOARD.GAME_BOARD[row][col] = value
    BOARD.MOVES_LEFT.remove(move)

def point_to_move(point):
    '''points to move as x and y '''
    row, col = point[0], point[1]
    move = ""

    for key, value in VALID_ROWS.items():
        if value == row:
            move += key
            break

    for key, value in VALID_COLS.items():
        if value == col:
            move += key
            break

    return move

def moves_and_symbols_from(line):
    '''this func replace the taken place with x an O symbols'''
    line_symbols = {}
    moves = set()
    for point in line:
        symbol = BOARD.GAME_BOARD[point[0]][point[1]]
        if symbol ==  NULL_CHAR:
            moves.add(point_to_move(point))
        elif symbol in line_symbols:
            line_symbols[symbol] += 1
        else:
            line_symbols[symbol] = 1

    return moves, line_symbols

# def enemy_is_winning(symbol_dict):
#     if len(symbol_dict.keys()) > 1:
#         return False
#     for key, value in symbol_dict.items():
#         if value > 1 and key != BOARD.ROLE[ AI]:
#             return True
#     return False


def get_move_from(player):
    '''this func check moves validations and constrictions'''
    taken=[]

    valid_move = None

    prompt_player(player)

    while not valid_move:
        move, address = sock.recvfrom( BUFLEN)
        print(BOARD.ROLE[address]+"<"+move)
        if address not in BOARD.ROLE:
            send_to_address( SERVER_FULL, address)
            print(BOARD.ROLE[address]+">"+SERVER_FULL)

            continue
        move = move.upper()

        if address != player:
            checkresign(move,address)
            send_to_address(TURN_ERROR, address)
            print(BOARD.ROLE[address]+">"+TURN_ERROR)

        elif move not in BOARD.MOVES_LEFT and move[0]=='M' and move[1] in VALID_ROWS and move[2] in VALID_COLS:
            send_to_address("spot is already taken",address)
            print(BOARD.ROLE[address]+">"+"spot is already taken")

            # print("spot is already taken")
        elif is_valid_move(move):
            valid_move = move
        
        elif checkresign(move,address):
            pass

    
        else:
            send_to_address(INPUT_ERROR, address)
            print(BOARD.ROLE[address]+">"+INPUT_ERROR)

            

    return valid_move

def manage_board():
    while True:
        # for each player do following steps 
        active_player = BOARD.PLAYERS[BOARD.PLAY_PTR]
        print(BOARD.ROLE[active_player]+">")
        broadcast_game()

        move = get_move_from(active_player)
        set_board_at(move, BOARD.ROLE[active_player])
        increment_play_order()
        winner = get_winner()
        if winner:
            broadcast_game()
            message = "%s" % winner
            broadcast(message)
            print(">"+message)
            broadcast( GAME_END)
            print("Game Ended")
            # break
            sys.exit()

# main loop 
while True:
    reset()
    await_players()
    launch_game()
