# -*- coding: utf-8 -*-
import pygame
import sys

# Lưu biến
bien = {}

# ----------- Hàm cơ bản của text_python -----------

def in_ra(van_ban):
    """In ra màn hình"""
    print(van_ban)

def cong(a, b):
    try:
        return float(a) + float(b)
    except:
        print("Loi: chi cong duoc so hoac chuoi")

def tru(a, b):
    try:
        return float(a) - float(b)
    except:
        print("Loi: tru chi ap dung voi so")

def dat(ten, gia_tri):
    bien[ten] = gia_tri

def inbien(ten):
    if ten in bien:
        print(bien[ten])
    else:
        print("Bien khong ton tai")

# ----------- Pygame module -----------

def tao_cua_so(rong, cao, tieu_de="text_python window"):
    pygame.init()
    man_hinh = pygame.display.set_mode((rong, cao))
    pygame.display.set_caption(tieu_de)
    return man_hinh

def ve_hinh_vuong(x, y, size, mau=(255,0,0)):
    surface = pygame.display.get_surface()
    if surface:
        pygame.draw.rect(surface, mau, (x, y, size, size))
        pygame.display.flip()
    else:
        print("Chua tao cua so pygame!")

def cho_dong_cua_so():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
