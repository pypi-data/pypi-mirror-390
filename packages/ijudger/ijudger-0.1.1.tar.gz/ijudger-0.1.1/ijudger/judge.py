#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, subprocess, shutil

ISOLATE_BIN = "isolate"
BOX_ID = 1
BOX_PATH = f"/var/local/lib/isolate/{BOX_ID}/box"

def compile_cpp(source_path, exe_path):
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

def run_with_isolate(source_path, input_data, time_limit, memory_limit=None, language="cpp"):
    # 初始化干净 box
    subprocess.run([ISOLATE_BIN, f"--box-id={BOX_ID}", "--init"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    exe_name = "prog" if language=="cpp" else "prog.py"
    box_exe = os.path.join(BOX_PATH, exe_name)
    input_file = os.path.join(BOX_PATH, "input.txt")
    output_file = os.path.join(BOX_PATH, "output.txt")
    error_file = os.path.join(BOX_PATH, "error.txt")
    meta_file = "./meta.txt"

    # 写入输入
    with open(input_file, "w") as f:
        f.write(input_data)

    # 准备可执行文件
    if language=="cpp":
        ok, err = compile_cpp(source_path, box_exe)
        if not ok:
            return "CE", 0.0, -1, err, {}
        os.chmod(box_exe, 0o755)
    else:
        # 读取原源码
        with open(source_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        # 自动加上 shebang 和编码声明
        header = "#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n"
        with open(box_exe, "w", encoding="utf-8") as f:
            f.write(header + source_code)
        os.chmod(box_exe, 0o755)

    # 构造命令，--run 后直接写文件名
    cmd = [
        ISOLATE_BIN, f"-b {BOX_ID}",
        "--run",
        "--stdin=input.txt", "--stdout=output.txt",
        "--stderr=error.txt", "--meta=meta.txt",
        f"--time={time_limit}", "--silent", f"--mem={memory_limit*1024}"
    ]
    cmd.append(f"./{exe_name}" if language=="cpp" else exe_name)

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    user_output = open(output_file).read() if os.path.exists(output_file) else ""
    err_output = proc.stderr or ""
    if os.path.exists(error_file):
        err_output += ("\n" + open(error_file).read()).lstrip("\n")

    meta = {}
    if os.path.exists(meta_file):
        for line in open(meta_file):
            if ':' in line:
                k, v = line.strip().split(':', 1)
                meta[k] = v

    exitcode = int(meta.get("exitcode", proc.returncode if proc.returncode is not None else 0))
    time_used = float(meta.get("time", "0") or 0.0)

    # cleanup
    subprocess.run([ISOLATE_BIN, f"--box-id={BOX_ID}", "--cleanup"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return user_output, time_used, exitcode, err_output, meta


def judge(problem_json_path, source_code_path, language):
    with open(problem_json_path, 'r') as f:
        problem = json.load(f)

    time_limit = problem["time_limit"]
    memory_limit = problem["memory_limit"]
    test_cases = problem["test_cases"]

    results = []

    for case in test_cases:
        output, t, exitcode, err, meta = run_with_isolate(
            source_code_path, case["input"], time_limit, memory_limit, language
        )
        if (output=='CE'):
            results.append({"status":"CE","time":round(t,3),"error":err.strip()})
            return results
        status = "UKE"
        max_rss = int(meta.get("max-rss", "0"))
        if meta.get("status")=="TO":
            status="TLE"
        elif "status"  in meta:
            status="RE/MLE"
        else:
            if "status" not in meta:
                if exitcode != 0: status="RE/MLE"
                else: status="AC" if output.strip()==case["output"].strip() else "WA"
            else:
                status="AC" if output.strip()==case["output"].strip() else "WA"


        results.append({"status":status,"time":round(t,3),"error":err.strip()})

    return results


if __name__ == "__main__":
    problem_json = "../test/aplusb.json"

    # C++ 测试
    source_code = "../test/aplusb.cpp"
    res = judge(problem_json, source_code, "cpp")
    for i,r in enumerate(res):
        print(f"C++ Test case {i}: {r}")

    # Python 测试
    # source_code = "../test/aplusb.py"
    # res = judge(problem_json, source_code, "py")
    # for i,r in enumerate(res):
    #     print(f"Python Test case {i}: {r}")
