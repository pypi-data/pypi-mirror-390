# Numerus

**Numerus** is an Esoteric Stack-based Programming Language (Esolang). It is a purely number-based language where all operations are represented by numerical codes.

## Installation (CLI)

Install the command-line interpreter (`nmc`) via PyPI:
```bash
pip install nmlang
```

## CLI Usage

Execute a Numerus source file (`.nm`) using the `nmc` command:
```bash
nmc your_program.nm
```

## Library Usage (Integration)

You can also use the Numerus interpreter directly in your Python projects.
```python
import numerus

# 1. Run a raw string
try:
    # Prints 'H' (ASCII 72)
    output = numerus.run_numerus_string("10 72 31 33")
    print(output)

except numerus.NumerusError as e:
    print(f"Code failed to run: {e}")


# 2. Run a file
try:
    output = numerus.run_numerus_file("hello_world.nm")
    print(output)

except FileNotFoundError:
    print("File not found!")
except numerus.NumerusError as e:
    print(f"Code failed to run: {e}")
```

## Quick Syntax Guide

| Code | Command    | Stack Behavior (TOS = Top of Stack)                             |
|------|------------|-----------------------------------------------------------------|
| 0-9  | PUSH_VALUE | Pushes the opcode value itself.                                 |
| 10   | PUSH_NEXT  | Pushes the next number in the source code.                      |
| 20   | ADD        | `(b, a)` -> `(b+a)`                                             |
| 21   | SUB        | `(b, a)` -> `(b-a)`                                             |
| 23   | DUP        | `(a)` -> `(a, a)`                                               |
| 31   | PRINT_CHAR | Pops and prints value as ASCII character.                       |
| 32   | JUMP_ZERO  | If popped value is 0, jumps to address provided in source code. |
| 33   | END        | Halts execution.                                                |

## Example Hello World Program (`hello_world.nm`)

```nm
10 72 31 10 101 31 10 108 31 10 108 31 10 111 31 10 44 31 10 32 31 10 87 31 10 111 31 10 114 31 10 108 31 10 100 31 10 33 31 33
```

## License

This project is under the **MIT License**.