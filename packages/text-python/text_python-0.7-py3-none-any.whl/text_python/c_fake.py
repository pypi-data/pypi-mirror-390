def chay_code_c_gian_don(code):
    # giả lập code C đơn giản, chỉ for/int/print
    dong = code.split('\n');
    env = {};
    for line in dong:
        line = line.strip();
        if line.startswith("int "):
            ten = line.split()[1];
            gia_tri = int(line.split()[-1]) if len(line.split()) > 2 else 0;
            env[ten] = gia_tri;
        elif line.startswith("for (int"):
            # ví dụ: for (int i = 0; i < n; i++)
            parts = line.replace('for (int','').replace(')','').split(';');
            bien = parts[0].strip().split()[0];
            start = int(parts[0].strip().split()[2]);
            cond = parts[1].strip();
            end_var = cond.split('<')[-1].strip();
            end = env.get(end_var, int(end_var));
            for i in range(start, end):
                env[bien] = i;
        elif line.startswith('in_ra'):
            args = line[line.find('(')+1:line.rfind(')')];
            args = args.replace('"','');
            print(args, end=" ");
    print();
