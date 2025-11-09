import sys
from .core import *

def chay_file(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        for dong in f:
            dong = dong.strip()
            if dong == "" or dong.startswith("#"):
                continue
            # Các lệnh cơ bản
            if dong.startswith("in "):
                in_ra(dong[3:].strip('"'))
            elif dong.startswith("cong "):
                _, a, b = dong.split()
                in_ra(cong(a, b))
            elif dong.startswith("tru "):
                _, a, b = dong.split()
                in_ra(tru(a, b))
            elif dong.startswith("dat "):
                ten, val = dong[4:].split("=")
                dat(ten.strip(), val.strip())
            elif dong.startswith("inbien "):
                inbien(dong[7:].strip())
            elif dong.startswith("ve_vuong "):
                _, x, y, size = dong.split()
                ve_hinh_vuong(int(x), int(y), int(size))
            elif dong in ["thoat", "exit"]:
                sys.exit()
            else:
                print(f"Khong hieu lenh: {dong}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        chay_file(sys.argv[1])
    else:
        print("Su dung: python -m text_python file.txtpy")
