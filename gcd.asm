; This is the solution for homework #5.
; This subroutine implements the Euclid's algorithm
; for computing the greatest common divisor of 2 unsigned integers.
; The 2 values are initially stored in memory addresses 00 and 01.
; This program destroys the initial values at these addresses,
; and returns the output in the accumulator, and memory address 00.
;
; This code was tested with the values listed at the bottom of the file.
;
; Revision History
;     13 Feb 22  Olivers Pranis     Solution code


Zero
                    ;if either value is 0, gcd is 0
        LDD   b     ;load b into acc
        CMPI  0     ;compare b with 0
        JE    EndN  ;if is equal, end the program without loading again
        NOP         ;
        LDD   a     ;load a into acc
        CMPI  0     ;compare a with 0
        JE    EndN  ;if is equal, end the program without loading again

Start
        LDD   a     ;load a
        SUB   b     ;and subtract b
        JB    Swap  ;if a ended up being smaller, swap the values
        NOP         ;
        STD   a     ;otherwise, store the value into a
        JMP   Start ;and start from beginning again

Swap
                    ;Swap a and b:
        LDD   a	    ;get a
        TAX	    ;and put it in X temporarily
        LDD   b	    ;now get b
        STD   a	    ;and store it in a
        TXA	    ;get original a back
        STD   b	    ;and store it in b
                    ;Test if b == 0:
        LDD   b     ;load b into acc
        CMPI  0     ;compare b with 0
        JE    End   ;if is equal, end the program
        NOP         ;
        JMP   Start ;otherwise, if b is not 0, jump to beginning

End
    LDD   a         ;load a into acc, which is now the GCD
EndN
    RTS             ;return

.dseg

a       1
b       1

;Test Cases:
;75 and 87 = 9
;87 and 75 = 9
;0 and 0   = 0
;0 and 16  = 0
;16 and 0  = 0
;1 and FF  = 1
;94 and 94 = 94
;11 and FB = 1
;19 and 7D = 19
;19 and 23 = 5