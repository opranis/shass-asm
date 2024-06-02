; This subroutine computes the 8-bit value of the nth Fibonacci number.  The
; nth Fibonacci number is defined recursively as:
;       f[n] = f[n-1] + f[n-2] for n >= 3 and
;       f[1] = f[2] = 1
; The value of n, an 8-bit value, is stored in memory in the variable n and at
; the end of the function the nth Fibonacci number is returned in the
; accumulator.  The value of n is destroyed by the program.  Note that there
; is no error checking on the value of n and a value of 0 or values larger
; than 13 (decimal) will cause an overflow and generate incorrect results.
;
; Revision History
;     2 Feb 18  Glen George      Initial revision
;     8 Jan 20  Glen George      Updated comments
;     9 Feb 21  Glen George      Updated comments

.cseg

start			;initialize variables
    LDI   0
    STD   f2		;f2 := f[n-2] = 0
    INC
    STD   f1		;f1 := f[n-1] = 1
    STD   f 		;Fibonacci number (f[1]) is 1 too

FibLoop			;loop, computing nth Fibonacci number
    LDD   n			;update the Fibonacci count by 1
    DEC
    JZ    Done		;if n is now 0, we're done
    ;JNZ  FibBody		;otherwise compute the next number
    STD   n			;always store new value of n (branch slot)

FibBody			;compute the next fibonacci number
    LDD   f1		;get the value of f1 in accumulator
    ADD   f2		;compute new fibonacci number (f1+f2)
    STD   f			;and store it
    STD   f1		;also store it in f1, it is new f[n-1]
    SUB   f2		;subtract f2 from f to get old f1
    STD   f2		;store this in f2, it is new f[n-2]
    JMP   FibLoop		;and loop
    NOP			;branch slot

Done			;done with the calculation
    LDD   f			;get returned Fibonacci value into accumulator
    RTS                     ;and return



;Variables
.dseg

f       1			;the current Fibonacci number
f1      1			;the Fibonacci number from last time
f2      1			;the Fibonacci number from 2 times ago
n       1			;the desired Fibonacci number index
