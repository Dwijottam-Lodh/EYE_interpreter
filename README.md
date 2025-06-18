
markdown
Copy
Edit
# 👁️ Eye — The Universal Interop Scripting Language

> **Write once. Eye sees it all.**

**Eye** is a lightweight, experimental scripting language built for *interop*. Whether it's Python talking to C#, a Typescript frontend syncing with a Rust backend, or your game engine nudging a database—Eye bridges them all using simple JSON and expression-first logic.

No classes. No indentation wars. No boilerplate. Just one interpreter file, and the freedom to wire up anything to anything.

---

## ✨ Features

- 🔗 **Cross-language interop** via shared JSON (`linkto`)
- 📄 **Simple file-based memory** (`_mem{}` and `host{}`)
- 🧠 **Polish notation** for fast logic & computation
- 🧰 **Built-in API requests** (`api(...)`)
- 🐞 **Debug tools** (`debug.msg(...)`, `debug.runs()`)
- 🧪 **One-file interpreter** written in Python—easily extensible
- ⚡ **No classes, no `main()`, no setup. Just run.**

---

## 🧠 Syntax Basics

### 📌 Linking to host data
```eye
Linkto("data.json")
This links Eye to a shared JSON file. All external data goes through host{}.

📦 Memory
eye
Copy
Edit
_mem{0} = host{city}
_mem{1} = 25
Use _mem{} to store working values.

➕ Polish notation expressions
eye
Copy
Edit
output(+, _mem{0}, _mem{1})   # adds two values
Operators come first:
+, -, *, /, ^, #, %, //, ', ++, --, ==, !=, <, >, <=, >=

🧾 Conditions
eye
Copy
Edit
==, _mem{0}, "+"
true?
output(+, _mem{1}, _mem{2})
return
Conditions set true_flag.
Blocks run only if the flag is true.

🔁 Loops
eye
Copy
Edit
is true?
  _mem{0} = -, _mem{0}, 1
  output(_mem{0})
return
Loop runs while the most recent condition is true.

🛰️ API calls
eye
Copy
Edit
_mem{1} = api("POST", "https://example.com/", _mem{0})
Make GET or POST requests. Data is saved to _mem{}.

🐛 Debug tools
eye
Copy
Edit
debug.msg("Something happened")
debug.alert("Something critical!")
debug.warn("Caution!")
debug.runs()        # shows which line is executing
🔧 Sample Eye Program
eye
Copy
Edit
Linkto("calc.json")

_mem{0} = host{2}
_mem{1} = host{1}
_mem{2} = host{0}

==, _mem{0}, "+"
true?
output(+, _mem{1}, _mem{2})
return

==, _mem{0}, "-"
true?
output(-, _mem{1}, _mem{2})
return
calc.json:

json
Copy
Edit
{
  "0": 20,
  "1": 10,
  "2": "+"
}
Output:

makefile
Copy
Edit
Result: 30
🚀 Running Eye
bash
Copy
Edit
$ python eye.py
Filename>>> main.eye
Eye reads the .eye file, links the specified JSON host file, executes, and writes results.

📁 Output Format
After execution, Eye writes to the linked JSON file:

json
Copy
Edit
{
  ...
  "_output": [
    "Result: 30",
    ...
  ]
}
📦 File Structure
bash
Copy
Edit
eye.py           # The interpreter
main.eye         # Your Eye code
data.json        # Your linked host file
❓ Built-In Help
Just include this in your script:

eye
Copy
Edit
helpme
It will print a full Eye syntax guide to the console.
