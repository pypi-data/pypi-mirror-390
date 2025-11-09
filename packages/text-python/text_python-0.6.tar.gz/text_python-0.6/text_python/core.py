import re
import pygame
import sys
import math
import random

# =====================
# Hàm Việt hóa
# =====================
def in_ra(*noi_dung):
    print(*noi_dung)

# =====================
# Cú pháp C/C++ đơn giản
# =====================
def chay_code_c_gian_don(code: str):
    """
    Hỗ trợ:
      - int x = 5;
      - for (int i=0; i<10; i++)
      - in_ra(...)
    """
    code = code.replace(";", "\n")
    code = re.sub(r"\bint\s+(\w+)\s*=\s*(.+)", r"\1 = \2", code)
    code = re.sub(
        r"for\s*\(\s*int\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<\s*(\d+)\s*;\s*\1\+\+\s*\)",
        r"for \1 in range(\2,\3):",
        code
    )
    exec(code, globals())

# =====================
# Các hàm Pygame cơ bản
# =====================
def ve_hinh_vuong(manhinh, mau, vitri, kichthuoc):
    pygame.draw.rect(manhinh, mau, (*vitri, kichthuoc, kichthuoc))

def ve_hinh_tron(manhinh, mau, vitri, ban_kinh):
    pygame.draw.circle(manhinh, mau, vitri, ban_kinh)

# =====================
# Vòng lặp / điều kiện Việt hóa
# =====================
def lap_lai(lan, ham, *args):
    for _ in range(lan):
        ham(*args)

def khi(dieu_kien, ham, *args):
    if dieu_kien:
        ham(*args)

def khi_nhan_phim(phim, ham, *args):
    keys = pygame.key.get_pressed()
    if keys[phim]:
        ham(*args)
