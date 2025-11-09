import pygame

pygame.init()

# Hàm in ra
def in_ra(*noi_dung):
    print(*noi_dung);

# Tạo màn hình
def tao_manhinh(kich_thuoc):
    man_hinh = pygame.display.set_mode(kich_thuoc);
    return man_hinh;

# Vẽ hình vuông
def ve_hinh_vuong(screen, mau, vi_tri, kich_thuoc):
    pygame.draw.rect(screen, mau, (*vi_tri, kich_thuoc, kich_thuoc));

# Vẽ hình tròn
def ve_hinh_tron(screen, mau, tam, ban_kinh):
    pygame.draw.circle(screen, mau, tam, ban_kinh);

# Vòng lặp đơn giản
def lap_lai(so_lan, ham, *args):
    for i in range(so_lan):
        ham(*args);
