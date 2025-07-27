import pygame
import platform
from config import WIDTH, HEIGHT, FPS
from input_handler import handle_input
from render import draw_scene

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Projection with Rotation")
font = pygame.font.SysFont("arial", 20)
clock = pygame.time.Clock()

def main():
    while True:
        handle_input()
        draw_scene(screen, font)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
