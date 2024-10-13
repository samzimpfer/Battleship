import pygame

class Button:
    
    def __init__(self, x, y, w, h, func, color, name='', show=True):
        """Defines a Rect to keep track of the button's position.
        Defines the function that will be executed when the button is clicked.
        Defines light and dark colors for if the button is hovered over by the
        mouse or not. Gives the button a name.
        """
        
        self.rect = pygame.Rect(x, y, w, h)
        self.surface = pygame.Surface((w, h,))
        
        self.func = func
        
        darkening = 20
        self.color = color
        self.light_color = color
        self.dark_color = self.get_darker_color(color, darkening)
        self.border_color = self.get_darker_color(self.dark_color,
                                                  darkening * 3)
        self.name = name
        
        self.show = show
        
    def set_visible(self, s):
        """Makes the button visible or invisible.
        Button cannot be clicked unless it is visible.
        """
        
        self.show = s
        
    def check_clicked(self, coords):
        """Returns True and runs the button's designated function if the button
        is clicked. Returns False otherwise.
        """
        
        if self.show:
            if self.rect.collidepoint(coords):
                self.func()
                return True
        return False
    
    def check_hovered(self, coords):
        """Returns True is the button is hovered over by the mouse. Darkens its
        color if so. Returns False and reverts the color to a lighter shade
        otherwise.
        """
        
        if self.show:
            if self.rect.collidepoint(coords):
                self.color = self.dark_color
                return True
            else:
                self.color = self.light_color

        return False
                
    def get_darker_color(self, color, amt):
        """Returns a shade of the color that is darker by the given amount."""
        r = color.r - amt
        if r > 255:
            r = 255
        elif r < 1:
            r = 1
        
        g = color.g - amt
        if g > 255:
            g = 255
        elif g < 1:
            g = 1
        
        b = color.b - amt
        if b > 255:
            b = 255
        elif b < 1:
            b = 1
        
        return pygame.Color(r, g, b)
        
    def draw(self, surf):
        """Displays the button if self.show=True.
        Writes the name on the button.
        """
        
        if self.show:
            self.surface.fill(self.color)
            
            font = pygame.font.SysFont('arial', int(self.rect.height * 0.8))
            text = font.render(self.name, True, self.border_color)
            text_rect = text.get_rect()
            text_rect.center = self.surface.get_rect().center
            self.surface.blit(text, text_rect)
            
            surf.blit(self.surface, self.rect)
            pygame.draw.rect(surf, self.border_color, self.rect, 3)