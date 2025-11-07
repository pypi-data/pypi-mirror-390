#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, subprocess, shutil

ISOLATE_BIN = "isolate"
BOX_ID = 1
BOX_PATH = f"/var/local/lib/isolate/{BOX_ID}/box"


def compile_cpp(source_path, exe_path):
    """编译 C++ 源文件"""
    try:
        result = subprocess.run(
            ["g++", "-O2", "-std=c++17", source_path, "-o", exe_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20
        )
        if result.returncode != 0:
            return False, result.stderr
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "Compilation timed out"


def init_box():
    """初始化 isolate box"""
    subprocess.run([ISOLATE_BIN, f"--box-id={BOX_ID}", "--init"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def cleanup_box():
    """清理 isolate box"""
    subprocess.run([ISOLATE_BIN, f"--box-id={BOX_ID}", "--cleanup"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_in_box(exe_name, input_data, time_limit, memory_limit):
    """在已初始化的 box 内运行程序"""
    input_file = os.path.join(BOX_PATH, "input.txt")
    output_file = os.path.join(BOX_PATH, "output.txt")
    error_file = os.path.join(BOX_PATH, "error.txt")
    meta_file = "./meta.txt"

    with open(input_file, "w") as f:
        f.write(input_data)

    cmd = [
        ISOLATE_BIN, f"-b{BOX_ID}",
        "--run",
        f"--time={time_limit}",
        f"--mem={memory_limit * 1024}",
        "--stdin=input.txt", "--stdout=output.txt",
        "--stderr=error.txt", "--meta=meta.txt",
        "--silent",
        f"./{exe_name}"
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 读取输出
    user_output = open(output_file).read() if os.path.exists(output_file) else ""
    err_output = proc.stderr
    if os.path.exists(error_file):
        err_output += "\n" + open(error_file).read()

    # 读取 meta
    meta = {}
    if os.path.exists(meta_file):
        for line in open(meta_file):
            if ':' in line:
                k, v = line.strip().split(':', 1)
                meta[k] = v

    exitcode = int(meta.get("exitcode", proc.returncode if proc.returncode is not None else 0))
    time_used = float(meta.get("time", "0") or 0.0)

    return user_output, time_used, exitcode, err_output.strip(), meta


def judge(problem_json_path, source_code_path, language):
    """主评测逻辑"""
    with open(problem_json_path, 'r') as f:
        problem = json.load(f)

    time_limit = problem["time_limit"]
    memory_limit = problem["memory_limit"]
    test_cases = problem["test_cases"]

    results = []

    # 1️⃣ 初始化沙盒
    init_box()

    # 2️⃣ 生成可执行文件
    if language == "cpp":
        exe_path = "./prog"
        ok, err = compile_cpp(source_code_path, exe_path)
        if not ok:
            cleanup_box()
            return [{"status": "CE", "time": 0.0, "error": err.strip()}]
        shutil.copy2(exe_path, BOX_PATH)
        os.chmod(os.path.join(BOX_PATH, "prog"), 0o755)
        exe_name = "prog"
    elif language == "py":
        exe_name = "prog.py"
        with open(source_code_path, "r", encoding="utf-8") as f:
            src = f.read()
        header = "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n"
        with open(os.path.join(BOX_PATH, exe_name), "w", encoding="utf-8") as f:
            f.write(header + src)
        os.chmod(os.path.join(BOX_PATH, exe_name), 0o755)
    else:
        cleanup_box()
        raise ValueError("Unsupported language")

    # 3️⃣ 逐测试点执行
    for case in test_cases:
        output, t, exitcode, err, meta = run_in_box(
            exe_name, case["input"], time_limit, memory_limit
        )

        status = "UKE"
        if meta.get("status") == "TO":
            status = "TLE"
        elif "status" in meta and meta["status"] in ("SG", "XX"):
            status = "RE/MLE"
        else:
            if exitcode != 0:
                status = "RE/MLE"
            else:
                status = "AC" if output.strip() == case["output"].strip() else "WA"

        results.append({"status": status, "time": round(t, 3), "error": err})

    # 4️⃣ 清理沙盒
    cleanup_box()
    return results


if __name__ == "__main__":
    problem_json = "../test/aplusb.json"

    # C++ 测试
    source_code = "../test/aplusb.cpp"
    res = judge(problem_json, source_code, "cpp")
    for i, r in enumerate(res):
        print(f"C++ Test case {i}: {r}")

    # Python 测试
    # source_code = "../test/aplusb.py"
    # res = judge(problem_json, source_code, "py")
    # for i, r in enumerate(res):
    #     print(f"Python Test case {i}: {r}")
