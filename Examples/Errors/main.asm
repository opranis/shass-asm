.org    9

Test
        DEC
        ASR
        INC
        LSL
        LSR
        NEG
        NOT

.include main_inc.asm

        CLC
        TAX
        TXA
        INX
        DEX
        TAS
        TSA
        INS
        DES
        RTS
        POPF
        PUSHF
        NOP
        ADCI    10
        ADDI    10
        ANDI    10
        CMPI    10
        ORI     10
        SBBI    10
        SUBI    10
        TSTI    10
        XORI    10
        LDI     10
        LDD     variable
        STD     variable
        JA      Test
        JNC     Test
        JAE     .IP
        JC      Test
        JB      Test
        JBE     Test
        JE      Test
        JZ      Test
        JG      Test
        JGE     Test
        JL      Test
        JLE     Test
        JNZ     Test
        JNE     Test
        JNS     Test
        JNU     Test
        JNV     Test
        JS      Test
        JU      Test
        JV      Test
        IN      10
        OUT     10
        JMP     .IP
        CALL    Test
        ST      X+ 10
        LD      -S 33
        ADC     54
        ADD     S 32
        AND     X 31
        CMP     S 10
        OR      variable5
        SBB     variable
        SUB     variable
        TST     variable3
        XOR     variable2

.dseg

variable5        1