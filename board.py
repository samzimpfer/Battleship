import pygame
import time

from tile import Tile
from ship import Ship

class Board:
    def __init__(self, w, gs, turn_length, title='', pb=False):
        """Sets up a grid of a specified size to fit inside the width given.
        Sets up letter labels for columns and number labels for rows.
        Gives the board a title.
        """
        
        self.is_player_board = pb
        
        self.grid_size = gs
        self.tile_size = w // (gs + 1)
        self.width = self.tile_size * (self.grid_size + 1)
        self.height = self.tile_size * (self.grid_size + 2)
        self.tiles = []
            
        self.board_x = 0
        self.board_y = 0
        self.grid_rect = pygame.Rect(0, 0, self.tile_size * self.grid_size,
                                     self.tile_size * self.grid_size)
        self.set_pos(0, 0)
            
        self.ships = []
            
        # display the title of the board on the board's surface
        font = pygame.font.SysFont('arial', int(self.tile_size * 0.8))
        title_surface = pygame.Surface((self.tile_size * (self.grid_size + 1),
                                        self.tile_size))
        title_surface.fill('white')
        text = font.render(title, True, 'black')
        text_rect = text.get_rect()
        text_rect.center = title_surface.get_rect().center
        title_surface.blit(text, text_rect)
        
        # display the letter labels on the board's surface
        font = pygame.font.SysFont('arial', self.tile_size // 2)
        letter_labels = pygame.Surface((self.tile_size * self.grid_size,
                                        self.tile_size))
        letter_labels.fill('white')
        
        for x in range(self.grid_size):
            text = font.render(chr(65 + x), True, 'black')
            outer_rect = pygame.Rect(x * self.tile_size, 0, self.tile_size,
                                     self.tile_size)
            text_rect = text.get_rect()
            text_rect.center = outer_rect.center
            letter_labels.blit(text, text_rect)
        
        # display the number labels on the board's surface
        number_labels = pygame.Surface((self.tile_size,
                                        self.tile_size * self.grid_size))
        number_labels.fill('white')
            
        for y in range(self.grid_size):
            text = font.render(str(y+1), True, 'black')
            outer_rect = pygame.Rect(0, y * self.tile_size, self.tile_size,
                                     self.tile_size)
            text_rect = text.get_rect()
            text_rect.center = outer_rect.center
            number_labels.blit(text, text_rect)
        
        # display each tile on the board's surface
        self.grid = pygame.Surface((self.tile_size * self.grid_size,
                                    self.tile_size * self.grid_size))
        
        for c in range(self.grid_size):
            column = []
            for r in range(self.grid_size):
                tile = Tile(self, c, r, self.tile_size)
                column.append(tile)
            self.tiles.append(column)
        
        # add a surface for text below the board
        self.text = pygame.Surface((0, 0))
        self.text.fill('white')
        self.text_rect = text.get_rect()
        self.previous_time = 0
        self.has_text = False
        
        # create the main surface to contain the title, labels, and tile grid
        self.surface = pygame.Surface((self.tile_size * (self.grid_size + 1),
                                       int(self.tile_size * (self.grid_size + 2))))
        self.surface.fill('white')
        self.surface.blit(title_surface, (0, 0))
        self.surface.blit(letter_labels, (self.tile_size, self.tile_size))
        self.surface.blit(number_labels, (0, self.tile_size * 2))
        self.surface.blit(self.grid, (self.tile_size, self.tile_size * 2))
        
        self.turn_length = turn_length
        
    def reset(self):
        """Resets each tile on the board."""
        
        for column in self.tiles:
            for tile in column:
                tile.reset()
        
    def set_pos(self, x, y):
        """Set's the board's position inside the window."""
        
        self.board_x = x
        self.board_y = y
        self.grid_rect.update(x + self.tile_size, y + (self.tile_size * 2),
                              self.grid_rect.width, self.grid_rect.height)
        
        for column in self.tiles:
            for tile in column:
                tile.set_pos(self.grid_rect)
                
    def set_text(self, line):
        """Displays text under the board to tell the player whether a guess is
        a hit or a miss.
        """
        
        font = pygame.font.SysFont('arial', self.tile_size // 2)
        self.text.fill('white')
        self.text = font.render(line, True, 'black')
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.grid_rect.center
        self.text_rect.y = self.board_y + self.height + (self.tile_size // 2)
        
        # sets a timer to make to text go away after 1 turn length
        self.previous_time = time.time()
        self.has_text = True
        
    def add_ship(self, name, length, x=0, y=0, show=True, locked=False):
        """Adds a ship to self.ships without placing it at a specific tile."""
        
        ship = Ship(name, length, self.tile_size, x, y, show, locked)
        self.ships.append(ship)

    def erase_ship(self, ship):
        """Takes a ship off the board and resets all the tiles the ship was on.
        """
        
        if ship.main_tile != None:
            column = ship.main_tile.column
            row = ship.main_tile.row
            
            for _ in range(ship.length):
                t = self.tiles[column][row]
                
                t.ship = None 
                
                if ship.horizontal:
                    column += 1
                else:
                    row += 1
                    
    def check_clicked(self, coords):
        """Returns True if the grid of tiles is clicked. Returns False
        otherwise.
        """
        
        return self.grid_rect.collidepoint(coords)

    def ship_at_valid_position(self, tile, ship, horizontal):
        """Checks whether a ship would be in a valid position if it is placed
        with its top left corner at a certain tile, and is either horizontal or
        vertical. Returns False if the ship is partially off the board, or if
        the ship overlaps another, or if the ship is right next to another ship.
        """
        
        column = tile.column
        row = tile.row
        
        for _ in range(ship.length):
            # make sure the ship isn't hanging off the board
            try:
                t = self.tiles[column][row]
            except IndexError:
                return False
            
            # make sure the ship isn't overlapping another
            if t.ship != None and t.ship != ship:
                return False
            
            if horizontal == ship.horizontal:
                # make sure the ship isn't right next to another in the case
                # that it is already rotated to the correct orientation
                if len(t.adjacent_ships) > 1:
                    return False
            else:
                # make sure the ship isn't right next to another in the case
                # that the user wants to rotate the ship
                if len(t.adjacent_ships) > 0 and ship not in t.adjacent_ships:
                    return False
            
            if horizontal:
                column += 1
            else:
                row += 1
            
        return True
    
    def guess(self, column, row):
        """Guesses a tile. Returns True if it is a hit and False if it is a
        miss.
        """
        
        hit = self.tiles[column][row].guess()
        
        # display appropriate text below the board to respond to a hit or miss
        if hit:
            self.set_text('Hit!')
            ship = self.tiles[column][row].ship
            if ship.sunk:
                if self.is_player_board:
                    self.set_text(f'Hit, your opponent sunk your {ship.name}')
                else:
                    self.set_text(f"Hit! You sunk your opponent's {ship.name}!")
                
                # turns all of the tiles around the ship into misses since
                # there can't be another ship right next to the ship that was
                # just sunk
                for column in self.tiles:
                    for tile in column:
                        if ship in tile.adjacent_ships and not tile.guessed:
                            tile.guess()
        else:
            self.set_text('Miss')
        
        return hit
    
    def get_tile(self, column, row):
        """Returns a tile in the specified column and row. Returns None if the
        tile is out of range.
        """
        
        if column < 0 or row < 0:
            return None
        
        try:
            return self.tiles[column][row]
        except IndexError:
            return None

    def update(self):
        """Updates each tile to know whether it contains a ship and whether
        there is a ship right next to it.
        """
        
        # check if each tile contains contains a ship
        for column in self.tiles:
            for t in column:
                done = False
                for s in self.ships:
                    if t.overlaps(s):
                        t.ship = s
                        done = True
                        break
                if not done:
                    t.ship = None
        
        # check if each tile is adjacent to a ship
        for column in self.tiles:
            for test_tile in column:
                # this loop cycles through every tile on the board
                test_tile.adjacent_ships = []
                for c in range(test_tile.column - 1, test_tile.column + 2):
                    for r in range(test_tile.row - 1, test_tile.row + 2):
                        # this loop cycles through every tile around the
                        # test_tile
                        comparison_tile = self.get_tile(c, r)
                        # check if each tile adjacent to the test tile exists
                        # and contains a ship
                        if (comparison_tile != None
                                and comparison_tile.ship != None):
                            # make sure the tile's list of adjacent ships
                            # doesn't already contain the ship
                            if (comparison_tile.ship not in
                                    test_tile.adjacent_ships):
                                test_tile.adjacent_ships.append(
                                    comparison_tile.ship)                    
        
    def draw(self, surf, x, y):
        """Displays the board at a specific location on the screen.
        (Used in addition to simply blitting onto the screen so that tiles can
        have a known location on the screen and be clickable.)
        Erases text under the board after 1 turn length.
        """
        
        # erase any txt under the board after 1 turn length
        if self.has_text and time.time() > (self.previous_time
                                            + self.turn_length):
            self.set_text('')
            self.has_text = False
        
        # set the position of the grid and each tile, then draw the tiles onto
        # the board
        self.set_pos(x, y)
        for column in self.tiles:
            for t in column:
                t.draw(self.grid)
        
        # draw the entire board
        self.surface.blit(self.grid, (self.tile_size, self.tile_size * 2))
        surf.blit(self.surface, (x, y))
        surf.blit(self.text, self.text_rect)
