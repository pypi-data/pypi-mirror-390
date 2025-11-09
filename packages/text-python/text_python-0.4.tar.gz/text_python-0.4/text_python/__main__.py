from .core import chay

while True:
    try:
        dong = input(">>> ")
        chay(dong)
    except SystemExit:
        break
    except Exception as e:
        print("Loi:", e)
