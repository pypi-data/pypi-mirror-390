import pygame, sys, builtins

pygame.init()

# --- Bien toan cuc ---
_bien = {}

# --- Ham co ban ---
def bien(ten, gia_tri):
    _bien[ten] = gia_tri
    globals()[ten] = gia_tri

def in_ra(*nd):
    print(*nd)

def ve_cua_so(rong, cao, mau=(255,255,255), tieu_de="Cua so"):
    man_hinh = pygame.display.set_mode((rong, cao))
    pygame.display.set_caption(tieu_de)
    man_hinh.fill(mau)
    pygame.display.flip()
    return man_hinh

def ve_hinh_vuong(mh, x, y, canh, mau=(0,0,0)):
    pygame.draw.rect(mh, mau, (x, y, canh, canh))
    pygame.display.flip()

def ve_hinh_tron(mh, x, y, bk, mau=(0,0,0)):
    pygame.draw.circle(mh, mau, (x, y), bk)
    pygame.display.flip()

def khi_nhan_phim():
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

# --- Bo sung toan bo ham co san cua Python va Pygame ---
def _nap_tat_ca():
    for ten in dir(builtins):
        if not ten.startswith("_"):
            globals()[ten] = getattr(builtins, ten)
    for ten in dir(pygame):
        if not ten.startswith("_"):
            globals()[ten] = getattr(pygame, ten)

_nap_tat_ca()

# --- Trinh phan tich cau lenh bang dau ; ---
def chay(code: str):
    """Chay code voi dau ; nhu C"""
    for dong in code.split(";"):
        dong = dong.strip()
        if dong:
            exec(dong, globals())

# --- Dang ky tat ca ham vao all ---
all = {
    "bien": bien,
    "in_ra": in_ra,
    "ve_cua_so": ve_cua_so,
    "ve_hinh_vuong": ve_hinh_vuong,
    "ve_hinh_tron": ve_hinh_tron,
    "khi_nhan_phim": khi_nhan_phim,
    "ket_thuc": ket_thuc,
    "chay": chay
}
globals().update(all)
