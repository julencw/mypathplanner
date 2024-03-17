import sys
from enum import Enum, StrEnum

import pygame
import pygame_gui

from grid.node import Node, NodeType
from visualization.button import Button


class TaskSetting(StrEnum):
    DEFAULT = "default"
    WAYPOINT = "waypoint"
    ELEVATION = "elevation"
    OPTIONS = "options"
    QUIT = "quit"

# -- Visualization of the grid and the pathfinding algorithm --


class CommonColors(Enum):
    GREY = (128, 128, 128)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_BLUE = (52, 78, 91)
    DARK_BROWN = (107, 67, 33)


COLORS = {
    NodeType.START: (235, 214, 202),
    NodeType.END: (195, 197, 177),
    NodeType.OBSTACLE: (50, 50, 50),
    NodeType.WAYPOINT: (145, 191, 74),
    NodeType.FREE: (249, 249, 249),
    NodeType.OPEN: (187, 210, 229),
    NodeType.CLOSED: (140, 157, 173),
    NodeType.PATH: (210, 218, 136),
}

# colors for elevation levels should be different brown tones, with level 0
# being white and level 5 being dark brown
ELEVATION_COLORS: dict[int, tuple[int, int, int]] = {}

BUTTONS: dict[TaskSetting, pygame.Surface] = {
    TaskSetting.DEFAULT: pygame.image.load("images/setting_1.png"),
    TaskSetting.WAYPOINT: pygame.image.load("images/setting_2.png"),
    TaskSetting.ELEVATION: pygame.image.load("images/setting_3.png"),
    # TaskSetting.OPTIONS: pygame.image.load("images/options.png"),
    TaskSetting.QUIT: pygame.image.load("images/quit.png"),
}


class Visualization:
    def __init__(
        self,
        window_width: int,
        window_height: int,
        topbar_height: int,
        task_setting: TaskSetting | None,
        max_elevation: int,
        elevation_step: int,
    ) -> None:
        pygame.init()
        self.task_setting = task_setting
        self.window_width = window_width
        self.window_height = window_height
        self.topbar_height = topbar_height
        self.window = pygame.display.set_mode(
            (self.window_width, self.window_height))
        self.load_buttons()
        self.click_button()
        self.clock = pygame.time.Clock()
        self.generate_brown_colors(max_elevation + elevation_step)

        self.pygame_gui_manager = pygame_gui.UIManager(
            (self.window_width, self.window_height))

    def load_buttons(self) -> None:
        self.buttons: dict[TaskSetting, Button] = {}
        img_scaler = 0.4
        for n_buttons, button in enumerate(BUTTONS):
            button_width = BUTTONS[button].get_width()
            x_position = 15 * (n_buttons + 1) + n_buttons * \
                button_width * img_scaler
            y_position = 10
            button_image = BUTTONS[button]
            button_scaler = img_scaler
            self.buttons[button] = Button(
                int(x_position), y_position, button_image, button_scaler)

    # Accessors
    def get_window(self) -> pygame.Surface:
        return self.window

    # Modifiers
    def set_task_setting(self, task_setting: TaskSetting) -> None:
        self.task_setting = task_setting

    def unclick_button(self) -> None:
        if self.task_setting is not None:
            self.buttons[self.task_setting].unclick()

    def click_button(self) -> None:
        if self.task_setting is not None:
            self.buttons[self.task_setting].click()

    def setup_text_entry(self) -> None:
        self.waypoint_textbox = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                (self.window_width/4, self.window_width/2),
                (self.window_width/2, 70)),
            manager=self.pygame_gui_manager,
            object_id="#num_waypoints",
            placeholder_text="Enter number of waypoints",
        )

    def darken_window(self) -> None:
        # darken window
        overlay = pygame.Surface(
            (self.window_width, self.window_height), pygame.SRCALPHA)
        # Fill the surface with semi-transparent black
        overlay.fill((0, 0, 0, 128))
        # Blit the semi-transparent surface onto the window
        self.window.blit(overlay, (0, 0))

    def waypoint_popup(self) -> int:
        self.darken_window()
        self.setup_text_entry()
        while True:
            ui_refresh_rate = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
                        event.ui_object_id == "#num_waypoints"):
                    # check if the input is a number
                    if event.text.isdigit():
                        return int(event.text)
                    print("Please enter a number")  # TODO: popup?
                    self.setup_text_entry()

                self.pygame_gui_manager.process_events(event)

            self.pygame_gui_manager.update(ui_refresh_rate)
            self.pygame_gui_manager.draw_ui(self.window)
            pygame.display.update()
            pygame.display.flip()

    def draw_topbar(self) -> tuple[TaskSetting | None, int | None]:
        pygame.draw.rect(self.window, CommonColors.DARK_BLUE.value,
                         (0, 0, self.window_width, self.topbar_height))
        for button in self.buttons:
            if self.buttons[button].draw(self.window):
                self.unclick_button()
                self.task_setting = button
                self.click_button()
                num_waypoints = None
                if self.task_setting == TaskSetting.WAYPOINT:
                    num_waypoints = self.waypoint_popup()

                return button, num_waypoints
        return None, None

    def draw_text(
            self,
            text: str,
            font_name: str,
            text_size: int,
            color: tuple[int, int, int],
            x: int,
            y: int,
    ) -> None:
        font = pygame.font.SysFont(font_name, text_size)
        text_surface: pygame.Surface = font.render(text, 1, color)
        self.window.blit(text_surface, (x, y))

    def draw_node(self, node: Node, rows: int, cols: int) -> None:
        cell_width = self.window_width // cols
        board_height = (self.window_height - self.topbar_height)
        cell_height = board_height // rows
        row, col = node.get_position()
        x = col * cell_width
        y = row * cell_height

        if node.get_terrain_level() > 0:
            elevation_color = ELEVATION_COLORS[node.get_terrain_level()]
            color = elevation_color if node.get_type() == NodeType.FREE else (
                COLORS[node.get_type()])
            pygame.draw.rect(
                self.window, color,
                (x, y + self.topbar_height, cell_width, cell_height),
            )
        else:
            pygame.draw.rect(
                self.window, COLORS[node.get_type()],
                (x, y + self.topbar_height, cell_width, cell_height),
            )

    def draw_grid_lines(self, rows: int, cols: int) -> None:
        cell_width = self.window_width // cols
        cell_height = (self.window_height - self.topbar_height) // rows
        for i in range(cols):
            # vertical lines
            pygame.draw.line(self.window,
                             CommonColors.GREY.value,
                             (i * cell_width, self.topbar_height),
                             (i * cell_width, self.window_height))
            for j in range(rows):
                # horizontal lines
                pygame.draw.line(
                    self.window,
                    CommonColors.GREY.value,
                    (0, self.topbar_height + j * cell_height),
                    (self.window_width, self.topbar_height + j * cell_height),
                )

    def draw_board(
            self,
            grid: list[list[Node]],
            n_rows: int,
            n_cols: int,
    ) -> None:
        # it should only fill the window part
        # belonging to the grid which is below the topbar
        board_rect: tuple[int, int, int, int] = (
            0,
            self.topbar_height,
            self.window_width,
            self.window_height - self.topbar_height,
        )
        self.window.fill(CommonColors.GREY.value, board_rect)

        for row in grid:
            for node in row:
                self.draw_node(node, n_rows, n_cols)

        self.draw_grid_lines(n_rows, n_cols)
        pygame.display.update()

    def normalize_mouse_position(
            self,
            mouse_position: tuple[int, int],
    ) -> tuple[int, int]:
        x, y = mouse_position
        return x, y - self.topbar_height

    def generate_brown_colors(self, num_colors: int) -> None:
        light_brown = CommonColors.WHITE.value
        dark_brown = CommonColors.DARK_BROWN.value

        step_r = (dark_brown[0] - light_brown[0]) / (num_colors - 1)
        step_g = (dark_brown[1] - light_brown[1]) / (num_colors - 1)
        step_b = (dark_brown[2] - light_brown[2]) / (num_colors - 1)

        for i in range(num_colors):
            r = int(light_brown[0] + i * step_r)
            g = int(light_brown[1] + i * step_g)
            b = int(light_brown[2] + i * step_b)
            ELEVATION_COLORS[i] = (r, g, b)
