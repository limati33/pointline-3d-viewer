import pygame
from config import WIDTH, HEIGHT
from render import draw_scene
from input_handler import handle_event

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Viewer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                handle_event(event)

        draw_scene(screen, font)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
