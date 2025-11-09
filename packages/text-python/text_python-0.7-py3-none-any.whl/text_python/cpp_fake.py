def chay_code_cpp_gian_don(code):
    dong = code.split('\n');
    env = {};
    for line in dong:
        line = line.strip();
        if line.startswith("int "):
            ten = line.split()[1].replace(';','');
            gia_tri = int(line.split()[-1].replace(';','')) if len(line.split()) > 2 else 0;
            env[ten] = gia_tri;
        elif line.startswith("for (int"):
            parts = line.replace('for (int','').replace(')','').split(';');
            bien = parts[0].strip().split()[0];
            start = int(parts[0].strip().split()[2]);
            cond = parts[1].strip();
            end_var = cond.split('<')[-1].strip();
            end = env.get(end_var, int(end_var));
            for i in range(start, end):
                env[bien] = i;
        elif 'cout' in line:
            args = line.split('<<');
            for arg in args[1:]:
                arg = arg.replace(';','').replace('"','');
                print(arg, end=" ");
    print();
