import pygame
import sys

# --- Khởi tạo ---
pygame.init()

# Tạo số biến động (tự quản lý namespace riêng)
_bien = {}

def bien(ten, gia_tri):
    """Tạo biến"""
    _bien[ten] = gia_tri

def in_ra(*noi_dung):
    """In ra màn hình"""
    print(*noi_dung)

def ve_cua_so(rong, cao, mau_nen=(255,255,255), tieu_de="Cua so"):
    """Tạo cửa sổ pygame"""
    man_hinh = pygame.display.set_mode((rong, cao))
    pygame.display.set_caption(tieu_de)
    man_hinh.fill(mau_nen)
    pygame.display.flip()
    return man_hinh

def ve_hinh_vuong(man_hinh, x, y, canh, mau=(0,0,0)):
    """Vẽ hình vuông"""
    pygame.draw.rect(man_hinh, mau, (x, y, canh, canh))
    pygame.display.flip()

def ve_hinh_tron(man_hinh, x, y, bk, mau=(0,0,0)):
    """Vẽ hình tròn"""
    pygame.draw.circle(man_hinh, mau, (x, y), bk)
    pygame.display.flip()

def khi_nhan_phim():
    """Lấy sự kiện bàn phím"""
    for sk in pygame.event.get():
        if sk.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if sk.type == pygame.KEYDOWN:
            return sk.key
    return None

def ket_thuc():
    pygame.quit()
    sys.exit()

# --- Cho phép import toàn cục ---
globals().update({
    'bien': bien,
    'in_ra': in_ra,
    've_cua_so': ve_cua_so,
    've_hinh_vuong': ve_hinh_vuong,
    've_hinh_tron': ve_hinh_tron,
    'khi_nhan_phim': khi_nhan_phim,
    'ket_thuc': ket_thuc
})
