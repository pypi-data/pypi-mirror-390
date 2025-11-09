def chay_code_cpp_gian_don(code):
    dong_cuoi = None;
    lines = code.split(";");
    for dong in lines:
        dong = dong.strip();
        if dong.startswith("for"):
            parts = dong.split(" ");
            n = int(parts[-1]) if parts[-1].isdigit() else 0;
            for i in range(n):
                print("C++ loop", i);
            dong_cuoi = i;
        elif dong.startswith("cout"):
            args = dong[dong.find("<<")+2:];
            print(args);
