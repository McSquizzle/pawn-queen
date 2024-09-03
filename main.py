import pygame
from pygame.locals import *
import time
import copy

# Initialize pygame
pygame.init()

# board scale
board_scale = 100

# Set up display
width, height = 4*board_scale, 4*board_scale
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Chess Bot')

# Colors
WHITE = (232, 235, 239)
BLACK = (125, 135, 150)

# Load images
pieces = {}
for piece in ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']:
    for color in ['white', 'black']:
        image = pygame.image.load(f'./images/{color}_{piece}.png')
        image = pygame.transform.scale(image, (board_scale, board_scale))
        pieces[f'{color}_{piece}'] = image

# Draw the chessboard
def draw_board():
    colors = [WHITE, BLACK]
    for row in range(4):
        for col in range(4):
            # RED SQUARES
            if (row == 3 and col == 1) or (row == 3 and col == 2):
                pygame.draw.rect(screen, (255,0,0), pygame.Rect(col*board_scale, row*board_scale, board_scale, board_scale))
            else:
                color = colors[(row + col) % 2]
                pygame.draw.rect(screen, color, pygame.Rect(col*board_scale, row*board_scale, board_scale, board_scale))

# Place pieces on the board
def place_pieces(board):
    for row in range(4):
        for col in range(4):
            piece = board[row][col]
            if piece != '_' and piece != '':
                screen.blit(pieces[piece], (col*board_scale, row*board_scale))

background = pygame.Surface(screen.get_size())
draw_board()

# Display board
def display_board(board):
    screen.blit(background, (0,0))
    place_pieces(board)
    pygame.display.flip()

# Draw buttons
def draw_button(text, x, y, width, height, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))

    font = pygame.font.Font(None, 28)
    text_surf = font.render(text, True, (0,0,0))
    text_rect = text_surf.get_rect(center=(x + width / 2, y + height / 2))
    screen.blit(text_surf, text_rect)

# UI screen with two buttons
def game_intro():
    intro = True

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill((255,255,255))

        # draw_button("Play Against Bot", 50, board_scale*4, 300, 50, (255,255,255), (40,40,40), play_against_bot)
        draw_button("Explore Permutations", 75, 75, 300, 50, (255,255,255), (40,40,40), view_all_iterations)

        pygame.display.update()

# ChessGame class with full movement rules
class ChessGame:
    def __init__(self):
        self.board = [
            ['white_knight', 'white_knight', 'white_knight', 'white_knight'],
            ['white_bishop', 'white_bishop', 'white_bishop', 'white_bishop'],
            ['white_rook', 'white_rook', 'white_rook', 'white_rook'],
            ['', '_', '_', 'white_pawn']
        ]
        self.current_turn = 'white'
        self.move_history = []
        self.prev_piece_moved = [] # [from x, from y, to x, to y]

    def get_all_possible_moves(self):
        moves = []
        for row in range(4):
            for col in range(4):
                if self.board[row][col].startswith(self.current_turn):
                    piece_type = self.board[row][col].split('_')[1]
                    if piece_type == 'pawn':
                        moves.extend(self.get_pawn_moves(row, col))
                    elif piece_type == 'rook':
                        moves.extend(self.get_rook_moves(row, col))
                    elif piece_type == 'knight':
                        moves.extend(self.get_knight_moves(row, col))
                    elif piece_type == 'bishop':
                        moves.extend(self.get_bishop_moves(row, col))
                    elif piece_type == 'queen':
                        moves.extend(self.get_queen_moves(row, col))
        
        return moves

    def is_valid_position(self, row, col):
        return 0 <= row < 4 and 0 <= col < 4

    def get_pawn_moves(self, row, col):
        moves = []
        direction = -1 if self.current_turn == 'white' else 1
        # Move forward
        if self.is_valid_position(row + direction, col) and self.board[row + direction][col] == '':
            moves.append((row, col, row + direction, col))
        
        return moves

    def get_rook_moves(self, row, col):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while self.is_valid_position(r, c):
                if self.board[r][c] == '':
                    if self.prev_piece_moved != [r, c, row, col]:
                        moves.append((row, col, r, c))
                else:
                    break
                r += dr
                c += dc
        return moves

    def get_knight_moves(self, row, col):
        moves = []
        directions = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if self.is_valid_position(r, c) and (self.board[r][c] == '' or self.board[r][c].startswith('black' if self.current_turn == 'white' else 'white')):
                if self.prev_piece_moved != [r, c, row, col]:
                    moves.append((row, col, r, c))
        return moves

    def get_bishop_moves(self, row, col):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while self.is_valid_position(r, c):
                if self.board[r][c] == '':
                    if self.prev_piece_moved != [r, c, row, col]:
                        moves.append((row, col, r, c))
                else:
                    break
                r += dr
                c += dc
        return moves

    def get_queen_moves(self, row, col):
        return self.get_rook_moves(row, col) + self.get_bishop_moves(row, col)


    def is_game_over(self):
        """ Check if the game is over by checkmate or stalemate """
        
        if self.board[0][3] == 'white_queen':
            return True
    
    def make_move(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        # captured_piece = self.board[end_row][end_col]

        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = ''

        if 'pawn' in piece and end_row == 0:
            self.board[end_row][end_col] = 'white_queen'

        # Store move history for undoing - piece is used so we can ensure queen promotions don't get improperly undone
        # Stores the old state piece, not the new state piece
        self.move_history.append(((start_row, start_col, end_row, end_col), piece))

        # self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.current_turn = 'white' # white stays playing for this game

    def undo_move(self):
        move, old_piece = self.move_history.pop()
        start_row, start_col, end_row, end_col = move
        
        self.board[start_row][start_col] = old_piece
        self.board[end_row][end_col] = ''

        # self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.current_turn = 'white' # white stays playing for this game


shortest_search = float('inf')

def dfs(game, depth=0, total_games=0, depth_limit=13, game_number=0):
    global shortest_search
    if depth > depth_limit or game.is_game_over():
        if game.is_game_over() and depth < shortest_search:
            print("Moves to promote queen: " + str(depth))
            print("Move history: " + str(game.move_history))
            print("")
            shortest_search = depth
        return total_games + 1

    moves = game.get_all_possible_moves()
    for move in moves:
        game.prev_piece_moved = [move[0], move[1], move[2], move[3]]
        game.make_move(move[0], move[1], move[2], move[3])
    
        # THE CODE BELOW DRAWS THE GAMES UPDATED STATE UPON EVERY SEARCH - UNCOMMENT TO SHOW ANIMATION 
        # BUT IT CONSUMES A TONNE OF COMPUTATIONAL TIME 
        
        # draw_board()
        # place_pieces(game.board)
        # pygame.display.flip()
                

        total_games = dfs(game, depth + 1, total_games, depth_limit)
        game.undo_move()

    return total_games
        

# Function to handle viewing all game iterations
def view_all_iterations():
    chess_game = ChessGame()
    running = True
    dfs_started = False
    total_games = 0

    while running:
        draw_board()
        place_pieces(chess_game.board)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_d and not dfs_started:  # Press 'P' to start DFS
                    dfs_started = True

                    start_time = time.time()

                    total_games = dfs(chess_game)
                    print(f'Total possible games: {total_games}')  # Output to terminal

                    end_time = time.time()

                    total_time = end_time - start_time
                    print(f"Total time for algorithm to run was: {total_time:.6f} ")

        pygame.display.flip()

    pygame.quit()

# Main game loop
def main():
    game_intro()

if __name__ == "__main__":
    main()