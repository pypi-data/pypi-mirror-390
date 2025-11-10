import pkgutil
__path__ = pkgutil.extend_path(__path__,__name__)
__path__.reverse()

import math
from contextlib import contextmanager
from .. import *

"""
RTMQ Version 2 Core Module

This module implements the enhanced RTMQ v2 (Real-Time Microsystem for Quantum physics) instruction set,
assembler, and runtime environment. It provides a comprehensive framework for programming a 32-bit
processor designed specifically for quantum experiment control and applications requiring
nanosecond-level timing precision.

## Core Architecture

The RTMQ v2 architecture features:

- Dual address spaces: Control-Status Register (CSR) space and Tightly-Coupled Stack (TCS) space
- Special registers: PTR (program counter), LNK (link register), RSM (resume control),
  EXC (exception control), EHN (exception handler), STK (stack pointer)
- Sub-file support for CSR expansion
- Extended instruction set with 32-bit operations
- RTLink communication protocol for node-to-node messaging

## Instruction Set Categories

### Type-C Instructions (CSR Operations)
- CHI/CLO: Immediate value loading to CSRs with different bit ranges
- AMK: Masked assignment with bit-level operations and numeric increment
- SFS: CSR subfile selection for expanded address space
- NOP: No-operation with flow control flags (Halt, Pause)

### Type-A Instructions (Arithmetic & Logic)
- Data transfer: CSR, GHI, GLO
- Arithmetic: ADD, SUB, CAD (carry add), CSB (carry subtract)
- Logic: AND, IAN (inverted AND), BOR (bitwise OR), XOR
- Comparison: NEQ, EQU, LST (less than), LSE (less than or equal)
- Bitwise: SHL, SHR, ROL, SAR (arithmetic shift right)
- Multiplication/Division: OPL, PLO, PHI, DIV, MOD

## Key Components

- **base_core**: Core structure definition with instruction set and register mapping
- **disassembler**: Machine code to assembly language translation
- **core_reg**: Register abstraction with operator overloading for intuitive programming
- **RTLink utilities**: Frame packing/unpacking and message transmission functions
- **Cache management**: Instruction and data cache operations with alignment support
- **Control flow constructs**: Higher-level programming abstractions (if, while, for, functions)

## Usage

This module provides a complete toolchain for developing, assembling, and executing programs
for the RTMQ v2 architecture, with particular emphasis on precise timing control and
low-latency communication between nodes.
"""

def bit_concat(*args):
    """

    Bit fields concatenation.

    Parameters
    ----------
    *args : 2-tuples as (V, W)
        Each argument corresponds to a bit field with value V and width W.
        Bit fields are concatenated from high to low.
        NOTE: V will be cropped if not less than (2 ** W)

    Returns
    -------
    dat : integer
        Concatenated value.

    Example
    -------
    bit_concat((0b11, 2), (0b10, 3), (0b11, 1)) == 0b110101

    """
    dat = 0
    ln = len(args)
    for i in range(ln - 1):
        dat |= args[i][0] & ((1 << args[i][1]) - 1)
        dat <<= args[i + 1][1]
    dat |= args[ln - 1][0] & ((1 << args[ln - 1][1]) - 1)
    return dat

def bit_split(dat, wids):
    """

    Split a number into bit fields.

    Parameters
    ----------
    dat : integer
        Number to be splitted.
    wids : list OR tuple of integers
        Width of each bit field.

    Returns
    -------
    bf : list of integers
        Values of bit fields.

    Example
    -------
    bit_split(0b110101, (2, 3, 1)) == [0b11, 0b10, 0b1]

    """
    bf = []
    for i in range(1, len(wids)):
        bf += [dat & ((1<<wids[-i])-1)]
        dat = dat >> wids[-i]
    bf += [dat & ((1<<wids[0])-1)]
    bf.reverse()
    return bf

def to_unsigned(rx, wid=32):
    """
    Convert a value to unsigned integer representation.
    
    Parameters
    ----------
    rx : int
        Input value to convert
    wid : int, optional
        Bit width for conversion (default: 32)
        
    Returns
    -------
    int
        Unsigned integer value within the specified bit width
    """
    return rx & ((1 << wid) - 1)

def to_signed(rx, wid=32):
    """
    Convert a value to signed integer representation using two's complement.
    
    Parameters
    ----------
    rx : int
        Input value to convert
    wid : int, optional
        Bit width for conversion (default: 32)
        
    Returns
    -------
    int
        Signed integer value using two's complement representation
    """
    return -(rx & (1 << (wid - 1))) | (rx & ((1 << wid) - 1))

class base_core:
    """
    RTMQ v2 Base Core Definition
    
    This class defines the core structure of the RTMQ v2 architecture, including
    register mappings, instruction set definitions, and RTLink communication
    parameters. It serves as the foundation for both assembly and execution
    environments.
    
    Class Attributes:
        RSV (list): Reserved special registers that are always present
        RTLK (dict): RTLink communication protocol parameters
        OPC (dict): Instruction set definitions with encoding information
    
    Instance Attributes:
        CSR (list): Combined list of reserved and user-defined CSRs
        csr (dict): Mapping from CSR names to their addresses
        NUM (list): List of numeric CSRs that support auto-increment
        SBF (dict): Subfile definitions for CSR expansion
        sbfs (dict): Nested mapping from subfile names to CSR names to addresses
        CAP_ICH (int): Instruction cache capacity
        CAP_DCH (int): Data cache capacity
    
    Parameters:
        csr (list): List of user-defined CSR names
        nums (list): List of numeric CSR names
        sbfs (dict): Dictionary mapping subfile names to their CSR lists
        cap_ich (int): Instruction cache capacity in words
        cap_dch (int): Data cache capacity in words
    """
    RSV = ["PTR", "LNK", "RSM", "EXC", "EHN", "STK"]
    RTLK = {"W_CHN_ADR": 5,
            "W_NOD_ADR": 16,
            "W_TAG_LTN": 20,
            "N_FRM_PLD": 2,
            "W_FRM_PAD": 4}
    OPC = {"NOP": [ 0, "-HP", "" , ""  , ""    ],
           "SFS": [ 0, "-"  , "C", "CG" , ""    ],
           "CHI": [ 8, "-"  , "C", "I" , ""    ],
           "CLO": [ 9, "-HP", "C", "I" , ""    ],
           "AMK": [13, "-HP", "C", "NG", "NICG"],
           "AND": [ 0, "-"  , "G", "IG", "IG"  ],
           "IAN": [ 1, "-"  , "G", "IG", "IG"  ],
           "BOR": [ 2, "-"  , "G", "IG", "IG"  ],
           "XOR": [ 3, "-"  , "G", "IG", "IG"  ],
           "CSR": [ 4, "-"  , "G", "C" , ""    ],
           "GHI": [ 5, "-"  , "G", "I" , ""    ],
           "SGN": [ 6, "-"  , "G", "IG", "IG"  ],
           "OPL": [ 7, "-"  , "G", "IG", ""    ],
           "PLO": [ 0, "-"  , "G", ""  , ""    ],
           "PHI": [ 1, "-"  , "G", ""  , ""    ],
           "DIV": [ 2, "-"  , "G", ""  , ""    ],
           "MOD": [ 3, "-"  , "G", ""  , ""    ],
           "GLO": [ 8, "-"  , "G", "I" , ""    ],
           "ADD": [12, "-"  , "G", "IG", "IG"  ],
           "SUB": [13, "-"  , "G", "IG", "IG"  ],
           "CAD": [14, "-"  , "G", "IG", "IG"  ],
           "CSB": [15, "-"  , "G", "IG", "IG"  ],
           "NEQ": [16, "-"  , "G", "IG", "IG"  ],
           "EQU": [17, "-"  , "G", "IG", "IG"  ],
           "LST": [18, "-"  , "G", "IG", "IG"  ],
           "LSE": [19, "-"  , "G", "IG", "IG"  ],
           "SHL": [20, "-"  , "G", "IG", "IG"  ],
           "SHR": [21, "-"  , "G", "IG", "IG"  ],
           "ROL": [22, "-"  , "G", "IG", "IG"  ],
           "SAR": [23, "-"  , "G", "IG", "IG"  ]}

    def __init__(self, csr, nums, sbfs, cap_ich, cap_dch):
        self.CSR = self.RSV + csr
        self.csr = dict()
        for i in range(len(self.CSR)):
            if self.CSR[i] is not None:
                self.csr[self.CSR[i]] = i
        self.NUM = ["PTR", "STK"] + nums
        self.SBF = sbfs
        self.sbfs = dict()
        for k, v in self.SBF.items():
            self.sbfs[k] = dict()
            for i in range(len(v)):
                if v[i] is not None:
                    self.sbfs[k][v[i]] = i
        self.CAP_ICH = cap_ich
        self.CAP_DCH = cap_dch
        wcad = self.RTLK["W_CHN_ADR"]
        wnad = self.RTLK["W_NOD_ADR"]
        wtag = self.RTLK["W_TAG_LTN"]
        npld = self.RTLK["N_FRM_PLD"]
        wpad = self.RTLK["W_FRM_PAD"]
        flen = 3 + wcad + wnad + wtag + npld * 32 + wpad
        self.RTLK["N_BYT"] = flen // 8

PL01 = False

C_BASE = base_core([], [], {}, 65536, 16384)
C_STD = base_core(
    ["ICF", "ICA", "ICD", "DCF", "DCA", "DCD",
     "NEX", "FRM", "SCP", "TIM", "WCL", "WCH", "LED", "TRM"],
    ["ICA", "DCA", "TIM"],
    {"NEX": [None]*32 + ["ADR", "BCE", "RTA", "RTD"],
     "FRM": (["PL0", "PL1"] if PL01 else ["PL1", "PL0"])+["TAG", "DST"],
     "SCP": ["MEM", "TGM", "CDM", "COD"],
     "WCL": ["NOW", "BGN", "END"],
     "WCH": ["NOW", "BGN", "END"]},
    65536, 16384)

asm = context(core=C_STD)
        
class disassembler:
    """
    RTMQ v2 Disassembler
    
    This class translates RTMQ v2 machine code back into human-readable assembly language.
    It supports all instruction types and formats defined in the RTMQ v2 ISA.
    
    Class Attributes:
        OPC_TYA (list): Type-A instruction opcodes lookup table
        OPC_EXT (list): Extended Type-A instruction opcodes lookup table
    
    Instance Attributes:
        core (base_core): Core definition used for register name mapping
        stat (int): Internal state for function call pattern
        func: Function to be disassembled (when used in callable mode)
        idxs: Index string prefix (when used in callable mode)
        idxw: Index width for formatting (when used in callable mode)
    
    Parameters:
        core (base_core, optional): Core definition to use for register mapping.
                                   If None, will attempt to use the core from the function context.
    
    Methods:
        __call__(*args, **kwargs): Main entry point for disassembling code or setting up function disassembly
        _disa(code, idx_str, idx_wid): Internal method that performs the actual disassembly
        _csr(adr): Converts CSR address to name if possible
        _sbf(adr, csr): Converts subfile CSR address to name if possible
        _imm(imm, typ): Formats immediate values according to their type
        _cli/_amk/_alu: Decode different instruction types
    """
    OPC_TYA = ["AND", "IAN", "BOR", "XOR", "CSR", "GHI", "SGN", "", "", "", "", "", 
               "ADD", "SUB", "CAD", "CSB", "NEQ", "EQU", "LST", "LSE", "SHL", "SHR", "ROL", "SAR"]
    OPC_EXT = ["PLO", "PHI", "DIV", "MOD"]

    def __init__(self, core=None):
        self.core = core
        self.stat = 0

    def _csr(self, adr):
        try:
            ret = self.core.CSR[adr] or f"&{csr:02X}"
        except:
            ret = f"&{adr:02X}"
        return ret

    def _sbf(self, adr, csr):
        try:
            ret = self.core.SBF[self.core.CSR[adr]][csr] or f"&{csr:02X}" 
        except:
            ret = f"&{csr:02X}"
        return ret

    def _imm(self, imm, typ):
        if typ == 0:
            return str(to_signed(imm, 8))
        if typ == 1:
            return f"{imm>>4:01X}.{imm%16:01X}"
        if typ == 2:
            return f"0x000_{imm:05X}"
        if typ == 3:
            return f"0x{imm:03X}_00000"
        if typ == 4:
            return str(to_signed(imm, 20))
        return ""

    def _cli(self, ard, trd, tia, fhp, trs, tr0, tr1, ar0, ar1):
        rd = self._csr(ard)
        if fhp == 0:
            if trs == 0:
                return f"CHI - {rd} {self._imm(bit_concat((ar0, 4), (ar1, 8)), 3)}"
            else:
                r1 = f"${ar1:02X}" if tr1 else self._sbf(ard, ar1)
                return f"SFS - {rd} {r1}"
        else:
            tmp = bit_concat((trs, 2), (tr0, 1), (tr1, 1), (ar0, 8), (ar1, 8))
            return f"CLO {'-HP'[fhp-1]} {rd} {self._imm(tmp, 2)}"
    
    def _amk(self, ard, trd, tia, fhp, trs, tr0, tr1, ar0, ar1):
        rd = self._csr(ard)
        hp = '-HP'[fhp-1]
        if (ard, trs, tr0, tr1, ar0, ar1) == (0, 0, 0, 0, 0, 0):
            return f"NOP {hp}"
        r0 = f"${ar0:02X}" if tr0 else self._imm(ar0, 1)
        r1 = self._imm(ar1, 1-tr1) if trs % 2 == 0 else (f"${ar1:02X}" if tr1 else self._csr(ar1))
        return f"AMK {hp} {rd} {r0} {r1}"
    
    def _alu(self, ard, trd, tia, fhp, trs, tr0, tr1, ar0, ar1):
        rd = f"${ard:02X}"
        r0 = f"${ar0:02X}" if tr0 else self._imm(ar0, 0)
        r1 = f"${ar1:02X}" if tr1 else self._imm(ar1, 0)
        opc = bit_concat((tia, 1), (fhp, 2), (trs, 2))
        if opc >> 2 == 2:
            tmp = bit_concat((trs, 2), (tr0, 1), (tr1, 1), (ar0, 8), (ar1, 8))
            return f"GLO - {rd} {self._imm(tmp, 4)}"
        fop = self.OPC_TYA[opc]
        if opc in (4, 5):
            r1 = self._csr(ar1) if opc == 4 else self._imm(bit_concat((ar0, 4), (ar1, 8)), 3)
            return f"{fop} - {rd} {r1}"
        if opc == 7:
            if (tr0, tr1) == (0, 0):
                return f"{self.OPC_EXT[ar1 % 4]} - {rd}"
            else:
                return f"OPL - {r0} {r1}"
        return f"{fop} - {rd} {r0} {r1}"

    def _disa(self, code, idx_str=None, idx_wid=1):
        prg = []
        for i in range(len(code)):
            fld = bit_split(code[i], (8, 1, 1, 2, 2, 1, 1, 8, 8))
            ins = (self._amk(*fld) if fld[2] else self._cli(*fld)) if fld[1] else self._alu(*fld)
            idx = "" if idx_str is None else f"{idx_str+i:0{idx_wid}X}: "
            prg += [idx + ins]
        if idx_str is None:
            return prg
        else:
            return "\n".join(prg)

    def __call__(self, *args, **kwargs):
        if self.stat == 0:
            self.func = args[0]
            self.idxs = args[1] if len(args) >= 2 else None
            self.idxw = args[2] if len(args) >= 3 else 4
            if self.core is None:
                self.core = getattr(self.func,'core',asm.core)
            if type(self.func) in (tuple,list,table):
                return self._disa(self.func[:], self.idxs, self.idxw)
            self.stat = 1
            return self
        self.stat = 0
        with asm:
            asm.core = self.core
            self.func(*args, **kwargs)
            return self._disa(asm[:], self.idxs, self.idxw)
        
def label(tag,put=True):
    """
    Label Management for RTMQ v2 Assembler
    
    This function handles the creation, lookup, and resolution of labels in the assembly code.
    Labels are used for jumps, branches, and references to specific memory locations.
    
    Parameters
    ----------
    tag : str or int
        Label name or identifier. String tags are automatically converted to uppercase.
    put : bool, int, list, or expr, optional
        Determines the action to perform:
        - True: Create label at current assembly position
        - int: Create label at specified position
        - list: Create label with position list
        - expr: Create forward reference to label
        - Other: Create forward reference placeholder
    
    Returns
    -------
    int or expr
        - If retrieving an existing label: Returns the label position (int)
        - If creating a forward reference: Returns an expression placeholder
    
    Special handling
    ---------------
    - Labels are stored in the assembly context's 'label' dictionary
    - String labels are automatically converted to uppercase
    - Forward references are tracked and resolved when the label is defined
    - Multiple forward references to the same label are collected in a list
    
    Examples
    --------
    >>> label('START')  # Create label at current position
    >>> label('LOOP', 100)  # Create label at position 100
    >>> pos = label('TARGET', False)  # Create forward reference
    >>> jmp(label('TARGET'))  # Use label in jump instruction
    """
    lbl = getattr(asm,'label',None)
    if lbl is None:
        lbl = {}
        asm.label = lbl
    if type(tag) is str:
        tag = tag.upper()
    pos = lbl.get(tag,None)
    if put is True or type(put) in (int,list):
        if put is True:
            put = len(asm)
        if type(put) is int:
            if type(pos) is list:
                if type(pos[0]) is expr and len(pos[0]) == 1 and type(pos[0][:][0]) is not expr:
                    pos[0][0] = put
                for i in pos[1:]:
                    if type(asm[i]) is not int:
                        asm[i] = asm[i]()
        lbl[tag] = put
    else:
        if type(pos) is int:
            return pos
        if pos is None:
            if not isinstance(put,expr):
                put = expr(put)
            pos = [put]
            lbl[tag] = pos
        pos.append(len(asm))
        return pos[0]
 
def cnv_opd(opd, idx, opc):
    if type(opd) is expr:
        return (label(id(opd),opd),1)
    try:
        field = ["flag", "RD", "R0", "R1"][idx-1]
        typ = asm.core.OPC[opc][idx]
        if type(opd) is int:
            if "I" not in typ:
                raise
            return (opd & 0xFFFF_FFFF, 1)
        opd = str(opd).upper()
        if idx == 1:
            res = typ.find(opd)
            return 0 if res < 0 else res
        if opd in asm.core.CSR:
            if "C" not in typ:
                raise
            res = (asm.core.csr[opd], 2)
        elif "." in opd:
            nib, pos = opd.split(".")
            nib = int(nib, 16)
            pos = int(pos, 16)
            if not ((0 <= nib < 16) and (0 <= pos < 16) and ("N" in typ)):
                raise
            res = ((nib << 4) + pos, 0)
        elif opd[0] == "&":
            reg = int(opd[1:], 16)
            if ("C" not in typ) or (reg > 255):
                raise
            res = (reg, 2)
        elif opd[0] == "$":
            reg = int(opd[1:], 16)
            if ("G" not in typ) or (reg > 255):
                raise
            res = (reg, 3)
        elif opd[0] == '#':
            if "I" not in typ:
                raise
            res = (label(opd[1:],None), 1)
        else:
            res = (int(opd,0) & 0xFFFF_FFFF, 1)
            if "I" not in typ:
                raise
    except:
        raise SyntaxError(f"Invalid {field} for {opc}: '{opd}'.")
    return res

H = 1
P = 2

def bubble(r, *args):
    bubl = getattr(asm,'bubble',None)
    if bubl is False:
        return
    for i in args:
        if type(i) is not int and str(i) == bubl:
            nop()
            break
    asm.bubble = None if r is None else str(r) 

def nop(n=1,hp=0):
    """
    No-Operation instruction with configurable cycles and flow control
    
    Generates a NOP instruction that consumes a specified number of clock cycles
    and can optionally halt or pause the execution flow. This instruction is used
    for timing control, synchronization, or padding.
    
    Parameters:
        n (int): When positive: Number of NOP instructions to generate (each consumes one cycle)
                 When negative: Creates a special instruction variant with code (13-n)<<20
        hp (int, optional): Flow control flag for positive n values only
                           (0=None, 1=Halt, 2=Pause) (not used when n < 0)
    
    Returns:
        list or int: Generated machine code instructions
    
    Special handling:
        - If n < 0: Generates a single instruction with the code (13-n)<<20, where negative n creates special instruction variants
        - If n >= 0: Generates n separate NOP instructions
        - Automatically adds pipeline bubble instructions as needed
    
    Examples:
        >>> nop()  # Single cycle NOP
        >>> nop(5)  # 5 separate single-cycle NOP instructions
        >>> nop(1, 1)  # Single cycle NOP with Halt flag
        >>> nop(1, 2)  # Single cycle NOP with Pause flag
        >>> nop(-1)  # Special instruction with code (13-(-1))<<20 = 14<<20
    """
    bubble(None)
    if n < 0:
        ins = (13-n)<<20
        asm(ins)
    else:
        ins = [(13+hp)<<20]*n
        asm.extend(ins)
    return ins

def sfs(sbf,csr):
    """
    Select CSR Subfile
    
    This instruction selects a specific subfile within a CSR register for subsequent
    operations. It must be called before accessing individual subfile registers.
    
    Parameters:
        sbf (str): Subfile name or identifier
        csr (str or int): CSR register name, register number, or alias
    
    Returns:
        int: Machine code for SFS instruction
    
    Raises:
        SyntaxError: If subfile name is invalid or register is not found in the subfile
    
    Special handling:
        - Automatically converts integer CSR to hexadecimal format
        - Supports both direct register addresses and register aliases
        - Validates that the specified register belongs to the selected subfile
    
    Examples:
        >>> sfs('SBF_NAME', 0x10)  # Select subfile with integer register
        >>> sfs('REGISTER_SUBFILE', 'REGISTER_ALIAS')  # Select using register alias
        >>> sfs('CSR_SUBFILE', '&10')  # Select using hex register address
    """
    bubble(None,csr)
    sbf = sbf.upper()
    RD, trd = cnv_opd(sbf,2,'SFS')
    if sbf[0] != "&" and sbf not in asm.core.SBF.keys():
        raise SyntaxError(f"'{sbf}' is not a register subfile.")
    csr = f'&{csr:02X}' if type(csr) is int else str(csr).upper()
    if csr[0] in '&$':
        R0, tr0 = cnv_opd(csr,3,'SFS')
        tr0 = tr0 % 2
    elif csr in asm.core.SBF[sbf]:
        R0 = asm.core.sbfs[sbf][csr]
        tr0 = 0
    else:
        raise SyntaxError(f"Invalid register '{csr}' in sub-file {sbf}.")
    ins = bit_concat((RD, 8), (8, 4), (8 + tr0, 4), (R0, 16))
    asm(ins)
    return ins

def opc0(opc,rd):
    return asm.core.OPC[opc][0],*cnv_opd(rd,2,opc)

def opr(opc,rd):
    bubble(rd)
    opcd,RD,trd = opc0(opc,rd)
    ins = bit_concat((RD, 8), (7, 6), (0, 2), (0, 8), (opcd, 8))
    asm(ins)
    return ins
    
for k in ('PLO','PHI','DIV','MOD'):
    globals()[k.lower()] = (lambda k:lambda rd:opr(k,rd))(k)
    
def opc1(opc,rd,r0):
    return *opc0(opc,rd),*cnv_opd(r0,3,opc)

def ghi(rd,r0):
    """
    GPR High Immediate
    
    Writes the high 12 bits of a 32-bit immediate value to a TCS (General Purpose Register).
    This instruction is typically used together with GLO to write a full 32-bit
    value to a TCS register when the value cannot fit in a single GLO instruction.
    
    Parameters:
        rd (str): Destination TCS register (e.g., '$20')
        r0 (int or expr): Immediate value (only high 12 bits are used)
    
    Returns:
        int: Machine code for GHI instruction
    
    Note:
        - The value is right-shifted by 20 bits internally before writing
        - Usually paired with GLO to write full 32-bit values
    
    Examples:
        >>> ghi('$20', 0x12345678)  # Writes 0x123 to TCS $20 high bits
    """
    bubble(rd)
    opcd,RD,trd,R0,tr0 = opc1('GHI',rd,r0)
    ins = bit_concat((RD, 8), (opcd, 6), (0, 2), (R0 >> 20, 16))
    asm(ins)
    return ins

def glo(rd,r0):
    """
    GPR Low Immediate
    
    Writes the low 20 bits of a 32-bit immediate value to a TCS (General Purpose Register).
    Can be used alone for values that fit in 20 bits or paired with GHI
    for full 32-bit values.
    
    Parameters:
        rd (str): Destination TCS register (e.g., '$20')
        r0 (int or expr): Immediate value (only low 20 bits are used)
    
    Returns:
        int: Machine code for GLO instruction
    
    Examples:
        >>> glo('$20', 42)  # Writes 42 to TCS $20
        >>> glo('$21', '#label')  # Loads address of label into TCS $21
    """
    bubble(rd)
    opcd,RD,trd,R0,tr0 = opc1('GLO',rd,r0)
    ins = bit_concat((RD, 8), (2, 4), (R0, 20))
    asm(ins)
    return ins

def gli(rd,r0):
    """
    GPR Load Immediate
    
    Writes a full 32-bit immediate value to a TCS (General Purpose Register). This function
    automatically uses either a single GLO instruction (for values that fit in
    20 bits) or a combination of GLO and GHI instructions (for full 32-bit values).
    
    Parameters:
        rd (str): Destination TCS register (e.g., '$20')
        r0 (int or expr): 32-bit immediate value to write
    
    Returns:
        list or int: Generated machine code instructions
    
    Special handling:
        - Automatically determines if single or dual instruction is needed
        - Optimizes by using only GLO when possible
    
    Examples:
        >>> gli('$20', 0x12345678)  # Writes 0x12345678 to TCS $20 (uses both GLO and GHI)
        >>> gli('$21', 0xFFFFF)  # Writes 0xFFFFF to TCS $21 (uses only GLO)
    """
    return glo(rd,r0) if r0 == to_signed(r0,20) else [glo(rd,r0),ghi(rd,r0)]

def csr(rd,r0):
    """
    CSR to GPR Data Transfer
    
    Transfers data from a Control-Status Register (CSR) to a General Purpose Register (GPR).
    This instruction reads the value from the specified CSR and writes it to the destination TCS register.
    
    Parameters
    ----------
    rd (str): Destination TCS (General Purpose) register (e.g., '$20')
    r0 (str): Source CSR register name or address
    
    Returns
    -------
    int: Machine code for CSR instruction
    
    Special handling
    ---------------
    - Automatically adds pipeline bubble instructions as needed
    - Supports both named CSR registers and direct addresses
    
    Examples
    --------
    >>> csr('$20', 'PTR')  # Copy program counter value to TCS $20
    >>> csr('$21', '&10')  # Copy CSR at address 0x10 to TCS $21
    """
    bubble(rd)
    opcd,RD,trd,R0,tr0 = opc1('CSR',rd,r0)
    ins = bit_concat((RD, 8), (opcd, 6), (0, 2), (0, 8), (R0, 8))
    asm(ins)
    return ins
        
def chi(rd,r0):
    """
    CSR High Immediate
    
    Writes the high 12 bits of a 32-bit immediate value to a CSR register.
    This instruction is typically used together with CLO to write a full 32-bit
    value to a CSR when the value cannot fit in a single CLO instruction.
    
    Parameters:
        rd (str): Destination CSR register name or address
        r0 (int or expr): Immediate value (only high 12 bits are used)
    
    Returns:
        int: Machine code for CHI instruction
    
    Note:
        - The value is right-shifted by 20 bits internally before writing
        - Usually paired with CLO to write full 32-bit values
    
    Examples:
        >>> chi('PTR', 0x12345678)  # Writes 0x123 to PTR high bits
    """
    bubble(None)
    opcd,RD,trd,R0,tr0 = opc1('CHI',rd,r0)
    ins = bit_concat((RD, 8), (opcd, 4), (R0 >> 20, 20))
    asm(ins)
    return ins
    
def clo(rd,r0,hp=0):
    """
    CSR Low Immediate
    
    Writes the low 20 bits of a 32-bit immediate value to a CSR register.
    Can be used alone for values that fit in 20 bits or paired with CHI
    for full 32-bit values.
    
    Parameters:
        rd (str): Destination CSR register name or address
        r0 (int or expr): Immediate value (only low 20 bits are used)
        hp (int, optional): Flow control flag (0=None, 1=Halt, 2=Pause)
    
    Returns:
        int: Machine code for CLO instruction
    
    Examples:
        >>> clo('COUNTER', 42)  # Writes 42 to COUNTER register
        >>> clo('PTR', '#label', P)  # Sets program counter to label with pause
    """
    bubble(None)
    opcd,RD,trd,R0,tr0 = opc1('CLO',rd,r0)
    ins = bit_concat((RD, 8), (opcd + hp, 4), (R0, 20))
    asm(ins)
    return ins

def cli(rd,r0,hp=0):
    """
    CSR Load Immediate
    
    Writes a full 32-bit immediate value to a CSR register using a combination
    of CHI and CLO instructions. This function always issues both instructions
    to ensure the complete 32-bit value is written.
    
    Parameters:
        rd (str): Destination CSR register name or address
        r0 (int or expr): 32-bit immediate value to write
        hp (int, optional): Flow control flag for CLO instruction (0=None, 1=Halt, 2=Pause)
    
    Returns:
        list: Generated machine code instructions [CHI, CLO]
    
    Examples:
        >>> cli('REG', 0x12345678)  # Writes 0x12345678 to REG using both CHI and CLO
        >>> cli('REG', 0xFFFFF, P)  # Writes 0xFFFFF to REG with pause after CLO
    """
    return [chi(rd,r0),clo(rd,r0,hp)]

def opl(rd,r0):
    """
    Operand Load for Extended Operations
    
    Prepares operands for extended ALU operations such as multiplication and division.
    This instruction loads the first operand into a hidden register used by subsequent
    PLO, PHI, DIV, or MOD instructions to perform the actual extended operation.
    
    Parameters
    ----------
    rd (str): First operand register or value
    r0 (str): Second operand register or value
    
    Returns
    -------
    int: Machine code for OPL instruction
    
    Special handling
    ---------------
    - Automatically adds pipeline bubble instructions as needed
    - Typically followed by one of: PLO, PHI, DIV, MOD after appropriate delay cycles
    - Part of the extended arithmetic instruction set
    
    Examples
    --------
    >>> opl('$20', '$21')  # Prepare operands for multiplication/division
    >>> opl(10, 3)  # Prepare immediate values for extended operations
    """
    bubble(None,rd,r0)
    opcd,RD,trd,R0,tr0 = opc1('OPL',rd,r0)
    ins = bit_concat((0, 8), (7, 6), (trd, 1), (tr0 >> 1, 1), (RD, 8), (R0, 8))
    asm(ins)
    return ins
    
def opc2(opc,rd,r0,r1):
    return *opc1(opc,rd,r0),*cnv_opd(r1,4,opc)

def amk(rd,r0,r1,hp=0):
    """
    Atomic Mask Operation
    
    Performs a masked write operation to a CSR register or TCS entry. This instruction
    allows selective updating of specific bits within a register while preserving
    the values of other bits. The mask (r0) determines which bits to update from the source (r1).
    
    Parameters:
        rd (str): Destination register (CSR or TCS)
        r0 (str, int, expr): Mask register or value
        r1 (str, int, expr): Source value/register
        hp (int, optional): Flow control flag (0=None, 1=Halt, 2=Pause)
    
    Returns:
        int: Machine code for AMK instruction
    
    Operation:
        - The mask value in r0 determines which bits of rd to update
        - For each bit set in r0, the corresponding bit in rd is updated from r1
        - Bits not set in r0 remain unchanged in rd
    
    Examples:
        >>> amk('CSR_REG', '$20', '$21')  # Masked write from TCS $21 to CSR_REG using mask in $20
        >>> amk('$22', 0xFF00, 'CSR_VAL')  # Write CSR_VAL to TCS $22 with 0xFF00 mask
        >>> amk('STATUS', '3.0', '$23', P)  # Write with pause after instruction
    """
    bubble(None,r0,r1)
    opcd,RD,trd,R0,tr0,R1,tr1 = opc2('AMK',rd,r0,r1)
    ins = bit_concat((RD, 8), (opcd + hp, 4), (tr1 >> 1, 2), (tr0, 1), (tr1, 1), (R0, 8), (R1, 8))
    asm(ins)
    return ins

def alu(opc,rd,r0,r1):
    """
    Arithmetic Logic Unit Operations
    
    Performs arithmetic and logical operations between two operands and stores the result
    in a destination register. This is a core function that handles various ALU operations
    defined in the RTMQ v2 instruction set.
    
    Parameters:
        opc (str): Operation code (e.g., 'ADD', 'SUB', 'AND', 'OR', 'XOR', etc.)
        rd (str): Destination register (CSR or TCS)
        r0 (str, int, expr): First operand register or value
        r1 (str, int, expr): Second operand register or value
    
    Returns:
        int: Machine code for the ALU instruction
    
    Supported operations:
        - ADD: Addition
        - SUB: Subtraction
        - AND: Logical AND
        - OR: Logical OR
        - XOR: Logical XOR
        - LSH: Left shift
        - RSH: Right shift
        - and potentially other operations based on the OPC table
    
    Examples:
        >>> alu('ADD', '$20', '$21', 42)  # Add $21 and 42, store in $20
        >>> alu('AND', 'STATUS', '$22', '$23')  # AND $22 and $23, store in STATUS
        >>> alu('SUB', '$24', '$25', '#label')  # Subtract address of label from $25
    """
    bubble(rd,r0,r1)
    opcd,RD,trd,R0,tr0,R1,tr1 = opc2(opc,rd,r0,r1)
    ins = bit_concat((RD, 8), (opcd, 6), (tr0 >> 1, 1), (tr1 >> 1, 1), (R0, 8), (R1, 8))
    asm(ins)
    return ins

for k in base_core.OPC.keys()-('NOP','SFS','CHI','CLO','AMK','CSR','GHI','OPL','PLO','PHI','DIV','MOD','GLO'):
    globals()['and_' if k == 'AND' else k.lower()] = (lambda k:lambda rd,r0,r1:alu(k,rd,r0,r1))(k)

def mul(r, a, b):
    """
    Unsigned Multiplication
    
    Performs unsigned multiplication of two operands and stores the result in a register.
    This function combines the OPL instruction with a delay and PLO instruction to
    complete the multiplication operation.
    
    Parameters
    ----------
    r (str): Destination register for the result
    a (str or int): First operand (multiplicand)
    b (str or int): Second operand (multiplier)
    
    Returns
    -------
    list: Generated machine code instructions (OPL + NOP + PLO)
    
    Special handling
    ---------------
    - Uses PLO instruction to get the low 16 bits of the result
    - Includes a 1-cycle pause delay between OPL and PLO instructions
    
    Examples
    --------
    >>> mul('$20', '$21', '$22')  # Multiply $21 and $22, store result in $20
    >>> mul('$23', 10, 20)  # Multiply immediate values 10 and 20
    """
    opl(a, b)
    nop(1, P)
    plo(r)

def div_u(r, a, b):
    """
    Unsigned Division
    
    Performs unsigned division of two operands and stores the quotient in a register.
    This function combines the OPL instruction with necessary delays and DIV instruction
    to complete the division operation.
    
    Parameters
    ----------
    r (str): Destination register for the quotient
    a (str or int): First operand (dividend)
    b (str or int): Second operand (divisor)
    
    Returns
    -------
    list: Generated machine code instructions (OPL + NOPs + DIV)
    
    Special handling
    ---------------
    - Uses DIV instruction to get the quotient
    - Includes a 5-cycle pause delay followed by an additional NOP for timing requirements
    - Only performs unsigned division
    
    Examples
    --------
    >>> div_u('$20', '$21', '$22')  # Divide $21 by $22, store quotient in $20
    >>> div_u('$23', 100, 10)  # Divide immediate values 100 and 10
    """
    opl(a, b)
    nop(5, P)
    nop()
    div(r)

def rem_u(r, a, b):
    """
    Unsigned Remainder
    
    Performs unsigned division of two operands and stores the remainder in a register.
    This function combines the OPL instruction with necessary delays and MOD instruction
    to complete the remainder operation.
    
    Parameters
    ----------
    r (str): Destination register for the remainder
    a (str or int): First operand (dividend)
    b (str or int): Second operand (divisor)
    
    Returns
    -------
    list: Generated machine code instructions (OPL + NOPs + MOD)
    
    Special handling
    ---------------
    - Uses MOD instruction to get the remainder
    - Includes a 5-cycle pause delay followed by an additional NOP for timing requirements
    - Only performs unsigned division remainder
    
    Examples
    --------
    >>> rem_u('$20', '$21', '$22')  # Divide $21 by $22, store remainder in $20
    >>> rem_u('$23', 100, 3)  # Calculate 100 % 3
    """
    opl(a, b)
    nop(5, P)
    nop()
    mod(r)

def mov(rd,r0,hp=0):
    """
    Move data between registers or from immediate to register
    
    This is a fundamental data transfer function that handles various transfer
    scenarios between CSRs, TCS entries, and immediate values. It automatically
    selects the appropriate underlying instructions based on source and destination types.
    
    Parameters:
        rd (str, int): Destination register ($xx for TCS, CSR name, or CSR.subfile)
        r0 (str, int, expr, callable): Source value/register
        hp (int, optional): Flow control flag (0=None, 1=Halt, 2=Pause)
    
    Returns:
        list or int: Generated machine code instructions
    
    Special handling:
        - For immediate values 0 and 0xFFFFFFFF, uses $00 and $01 respectively
        - For CSR destinations, uses CHI/CLO for immediate values
        - For TCS destinations, uses GHI/GLO for immediate values
        - For register-to-register transfers, uses appropriate move instruction
        - Supports subfile CSR access with automatic SFS instruction generation
        - Handles masked transfers when source is a (value, mask) tuple
    
    Examples:
        >>> mov('$20', 42)  # Load 42 into TCS entry $20
        >>> mov('PTR', '#label', P)  # Set program counter to label with pause
        >>> mov('CSR_NAME', ('$20', '3.0'))  # Masked transfer from $20 to CSR
        >>> mov('SUBFILE.REG', 0x1234)  # Write to subfile register
    """
    if rd is None or r0 is None:
        return
    if type(r0) is int:
        if r0 == 0:
            return mov(rd,'$00',hp)
        elif r0&0xffffffff == 0xffffffff:
            return mov(rd,'$01',hp)
    rd = str(rd)
    if callable(r0) and type(r0) is not expr:
        if rd[0] != '$' and str(r0)[0] == '<':
            r0(tmp(-1))
            return mov(rd,tmp(-1),hp)
        else:
            return r0(rd)
    if rd[0] == '$':
        if type(r0) in (int,expr):
            return gli(rd,r0)
        r0 = str(r0)
        if r0[0] == '$':
            if rd == r0:
                return
            else:
                return add(rd,'$00',r0)
        else:
            if '.' in r0:
                r0,sub = r0.split('.')
                sfs(r0, sub)
                nop(1,P)
            return csr(rd, r0)          
    else:
        if '.' in rd:
            rd, sub = rd.split('.')
            sfs(rd, sub)
        if type(r0) in (int,expr):
            return cli(rd,r0,hp)
        elif type(r0) in (tuple,list): 
            r0,msk = r0
            top = tmp.top            
            if type(r0) in (int,expr):
                if type(msk) is int:
                    if msk == 0xfffff:
                        return clo(rd,r0,hp)
                    elif msk == 0xfff00000:
                        return chi(rd,r0)
                r0 = tmp(None,r0)
            elif callable(r0) and type(r0) is not expr:
                r0 = tmp(None,r0)
            if type(msk) is int:
                sca = int(math.log2(msk & -msk))
                if sca & 1:
                    sca -= 1
                msk >>= sca
                if msk < 0x10 and sca < 0x20:
                    msk = f'{msk:x}.{(sca>>1):x}'
                else:
                    msk = tmp(None,msk<<sca,False)
            elif callable(msk) and type(msk) is not expr:
                msk = tmp(None,msk)
            tmp.top = top
            return amk(rd,msk,r0,hp)
        r0 = str(r0)
        if '.' in r0:
            r0,sub = r0.split('.')
            sfs(r0, sub)
            nop(1,P)
        msk = '2.0' if rd.upper() in asm.core.NUM else '$01'
        return amk(rd,msk,r0,hp)

def tmp(rd,r0=None,imm=True):
    """
    Temporary Register Management
    
    This function provides utilities for managing temporary registers in the TCS space.
    It can allocate temporary registers, initialize them with values, and optimize
    register usage by avoiding unnecessary moves for immediate values.
    
    Parameters
    ----------
    rd (str or int): Register specifier or offset from base/top
        - str: Direct register reference (e.g., '$20')
        - int: Offset from tmp.base (if positive) or tmp.top (if negative)
    r0 (str, int, or None, optional): Value to store in the temporary register
        - None: Just return the register reference
        - int: Immediate value to store
        - str: Register or expression to move
    imm (bool, optional): Whether to optimize immediate values (default: True)
        - True: Skip moves for small immediates and known registers
        - False: Always use the temporary register
    
    Returns
    -------
    str: Register reference string (e.g., '$20')
    
    Class Attributes
    ---------------
    tmp.base: Base address for positive offsets (default: 0xf0)
    tmp.top: Top address for negative offsets, decrements when allocating (default: 0x100)
    
    Special handling
    ---------------
    - For r0 = 0: Returns '$00' without allocating a register
    - For r0 = -1 (0xFFFFFFFF): Returns '$01' without allocating a register
    - For small immediates and direct register references: May return directly without allocation
    - For other values: Allocates a temporary register if rd is None
    
    Examples
    --------
    >>> tmp(0)  # Get register at tmp.base + 0 (usually '$F0')
    >>> tmp(-1)  # Allocate a new temporary register
    >>> tmp('$20', 42)  # Store 42 in register $20
    >>> tmp(None, 'CSR_NAME')  # Allocate temp and move CSR value
    """
    if type(rd) is int:
        rd = f'${((tmp.base if rd >= 0 else tmp.top)+rd):02X}'
    if r0 is None:
        return rd
    if type(r0) is int:
        if r0 == 0:
            return '$00'
        elif r0&0xffffffff == 0xffffffff:
            return '$01'
    if not (imm and type(r0) is int and r0 == to_signed(r0,8) or str(r0)[0] == '$'):
        if rd is None:
            tmp.top -= 1
            rd = f'${tmp.top:02X}'
        mov(rd, r0)
        r0 = rd
    return r0

tmp.base = 0xf0
tmp.top = 0x100

@multi(asm)
def inline(prg):
    if type(prg) not in (tuple,list):
        prg = str(prg).splitlines()
    for line in prg:
        instr = line.strip()
        if len(instr) == 0 or instr[0] == '%':
            continue
        if instr[0] == '#' and instr[-1] == ':':
            label(instr[1:-1])
        else:
            instr = instr.split()
            if len(instr) == 1:
                asm(int(instr[0],16))
            else:
                opc = instr[0].lower()
                hp = instr[1]
                if hp == '-':
                    globals()['and_' if opc == 'and' else opc](*instr[2:])
                else:
                    globals()[opc](*instr[2:],hp=cnv_opd(hp,1,opc.upper()))
                    
# -----------------------------------------------------------------------------
# --------- StdLib ------------------------------------------------------------
# -----------------------------------------------------------------------------

def init01():
    """
    Initialize Special Registers
    
    Sets up the special registers $00 and $01 with fixed values. $00 is initialized to 0
    and $01 is initialized to -1 (0xFFFFFFFF). These registers are often used as
    constants throughout RTMQ v2 assembly code.
    
    Returns
    -------
    None
    
    Notes
    -----
    - $00 is commonly used as a zero constant
    - $01 is commonly used as a mask for full register operations
    - Includes a NOP instruction after initialization
    
    Examples
    --------
    >>> init01()  # Initialize special registers at the start of a program
    """
    glo('$00',0)
    glo('$01',-1)
    nop()

@multi(asm)
def setup(core=C_STD,dnld=1):
    """
    Assembler Setup Configuration
    
    Configures the assembly environment with the specified core definition
    and download settings. This function should be called at the beginning
    of an assembly program to set the correct architecture context.
    
    Parameters
    ----------
    core (base_core, optional): Core definition to use for assembly
        - Defaults to C_STD (standard core configuration)
    dnld (int, optional): Download flag
        - 1: Enable download operations (default)
        - 0: Disable download operations
    
    Returns
    -------
    None
    
    Examples
    --------
    >>> setup()  # Use default standard core configuration
    >>> setup(core=C_CUSTOM)  # Use a custom core configuration
    >>> setup(dnld=0)  # Disable download operations
    """
    asm.core = core
    asm.dnld = dnld

@multi(asm)
def finish():
    """
    Program Finalization
    
    Finalizes the assembly program by sending the appropriate download signals
    and halt instruction. This function should be called at the end of an assembly
    program to properly terminate execution.
    
    Returns
    -------
    None
    
    Special handling
    ---------------
    - Only performs download operations if asm.dnld is True (default)
    - Sends a download complete signal (oper=0)
    - Issues a halt instruction after a 2-cycle delay
    - Sends link information (info=1) after calculating the program length
    
    Examples
    --------
    >>> # At the end of a program
    >>> finish()  # Finalize and prepare for execution
    """
    dnld = getattr(asm,'dnld',1)
    if dnld:
        intf_send(oper=0)
        nop(2, H)
        pos = len(asm[:])
        intf_send('lnk', info=1)
        intf_send('exc', info=0)
        nop(2, H)
    flw = asm()
    with asm as cfg:
        if dnld:
            clo("exc", 1, P)
            chi("exc", 0)
            chi("rsm", 0)
            clo("rsm", 1)
            glo("$00", 0)
            glo("$01", -1)
            ich_dnld(flw[:], 0)
            amk("exc", "0.0", "exc")
            amk("ptr", "2.0", 0, P)
            cli("ehn", pos)
            amk("stk", "2.0", 0)
            amk("exc", "1.0", "0.0", P)
        else:
            set_bit("exc", "1.0", P)
            asm.extend(flw[:])
            clr_bit("exc", "1.0", P)
    flw.clear()
    flw.extend(cfg[:])

def w2h(w):
    """
    Word to Half-word Conversion
    
    Converts 32-bit words to a list of 16-bit half-words. Each 32-bit word is split
    into two 16-bit values: the lower half (LSB) followed by the upper half (MSB).
    
    Parameters
    ----------
    w : int or list or tuple
        Single 32-bit word or list/tuple of 32-bit words to convert
        - If int: Treated as a single 32-bit word
        - If list/tuple: Each element is treated as a 32-bit word
    
    Returns
    -------
    list
        List of 16-bit half-words. For each input word, two half-words are returned.
    
    Examples
    --------
    >>> w2h(0x12345678)  # Convert single word
    [0x5678, 0x1234]
    >>> w2h([0x12345678, 0x9ABCDEF0])  # Convert multiple words
    [0x5678, 0x1234, 0xDEF0, 0x9ABC]
    
    Notes
    -----
    - Useful for memory operations that require half-word access
    - The order is little-endian: lower half first, then upper half
    """
    if type(w) not in (tuple,list):
        w = [w]
    h = []
    for i in w:
        h += [i&0xFFFF,i>>16]
    return h

@multi(asm)
def copy(dst, src, align=4, batch=None):
    """
    Memory Copy Operations
    
    Copies data between memory locations with configurable alignment and batch mode.
    This function handles various copy scenarios including single values, arrays, and
    batch memory operations using the data cache interface.
    
    Parameters
    ----------
    dst : str, int, list, or tuple
        Destination address or list of destination addresses
        - Single value: Address where data will be copied to
        - List/tuple: Multiple destination addresses
    src : str, int, list, or tuple
        Source value or list of source values/addresses
        - Single value: Data or address to copy from
        - List/tuple: Multiple values or addresses to copy
    align : int, optional
        Memory alignment in bytes (default: 4)
        - Only the lower 2 bits are used (0-3)
    batch : bool, optional
        Batch mode flag
        - True: Use batch memory operations
        - False: Use individual memory operations
        - None: Use value from asm.dnld (default)
    
    Returns
    -------
    Varies
        - For single value copy: Returns the result of mov()
        - For multi-value copy: None
    
    Special handling
    ---------------
    - For single value copies, delegates to mov()
    - Uses DCA (Data Cache Address) and DCD (Data Cache Data) registers
    - Configures DCF (Data Cache Flag) with alignment and batch information
    - Handles both single-word and multi-word transfers
    - For list-to-list copies, transfers each element individually
    - Includes appropriate delay instructions for memory operations
    
    Examples
    --------
    >>> copy('$20', 42)  # Single value copy (same as mov)
    >>> copy('$30', ['$10', '$11'])  # Copy from list of registers to memory
    >>> copy(['$40', '$41'], 'CSR_REG')  # Copy CSR value to multiple registers
    >>> copy('dst_addr', src_list, align=2, batch=False)  # Non-aligned, non-batch copy
    """
    if batch is None:
        batch = getattr(asm,'dnld',1)
    if type(dst) not in (tuple,list) and type(src) not in (tuple,list):
        return mov(dst,src)
    if type(dst) not in (tuple,list):
        if len(src) == 1:
            mov('dcf', (align&3)<<30)
            mov('dca', dst)
            mov('dcd', src[0])
        else:
            mov('dcf', ((align&3)<<30)+(len(src) if batch else 0))
            if batch:
                mov('dca', dst)
                for s in src:
                    if type(s) is int:
                        clo('dcd', s)
                    else:
                        mov('dcd', s)
            else:
                mov(tmp(0), dst)
                for i in range(len(src)):
                    mov('dca', tmp(0))
                    add(tmp(0), tmp(0), align)
                    mov('dcd', src[i])
    elif type(src) not in (tuple,list):
        if len(dst) == 1:
            mov('dcf', (align&3)<<30)
            mov('dca', src)
            nop(1, P)
            nop(2)
            mov(dst[0], 'dcd')
        else:
            mov('dcf', ((align&3)<<30)+(len(dst) if batch else 0))
            if batch:
                mov('dca', src)
                nop(1, P)
                nop(2)
                for d in dst:
                    if type(d) is int:
                        asm(d)
                    else:
                        mov(d, 'dcd')
            else:
                mov(tmp(0), src)
                for i in range(len(dst)):
                    mov('dca', tmp(0))
                    add(tmp(0), tmp(0), align)
                    nop(1, P)
                    nop(1)
                    mov(dst[i], 'dcd')
    else:
        for i in range(min(len(dst),len(src))):
            mov(dst[i], src[i])
                
def block(*args):
    """
    Block Management for Control Flow
    
    Creates and manages code blocks for implementing control structures like loops,
    conditional statements, and functions. Blocks track their start position and
    can contain additional metadata for control flow operations.
    
    Parameters
    ----------
    *args : variable
        Variable arguments for block configuration:
        - If empty: Creates a new block with None as the first element
        - First argument: Typically the start position of the block
        - Other arguments: Additional metadata (e.g., block type like 'while', 'for')
        - If last argument is a dict: Treated as label definitions for the block
    
    Returns
    -------
    None
    
    Special handling
    ---------------
    - If first element is None: Creates a new expression placeholder for the block start
    - If last element is a dict: Populates assembly context with the dictionary items
    - Stores blocks in a stack structure in asm.block
    - Uses labels to track block positions for branching
    
    Examples
    --------
    >>> block()  # Create an empty block
    >>> block('while')  # Create a while loop block
    >>> block('for', '$20', 1)  # Create a for loop block with index register and step
    >>> block({'loop_end': len(asm)})  # Create block with label dictionary
    """
    blk = [None] if len(args) == 0 else list(args)
    if blk[0] is None:
        pos = expr(0)
        label(id(pos),[pos])
        blk[0] = pos
    if type(blk[-1]) is dict:
        lbl = blk.pop()
        for k,v in lbl.items():
            asm[k] = v
        label(id(blk[0]),[blk[0]]+list(lbl.keys()))
    asm.block = [blk] + getattr(asm,'block',[])

def loop(*args):
    """
    Loop Block Creation
    
    Creates a loop block with the current program position as its start. This is a
    convenience function that calls block() with the current assembly position as
    the first argument, followed by any additional arguments.
    
    Parameters
    ----------
    *args : variable
        Additional arguments to pass to block()
        - These typically include loop type ('while', 'for') and other metadata
    
    Returns
    -------
    None
    
    Examples
    --------
    >>> loop()  # Create a basic loop block
    >>> loop('while')  # Create a while loop block
    >>> loop('for', '$20', 1)  # Create a for loop with index and step
    
    Notes
    -----
    - This function is equivalent to block(len(asm), *args)
    - The loop start position is set to the current length of the assembly code
    """
    block(len(asm),*args)

@multi(asm)
def end(tag=None):
    if len(getattr(asm,'block',[])) == 0:
        return
    blk = asm.block[0]
    if len(blk) > 1:
        if blk[1] == 'while':
            br(0)
        elif blk[1] == 'for':
            rd,step = blk[2:]
            add(rd, rd, tmp(-1,step))
            br(0)
    pos = blk[0]
    if type(pos) is expr:
        lbl = asm.label[id(pos)]
        blk.append({k:asm[k] for k in lbl[1:]})
        label(id(pos))
        del asm.label[id(pos)]
    asm.block = asm.block[1:]
    if len(blk) > 1 and tag != blk[1]:
        if type(blk[1]) is str and blk[1] in ('if','elif','while','for'):
            end()
    return blk

def br(depth=0):
    """
    Branch to Block Start
    
    Creates an unconditional branch to the start of a specified block level. This function
    is used for implementing control flow structures like loops and conditional statements.
    
    Parameters:
        depth (int, optional): Block nesting depth (default: 0)
            - 0: Current block
            - 1: Parent block
            - Higher values: Nested parent blocks
    
    Returns:
        None
    
    Operation:
        1. Calculates the relative address to the block start
        2. Loads the relative offset into a temporary register
        3. Updates the program counter (PTR) with the new address
        4. Pauses execution after the branch (uses P flag)
    
    Examples:
        >>> br()  # Branch to current block start
        >>> br(1)  # Branch to parent block start
    """
    pos = asm.block[depth][0]
    rel = pos-len(asm)-2
    if type(pos) is expr:
        label(id(pos),None)
    glo(tmp(-1), rel)
    if type(pos) is expr:
        del asm.label[id(rel)]
    amk('ptr', '3.0', tmp(-1), P)

def br_if(a, depth=0, met=None):
    """
    Conditional Branch to Block Start
    
    Creates a conditional branch to the start of a specified block level based on a condition.
    This function is fundamental for implementing if-else statements, loops, and other control structures.
    
    Parameters:
        a (str, int, expr): Condition register or value
        depth (int, optional): Block nesting depth (default: 0)
        met (bool, optional): Condition matching behavior:
            - None: Use 'a' directly as the branch condition
            - True: Branch when 'a' is NOT equal to $00
            - False: Branch when 'a' is equal to $00
    
    Returns:
        None
    
    Operation:
        1. Calculates the relative address to the block start
        2. Loads the relative offset into a temporary register
        3. For direct condition: Uses 'a' as the branch condition mask
        4. For met=True/False: Performs comparison with $00 and uses result as mask
        5. Updates the program counter (PTR) with the new address if condition is met
        6. Pauses execution after the branch (uses P flag)
    
    Examples:
        >>> br_if('$20')  # Branch based on $20 value
        >>> br_if(tmp(-2, condition), 0, False)  # Branch when condition is false
        >>> br_if('#label', 1, True)  # Branch when condition is true to parent block
    """
    pos = asm.block[depth][0]
    rel = pos-len(asm)-(2 if met is None else 3)
    if type(pos) is expr:
        label(id(pos),None)
    glo(tmp(-1), rel)
    if type(pos) is expr:
        del asm.label[id(rel)]
    if met is None:
        amk('ptr', a, tmp(-1), P)
    else:
        (neq if met else equ)(tmp(-2), a, '$00')
        amk('ptr', tmp(-2), tmp(-1), P)
        
@multi(asm)
def if_(cond):
    """
    If Conditional Statement
    
    Creates an if conditional statement block. This is the first part of a conditional
    control structure, which will execute the subsequent code only if the condition is true.
    
    Parameters
    ----------
    cond : str, int, expr
        The condition to evaluate
        - If non-zero: Code inside the if block will execute
        - If zero: Code inside the if block will be skipped
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Creates an outer block for the if statement
    2. Creates a nested block labeled 'if'
    3. Evaluates the condition and branches around the if block if the condition is false
    
    Examples
    --------
    >>> if_('$20')  # Check if $20 is non-zero
    >>> # Code to execute if condition is true
    >>> end()  # End of if block
    >>> 
    >>> if_(neq('$21', '$00'))  # Check if $21 != $00
    >>> # Code to execute if condition is true
    >>> end()
    """
    block()
    block(None,'if')
    br_if(tmp(-2,cond), 0, False)

@multi(asm)
def else_():
    """
    Else Branch Statement
    
    Creates an else branch following an if statement. This is the alternative code path
    that will execute when the preceding if condition is false.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Branches to the end of the if-else structure (skipping the else block if the if condition was true)
    2. Ends the preceding if block
    
    Examples
    --------
    >>> if_('$20')
    >>> # Code for true condition
    >>> else_()
    >>> # Code for false condition
    >>> end()  # End of else block
    """
    br(1)
    end('if')

@multi(asm)
def elif_(cond):
    """
    Else If Conditional Statement
    
    Creates an else-if conditional branch, which is a combination of an else followed by a new if.
    This allows for multiple alternative conditions to be checked sequentially.
    
    Parameters
    ----------
    cond : str, int, expr
        The condition to evaluate for this else-if branch
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Creates an else branch (jumping to the end if previous conditions were true)
    2. Creates an 'elif' block
    3. Creates a nested 'if' block
    4. Evaluates the condition and branches around if false
    
    Examples
    --------
    >>> if_('$20')
    >>> # First condition code
    >>> elif_('$21')
    >>> # Second condition code
    >>> else_()
    >>> # Default code
    >>> end()
    """
    else_()
    block(None,'elif')
    block(None,'if')
    br_if(tmp(-2,cond), 0, False)

@multi(asm)    
def while_(cond=None):
    """
    While Loop Structure
    
    Creates a while loop that continues executing as long as the condition remains true.
    
    Parameters
    ----------
    cond : str, int, expr, optional
        The loop continuation condition
        - If non-zero: Loop continues
        - If zero: Loop terminates
        - If None: Creates an infinite loop
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Creates an outer block for the while loop
    2. Creates a loop block labeled 'while'
    3. If a condition is provided, evaluates it and breaks out of the loop if false
    
    Examples
    --------
    >>> mov('$20', 10)
    >>> while_('$20')  # Loop while $20 is non-zero
    >>> sub('$20', '$20', 1)
    >>> end()  # End of while loop
    >>> 
    >>> while_(None)  # Infinite loop
    >>> # Loop body
    >>> # (Must have a break condition inside)
    >>> end()
    """
    block()
    loop('while')
    if cond is not None:
        br_if(tmp(-2,cond), 1, False)

@multi(asm)
def for_(rd,rng):
    """
    For Loop Structure
    
    Creates a for loop with an index register and range specification. This provides
    a convenient way to iterate over a range of values.
    
    Parameters
    ----------
    rd : str
        The register to use as the loop index
    rng : int or tuple/list
        Range specification:
        - If int: Iterates from 0 to rng-1
        - If tuple/list (start, stop): Iterates from start to stop-1
        - If tuple/list (start, stop, step): Iterates with custom step
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Parses the range specification into start, stop, and step values
    2. Creates an outer block for the for loop
    3. Initializes the index register with the start value
    4. Creates a loop block labeled 'for' with index and step information
    5. Generates the appropriate loop termination condition based on step direction
    6. Jumps to the end if the termination condition is met
    
    Examples
    --------
    >>> for_('$20', 5)  # Iterate 5 times (0-4)
    >>> # Loop body here
    >>> end()
    >>> 
    >>> for_('$20', (2, 10))  # Iterate from 2 to 9
    >>> # Loop body here
    >>> end()
    >>> 
    >>> for_('$20', (10, 0, -2))  # Iterate from 10 down to 2, step -2
    >>> # Loop body here
    >>> end()
    """
    if type(rng) not in (tuple,list):
        rng = (rng,)
    if len(rng) == 1:
        start = 0
        stop = rng[0]
    else:
        start = rng[0]
        stop = rng[1]
    step = rng[2] if len(rng) > 2 else 1
    block()
    mov(rd, start)
    loop('for', rd, step)
    if type(step) is int:
        stop = tmp(-2,stop)
        if step > 0:
            lse(tmp(-2), stop, rd)
        else:
            lse(tmp(-2), rd, stop)
    else:
        step = tmp(-1,step)
        sgn(tmp(-2), step, tmp(-2,stop))
        sgn(tmp(-1), step, rd)
        lse(tmp(-2), tmp(-2), tmp(-1))
    br_if(tmp(-2), 1)

@contextmanager
def If(cond):
    """
    Context Manager for If Statement
    
    Provides a Pythonic context manager interface for the if_() function, allowing
    the use of Python's 'with' statement for cleaner conditional code blocks.
    
    Parameters
    ----------
    cond : str, int, expr
        The condition to evaluate
        - If non-zero: Code inside the context will execute
        - If zero: Code inside the context will be skipped
    
    Yields
    ------
    None
    
    Operation
    ---------
    1. Sets up the if condition using if_()
    2. Yields control to the context block
    3. On exit, properly closes the if block and manages the if stack
    4. Handles exceptions by re-raising them while maintaining proper stack state
    
    Examples
    --------
    >>> with If('$20'):
    ...     # Code to execute if $20 is non-zero
    >>> # Rest of code after if block
    
    >>> with If(neq('$21', '$00')):
    ...     # Code for true condition
    ...     with Else():
    ...         # Code for false condition
    """
    try:
        yield if_(cond)
    except Exception:
        raise
    else:
        asm.last_if = [end('if'),end()]

@contextmanager
def Elif(cond):
    """
    Context Manager for Else-If Statement
    
    Provides a Pythonic context manager interface for the elif_() function, allowing
    chaining of conditional statements in a clean, Pythonic way.
    
    Parameters
    ----------
    cond : str, int, expr
        The condition to evaluate for this else-if branch
    
    Yields
    ------
    None
    
    Operation
    ---------
    1. Properly handles nested blocks from previous if/elif statements
    2. Sets up the elif condition using elif_()
    3. Yields control to the context block
    4. On exit, properly closes all necessary blocks and updates the if stack
    5. Handles exceptions by re-raising them while maintaining proper stack state
    
    Examples
    --------
    >>> with If('$20'):
    ...     # Code for first condition
    >>> with Elif('$21'):
    ...     # Code for second condition
    >>> with Else():
    ...     # Code for default case
    """
    try:
        for i in range(min(3,len(asm.last_if))):
            block(*asm.last_if.pop())
        yield elif_(cond)
    except Exception:
        raise
    else:
        asm.last_if += [end('if'),end('elif'),end()]

@contextmanager
def Else():
    """
    Context Manager for Else Statement
    
    Provides a Pythonic context manager interface for the else_() function, allowing
    clean definition of alternative code paths when using the 'with' statement.
    
    Parameters
    ----------
    None
    
    Yields
    ------
    None
    
    Operation
    ---------
    1. Cleans up all pending blocks from previous if/elif statements
    2. Sets up the else branch using else_()
    3. Yields control to the context block
    4. On exit, properly closes the else block
    5. Handles exceptions by re-raising them while maintaining proper stack state
    
    Examples
    --------
    >>> with If('$20'):
    ...     # Code for true condition
    >>> with Else():
    ...     # Code for false condition
    """
    try:
        while len(asm.last_if):
            block(*asm.last_if.pop())
        yield else_()
    except Exception:
        raise
    else:
        end()

@contextmanager
def While(cond=None):
    """
    Context Manager for While Loop
    
    Provides a Pythonic context manager interface for the while_() function, allowing
    the use of Python's 'with' statement for cleaner loop structures.
    
    Parameters
    ----------
    cond : str, int, expr, optional
        The loop continuation condition
        - If non-zero: Loop continues
        - If zero: Loop terminates
        - If None: Creates an infinite loop
    
    Yields
    ------
    None
    
    Operation
    ---------
    1. Sets up the while loop using while_()
    2. Yields control to the context block (loop body)
    3. On exit, properly closes the while loop block
    4. Handles exceptions by re-raising them while maintaining proper stack state
    
    Examples
    --------
    >>> mov('$20', 10)
    >>> with While('$20'):
    ...     sub('$20', '$20', 1)
    >>> # Code after loop
    
    >>> with While(None):  # Infinite loop
    ...     # Loop body
    ...     # (Must have a break condition inside)
    """
    try:
        yield while_(cond)
    except Exception:
        raise
    else:
        end()

@contextmanager
def For(rd, rng):
    """
    Context Manager for For Loop
    
    Provides a Pythonic context manager interface for the for_() function, allowing
    the use of Python's 'with' statement for cleaner for loop structures.
    
    Parameters
    ----------
    rd : str
        The register to use as the loop index
    rng : int or tuple/list
        Range specification:
        - If int: Iterates from 0 to rng-1
        - If tuple/list (start, stop): Iterates from start to stop-1
        - If tuple/list (start, stop, step): Iterates with custom step
    
    Yields
    ------
    None
    
    Operation
    ---------
    1. Sets up the for loop using for_()
    2. Yields control to the context block (loop body)
    3. On exit, properly closes the for loop block
    4. Handles exceptions by re-raising them while maintaining proper stack state
    
    Examples
    --------
    >>> with For('$20', 5):
    ...     # Loop body (executes 5 times)
    >>> # Code after loop
    
    >>> with For('$20', (2, 10)):
    ...     # Loop body (iterates from 2 to 9)
    """
    try:
        yield for_(rd,rng)
    except Exception:
        raise
    else:
        end()

def frame(*args):
    """
    Stack Frame Management
    
    Manages the stack frame for function calls, tracking arguments and local variables.
    Can both retrieve the current frame configuration or set up a new one.
    
    Parameters
    ----------
    *args : int, optional
        Frame configuration:
        - If empty: Returns the current frame configuration
        - First argument: Number of function arguments
        - Second argument: Number of local variables
    
    Returns
    -------
    tuple or str or list
        - When called with no arguments: Returns the current frame tuple (args, locals)
        - When setting up a new frame: Returns the first local variable register (or list of all locals)
    
    Special handling
    ---------------
    - Maintains the current frame in asm.frame
    - Excludes the stack pointer and link register from the returned local variables
    - Uses a predefined register list (R) for variable mapping
    
    Examples
    --------
    >>> frame()  # Get current frame
    (0,)  # Default frame with no arguments or locals
    >>> 
    >>> frame(2, 3)  # Set up frame with 2 args and 3 locals
    '$20'  # First local variable register
    """
    if len(args) == 0:
        return getattr(asm, 'frame', (0,))
    asm.frame = args
    vars = [R[i] for i in range(2+sum(args))]
    vars = vars[:args[0]]+vars[(args[0]+2):]
    return vars[0] if len(vars) == 1 else vars

def function(name, args=0, locals=0):
    """
    Function Definition
    
    Defines a new function with the specified name, argument count, and local variable count.
    Sets up the function prologue including label, stack frame, and link register handling.
    
    Parameters
    ----------
    name : str
        The name of the function (used as label)
    args : int, optional
        Number of arguments the function accepts (default: 0)
    locals : int, optional
        Number of local variables the function requires (default: 0)
    
    Returns
    -------
    str or list
        The first local variable register (or list of all locals) for easy reference
    
    Operation
    ---------
    1. Creates a bubble (alignment padding)
    2. Creates a label with the function name
    3. Sets up the stack pointer by subtracting from itself
    4. Saves the link register to a register
    5. Initializes the frame with the specified arguments and locals
    
    Examples
    --------
    >>> function('my_func', 2, 3)  # Define function with 2 args, 3 locals
    '$22'  # First local variable register
    >>> # Function body here
    >>> return_('$22')  # Return a value
    """
    bubble(None)
    label(name)
    sub(f'${(0x20+args):02X}', '$00', f'${(0x20+args):02X}')
    csr(f'${(0x21+args):02X}', 'lnk')
    return frame(args,locals)

def return_(*rets):
    """
    Function Return
    
    Handles function return operations, including setting return values and restoring the
    stack and program counter from the link register.
    
    Parameters
    ----------
    *rets : str, int, expr, optional
        Return values to be placed in the return registers
        - If none: Returns without setting any return values
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Retrieves the current frame's argument count
    2. Identifies the stack pointer and link register locations
    3. Adjusts registers if there are more return values than arguments
    4. Moves return values into the appropriate registers
    5. Restores the stack pointer (STK)
    6. Jumps to the return address stored in the link register (PTR)
    7. Pauses execution after the return
    
    Examples
    --------
    >>> return_()  # Return with no value
    >>> return_('$20')  # Return a single value
    >>> return_(tmp(-1, result1), tmp(-2, result2))  # Return multiple values
    """
    args = frame()[0]
    stk = f'${(0x20+args):02X}'
    lnk = f'${(0x21+args):02X}'
    if len(rets) > args:
        mov(tmp(-1), stk)
        stk = tmp(-1)
        if len(rets) > args + 1:
            mov(tmp(-2), lnk)
            lnk = tmp(-2)
    for i in range(len(rets)):
        mov(f'${(0x20+i):02X}', rets[i])
    amk('stk', '3.0', stk)
    amk('ptr', '2.0', lnk, P)

def call(func, *args):
    """
    Function Call
    
    Makes a function call to the specified function, passing the provided arguments.
    Handles stack frame setup and program counter manipulation.
    
    Parameters
    ----------
    func : str or expr
        The function to call
        - If string without # prefix: Treated as a label name
        - If string with # prefix: Treated as a direct address
        - If expr: Used directly as the target address
    *args : str, int, expr
        Arguments to pass to the function
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Calculates the size of the current stack frame
    2. Stores the frame size on the stack
    3. Copies each argument to the appropriate register
    4. Adjusts the function name to ensure it's a label reference if needed
    5. Updates the stack pointer (STK) to create a new frame
    6. Jumps to the function address and pauses execution
    
    Examples
    --------
    >>> call('my_func')  # Call function with no arguments
    >>> call('my_func', '$20', 42)  # Call function with two arguments
    >>> call('#0x1000')  # Call function at direct address
    """
    size = 2+sum(frame())  
    mov(f'${(0x20+size+len(args)):02X}', size)
    for i in range(len(args)):
        mov(f'${(0x20+size+i):02X}', args[i])
    if type(func) is str and func[0] != '#':
        func = '#' + func
    if size > 0:
        amk('stk', '3.0', f'${(0x20+size+len(args)):02X}')
    clo('ptr', func, P)
    return R[size]

Return = return_
Call = call

@contextmanager
def Func(name, *regs):
    """
    Context Manager for Function Definition
    
    Provides a Pythonic context manager interface for defining functions with
    automatic register management. This simplifies function creation by handling
    both definition and return.
    
    Parameters
    ----------
    name : str
        The name of the function (used as label)
    *regs : int
        Register range specification:
        - If one argument: Number of arguments (local variables = 0)
        - If two arguments: First and last register indices for function use
    
    Yields
    ------
    str or list
        The first local variable register (or list of all locals)
    
    Operation
    ---------
    1. Calculates the number of arguments and local variables based on regs
    2. Creates a function using function() with the calculated parameters
    3. Yields control to the context block (function body)
    4. On exit, automatically adds a return instruction if not already present
    5. Handles exceptions by re-raising them while maintaining proper function structure
    
    Examples
    --------
    >>> with Func('my_func', 2):  # Function with 2 arguments
    ...     # Function body
    ...     # No need to explicitly add return_()
    >>> # Function ends with automatic return
    
    >>> with Func('calc', 0, 3):  # Function using registers 0-3
    ...     # Function body with more control over register usage
    """
    try:
        if len(regs) == 1:
            args = regs[0] + 1
            locals = 0
        else:
            args = regs[0] - 2
            locals = regs[1] + 1 - regs[0]
        yield function(name,args,locals)
    except Exception:
        raise
    else:
        lnk = f'${(0x21+frame()[0]):02X}'
        core = asm.core
        with asm:
            asm.core = core
            ins = amk('ptr', '2.0', lnk, P)
        if asm[-1] != ins:
            return_()
            
Set = mov
"""
Alias for mov() function for register assignment

This is a convenience alias that makes register assignments more readable
in certain contexts, particularly when used with the core_reg class.

Parameters
----------
rd : str
    Destination register
r0 : str, int, expr
    Source value or register

Returns
-------
Varies
    Same return value as mov()

Examples
--------
>>> Set('$20', 42)  # Same as mov('$20', 42)
>>> R['PTR'] = 0x1000  # Uses Set internally
"""

class core_reg:
    """
    RTMQ v2 Register Abstraction
    
    This class provides an object-oriented abstraction for RTMQ v2 registers with
    operator overloading support. It allows for intuitive register manipulation
    using Python's arithmetic and comparison operators, which get translated
    into appropriate RTMQ assembly instructions.
    
    Instance Attributes:
        _key (str): Register identifier (e.g., '$20', 'PTR')
        _base (int): Base address offset for numeric register references
    
    Parameters:
        key (str, int, or core_reg, optional): Register identifier
        base (int, optional): Base address for numeric register references
    
    Features:
        - Operator overloading for arithmetic operations (+, -, *, /, etc.)
        - Operator overloading for bitwise operations (&, |, ^, <<, >>)
        - Operator overloading for comparisons (==, !=, <, >, <=, >=)
        - Attribute and item access for register subfiles
        - Callable interface for register assignment
    
    Examples:
        >>> R['PTR'] = 0x1000  # Set PTR register to 0x1000
        >>> R['$20'] = R['$21'] + 5  # Add 5 to $21 and store in $20
        >>> R.some_subfile.register = 10  # Access subfile register
    """
    def __init__(self, key=None, base=0x20):
        if type(key) is int:
            key = f'${(key+base):02X}'
        elif type(key) is str:
            key = key.upper()
        elif type(key) is self.__class__:
            key = key._key
        object.__setattr__(self,'_key',key)
        object.__setattr__(self,'_base',base)
    def __repr__(self):
        return str(self._key)
    def __getattr__(self, key):
        return self[key]
    def __getitem__(self, key):
        if self._key is None:
            if type(key) is slice:
                return [self[i] for i in range(256)[key]]
            key = f'${(key+self._base):02X}' if type(key) is int else str(key).upper()
            val = self.__dict__.get(key, None)
            if val is None:
                val = self.__class__(key)
                self.__dict__[key] = val
            return val
        elif type(self._key) is str and self._key[0] != '$':
            sfs(self._key, key)
            nop(1, P)
            return self
    def __setattr__(self, key, val):
        self[key] = val
    def __setitem__(self, key, val):
        if self._key is None:
            key = f'${(key+self._base):02X}' if type(key) is int else str(key).upper()
            Set(key, val._key if type(val) is self.__class__ else val)
        elif type(self._key) is str and self._key[0] != '$':
            key = self._key + '.' + (f'&{key:02X}' if type(key) is int else str(key).upper())
            Set(key, val._key if type(val) is self.__class__ else val)
    def __dir__(self):
        if self._key is None:
            return asm.core.CSR
        elif type(self._key) is str and self._key[0] != '$':
            return asm.core.SBF[self._key]
    def __call__(self, rd):
        Set(rd, self._key)
    def _oper(self, oper, other):
        def wrap(rd):
            top = tmp.top
            r0 = tmp(rd if str(rd) == f'${tmp.top:02X}' else None,self,oper not in (mul,div_u,rem_u))
            r1 = tmp(rd if str(rd) == f'${tmp.top:02X}' and r0 != rd else None,other)
            oper(rd,r0,r1)
            tmp.top = top
        return self.__class__(wrap)
    def _roper(self, oper, other):
        def wrap(rd):
            top = tmp.top
            r0 = tmp(rd if str(rd) == f'${tmp.top:02X}' else None,other,oper not in (mul,div_u,rem_u))
            r1 = tmp(rd if str(rd) == f'${tmp.top:02X}' and r0 != rd else None,self)
            oper(rd,r0,r1)
            tmp.top = top
        return self.__class__(wrap)
    def __eq__(self, other):
        return self._oper(equ, other)
    def __ne__(self, other):
        return self._oper(neq, other)
    def __lt__(self, other):
        return self._oper(lst, other)
    def __gt__(self, other):
        return self._roper(lst, other)
    def __le__(self, other):
        return self._oper(lse, other)
    def __ge__(self, other):
        return self._roper(lse, other)
    def __add__(self, other):
        return self._oper(add, other)
    def __sub__(self, other):
        return self._oper(sub, other)
    def __mul__(self, other):
        return self._oper(mul, other)
    def __truediv__(self, other):
        return self._oper(div_u, other)
    def __mod__(self, other):
        return self._oper(rem_u, other)
    def __and__(self, other):
        return self._oper(and_, other)
    def __or__(self, other):
        return self._oper(bor, other)
    def __xor__(self, other):
        return self._oper(xor, other)
    def __lshift__(self, other):
        return self._oper(shl, other)
    def __rshift__(self, other):
        return self._oper(sar, other)
    def __radd__(self, other):
        return self._roper(add, other)
    def __rsub__(self, other):
        return self._roper(sub, other)
    def __rmul__(self, other):
        return self._roper(mul, other)
    def __rtruediv__(self, other):
        return self._roper(div_u, other)
    def __rmod__(self, other):
        return self._roper(rem_u, other)
    def __rand__(self, other):
        return self._roper(and_, other)
    def __ror__(self, other):
        return self._roper(bor, other)
    def __rxor__(self, other):
        return self._roper(xor, other)
    def __rlshift__(self, other):
        return self._roper(shl, other)
    def __rrshift__(self, other):
        return self._roper(sar, other)
    def __neg__(self):
        return 0 - self
    def __invert__(self):
        return self._oper(ian, '$01')
    def __imatmul__(self, other):
        R[self] = other
        return self
    def __iadd__(self, other):
        R[self] = self + other
        return self
    def __isub__(self, other):
        R[self] = self - other
        return self
    def __imul__(self, other):
        R[self] = self * other
        return self
    def __itruediv__(self, other):
        R[self] = self / other
        return self
    def __imod__(self, other):
        R[self] = self % other
        return self
    def __iand__(self, other):
        R[self] = self & other
        return self
    def __ior__(self, other):
        R[self] = self | other
        return self
    def __ixor__(self, other):
        R[self] = self ^ other
        return self
    def __ilshift__(self, other):
        R[self] = self << other
        return self
    def __irshift__(self, other):
        R[self] = self >> other
        return self
    
R = core_reg()
        
core_ctx = lambda core=asm.core:{k:R[k] for k in core.CSR}|{k:globals()[k] for k in ('Set','If','Elif','Else','While','For','Return','Call','Func')}
core_regq = lambda core=asm.core:lambda s:s == 'R' or s in core.CSR
core_domain = lambda core=asm.core,sub=True,dump=False:domain(core_ctx(core),core_regq(core),sub=sub,dump=dump)

class core_cache:
    """
    RTMQ v2 Cache Management
    
    This class provides an interface for managing instruction and data caches
    in the RTMQ v2 architecture. It supports aligned memory access and offset-based
    addressing with flexible pointer manipulation.
    
    Instance Attributes:
        typ (str): Cache type ('dat' for data cache, 'ins' for instruction cache)
        ptr (int): Current pointer position within the cache
        align (int): Memory alignment requirement (default: 4 bytes)
    
    Parameters:
        typ (str): Cache type identifier
        ptr (int, optional): Initial pointer offset
        align (int, optional): Memory alignment in bytes
    
    Methods:
        __setitem__(key, val): Write values to cache at specified address
        __getitem__(key): Read values from cache at specified address
        __add__(ptr): Create new cache object with adjusted pointer
        __call__(size, align): Allocate memory block in cache
    
    Examples:
        >>> DCH[0x100] = 0x1234  # Write 0x1234 to data cache at address 0x100
        >>> val = DCH[0x100]  # Read from data cache at address 0x100
        >>> block = DCH(100, 4)  # Allocate 100 words with 4-byte alignment
    """
    def __init__(self, typ, ptr=0, align=4):
        """
        Initialize cache interface
        
        Parameters
        ----------
        typ : str
            Cache type identifier
            - 'dat': Data cache
            - 'ins': Instruction cache
        ptr : int, optional
            Initial pointer offset within the cache (default: 0)
        align : int, optional
            Memory alignment requirement in bytes (default: 4)
        """
        self.typ = typ
        self.ptr = ptr
        self.align = align
    def __setitem__(self, key, val):
        """
        Write to cache at specified address
        
        Parameters
        ----------
        key : int
            Memory address within the cache
        val : int, str, list, tuple
            Value(s) to write
            - Single value: Writes one word
            - List/tuple: Writes multiple consecutive words
        
        Returns
        -------
        None
        
        Operation
        ---------
        For data cache:
        1. Adjusts address based on alignment requirements
        2. Uses copy operation to transfer data
        
        For instruction cache:
        1. Writes each value to consecutive instruction cache entries
        2. Uses mov instructions to set address and data
        """
        if type(val) not in (tuple,list):
            val = [val]
        if self.typ[0] == 'd':
            sca = 2 if self.align > 2 else (self.align-1)
            copy((key if sca==0 else (key<<sca))+self.ptr,val,self.align,False)
        else:
            for i in range(len(val)):
                mov('ica', key+i)
                mov('icd', val[i])
    def __getitem__(self, key):
        """
        Read from cache at specified address
        
        Parameters
        ----------
        key : int
            Memory address within the cache
        
        Returns
        -------
        str
            Register name containing the read value
            - For data cache: Returns 'dcd' register
            - For instruction cache: Returns 'icd' register
        
        Operation
        ---------
        For data cache:
        1. Adjusts address based on alignment requirements
        2. Uses copy operation to read data into dcd register
        
        For instruction cache:
        1. Sets instruction cache address register
        2. Inserts pipeline synchronization (nop with P flag)
        3. Returns icd register name
        """
        if self.typ[0] == 'd':
            sca = 2 if self.align > 2 else (self.align-1)
            copy([None],(key if sca==0 else (key<<sca))+self.ptr,self.align,False)
            return R.dcd
        else:
            mov('ica', key)
            nop(1,P)
            return R.icd
    def __add__(self, ptr):
        """
        Create new cache object with adjusted pointer
        
        Parameters
        ----------
        ptr : int
            Offset to add to the current pointer
        
        Returns
        -------
        core_cache
            New cache object with updated pointer position
        
        Examples
        --------
        >>> block = DCH + 100  # Create new cache view starting at offset 100
        """
        return self.__class__(self.typ,self.ptr+ptr,self.align)
    def __call__(self, size, align=None):
        """
        Allocate memory block in cache
        
        Parameters
        ----------
        size : int
            Size of the memory block in words
        align : int, optional
            Alignment requirement for the allocation (default: self.align)
        
        Returns
        -------
        core_cache
            New cache object pointing to the allocated block
        
        Operation
        ---------
        1. Gets the current allocation pointer from the assembly context
        2. Updates the allocation pointer with the new block size
        3. Creates a new cache object pointing to the allocated block
        
        Examples
        --------
        >>> block = DCH(100)  # Allocate 100 words with default alignment
        >>> block = DCH(50, 8)  # Allocate 50 words with 8-byte alignment
        """
        ptr = getattr(asm,self.typ,0)
        asm[self.typ] = ptr+size*(align or self.align)
        return self.__class__(self.typ,self.ptr+ptr,align or self.align)

DCH = core_cache('dat')
ICH = core_cache('ins')

def set_csr(csr, val, msk=None, hp=0, align=False):
    """
    CSR Register Write with Masking
    
    Writes a value to a Control and Status Register (CSR) with optional bit masking.
    Supports both direct register addressing and subfield access.
    
    Parameters
    ----------
    csr : str
        CSR name or CSR.subfield name
    val : str, int
        Value to write to the CSR
        - If string without # prefix: Treated as a register reference
        - If other: Treated as a direct value
    msk : str, optional
        Bit mask for selective updates
        - None: Automatically selects mask based on CSR type ("2.0" for numeric, "$01" for others)
        - "2.0": Full update mask
        - "$01": Single bit mask
    hp : int, optional
        High priority flag (default: 0)
        - 0: Normal priority
        - Non-zero: High priority
    align : bool, optional
        Insert NOP instruction for alignment (default: False)
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Parses CSR name and optional subfield
    2. Selects appropriate subfield if specified
    3. Determines update method based on value type
    4. Applies optional alignment NOP
    5. Updates the CSR with the specified value and mask
    
    Examples
    --------
    >>> set_csr("ptr", 0x1000)  # Set program counter to 0x1000
    >>> set_csr("cfg.en", "$01")  # Enable configuration flag
    >>> set_csr("tim", tmp(0), "2.0")  # Set timer from register with full mask
    """
    gap = True
    if "." in csr:
        csr, sub = csr.split(".")
        gap = False
        sfs(csr, sub)
    if isinstance(val, str) and val[0] != "#":
        if gap and align:
            nop()
        if msk is None:
            msk = "2.0" if csr.upper() in asm.core.NUM else "$01"
        amk(csr, msk, val, hp)
    else:
        cli(csr, val, hp)

def set_bit(csr, msk, hp=0):
    """
    Set Bit in CSR
    
    Sets specific bit(s) in a Control and Status Register (CSR) to 1.
    
    Parameters
    ----------
    csr : str
        CSR name or CSR.subfield name
    msk : str
        Bit mask specifying which bit(s) to set
    hp : int, optional
        High priority flag (default: 0)
    
    Returns
    -------
    None
    
    Examples
    --------
    >>> set_bit("exc", "2.0")  # Set the timer exception bit
    >>> set_bit("cfg", "$01")  # Set bit 0 in the cfg register
    """
    set_csr(csr, "$01", msk, hp)

def clr_bit(csr, msk, hp=0):
    """
    Clear Bit in CSR
    
    Clears specific bit(s) in a Control and Status Register (CSR) to 0.
    
    Parameters
    ----------
    csr : str
        CSR name or CSR.subfield name
    msk : str
        Bit mask specifying which bit(s) to clear
    hp : int, optional
        High priority flag (default: 0)
    
    Returns
    -------
    None
    
    Examples
    --------
    >>> clr_bit("exc", "2.0")  # Clear the timer exception bit
    >>> clr_bit("cfg", "$01")  # Clear bit 0 in the cfg register
    """
    set_csr(csr, "$00", msk, hp)

@multi(asm)
def count_down(dur, strict=True):
    """
    Countdown Timer Setup
    
    Configures and starts the countdown timer with the specified duration.
    Can be configured for strict timing requirements.
    
    Parameters
    ----------
    dur : int or expr
        Countdown duration in clock cycles
        - If int: Automatically decremented by 1
    strict : bool, optional
        Whether to enable strict timing mode (default: True)
        - True: Enables timer exception
        - False: Disables timer exception
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Adjusts duration if it's an integer (subtracts 1)
    2. Writes the duration to the timer register
    3. Configures exception handling based on strict flag
    4. Starts the countdown by setting the reset bit
    
    Examples
    --------
    >>> count_down(100)  # 100-cycle countdown with exceptions
    >>> count_down(tmp(-1, delay), False)  # Custom delay without exceptions
    """
    if isinstance(dur, int):
        dur = dur - 1
    mov("tim", dur)
    if strict:
        set_bit("exc", "2.0")
    else:
        clr_bit("exc", "2.0")
    set_bit("rsm", "4.0")

@multi(asm)
def wait(dur=None):
    """
    Wait/Halt Execution
    
    Pauses execution either indefinitely or for a specified duration.
    
    Parameters
    ----------
    dur : int or expr, optional
        Duration to wait in clock cycles
        - If None: Infinite wait (halt)
        - If specified: Waits for the given number of cycles
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. If duration is specified: Sets up a countdown timer with non-strict mode
    2. Issues a halt instruction (nop with H flag)
    
    Examples
    --------
    >>> wait()  # Infinite halt
    >>> wait(10)  # Wait for 10 clock cycles
    >>> wait(tmp(-1, calculated_delay))  # Wait for dynamic duration
    """
    if dur is not None:
        count_down(dur, False)
    nop(1, H)

def get_wck(lo, hi):
    """
    Get Clock Parameters
    
    Reads the low and high watermark clock values into specified registers.
    
    Parameters
    ----------
    lo : str
        Register to store the low watermark clock value (wcl)
    hi : str
        Register to store the high watermark clock value (wch)
    
    Returns
    -------
    None
    
    Examples
    --------
    >>> get_wck('$20', '$21')  # Read clock parameters into $20 and $21
    """
    mov(lo, "wcl")
    mov(hi, "wch")

def jmp_rel(dst, cond=None):
    """
    Relative Jump
    
    Performs a relative jump to the specified destination with an optional condition.
    
    Parameters
    ----------
    dst : str, int, expr
        Target destination (relative offset)
    cond : str, int, expr, optional
        Jump condition mask
        - None: Unconditional jump ("3.0")
        - Otherwise: Used as the condition mask
    
    Returns
    -------
    None
    
    Examples
    --------
    >>> jmp_rel(10)  # Jump forward 10 instructions
    >>> jmp_rel(-5, '$20')  # Jump backward 5 instructions if $20 is non-zero
    """
    cnd = "3.0" if cond is None else cond
    amk("ptr", cnd, dst, P)

def jmp_abs(dst, cond=None):
    """
    Absolute Jump
    
    Performs an absolute jump to the specified destination address with an optional condition.
    
    Parameters
    ----------
    dst : str, int, expr
        Target destination address
    cond : str, int, expr, optional
        Jump condition
        - None: Unconditional jump
        - Otherwise: Used as the condition
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. For unconditional jumps: Uses set_csr to directly set the program counter
    2. For conditional jumps: 
       - Moves condition to temporary register
       - Shifts condition left by 1
       - Uses AMK instruction to perform conditional jump
    
    Examples
    --------
    >>> jmp_abs('#0x1000')  # Unconditional jump to address 0x1000
    >>> jmp_abs('#label', '$20')  # Jump to label if $20 is non-zero
    """
    if cond is None:
        set_csr("ptr", dst, "2.0", P)
    else:
        mov(tmp(0), cond)
        shl(tmp(0), tmp(0), 1)
        amk("ptr", tmp(0), dst, P)

# -----------------------------------------------------------------------------
# --------- RTLink ------------------------------------------------------------
# -----------------------------------------------------------------------------

def pack_frame(flg, chn, adr, tag, pld):
    """
    Pack Frame for RTLK Communication
    
    Creates a packed binary frame for RTLK (Real-Time Link) communication by combining
    frame flags, channel information, address, tag, and payload data into a single byte array.
    
    Parameters
    ----------
    flg : int
        Frame flags (3 bits)
        - First bit: Type (0 for data, 1 for instruction)
        - Remaining bits: Source information
    chn : int
        Channel address (width defined by W_CHN_ADR in RTLK configuration)
    adr : int
        Node address (width defined by W_NOD_ADR in RTLK configuration)
    tag : int
        Tag value (width defined by W_TAG_LTN in RTLK configuration)
    pld : list or tuple
        Payload data (list of integers, each up to 32 bits)
        - Must have length <= N_FRM_PLD (defined in RTLK configuration)
    
    Returns
    -------
    bytes
        Packed binary frame ready for RTLK transmission
    
    Operation
    ---------
    1. Concatenates header fields (flg, chn, adr, tag) into a binary header
    2. Appends each payload word as a 4-byte big-endian value
    3. Handles endianness differences based on PL01 flag
    
    Examples
    --------
    >>> frame = pack_frame(0, 1, 0x1000, 0, [0x1234, 0x5678])
    >>> # Creates a binary frame with data type, channel 1, address 0x1000, and payload [0x1234, 0x5678]
    """
    wcad = C_BASE.RTLK["W_CHN_ADR"]
    wnad = C_BASE.RTLK["W_NOD_ADR"]
    wtag = C_BASE.RTLK["W_TAG_LTN"]
    npld = C_BASE.RTLK["N_FRM_PLD"]
    nhdr = C_BASE.RTLK["N_BYT"] - 4*npld
    tmp = bit_concat((flg, 3), (chn, wcad), (adr, wnad), (tag, wtag)).to_bytes(nhdr,'big')
    rng = range(npld-1, -1, -1) if PL01 else range(npld)
    for i in rng:
        tmp += int(pld[i]).to_bytes(4,'big')
    return tmp

def unpack_frame(frm):
    """
    Unpack RTLK Frame
    
    Parses a binary RTLK frame into its component parts: flags, channel, address, tag, and payload.
    
    Parameters
    ----------
    frm : bytes
        Binary frame data received from RTLK communication
    
    Returns
    -------
    tuple
        (flg, chn, adr, tag, pld) where:
        - flg: Frame flags (3 bits)
        - chn: Channel address
        - adr: Node address
        - tag: Tag value
        - pld: List of payload words (integers)
    
    Operation
    ---------
    1. Extracts the header portion of the frame
    2. Splits the header into individual fields using bit operations
    3. Extracts each payload word from the binary data
    4. Adjusts payload order based on PL01 flag to handle endianness differences
    
    Examples
    --------
    >>> flg, chn, adr, tag, pld = unpack_frame(received_frame)
    >>> # Parses the received binary frame into its component parts
    """
    wcad = C_BASE.RTLK["W_CHN_ADR"]
    wnad = C_BASE.RTLK["W_NOD_ADR"]
    wtag = C_BASE.RTLK["W_TAG_LTN"]
    npld = C_BASE.RTLK["N_FRM_PLD"]
    fhdr = int.from_bytes(frm[0:-(npld*4)], "big")
    fpld = frm[-(npld*4):]
    flg, chn, adr, tag = bit_split(fhdr, (3, wcad, wnad, wtag))
    pld = [0] * npld
    for i in range(npld):
        pld[i] = int.from_bytes(fpld[i*4:i*4+4], "big")
    if PL01:
        pld.reverse()
    return flg, chn, adr, tag, pld

def ich_dnld(payloads, start=0):
    """
    Instruction Cache Download
    
    Downloads a list of instructions into the instruction cache starting at the specified index.
    
    Parameters
    ----------
    payloads : list
        List of instruction words to download (each word is an integer)
    start : int, optional
        Starting index in the instruction cache (default: 0)
    
    Returns
    -------
    None
    
    Raises
    ------
    RuntimeError
        If the number of instructions exceeds the maximum instruction cache capacity
    
    Operation
    ---------
    1. Checks if the number of instructions fits in the cache
    2. Initializes the instruction cache address register
    3. For each instruction:
       - Sets the cache index
       - Writes the instruction word to the cache data register
    
    Examples
    --------
    >>> ich_dnld([0x12345678, 0x87654321], 10)  # Download two instructions starting at index 10
    """
    cap = asm.core.CAP_ICH
    ln = len(payloads)
    if ln > cap:
        raise RuntimeError("Maximum instruction cache capacity exceeded.")
    chi('ica', 0)
    for i in range(ln):
        clo('ica', i + start)
        cli('icd', payloads[i])

@multi(asm)
def rtlk_send(flg, chn, adr, tag, tag_inc, pld, rng=None, align=None):
    """
    RTLK Protocol Send
    
    Sends data or instructions over the Real-Time Link (RTLK) interface with support for both
    single data transfers and bulk data streaming.
    
    Parameters
    ----------
    flg : int or str
        Frame flags or flag string
        - If int: Direct flag value (bits 0-2)
        - If str: Format "[di][nbed]" where:
          * First character: 'd' for data (0), 'i' for instruction (1)
          * Second character: 'n' (0), 'b' (1), 'e' (2), or 'd' (3)
    chn : int or str
        Channel identifier
    adr : int or str
        Address to send data to
    tag : int or str
        Tag value for the transaction
    tag_inc : int or str or None
        Tag increment value for subsequent frames
        - Special value -7 is used for instruction blocks
    pld : int or str or list or tuple
        Payload data
        - Single value: One word of data
        - List/tuple: Multiple words of data
    rng : tuple or list, optional
        Range specification for bulk transfers
        - (stop): 0 to stop with default step
        - (start, stop): Start to stop with default step
        - (start, stop, step): Full range specification
    align : int, optional
        Memory alignment for bulk transfers (default: 4)
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Converts flag string to integer if necessary
    2. Sets up the tag register (combines flags and tag)
    3. Sets up the destination register (combines channel and address)
    4. Handles different payload formats:
       - Single/multiple words: Direct transfer
       - Range-based: Iterates over the specified range
    5. Supports both download and non-download modes
    6. Handles endianness differences based on PL01 flag
    
    Examples
    --------
    >>> # Send two words of data
    >>> rtlk_send(0, 1, 0x1000, 0, 1, [0x1234, 0x5678])
    >>> 
    >>> # Send data with string flag
    >>> rtlk_send("dn", 2, 0x2000, 0, 0, 0xABCD)
    >>> 
    >>> # Bulk transfer with range
    >>> rtlk_send(0, 3, "src_ptr", 100, 1, "dst_ptr", (0, 100, 4))
    """
    # for instr. block, use tag_inc = -7
    if type(flg) is not int:
        flg = str(flg)
        if flg[0] != '$':
            typ = {"d": 0, "i": 1}[flg[0].lower()]
            srf = {"n": 0, "b": 1, "e": 2, "d": 3}[flg[1].lower()]
            flg = (typ<<2) + srf
    # R.$f0 = (flg<<20) + tag
    if type(flg) is int and type(tag) is int:
        mov(tmp(0), (flg<<20)+tag)
    elif flg == 0:
        mov(tmp(0), tag)
    else:
        if type(flg) is int:
            mov(tmp(0), flg << 20)
        else:
            shl(tmp(0), flg, 20)
        add(tmp(0), tmp(0), tmp(-1,tag))        
    # R.frm.dst = (chn<<2) + adr
    if type(chn) is int and type(adr) is int:
        mov('frm.dst', (chn<<20)+adr)
    elif chn == 0:
        mov('frm.dst', adr)
    else:
        if type(chn) is int:
            mov(tmp(-1), chn << 20)
        else:
            shl(tmp(-1), chn, 20)
        add(tmp(-1), tmp(-1), tmp(-2,adr))
        mov("frm.dst", tmp(-1))
    if rng is None:
        if type(pld) not in (tuple,list):
            pld = (pld,0)
        if len(pld) % 2 == 1:
            pld = list(pld) + [0]
        for i in range(0, len(pld), 2):
            mov("frm.tag", tmp(0))
            if tag_inc:
                add(tmp(0), tmp(0), tmp(-1,tag_inc))
            if PL01:
                mov("frm.pl1", pld[i+1])
                mov("frm.pl0", pld[i])
            else:
                mov("frm.pl0", pld[i])
                mov("frm.pl1", pld[i+1])
    else:
        if type(pld) in (tuple,list):
            pld = pld[0]
        align = align or 4
        if type(pld) not in (int,str):
            pld = str(pld)
        if type(rng) not in (tuple,list):
            rng = (rng,)
        if len(rng) == 1:
            start = 0
            stop = rng[0]
        else:
            start = rng[0]
            stop = rng[1]
        step = rng[2] if len(rng) > 2 else align
        dnld = getattr(asm, 'dnld', 1)
        if dnld:
            for_(tmp(1),(start,stop,step))
            for i in range(2):
                if PL01:
                    if type(pld) is str and pld[0] != '$':
                        mov('frm.pl1' if i&1 else tmp(2), pld+'.'+tmp(1))
                    else:
                        add(tmp(-1), tmp(1), tmp(-1,pld))
                        copy(['frm.pl1' if i&1 else tmp(2)], tmp(-1), align)
                    if i&1:
                        mov('frm.tag', tmp(0))
                        mov('frm.pl0', tmp(2))
                    else:
                        add(tmp(1), tmp(1), step)
                else:
                    if i&1:
                        mov('frm.tag', tmp(0))
                    if type(pld) is str and pld[0] != '$':
                        mov(f'frm.pl{i&1}', pld+'.'+tmp(1))
                    else:
                        add(tmp(-1), tmp(1), tmp(-1,pld))
                        copy([f'frm.pl{i&1}'], tmp(-1), align)
                    if not i&1:
                        add(tmp(1), tmp(1), step)
            if tag_inc:
                add(tmp(0), tmp(0), tmp(-1,tag_inc))
            end()
        else:
            if type(pld) is str and pld[0] == '$':
                add(tmp(1), pld, tmp(-1,start))
            while start < stop:
                for i in range(2):
                    if PL01:
                        if type(pld) is str and pld[0] != '$':
                            mov('frm.pl1' if i else tmp(2), pld+f'.&{start:x}')
                        else:
                            if type(pld) is str and pld[0] == '$':
                                add(tmp(1), tmp(1), tmp(-1,step))
                            else:
                                mov(tmp(1), pld+start)
                            copy(['frm.pl1' if i else tmp(2)], tmp(1), align)
                        if i:
                            mov('frm.tag', tmp(0))
                            mov('frm.pl0', tmp(2))
                    else:
                        if i:
                            mov('frm.tag', tmp(0))
                        if type(pld) is str and pld[0] != '$':
                            mov(f'frm.pl{i&1}', pld+f'.&{start:x}')
                        else:
                            if type(pld) is str and pld[0] == '$':
                                add(tmp(1), tmp(1), tmp(-1,step))
                            else:
                                mov(tmp(1), pld+start)
                            copy([f'frm.pl{i&1}'], tmp(1), align)
                    start += step
                if tag_inc:
                    add(tmp(0), tmp(0), tmp(-1,tag_inc))

@multi(asm)       
def intf_send(*pld, rng=None, align=None, oper=None, narg=None, info=None):
    """Send data through the interface with various communication modes.
    
    This function handles communication through the configured interface, supporting
    different types of transfers including data frames, operation frames, and information frames.
    It automates the process of sending data to the appropriate local channel and node address.
    
    Parameters
    ----------
    *pld : variable
        Payload data to be sent
    rng : tuple or list, optional
        Range specification for bulk transfers (same format as rtlk_send)
    align : int, optional
        Memory alignment for bulk transfers (default: 4)
    oper : int, optional
        Operation code to be executed
    narg : int, optional
        Number of arguments for the operation
    info : int, optional
        Information code for special information frames
    
    Returns
    -------
    None or result of rtlk_send
        Returns None if no interface is available, otherwise returns the result of rtlk_send
    
    Notes
    -----
    - Automatically retrieves the interface from asm.intf or asm.cfg.intf
    - Supports three types of frame transmission:
      1. Information frames (when info is specified)
      2. Data frames (when payload is provided)
      3. Operation frames (when oper is specified)
    - Uses 'nex.adr' as the tag source for data frames
    - Uses special encoding for operation frames with optional argument count
    
    Examples
    --------
    >>> # Send data payload
    >>> intf_send(0x1234, 0x5678)
    
    >>> # Send data with operation code
    >>> intf_send(0xABCD, oper=1)
    
    >>> # Send information frame
    >>> intf_send(0xDEADBEEF, info=0x01)
    
    >>> # Send data with range specification
    >>> intf_send([0x11, 0x22, 0x33], rng=(0, 10, 2))
    """
    intf = getattr(asm, 'intf', None)
    if intf is None:
        cfg = getattr(asm, 'cfg', None)
        if cfg is None:
            return
        intf = cfg.intf
    if info is not None:
        mov(tmp(1),'nex.adr')
        and_(tmp(1),tmp(1),tmp(-1,0xffff))
        add(tmp(1),tmp(1),tmp(-1,info<<20))
        return rtlk_send(4, intf.loc_chn, intf.nod_adr, 0, 0, [tmp(1),pld[0]])
    if len(pld) > 0:
        rtlk_send(0, intf.loc_chn, intf.nod_adr, 'nex.adr', 0, pld, rng, align)
    if oper is not None:
        mov(tmp(1),'nex.adr')
        and_(tmp(1),tmp(1),tmp(-1,0xffff))
        if narg is not None:
            add(tmp(1),tmp(1),tmp(-1,narg<<16))
        rtlk_send(0, intf.loc_chn, intf.nod_adr, 0xffff, 0, [tmp(1),oper])

def intf_run(func,sync=True,intf=None,cfg=None):
    """Run a function through the specified interface with configurable synchronization.
    
    This function executes the provided function through the specified interface,
    supporting both synchronous and asynchronous execution modes. It automatically
    handles core configuration and interface setup.
    
    Parameters
    ----------
    func : callable
        The function to be executed through the interface
    sync : bool, optional
        Synchronization mode flag (default: True)
        - True: Wait for execution to complete and return results
        - False: Start execution asynchronously and return immediately
    intf : object, optional
        Interface object to use for execution
    cfg : object, optional
        Configuration object containing interface and core settings
    
    Returns
    -------
    object or None
        Result of function execution if sync=True, otherwise None
    
    Notes
    -----
    - Saves the current core configuration
    - If no interface is provided, it attempts to use the configuration's interface
    - Handles both synchronous and asynchronous operation modes
    - Restores the original core configuration after execution
    
    Examples
    --------
    >>> # Run function synchronously through an interface
    >>> intf_run(my_function, sync=True, intf=my_interface)
    
    >>> # Run function asynchronously with configuration
    >>> intf_run(my_function, sync=False, cfg=my_config)
    """
    core = asm.core
    if intf is None:
        intf = getattr(asm, 'intf', None)
    if intf is None:
        if cfg is None:
            cfg = getattr(asm, 'cfg', None)
        if cfg is None:
            return lambda *args:None
        intf = cfg.intf
        core = cfg.core
    oper = intf.oper.get((id(func)<<1)|sync,None)
    if oper is None:
        def cb(buf,cfg):
            if sync:
                with asm:
                    asm.dnld = 0
                    asm.core = core
                    func(buf)
                    clr_bit("exc", "1.0", P)
                    cfg(asm[:],rply=0)
            else:
                cfg.core = core
                cfg(func,dnld=0)(buf)
        oper = len(intf.oper) + 1
        intf.oper[(id(func)<<1)|sync] = oper
        intf.oper[oper] = cb
    def wrap(*args,**kwargs):
        narg = kwargs.get('narg',None)
        if narg is None:
            narg = len(args)
            if narg&1:
                narg += 1
            kwargs['narg'] = narg
        intf_send(*args,**kwargs,oper=oper)
        if sync:
            set_bit("exc", "1.0", P)
    return wrap

intf_run_async = lambda func: intf_run(func,sync=False)

@multi(asm)
def scp_read(adr, dst):
    """Read data from Scratchpad Memory (SCP) to a destination.
    
    This function reads data from the Scratchpad Memory (SCP) at the specified address
    and moves it to the destination register or memory location.
    
    Parameters
    ----------
    adr : int, str, or expr
        Source address in the scratchpad memory to read from
    dst : str, or expr
        Destination register or memory location to store the read data
    
    Returns
    -------
    None
    
    Notes
    -----
    - Uses 'scp.mem' CSR to set the read address
    - Includes a NOP instruction with P flag to wait for data to be available
    - Moves the data from 'scp' CSR to the destination
    
    Examples
    --------
    >>> # Read from address 0x100 in SCP to register $20
    >>> scp_read(0x100, '$20')
    
    >>> # Read from address stored in $21 to register $22
    >>> scp_read('$21', '$22')
    """
    mov("scp.mem", adr)
    nop(1, P)
    mov(dst, "scp")

@multi(asm)
def wait_rtlk_trig(typ, cod, tout=None):
    """Wait for RTLink trigger event with optional timeout.
    
    This function configures the system to wait for a specific RTLink trigger event
    of the specified type and code. It can optionally set a timeout period.
    
    Parameters
    ----------
    typ : str
        Trigger type: 'c' for code-based trigger, 't' for tag-based trigger
    cod : int, str, or expr
        Trigger code or tag value to wait for
    tout : int, optional
        Timeout period in clock cycles. If None, no timeout is set.
    
    Returns
    -------
    None
    
    Notes
    -----
    - Configures either 'scp.cdm' (for code-based) or 'scp.tgm' (for tag-based) trigger
    - Sets the '2.F' bit in 'scp' CSR to enable trigger monitoring
    - If timeout is specified, configures the timer with the timeout value
    - Uses 'rsm' CSR to set up the resume condition
    - Clears the exception bit '2.0' with H flag to wait for the trigger
    - Cleans up the configuration after the trigger is received
    
    Examples
    --------
    >>> # Wait for code-based trigger with code 0x1234
    >>> wait_rtlk_trig('c', 0x1234)
    
    >>> # Wait for tag-based trigger with tag 0x5678 and 10000 cycle timeout
    >>> wait_rtlk_trig('t', 0x5678, tout=10000)
    """
    mov({"c": "scp.cdm", "t": "scp.tgm"}[typ], cod)
    set_bit("scp", "2.F")
    if tout is not None:
        flg = "6.0"
        set_csr("tim", tout, "2.0")
    else:
        flg = "2.0"
    set_bit("rsm", flg)
    clr_bit("exc", "2.0", H)
    clr_bit("rsm", flg)
    clr_bit("scp", "2.F")

@multi(asm)
def send_trig_code(flg, adr, ltn, code):
    """Send trigger code through RTLink network to a target node.
    
    This function generates an instruction frame containing trigger code to be executed
    on a remote RT-Core via the RTLink network. It configures the scratchpad memory
    (SCP) with the specified code and sends it using the RTLink protocol.
    
    Parameters
    ----------
    flg : int or str
        Frame routing flags: 0 for normal, 1 for broadcast, 2 for echo, 3 for directed frame
    adr : int
        16-bit destination node address
    ltn : int
        Required latency (in clock cycles) between frame generation and consumption
    code : int or TCS entry
        The trigger code to be sent:
        - If int: Directly encoded into the instruction
        - If TCS entry: Contents of the TCS entry will be used as the code
    
    Returns
    -------
    None
    
    Notes
    -----
    - The function uses SFS instruction to select the 'cod' CSR in the 'scp' subfile
    - Depending on whether code is an integer or a TCS entry, it uses either CLO or AMK instruction
    - The generated instructions are sent as an instruction frame with CHN=0 (RT-Core)
    
    Examples
    --------
    >>> # Send a trigger code with normal routing to node 0x0001 with 100 cycle latency
    >>> send_trig_code(0, 0x0001, 100, 0xABCD)
    
    >>> # Send a broadcast trigger code using a TCS value
    >>> mov('$20', 0x1234)
    >>> send_trig_code(1, 0xFFFF, 50, '$20')
    """
    with asm as trg:
        sfs("scp", "cod")
        if isinstance(code, int):
            clo("scp", code)
        else:
            amk("scp", "$01", code)
    rtlk_send(flg, 0, adr, ltn, 0, trg[:])

# -----------------------------------------------------------------------------
# --------- Debug Helper ------------------------------------------------------
# -----------------------------------------------------------------------------

class ich_cfg:
    """
    Instruction Cache Configuration
    
    This class provides a configuration interface for generating instruction cache contents
    and saving them to a file for external use. It supports a two-phase call pattern to
    capture both the function to be assembled and its execution arguments.
    
    Instance Attributes:
        fn : str
            Output file path for the generated instruction cache content
        core : object, optional
            Core configuration to use (defaults to current asm.core)
        stat : int
            Internal state tracker (0: initial, 1: function captured)
        func : callable
            The function to be assembled into instruction cache content
    
    Parameters
    ----------
    fn : str
        Path to the output file where instruction cache content will be saved
    core : object, optional
        Specific core configuration to use (default: None - uses current asm.core)
    
    Methods
    -------
    __call__(func)
        First phase: Capture the function to be assembled
    __call__(*args, **kwargs)
        Second phase: Execute the function, generate instruction cache content, and save to file
    
    Examples
    --------
    >>> # Configure instruction cache and generate content
    >>> cfg = ich_cfg("instructions.hex", core=my_core)
    >>> cfg(lambda:
    ...     mov('$20', 42)
    ...     add('$21', '$20', '$20')
    ... )(arg1, arg2)  # Saves generated instructions to "instructions.hex"
    """
    def __init__(self, fn, core=None):
        """
        Initialize instruction cache configuration
        
        Parameters
        ----------
        fn : str
            Path to the output file for instruction cache content
        core : object, optional
            Core configuration to use
        """
        self.fn = fn
        self.core = core
        self.stat = 0

    def __call__(self, *args, **kwargs):
        """
        Two-phase call implementation
        
        First call: Captures the function to be assembled
        Second call: Executes the function, generates instructions, and saves to file
        
        Parameters
        ----------
        *args : variable
            First call: Function to be assembled
            Second call: Arguments to pass to the assembled function
        **kwargs : variable
            Second call: Additional keyword arguments
        
        Returns
        -------
        self or None
            First call: Returns self for method chaining
            Second call: Returns None
        
        Operation
        ---------
        First phase:
        1. Stores the function reference
        2. Sets internal state to 1
        3. Returns self to enable method chaining
        
        Second phase:
        1. Resets internal state
        2. Sets up core configuration
        3. Assembles the function
        4. Initializes special registers
        5. Formats instruction cache content as hex strings
        6. Writes content to the specified file
        """
        if self.stat == 0:
            self.func = args[0]
            self.stat = 1
            return self
        self.stat = 0
        if self.core is None:
            self.core = asm.core
        with asm:
            asm.core = self.core
            init01()
            self.func(*args, **kwargs)
            nop(2, H)
            ram = "@00000000\n"
            for ins in asm[:]:
                ram += f"{ins:08X}\n"
            with open(self.fn, "w") as f:
                f.write(ram)

class run_cfg:
    """
    Runtime Configuration for RTMQ Execution
    
    This class provides a comprehensive configuration interface for executing RTMQ programs
    across multiple nodes or destinations. It supports a two-phase call pattern to first
    capture the function to be executed and then configure execution parameters.
    
    Instance Attributes:
        intf : object
            Interface object for communication
        flg : int
            Frame flags (parsed from string if needed)
        chn : int
            Channel identifier
        dst : list
            List of destination addresses
        mon : list
            List of monitor addresses
        tag : int
            Initial tag value
        core : object, optional
            Core configuration
        stat : int
            Internal state tracker (0: initial, 1: function captured)
        func : callable or object
            The function or flow to be executed
        dnld : int
            Download mode flag
        rply : int
            Reply mode flag
        tout : float
            Timeout value in seconds
        proc : callable, optional
            Result processing function
    
    Parameters
    ----------
    intf : object
        Interface for communication with cores
    dst : list
        List of destination addresses
    mon : list, optional
        List of monitoring addresses (default: same as dst)
    chn : int, optional
        Channel identifier (default: 0)
    flg : str or int, optional
        Frame flags as string (e.g., "in") or integer (default: "in")
        - String format: "[di][nbed]"
          * First character: 'd' for data (0), 'i' for instruction (1)
          * Second character: 'n' (0), 'b' (1), 'e' (2), or 'd' (3)
    tag : int, optional
        Initial tag value (default: 0)
    core : object, optional
        Core configuration to use
    
    Methods
    -------
    __call__(func, **kwargs)
        First phase: Capture function and configure execution parameters
    __call__(*args, **kwargs)
        Second phase: Execute the function with the specified configuration
    
    Examples
    --------
    >>> # Configure and run a function
    >>> cfg = run_cfg(my_interface, [0x1000, 0x2000], chn=1, flg="in")
    >>> cfg(lambda x: 
    ...     mov('$20', x)
    ...     add('$21', '$20', 10)
    ... , dnld=1, tout=2.0)(42)  # Executes on destinations with value 42
    """
    def __init__(self, intf, dst, mon=None, chn=0, flg="in", tag=0, core=None):
        """
        Initialize runtime configuration
        
        Parameters
        ----------
        intf : object
            Interface for communication
        dst : list
            List of destination addresses
        mon : list, optional
            List of monitor addresses
        chn : int, optional
            Channel identifier (default: 0)
        flg : str or int, optional
            Frame flags (default: "in")
        tag : int, optional
            Initial tag value (default: 0)
        core : object, optional
            Core configuration
        """
        if isinstance(flg, str):
            typ = {"d": 0, "i": 1}[flg[0].lower()]
            srf = {"n": 0, "b": 1, "e": 2, "d": 3}[flg[1].lower()]
            flg = typ * 4 + srf
        self.intf = intf
        self.flg = flg
        self.chn = chn
        self.dst = dst
        self.mon = dst if mon is None else mon
        self.tag = tag
        self.core = core
        self.stat = 0

    def __call__(self, *args, **kwargs):
        if self.stat == 0:
            self.func = args[0]
            self.dnld = kwargs["dnld"] if "dnld" in kwargs else 1
            self.rply = kwargs["rply"] if "rply" in kwargs else 1
            self.dst  = kwargs["dst"] if "dst" in kwargs else self.dst
            self.mon  = kwargs["mon"] if "mon" in kwargs else self.mon
            self.tout = kwargs["tout"] if "tout" in kwargs else 1.0
            self.proc = kwargs["proc"] if "proc" in kwargs else None
            if type(self.func) is not table and callable(self.func):
                self.stat = 1
                return self
        self.stat = 0
        if not callable(self.func):
            flw = self.func
        else:
            with asm as flw:
                asm.intf = self.intf
                asm.tout = self.tout
                asm.proc = self.proc
                if type(self.func) is table:
                    nodes = getattr(self.func,'multi',None)
                    if nodes is None:
                        asm.dnld = self.dnld
                        asm(*self.func[:],**self.func.__dict__)
                    else:
                        asm.multi = nodes
                        for adr in nodes:
                            asm[str(adr)] = self.func[str(adr)].copy()
                            if getattr(asm[str(adr)],'dnld',None) is None:
                                asm[str(adr)].dnld = self.dnld
                else:
                    if self.core is not None:
                        asm.core = self.core
                    asm.dnld = self.dnld
                    res = self.func(*args, **kwargs)
                    if len(asm) == 0:
                        return res
                finish()
        with self.intf:
            nodes = getattr(flw,'multi',None)
            if nodes is None:
                rply = getattr(flw,'rply',getattr(flw,'dnld',self.rply))
                for adr in self.dst:
                    self.intf.write(self.flg, self.chn, adr, self.tag, flw[:])
            else:
                flws = flw
                rply = 0
                for i in range(len(self.dst)):
                    flw = flws[str(nodes[i])]
                    rply += getattr(flw,'rply',flw.dnld and self.rply)
                    self.intf.write(self.flg, self.chn, self.dst[i], self.tag, flw[:])
            if (self.intf.thread and self.intf.thread.running) or not rply:
                return None
            tout = getattr(flw,'tout',self.tout)
            res = self.intf.monitor(self.mon, round(tout * 10))
            proc = getattr(flw,'proc',self.proc)
            if proc is None:
                return None if len(res) == 0 else res
            else:
                ret = dict()
                for k, v in res.items():
                    ret[k] = proc(k, v)
                return ret
        
class assembler:
    """
    RTMQ v2 Assembler Interface
    
    This class provides the main interface for RTMQ v2 assembly and execution. It manages
    the configuration of cores, interfaces, and supports both single-core and multi-core
    assembly operations through a context management system.
    
    Instance Attributes:
        cfg: Configuration object containing core and interface settings
        asm: The active assembly context
        [node_names]: Dynamic attributes for multi-core setups
    
    Parameters:
        cfg (optional): Configuration object with 'core' and 'intf' attributes
        multi (optional): List of core identifiers or (node_name, core) tuples for multi-core setup
    
    Methods:
        __getitem__(key): Access node-specific assembly contexts in multi-core mode
        __setitem__(key, val): Set node-specific attributes
        run(): Execute the assembled program
        clear(): Reset the assembly state
    
    Special features:
        - Supports both single-core and multi-core assembly
        - Provides context management for assembly operations
        - Automatically configures interfaces and cores
        - Enables node-specific assembly contexts in multi-core mode
    
    Examples:
        >>> # Single-core assembly
        >>> with assembler(cfg) as program:
        >>>     mov('$20', 42)
        >>>     program.run()
        
        >>> # Multi-core assembly
        >>> with assembler(cfg, ['node1', 'node2']) as program:
        >>>     with program.node1:
        >>>         mov('$20', 1)
        >>>     with program.node2:
        >>>         mov('$20', 2)
        >>>     program.run()
    """
    def __init__(self, cfg=None, multi=None):
        self.cfg = cfg
        core = cfg and cfg.core or asm.core
        intf = cfg and cfg.intf or getattr(asm,'intf',None)
        with asm as self.asm:
            if multi is None:
                setup(core)
                asm.intf = intf
            else:
                nodes = []
                cores = []
                for i in multi:
                    if type(i) in (tuple,list):
                        nodes.append(str(i[0]))
                        cores.append(i[1])
                    else:
                        nodes.append(str(i))
                        cores.append(core)
                asm.multi = nodes
                for i in range(len(nodes)):
                    name = nodes[i]
                    setup[name](cores[i])
                    asm[name].intf = intf
                    self[name] = asm < asm[name]
                        
    def __getitem__(self, key):
        return getattr(self, str(key))
    
    def __setitem__(self, key, val):
        return setattr(self, str(key), val)
    
    def run(self, disa=False):
        if disa:
            multi = getattr(self.asm,'multi',None)
            if multi is None:
                print(disassembler()(self.asm,0))
            else:
                for i in multi:
                    print(i)
                    print(disassembler()(self.asm[str(i)],0))
        if self.cfg and self.cfg.intf:
            return self.cfg(self.asm)
    
    def clear(self):
        multi = getattr(self.asm,'multi',None)
        if multi is None:
            self.asm.clear()
        else:
            for i in multi:
                self.asm[str(i)].clear()
        return self

    def __enter__(self):
        self.asm = asm <= self.asm

    def __exit__(self, exc_type, exc_value, traceback):
        self.asm = asm <= self.asm

    def __call__(self, *args, **kwargs):
        if len(args) > 0:
            multi = getattr(self.asm,'multi',None)
            if multi is None:
                with self:
                    args[0](*args[1:],**kwargs)
            elif callable(args[0]):
                for i in multi:
                    with self[i]:
                        args[0](i,*args[1:],**kwargs)
            elif len(args) > 1:
                env = self if args[0] is None else getattr(self,str(args[0]),None)
                if env is not None:
                    with env:
                        args[1](*args[2:],**kwargs)
        return self
                    
def core_run(func):
    """
    Core Execution Decorator
    
    Decorator that wraps functions to handle core execution in both direct and configured modes.
    When a configuration is available, it uses the configuration to execute the function.
    Otherwise, it executes the function directly.
    
    Parameters
    ----------
    func : callable
        The function to be wrapped for core execution
    
    Returns
    -------
    callable
        Wrapper function that handles both direct and configured execution modes
    
    Operation
    ---------
    1. Checks if a configuration object is available in the assembly context
    2. If no configuration exists, calls the function directly
    3. If configuration exists, uses it to execute the function
    
    Examples
    --------
    >>> @core_run
    >>> def my_function(x, y):
    >>>     return x + y
    
    >>> # Will execute directly when no cfg is set
    >>> # Will use cfg when it's available
    """
    def wrap(*args, **kwargs):
        cfg = getattr(asm,'cfg',None)
        return func(*args, **kwargs) if cfg is None else cfg(func)(*args,**kwargs)
    return wrap

@core_run
def core_read(*args, **kwargs):
    """
    Core Read Operation
    
    Performs read operations on the core through the configured interface.
    Uses the core_run decorator to handle both direct and configured execution modes.
    
    Parameters
    ----------
    *args : variable
        Arguments to be passed to the interface send operation
        - Typically includes source address or buffer information
    **kwargs : variable
        Additional keyword arguments
        - proc : Optional processing function to apply to read results
        - Other arguments are passed to intf_send
    
    Returns
    -------
    object
        Result from the interface operation, possibly processed through proc
    
    Operation
    ---------
    1. Sets download mode to disabled
    2. Sets reply mode to enabled
    3. Configures processing function if provided
    4. Calls intf_send with operation code 0 for read
    
    Examples
    --------
    >>> # Basic core read
    >>> core_read(0x1000)
    
    >>> # Core read with result processing
    >>> core_read(0x2000, proc=lambda x: x * 2)
    """
    asm.dnld = 0
    asm.rply = 1
    proc = kwargs.get('proc',None)
    if proc is not None:
        kwargs.pop('proc')
        asm.proc = lambda a, x: proc(x)
    intf_send(*args,**kwargs,oper=0)

@core_run
def core_write(dst, val, align=4):
    """
    Core Write Operation
    
    Performs write operations to the core through the configured interface.
    Uses the core_run decorator to handle both direct and configured execution modes.
    
    Parameters
    ----------
    dst : str, int, expr
        Destination address or register for the write operation
    val : int, str, list, tuple, expr
        Value(s) to write
        - Single value: Writes one word
        - List/tuple: Writes multiple consecutive words
    align : int, optional
        Memory alignment requirement in bytes (default: 4)
    
    Returns
    -------
    None
    
    Operation
    ---------
    1. Sets download mode to disabled
    2. Uses the copy function to perform the write operation
    
    Examples
    --------
    >>> # Write single value
    >>> core_write(0x1000, 0x12345678)
    
    >>> # Write multiple values with custom alignment
    >>> core_write(0x2000, [0x1111, 0x2222, 0x3333], align=8)
    
    >>> # Write to register
    >>> core_write('$20', 42)
    """
    asm.dnld = 0
    copy(dst, val, align=align)
