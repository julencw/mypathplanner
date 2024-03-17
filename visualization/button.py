import pygame


class Button:
    def __init__(
            self,
            x: int,
            y: int,
            img: pygame.Surface,
            scale: float,
    ) -> None:
        width = img.get_width()
        height = img.get_height()
        self.or_img = pygame.transform.scale(
            img, (int(width * scale), int(height * scale)))
        self.clicked_img = self.darken_image(self.or_img, 0.95)
        self.img = self.or_img
        self.rect = self.img.get_rect()
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)
        self.clicked = False

    def darken_image(self, img: pygame.Surface, scale: float) -> pygame.Surface:
        scaled_img = pygame.transform.scale(
            img, (int(img.get_width() * scale), int(img.get_height() * scale)))

        darkened_img = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)

        for y in range(scaled_img.get_height()):
            for x in range(scaled_img.get_width()):
                # Get the color of the pixel
                color = scaled_img.get_at((x, y))
                # Darken the color by multiplying its RGB values by 0.7
                # (adjust this value as needed)
                darkened_color = (
                    int(color[0] * 0.7),
                    int(color[1] * 0.7),
                    int(color[2] * 0.7),
                    color[3],
                )
                # Set the color of the pixel in the new surface
                darkened_img.set_at((x, y), darkened_color)

        return darkened_img

    def click(self) -> None:
        self.rect = self.clicked_img.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.img = self.clicked_img

    def unclick(self) -> None:
        self.rect = self.or_img.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.img = self.or_img

    def draw(self, window: pygame.Surface) -> bool:
        action = False
        mouse_position = pygame.mouse.get_pos()
        if (self.rect.collidepoint(mouse_position)
                and pygame.mouse.get_pressed()[0]
                and not self.clicked):
            self.clicked = True
            action = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        window.blit(self.img, (self.rect.x, self.rect.y))
        return action
