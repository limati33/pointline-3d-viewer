import pygame
from config import WIDTH, HEIGHT
from render import draw_scene, set_render_context
from input_handler import handle_input

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Viewer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24)

    # Инициализация контекста рендеринга
    set_render_context(screen, font)

    running = True
    while running:
        handle_input()  # Вызываем handle_input вместо handle_event
        draw_scene(screen, font)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()