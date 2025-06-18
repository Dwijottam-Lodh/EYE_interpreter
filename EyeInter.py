import re
import json
import requests
import os

memory = {}
true_flag = False
executing = True
output = []
functions = {}
host = {}

def resolve(val):
    if val.startswith("_mem{") and val.endswith("}"):
        return memory.get(int(val[5:-1]), 0)
    elif val.startswith("host{") and val.endswith("}"):
        return host.get(val[5:-1], "")
    elif val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    try:
        return float(val) if "." in val else int(val)
    except:
        return val

def eval_expr(expr):
    tokens = [x.strip() for x in expr.split(",")]
    if not tokens:
        print(f"[WARN] Empty expression: '{expr}'")
        return ""

    # Allow literal values (no operator)
    if len(tokens) == 1:
        return resolve(tokens[0])

    op = tokens[0]
    args = list(map(resolve, tokens[1:]))

    try:
        # Math
        if op == "+": return args[0] + args[1]
        if op == "-": return args[0] - args[1]
        if op == "*": return args[0] * args[1]
        if op == "/": return args[0] / args[1]
        if op == "^": return args[0] ** args[1]
        if op == "#": return args[1] ** (1 / args[0])
        if op == "//": return args[0] // args[1]
        if op == "%": return args[0] % args[1]
        if op == ",/": return -(-args[0] // args[1])  # ceiling div

        # String ops
        if op == "++": return str(args[0]) + str(args[1])
        if op == "--": return str(args[0]).replace(str(args[1]), "")

        # Comparisons
        if op == "==": return args[0] == args[1]
        if op == "!=": return args[0] != args[1]
        if op == "<": return args[0] < args[1]
        if op == "<=": return args[0] <= args[1]
        if op == ">": return args[0] > args[1]
        if op == ">=": return args[0] >= args[1]

        print(f"[WARN] Unknown operator '{op}' in: '{expr}'")
    except Exception as e:
        print(f"[ERROR] eval_expr('{expr}') → {e}")
    return ""

def execute_line(line):
    global memory, true_flag, executing, output

    if not executing and not any(line.startswith(x) for x in ("true?", "false?", "is true?", "is false?", "return")):
        return

    if line.startswith("_mem{"):
        match = re.match(r'_mem\{(\d+)\}\s*=\s*(.+)', line)
        if match:
            key = int(match.group(1))
            val = eval_expr(match.group(2))
            memory[key] = val

    elif line.startswith("output(") and executing:
        val = str(eval_expr(line[7:-1]))
        output.append(val)

    elif line.startswith("call("):
        func = line[5:-1].strip()
        if func in functions:
            for subline in functions[func]:
                execute_line(subline)

    elif any(line.startswith(x) for x in ("==", "!=", "<", "<=", ">", ">=")):
        true_flag = bool(eval_expr(line))

    elif line.startswith("api("):
        method_match = re.search(r'"(GET|POST)"', line)
        url_match = re.search(r'"(http[s]?://[^"]+)"', line)
        data_match = re.search(r'data=_mem\{(\d+)\}', line)
        save_match = re.search(r'save_to=_mem\{(\d+)\}', line)

        method = method_match.group(1) if method_match else "GET"
        url = url_match.group(1) if url_match else ""
        data = memory.get(int(data_match.group(1)), "") if data_match else None
        save_key = int(save_match.group(1)) if save_match else None

        try:
            response = requests.get(url) if method == "GET" else requests.post(url, data=data)
            if save_key is not None:
                memory[save_key] = response.text
        except Exception as e:
            if save_key is not None:
                memory[save_key] = f"[API error] {e}"

def run_eye_script(filename):
    global executing, true_flag, host

    with open(filename, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    host_file = "host.json"
    for line in lines:
        if line.startswith("linkto(") and line.endswith(")"):
            host_file = line[7:-1].strip('"')
            break

    if not os.path.exists(host_file):
        with open(host_file, "w") as newfile:
            json.dump({}, newfile)

    with open(host_file, "r") as h:
        host = json.load(h)

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("in (") and line.endswith(") do"):
            func_name = line[4:-4].strip()
            func_block = []
            i += 1
            while i < len(lines) and lines[i] != "return":
                func_block.append(lines[i])
                i += 1
            functions[func_name] = func_block

        elif line == "true?":
            executing = true_flag

        elif line == "false?":
            executing = not true_flag

        elif line == "return":
            executing = True

        elif line == "is true?":
            if true_flag:
                loop_block = []
                i += 1
                while i < len(lines) and lines[i] != "return":
                    loop_block.append(lines[i])
                    i += 1
                while true_flag:
                    for subline in loop_block:
                        execute_line(subline)
            executing = True

        elif line == "is false?":
            if not true_flag:
                loop_block = []
                i += 1
                while i < len(lines) and lines[i] != "return":
                    loop_block.append(lines[i])
                    i += 1
                while not true_flag:
                    for subline in loop_block:
                        execute_line(subline)
            executing = True
        elif line.startswith("#") or line.startswith("//"):
               pass
        elif line=="helpme":
            print(''' Eye Language Help 

Syntax:
  linkto("...")                 → Links the file to a host json file (to access just write host{})
  _mem{key} = expression        → Set memory key to result of expression
  output(expression)            → Print expression result
  ==, <, >, etc.                → Comparison, sets true_flag
  true? / false?                → Conditional block (ends with return)
  is true? / is false?          → Loop block (runs while flag is true/false)
  in (name) do ... return       → Define a function
  call(name)                    → Call a function
  api("GET"/"POST", url, ...)   → Make an API request

Operators (Polish Notation):
  +, -, *, /, ^, #              → Math
  %, //, '/                     → Mod, floor div, ceil div
  ++, --                        → String concat, remove substring

Example:
  _mem{1}=10
  _mem{2}=20
  output(+,_mem{1},_mem{2})     → Outputs 30

Enjoy the Eye.
''')

        elif line.startswith("debug.msg("):
            msg = line[10:-1]
            print(f"[MSG] {resolve(msg)}")

        elif line.startswith("debug.alert("):
            msg = line[13:-1]
            print(f"[ALERT] {resolve(msg)}")

        elif line.startswith("debug.warn("):
            msg = line[12:-1]
            print(f"[WARN] {resolve(msg)}")

        elif line.startswith("debug.runsmsg("):
            msg = line[14:-1]
            print(f"[RUNS] {resolve(msg)}")


        elif line.strip() == "debug.runs()":
            print(f"[RUNS] Line {i+1}")


        else:
            execute_line(line)

        i += 1

    host["_output"] = output
    with open(host_file, "w") as h:
        json.dump(host, h, indent=2)

if __name__ == "__main__":
    run_eye_script(input("Filename >>> "))
