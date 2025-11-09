import pygame

pygame.init()

# Biến toàn cục
bien = {}

# Hàm cơ bản
def in_ra(*args):
    print(*args)

def tao_cua_so(w, h):
    return pygame.display.set_mode((w,h))

def ve_hinh_vuong(x, y, size, mau):
    man_hinh = pygame.display.get_surface()
    pygame.draw.rect(man_hinh, mau, (x, y, size, size))
    pygame.display.flip()

def bien_tao(ten, gia_tri):
    bien[ten] = gia_tri

# Vòng lặp
def lap_lai(dieu_kien, hanh_dong):
    while eval(str(dieu_kien)):
        eval(str(hanh_dong))

# Điều kiện
def khi(dieu_kien, hanh_dong):
    if eval(str(dieu_kien)):
        eval(str(hanh_dong))

# Sự kiện bàn phím
def khi_nhan_phim(ham):
    running = True
    man_hinh = pygame.display.get_surface()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                ham(event.key)
    pygame.quit()

# Parser cú pháp mới
def chay_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    # Tách câu lệnh theo ;
    cau_lenh = [c.strip() for c in code.split(";") if c.strip()]

    # Map tên lệnh sang hàm Python
    mapping = {
        "in_ra": in_ra,
        "tao_cua_so": tao_cua_so,
        "ve_hinh_vuong": ve_hinh_vuong,
        "bien": bien_tao,
        "lap_lai": lap_lai,
        "khi": khi,
        "khi_nhan_phim": khi_nhan_phim
    }

    for c in cau_lenh:
        if "(" not in c:
            continue
        ten, thamso = c.split("(", 1)
        thamso = thamso.rstrip(")")
        args = eval("["+thamso+"]")
        if ten in mapping:
            mapping[ten](*args)
