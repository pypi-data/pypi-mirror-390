import tkinter as tk;

giao_dien = None;

def tao_giao_dien():
    global giao_dien;
    giao_dien = tk.Tk();
    return giao_dien;

def tao_nut(chu_thich, hanh_dong):
    global giao_dien;
    nut = tk.Button(giao_dien, text=chu_thich, command=hanh_dong);
    nut.pack();

def tao_nhan(chu_thich):
    global giao_dien;
    nhan = tk.Label(giao_dien, text=chu_thich);
    nhan.pack();

def chay_giao_dien():
    global giao_dien;
    giao_dien.mainloop();
