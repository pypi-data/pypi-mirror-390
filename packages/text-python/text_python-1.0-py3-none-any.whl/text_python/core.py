import pygame;
pygame.init();

man_hinh = None;

def tao_manhinh(kich_thuoc):
    global man_hinh;
    man_hinh = pygame.display.set_mode(kich_thuoc);
    return man_hinh;

def cap_nhat_man_hinh():
    pygame.display.update();

def ve_hinh_vuong(screen, mau, toa_do, kich_thuoc):
    pygame.draw.rect(screen, mau, (toa_do[0], toa_do[1], kich_thuoc, kich_thuoc));

def ve_hinh_tron(screen, mau, toa_do, ban_kinh):
    pygame.draw.circle(screen, mau, (toa_do[0], toa_do[1]), ban_kinh);

def in_ra(*noi_dung):
    print(*noi_dung);

def lap_lai(so_lan, ham, *tham_so):
    for i in range(so_lan):
        ham(*tham_so);
