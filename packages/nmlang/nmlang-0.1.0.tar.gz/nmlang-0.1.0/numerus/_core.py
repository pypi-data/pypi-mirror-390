# -*- coding: utf-8 -*-
#
# _core.py - Numerus Core Logic (VM, Parser, Opcodes)
# This file is "internal" and not meant for direct user import.
#

import sys
from enum import Enum

# --- 1. Custom Error ---

class NumerusError(Exception):
    """Base exception for all runtime or parse errors in Numerus."""
    def __init__(self, message, pc=None):
        if pc is not None:
            super().__init__(f"(PC={pc}) {message}")
        else:
            super().__init__(message)

# --- 2. Instruction Definitions ---

class OpCode(Enum):
    PUSH_VALUE = 0
    PUSH_NEXT = 10
    ADD = 20
    SUB = 21
    MUL = 22
    DUP = 23
    DROP = 24
    PRINT_NUM = 30
    PRINT_CHAR = 31
    JUMP_ZERO = 32
    END = 33

class Instruction:
    """Represents a parsed Numerus instruction"""
    def __init__(self, opcode: OpCode, argument: int = None):
        self.opcode = opcode
        self.argument = argument
        
    def __repr__(self):
        if self.argument is not None:
            return f"<{self.opcode.name} {self.argument}>"
        return f"<{self.opcode.name}>"

# --- 3. Parser (Merged Lexer/Parser) ---

def parse_numerus_program(program_code: str) -> list[Instruction]:
    """
    Parses the Numerus code string into a list of instructions.
    Raises:
        NumerusError: If syntax is invalid.
    """
    tokens = program_code.split()
    try:
        tokens = [int(t) for t in tokens if t]
    except ValueError as e:
        raise NumerusError(f"Syntax Error: All tokens must be integers. Found: {e}")
    
    instructions = []
    i = 0
    while i < len(tokens):
        opcode_val = tokens[i]
        
        if 0 <= opcode_val <= 9:
            instructions.append(Instruction(OpCode.PUSH_VALUE, opcode_val))
            i += 1
            continue

        if 10 <= opcode_val <= 19:
            if i + 1 >= len(tokens):
                raise NumerusError(f"Syntax Error: PUSH_NEXT (10) missing argument at position {i}")
            argument = tokens[i+1]
            instructions.append(Instruction(OpCode.PUSH_NEXT, argument))
            i += 2
            continue

        try:
            opcode = OpCode(opcode_val)
            if opcode == OpCode.JUMP_ZERO:
                 if i + 1 >= len(tokens):
                    raise NumerusError(f"Syntax Error: JUMP_ZERO (32) missing jump address at position {i}")
                 instructions.append(Instruction(OpCode.JUMP_ZERO, tokens[i+1]))
                 i += 2
                 continue
                 
            instructions.append(Instruction(opcode))
            i += 1
            
        except ValueError:
            raise NumerusError(f"Syntax Error: Unknown opcode {opcode_val} at position {i}")
            
    return instructions

# --- 4. Numerus Virtual Machine (VM) ---

class NumerusVM:
    """
    A simple Virtual Machine to execute Numerus instructions.
    This VM does not print directly; it returns its output.
    """
    def __init__(self, instructions: list[Instruction]):
        self.instructions = instructions
        self.stack = []
        self.pc = 0
        self.output = ""
        
    def run(self) -> str:
        """
        Executes the loaded program.
        Returns:
            str: The accumulated standard output (from PRINT_CHAR/PRINT_NUM).
        Raises:
            NumerusError: If parsing or execution fails.
        """
        
        while self.pc < len(self.instructions):
            instr = self.instructions[self.pc]
            original_pc = self.pc 
            self.pc += 1

            try:
                if instr.opcode == OpCode.PUSH_VALUE or instr.opcode == OpCode.PUSH_NEXT:
                    self.stack.append(instr.argument)

                elif instr.opcode == OpCode.DROP:
                    if not self.stack: raise NumerusError("Stack is empty.", original_pc)
                    self.stack.pop()

                elif instr.opcode == OpCode.DUP:
                    if not self.stack: raise NumerusError("Stack is empty.", original_pc)
                    self.stack.append(self.stack[-1])

                elif instr.opcode in [OpCode.ADD, OpCode.SUB, OpCode.MUL]:
                    if len(self.stack) < 2: raise NumerusError("Requires 2 values on Stack.", original_pc)
                    a = self.stack.pop()
                    b = self.stack.pop()
                    
                    if instr.opcode == OpCode.ADD: result = b + a
                    elif instr.opcode == OpCode.SUB: result = b - a
                    elif instr.opcode == OpCode.MUL: result = b * a
                    self.stack.append(result)

                elif instr.opcode == OpCode.PRINT_NUM:
                    if not self.stack: raise NumerusError("Stack is empty.", original_pc)
                    self.output += str(self.stack.pop())

                elif instr.opcode == OpCode.PRINT_CHAR:
                    if not self.stack: raise NumerusError("Stack is empty.", original_pc)
                    val = self.stack.pop()
                    try:
                        self.output += chr(val)
                    except ValueError:
                        raise NumerusError(f"Invalid ASCII code: {val}.", original_pc)

                elif instr.opcode == OpCode.JUMP_ZERO:
                    if not self.stack: raise NumerusError("Requires a test value on Stack.", original_pc)
                    check_val = self.stack.pop() 
                    jump_addr = instr.argument

                    if check_val == 0:
                        if 0 <= jump_addr < len(self.instructions):
                            self.pc = jump_addr
                        else:
                            raise NumerusError(f"Invalid jump address: {jump_addr}", original_pc)
                    
                elif instr.opcode == OpCode.END:
                    return self.output # Program halted successfully

            except NumerusError as e:
                # Re-raise with PC info if it wasn't added already
                if "(PC=" not in str(e):
                    raise NumerusError(f"{e} (Op: {instr.opcode.name})", original_pc)
                raise e
            except Exception as e:
                # Catch unknown errors
                raise NumerusError(f"Unknown VM Error: {e} (Op: {instr.opcode.name})", original_pc)

        return self.output # Program finished without END