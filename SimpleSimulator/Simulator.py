#Vaibhav's work
DATA_MEM_BASE = 0x00010000
DATA_MEM_END  = 0x0001007F
STACK_BASE    = 0x00000100
STACK_END     = 0x0000017F

def to_signed32(val):
    val = val & 0xFFFFFFFF
    if val >= (1 << 31):
        val -= (1 << 32)
    return val

def to_unsigned32(val):
    return val & 0xFFFFFFFF