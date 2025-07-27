import asyncio
import platform
import pygame
from config import WIDTH, HEIGHT, FPS
from input_handler import handle_input
from render import draw_scene

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Projection with Rotation")
font = pygame.font.SysFont("arial", 20)

async def main():
    while True:
        handle_input()
        draw_scene(screen, font)
        await asyncio.sleep(1 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
