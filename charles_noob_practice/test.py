import pygame as pg
import random
pg.init()
pg.mixer.init()
clock=pg.time.Clock()
w,h=1300,700
screen=pg.display.set_mode((w,h))
pg.display.set_caption("practice")
bg=pg.Surface(screen.get_size())
bg=bg.convert()
bg.fill((255,255,255)) # white
picture1=pg.image.load("picture/sybau/sybau1.png")
picture1.convert()
picture1=pg.transform.rotozoom