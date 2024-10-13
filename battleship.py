print("Loading...")

import math
import pygame
import random
import time

from board import Board
from tile import Tile
from ship import Ship
from button import Button

pygame.init()

screen = pygame.display.set_mode((0, 0))
clock = pygame.time.Clock()

def setup():
    """Initializes the player's board and the opponent's board and sizes them
    correctly according to the window width.
    Updates the window height to look good with boards.
    Initializes the player's ships.
    """
    
    global player_board, opponent_board, player_board_x, opponent_board_x, \
           window_width, padding, game_state, turn_length
    
    # set up the window and the boards
    window_width = 1000
    padding = 80
    player_board_x = padding
    opponent_board_x = (window_width // 2) + (padding // 2)
    board_width = (window_width - padding * 3) // 2
    
    turn_length = 1
    
    player_board = Board(board_width, 10, turn_length, 'Your Board', True)
    player_board.set_pos(player_board_x, padding)
    
    opponent_board = Board(board_width, 10, turn_length, "Opponent's Board")
    opponent_board.set_pos(opponent_board_x, padding)
    
    window_height = (player_board.height + (player_board.tile_size * 2)
                     + (padding * 2))
    screen = pygame.display.set_mode((window_width, window_height))
    
    # define constants for elements that get displayed under the boards
    global visual_center_x, under_boards_y
    visual_center_x = (window_width // 2) + (player_board.tile_size // 2)
    under_boards_y = (padding + player_board.height
                      + (player_board.tile_size // 2))
    
    # initialize ships
    opponent_board.add_ship('carrier', 5, 0, 0, False)
    opponent_board.add_ship('battleship', 4, 0, 0, False)
    opponent_board.add_ship('submarine', 3, 0, 0, False)
    opponent_board.add_ship('cruiser', 3, 0, 0, False)
    opponent_board.add_ship('destroyer', 2, 0, 0, False)
    
    ship_x = player_board_x + player_board.tile_size
    player_board.add_ship('carrier', 5, ship_x, under_boards_y)
    player_board.add_ship('battleship', 4, ship_x, under_boards_y, False)
    player_board.add_ship('submarine', 3, ship_x, under_boards_y, False)
    player_board.add_ship('cruiser', 3, ship_x, under_boards_y, False)
    player_board.add_ship('destroyer', 2, ship_x, under_boards_y, False)
    
    # set up text area under the boards and buttons
    global text_surface, text_x
    text_surface = pygame.Surface((player_board.width,
                                   window_height - under_boards_y))
    text_surface.fill('white')
    text_x = visual_center_x - (player_board.width // 2)
    
    global instructions
    instructions = ('Drag your ships onto your board. Right click on a ship to'
                    + ' rotate it 90 degrees. Ships must be fully on the board'
                    + ' and may not overlap each other or be touching each'
                    + ' other.')
    
    global ready_button, play_again_button
    button_width = window_width // 5
    ready_button = Button(visual_center_x - (button_width // 2),
                          under_boards_y, button_width, button_width // 3,
                          start, Tile.BLUE, 'Ready', False)
    play_again_button = Button(visual_center_x - (button_width // 2),
                               under_boards_y + player_board.tile_size,
                               button_width, button_width // 4, reset,
                               Tile.BLUE, 'Play again', False)
    
    # initialize variables to control the flow of the player's turns and the
    # computer's guessing logic
    global first_turn, tile_clicked
    
    global computer_unresolved_hit, computer_first_hit_column, \
           computer_first_hit_row, computer_last_hit_column, \
           computer_last_hit_row, computer_knows_horizontal, \
           computer_knows_vertical, not_up, not_right, not_down, not_left
    
    reset()
    
def reset():
    """Resets the boards."""
    
    global game_state, turn_length, first_turn, tile_clicked, not_up, \
           not_right, not_down, not_left, computer_knows_horizontal, \
           computer_knows_vertical, computer_unresolved_hit
    
    # reset the player's ships
    for ship in player_board.ships:
        player_board.erase_ship(ship)
        ship.reset()
        ship.set_position(player_board_x + player_board.tile_size,
                          under_boards_y)
        
        if ship.name == 'carrier':
            ship.lock(False)
        else:
            ship.lock(True)
            ship.set_visible(False)
    
    player_board.reset()
    player_board.update()
    
    # reset opponent's ships
    for ship in opponent_board.ships:
        opponent_board.erase_ship(ship)
        ship.reset()
        ship.set_visible(False)
    
    opponent_board.reset()
    randomize_opponent_board()
    
    # display setup instructions
    set_text(instructions)
    
    # reset logic for player's turn and computer guessing
    tile_clicked = False
    first_turn = True
    not_up = False
    not_right = False
    not_down = False
    not_left = False
    computer_knows_horizontal = False
    computer_knows_vertical = False
    computer_unresolved_hit = False
    
    game_state = 'setup'
    turn_length = 1
    
def randomize_opponent_board():
    """Sets up the opponent's board randomly."""
    
    for ship in opponent_board.ships:
        ship.reset()
        
        horizontal = True
        tile = opponent_board.tiles[0][0]
        
        while (ship.main_tile == None
               or not opponent_board.ship_at_valid_position(tile, ship,
                                                            horizontal)):
            horizontal = random.choice((True, False))
            row = random.randint(0, 9)
            column = random.randint(0, 9)
            tile = opponent_board.tiles[column][row]
            ship.place_directly_at(tile, horizontal)
            opponent_board.update()
            
def set_text(sentence):
    """Sets the text to be displayed under the board."""
              
    global text_surface
              
    text_width = text_surface.get_rect().width
    text_surface.fill('white')
              
    if sentence != '':
        font = pygame.font.SysFont('arial', player_board.tile_size // 2)
        words = sentence.split()
        lines = []
        
        # break the sentence into lines that will fit on the text surface
        done = False
        n = 0
        while not done:
            line = ''
            test_string = words[n]
            while font.size(test_string)[0] < text_width:
                line += ' ' + words[n]
                test_string += ' ' + words[n+1]
                n += 1
                if n+1 == len(words):
                    line += ' ' + words[n]
                    done = True
                    break
                
            lines.append(line)
        
        # display each line on the text surface
        for y, line in enumerate(lines):
            text = font.render(line, True, 'black')
            text_rect = text.get_rect()
            text_rect.center = text_surface.get_rect().center
            text_rect.y = int(y * player_board.tile_size * 0.8)
            text_surface.blit(text, text_rect)
        
def start():
    """Changes the game state to 'player turn'."""
    
    global game_state
    game_state = 'player turn'
    set_text(("Your turn: Click the tile you want to guess on your opponent's"
              + " board. Red means hit, grey means miss. Have fun!"))
    
def computer_guess():
    """Simulates a guess from the opponent."""
    
    global turn_length
    global computer_unresolved_hit, computer_first_hit_column, \
           computer_first_hit_row, computer_last_hit_column, \
           computer_last_hit_row, not_up, not_right, not_down, not_left, \
           computer_knows_horizontal, computer_knows_vertical
    
    column = 0
    row = 0
    column_change = 0
    row_change = 0
    
    has_potential_guess = False
    
    # loop until there is a valid tile available to guess
    while (not has_potential_guess or player_board.get_tile(column, row) == None
               or player_board.tiles[column][row].guessed):
                
        # choose random point if there is no unresolved hit
        if not computer_unresolved_hit:
            column = random.randint(0, 9)
            row = random.randint(0, 9)
            
        else:
            column = computer_last_hit_column
            row = computer_last_hit_row
            column_change = 0
            row_change = 0

            if computer_knows_horizontal:
                if not_left and not_right:
                    # choose the point at the other end of the ship if there
                    # was a miss off one end
                    column = computer_first_hit_column
                    if computer_last_hit_column > computer_first_hit_column:
                        column_change = -1
                        not_left = False
                    else:
                        column_change = 1
                        not_right = False
                        
                elif not_left:
                    # choose point to the right if it is definitely horizontal
                    # but not left
                    column_change = 1
                    not_right = False
                elif not_right:
                    # choose point to the left if it is definitely horizontal
                    # but not right
                    column_change = -1
                    not_left = False
                else:
                    # choose random point horizontal to last hit if it is
                    # definitely horizontal but could be either end
                    column_change = random.choice((-1, 1))

            elif computer_knows_vertical:
                if not_up and not_down:
                    # choose the point at the other end of the ship if there
                    # was a miss off one end
                    row = computer_first_hit_row
                    if computer_last_hit_row > computer_first_hit_row:
                        row_change = -1
                        not_up = False
                    else:
                        row_change = 1
                        not_down = False
                        
                elif not_up:
                    # choose point below if it is definitely vertical but
                    # not up
                    row_change = 1
                    not_down = False
                elif not_down:
                    # choose point above if it is definitely vertical but
                    # not down
                    row_change = -1
                    not_up = False
                else:
                    # choose random point vertical to last hit if it is
                    # definitely vertical but could be either end
                    row_change = random.choice((-1, 1))
            else:
                # choose random point around last hit if nothing else is known
                if random.choice((True, False)):
                    column_change = random.choice((-1, 1))
                else:
                    row_change = random.choice((-1, 1))
                    
        column += column_change
        row += row_change
                    
        has_potential_guess = True
    
    # make the guess
    hit = player_board.guess(column, row)
    
    # analize hit or miss
    if hit:
        if not computer_unresolved_hit:
            computer_first_hit_column = column
            computer_first_hit_row = row

        computer_last_hit_column = column
        computer_last_hit_row = row
        
        computer_unresolved_hit = True
        
    if computer_unresolved_hit:
        # check for invalid future guesses around last hit
        if (player_board.get_tile(computer_last_hit_column,
                                  computer_last_hit_row - 1) == None
            or player_board.get_tile(computer_last_hit_column,
                                     computer_last_hit_row - 1).guessed):
            not_up = True

        if (player_board.get_tile(computer_last_hit_column,
                                  computer_last_hit_row + 1) == None
            or player_board.get_tile(computer_last_hit_column,
                                     computer_last_hit_row + 1).guessed):
            not_down = True
            
        if (player_board.get_tile(computer_last_hit_column - 1,
                                  computer_last_hit_row) == None
            or player_board.get_tile(computer_last_hit_column - 1,
                                     computer_last_hit_row).guessed):
            not_left = True
            
        if (player_board.get_tile(computer_last_hit_column + 1,
                                  computer_last_hit_row) == None
            or player_board.get_tile(computer_last_hit_column + 1,
                                     computer_last_hit_row).guessed):
            not_right = True
            
        # check if ship is definitly horizontal/vertical based on two adjacent
        # hits
        if (not computer_knows_vertical
            and computer_last_hit_column != computer_first_hit_column):
            computer_knows_horizontal = True
            
        elif (not computer_knows_horizontal
              and computer_last_hit_row != computer_first_hit_row):
            computer_knows_vertical = True
        
        # check if ship is definitely horizontal/vertical based on an invalid
        # future guess on either side of a single hit
        elif not computer_knows_vertical and not_up and not_down:
            computer_knows_horizontal = True
              
        elif not computer_knows_horizontal and not_left and not_right:
            computer_knows_vertical = True
    
    # reset all variables once the ship is sunk
    if hit and player_board.tiles[column][row].ship.sunk:
        not_up = False
        not_right = False
        not_down = False
        not_left = False
        computer_knows_horizontal = False
        computer_knows_vertical = False
        computer_unresolved_hit = False
        
        turn_length = 2
    
def check_win():
    """Returns True if either the player or the computer wins. Returns False
    otherwise.
    """

    for n, ship in enumerate(opponent_board.ships):
        if not ship.sunk:
            break
        elif n == 4:
            set_text('You won!')
            return True
        
    for n, ship in enumerate(player_board.ships):
        if not ship.sunk:
            break
        elif n == 4:
            set_text('Your opponent won')
            return True
    
    return False
        
def control_game_flow():
    """Changes the game state when appropriate."""
    
    global game_state, turn_length, tile_clicked
    
    # display one ship at a time until it is placed on the board.
    # display the ready button after all ships are placed
    if game_state == 'setup' or game_state == 'ready':
        for i, ship in enumerate(player_board.ships):
            if ship.main_tile == None:
                    ship.set_visible(True)
                    ship.lock(False)
                    break
            elif i == 4:
                game_state = 'ready'
                set_text('')
                ready_button.set_visible(True)
    
    # handle the player's turn
    elif game_state == 'player turn':
        if tile_clicked:
            first_turn = False
            render_graphics()
            time.sleep(turn_length)
            
            if check_win():
                game_state = 'game over'
            else:
                game_state = 'computer turn'
                set_text("Opponent's turn")
                tile_clicked = False 
    
    # handle the computer's turn
    elif game_state == 'computer turn':
        computer_guess()
        render_graphics()
        time.sleep(turn_length)
        
        if check_win():
            game_state = 'game over'
        else:
            game_state = 'player turn'
            set_text('Your turn')
    
    # display the play again button once there is a winner
    elif game_state == 'game over':
        play_again_button.set_visible(True)
        
    turn_length = 1
        
def render_graphics():
    """Displays everything on the screen."""
    
    screen.blit(text_surface, (text_x, under_boards_y))
    
    player_board.draw(screen, player_board_x, padding)
    opponent_board.draw(screen, opponent_board_x, padding)
    
    for s in player_board.ships:
        s.draw(screen)
    for s in opponent_board.ships:
        s.draw(screen)
        
    if game_state == 'ready':
        ready_button.draw(screen)
        
    if game_state == 'game over':
        play_again_button.draw(screen)
    
    pygame.display.flip()


def main():
    """Sets the window and its contents up then runs the main game loop.
    Handles events, game logic, and the display at 60 fps.
    """
    
    setup()
    
    global game_state, turn_length
    
    while True:
        #Process inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                
                # handle left clicks
                if pygame.mouse.get_pressed()[0] == True:
                    
                    if game_state == 'setup' or game_state == 'ready':
                        # check if ships are dragged
                        for s in player_board.ships:
                            if s.check_clicked(pygame.mouse.get_pos()):
                                # reset tiles occupied by the ship if it was
                                # already on the board
                                if s.main_tile != None:
                                    player_board.erase_ship(s)
                                pygame.mouse.get_rel()
                                break
                            
                        # check if ready button is clicked
                        ready_button.check_clicked(pygame.mouse.get_pos())
                    
                    elif game_state == 'player turn':
                        # check if opponent tiles are clicked
                        if opponent_board.check_clicked(pygame.mouse.get_pos()):
                            for column in opponent_board.tiles:
                                for tile in column:
                                    # guess the tile if it was clicked
                                    if (tile.check_clicked(pygame.mouse.get_pos())
                                            and not tile.guessed):
                                        # guess tile
                                        opponent_board.guess(tile.column,
                                                             tile.row)
                                        
                                        # make the ship visible once it is sunk
                                        if tile.ship != None and tile.ship.sunk:
                                            tile.ship.set_visible(True)
                                            turn_length = 2
                                            
                                        global tile_clicked
                                        tile_clicked = True
                                        break
                            
                    elif game_state == 'game over':
                        # check if play again button is clicked
                        play_again_button.check_clicked(pygame.mouse.get_pos())
                            
                
                # handle right clicks
                elif pygame.mouse.get_pressed()[2] == True:
                    
                    if game_state == 'setup' or game_state == 'ready':
                        # check if player ships are rotated
                        for s in player_board.ships:
                            if s.check_right_clicked(pygame.mouse.get_pos()):
                                # rotate ship if it is not on the board yet
                                if s.main_tile == None:
                                    s.rotate()
                                else:
                                    # rotate ship and reset its old tiles if it
                                    # was already on the board
                                    player_board.erase_ship(s)
                                    if player_board.ship_at_valid_position(
                                                    s.main_tile, s,
                                                    not s.horizontal):
                                        s.rotate()
                                break
            
            
            # handle mouse button releases
            elif event.type == pygame.MOUSEBUTTONUP:
                
                if game_state == 'setup' or game_state == 'ready':
                    # check if ships are released after being dragged 
                    for s in player_board.ships:
                        if s.dragged:
                            s.set_dragging(False)
                            
                            # check if ship is in a valid position before
                            # placing
                            done = False
                            valid = False
                            for column in player_board.tiles:
                                for t in column:
                                    if t.overlaps(s):
                                        if player_board.ship_at_valid_position(
                                                        t, s, s.horizontal):
                                            # place ship at the right tile if it
                                            # is valid
                                            s.place_at(t)
                                            valid = True
                                        done = True
                                        break
                                if done:
                                    break
                            
                            # send ship back to previous position if new
                            # position is not valid
                            if not valid:
                                s.glide_to_default_position()
                                    
                    # reset any tiles that a ship hovered over
                    for column in player_board.tiles:
                        for t in column:
                            t.cancel_hovered()

            
            # handle mouse movement
            elif event.type == pygame.MOUSEMOTION:
                
                if game_state == 'setup' or game_state == 'ready':
                    # check if ships are moved while being dragged
                    for s in player_board.ships:
                        if s.dragged == True:
                            s.drag(pygame.mouse.get_rel())
                            
                            # update tiles that the ship hovers over
                            for column in player_board.tiles:
                                for t in column:
                                    t.check_hovered(s)
                            break
                        
                    # check if ready button is hovered over
                    ready_button.check_hovered(pygame.mouse.get_pos())
                    
                elif game_state == 'game over':
                    # check if play again button is hovered over
                    play_again_button.check_hovered(pygame.mouse.get_pos())
        
        # handle game locic and display
        player_board.update()
        opponent_board.update()
        
        control_game_flow()
            
        screen.fill('white')    
        render_graphics()
        
        clock.tick(60)

if __name__ == '__main__':
    main()
