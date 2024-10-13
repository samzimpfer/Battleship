import pygame

class Tile:
    
    # define colors to be used in each tile
    BLUE = pygame.Color(60, 160, 190)
    DARK_BLUE = pygame.Color(20, 120, 150)
    RED = pygame.Color(220, 20, 20)
    GREY = pygame.Color(180, 170, 160)
    
    def __init__(self, board, c=0, r=0, s=0):
        """Gives the tile a column and a row.
        Initializes a Rect and a Surface to draw the tile in.
        Sets up varibales to control its interaction with the player.
        """
        
        self.board = board
        self.column = c
        self.row = r
        self.size = s
        
        self.rect = pygame.Rect(0, 0, s, s)
        self.surface = pygame.Surface((s, s))
        self.color = self.BLUE
        
        self.hovered = False
        self.ship = None
        self.adjacent_ships = []
        self.guessed = False
        self.pin_color = None
        
    def reset(self):
        """Reverts the tile to its original state."""
        
        self.hovered = False
        self.ship = None
        self.adjacent_ships = []
        self.guessed = False
        self.pin_color = None
        
    def set_pos(self, grid):
        """Sets the position of the tile on the screen based on the position of
        the grid of the board the tile belongs to and the column/row the tile
        is in.
        """
        
        self.rect.update(grid.x + (self.column * self.size),
                         grid.y + (self.row * self.size), self.size, self.size)
        
    def check_hovered(self, ship):
        """Darkens the color of the tile if a ship is hovering over more than
        half of it.
        """
        
        if self.overlaps(ship) and ship.dragged:
            self.hovered = True
            self.color = self.DARK_BLUE
        else:
            self.hovered = False
            self.color = self.BLUE
            
    def overlaps(self, ship):
        """Returns True if a ship is hovering over more than half of the tile.
        """
        
        if self.rect.colliderect(ship.rect):
            if (ship.rect.left < self.rect.right - (self.size // 2)
                    and ship.rect.right > self.rect.left + (self.size // 2)
                    and ship.rect.top < self.rect.bottom - (self.size // 2)
                    and ship.rect.bottom > self.rect.top + (self.size // 2)):
                return True
        return False
            
    def cancel_hovered(self):
        """Reverts the tile to its original color."""
        
        self.hovered = False
        self.color = self.BLUE
        
    def check_clicked(self, coords):
        """Returns true if the tile is clicked."""
        
        return self.rect.collidepoint(coords)
    
    def guess(self):
        """Returns True and changes the tile color to red if it is a hit.
        Also puts a red circle on the ship where the hit is.
        Returns False and changes the tile color to grey if it is a miss.
        """
        
        self.guessed = True
        if self.ship != None:
            self.ship.hit(self)
            self.pin_color = self.RED
            return True
        else:
            self.pin_color = self.GREY
            return False
    
    def draw(self, surf):
        """Draws the tile on the screen."""
        
        self.surface.fill(self.color)
        if self.guessed:
            pygame.draw.circle(self.surface, self.pin_color, (self.size // 2, self.size // 2), self.size // 4)
        pygame.draw.rect(self.surface, 'black', pygame.Rect(0, 0, self.size, self.size), 1)
        surf.blit(self.surface, (self.column * self.size, self.row * self.size))
        
    def __str__(self):
        """Returns a string the represent the tile in the format {column}{row}.
        (Example: A1)
        """
        
        return chr(65 + self.column) + str(self.row + 1)
