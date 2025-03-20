import argparse

sequence = "EGBOKLCJFAIPMDNH"

instruction_ids = {
    "A": "add", "B": "addi", "C": "sub", "D": "subi",
    "E": "and", "F": "andi", "G": "or", "H": "ori",
    "I": "sll", "J": "srl", "K": "nor", "L": "sw",
    "M": "lw", "N": "beq", "O": "bneq", "P": "j"
}

operation_map = {
    "A": "Arithmetic", "B": "Arithmetic", "C": "Arithmetic", "D": "Arithmetic",
    "E": "Logic", "F": "Logic", "G": "Logic", "H": "Logic",
    "I": "Logic", "J": "Logic", "K": "Logic", "L": "Memory",
    "M": "Memory", "N": "Control", "O": "Control", "P": "Control"
}

# Define register memory map
register_map = {
    "$zero": "0000",
    "$t0": "0111",
    "$t1": "0001",
    "$t2": "0010",
    "$t3": "0011",
    "$t4": "0100",
    "$sp": "0110",
}

# Define opcode map
opcode_map = {}
for i, char in enumerate(sequence):
    opcode_map[instruction_ids[char]] = f"{i:04b}"

# Function to convert R-type instruction to machine code
def r_type(opcode, src_reg1, src_reg2, dst_reg, shft_amnt):
    return f"{opcode}{src_reg1}{src_reg2}{dst_reg}{shft_amnt}"

# Function to convert I-type instruction to machine code
def i_type(opcode, src_reg1, src_reg2, immediate):
    return f"{opcode}{src_reg1}{src_reg2}{immediate & 0xFF:08b}"

# Function to convert J-type instruction to machine code
def j_type(opcode, target_address):
    return f"{opcode}{target_address:08b}00000000"

# Main function to convert MIPS instruction to machine code
def mips_to_machine_code(instruction, label_map, current_address):
    # Split the instruction into operation and arguments
    parts = instruction.split(maxsplit=1)
    instr_type = parts[0]
    opcode = opcode_map[instr_type]

    # Split the arguments by commas and remove whitespace
    args = [arg.strip() for arg in parts[1].split(",")]

    if instr_type in ["add", "sub", "and", "or", "nor"]:
        # R-type
        dst_reg = register_map[args[0]]  # Destination register
        src_reg1 = register_map[args[1]]  # Source register 1
        src_reg2 = register_map[args[2]]  # Source register 2
        shft_amnt = "0000"  # No shift amount for these instructions
        return r_type(opcode, src_reg1, src_reg2, dst_reg, shft_amnt)
    elif instr_type in ["addi", "andi", "ori", "subi"]:
        # I-type
        src_reg1 = register_map[args[0]]  # Destination register
        src_reg2 = register_map[args[1]]  # Source register
        immediate = int(args[2])  # Immediate value
        return i_type(opcode, src_reg2, src_reg1, immediate)
    elif instr_type in ["sll", "srl"]:
        # R-type with shift amount
        dst_reg = register_map[args[0]]  # Destination register
        src_reg1 = register_map[args[1]]  # Source register
        # src_reg2 = "0000"  # No second source register
        # shft_amnt = f"{int(args[2]):04b}"  # Shift amount
        # return r_type(opcode, src_reg1, dst_reg, src_reg2, shft_amnt)
        immediate = int(args[2])  # Shift amount
        immediate_bin = f"{immediate:04b}"  # 4-bit immediate for shift amount
        return i_type(opcode, src_reg1, dst_reg, int(immediate_bin, 2))
    elif instr_type == "j":
        # J-type with label or absolute address
        target = args[0]
        if target.isdigit():  # Absolute address
            target_address = int(target)
        else:  # Label
            target_address = label_map[target]
        return j_type(opcode, target_address)
    elif instr_type in ["lw", "sw"]:
        # I-type memory operations
        dst_reg = register_map[args[0]]  # For lw: destination register; for sw: source register
        offset, base_reg = args[1].split("(")
        base_reg = base_reg[:-1]  # Remove closing parenthesis from base register
        src_reg1 = register_map[base_reg]  # Base register
        immediate = int(offset)  # Offset value
        return i_type(opcode, src_reg1, dst_reg, immediate)
    elif instr_type in ["beq", "bneq"]:
        # I-type branch instructions with label or relative offset
        src_reg1 = register_map[args[0]]  # First register
        src_reg2 = register_map[args[1]]  # Second register
        target = args[2]
        if target.lstrip('-').isdigit():  # Relative offset
            immediate = int(target)
        else:  # Label
            immediate = label_map[target] - current_address - 1
        return i_type(opcode, src_reg1, src_reg2, immediate)
    else:
        raise ValueError(f"Unknown instruction type: {instr_type}")

# Preprocess labels and replace them with addresses
def preprocess_labels(lines):
    label_map = {}
    instructions = []
    address = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            label, instr = line.split(":", 1)
            label_map[label.strip()] = address
            line = instr.strip()
        if line:
            instructions.append(line)
            address += 1
    return label_map, instructions

# Function to read MIPS instructions and write to binary and hex output files
def process_mips_file(input_file, binary_file, hex_file):
    try:
        with open(input_file, "r") as infile, open(binary_file, "w") as bin_out, open(hex_file, "w") as hex_out:
            hex_out.write("v2.0 raw\n")  # Header for hex file
            lines = infile.readlines()
            label_map, instructions = preprocess_labels(lines)

            for address, line in enumerate(instructions):
                try:
                    if line.startswith("#"):
                        continue
                    machine_code = mips_to_machine_code(line, label_map, address)
                    bin_out.write(machine_code + "\n")  # Write binary code
                    hex_code = f"{int(machine_code, 2):x}"  # Convert to hex and remove leading zeros
                    hex_out.write(hex_code + " ")
                except ValueError as e:
                    print(f"Error processing line: {line} - {e}")
            hex_out.write("\n")  # Final newline for the hex file
    except FileNotFoundError:
        print(f"File not found: {input_file}")


# take input from file in the same directory
input_file = "in.txt"
binary_file = "binOut.txt"
hex_file = "hexOut.txt"

process_mips_file(input_file, binary_file, hex_file)