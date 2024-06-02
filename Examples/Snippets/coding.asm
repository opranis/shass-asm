;below are a number of code examples for doing simple operations on
;the Caltech10 Microprocessor


;Revision History
;   14 Feb 19   Glen George        initial revision
;   22 Jan 20   Glen George        updated comments

.dseg

;the examples use the following variables
var1    1			;any variable
var2    1			;any other variable
a16High	1			;high byte of a16 (16-bit value)
a16Low	1			;low byte of a16 (16-bit value)
b16High	1			;high byte of b16 (16-bit value)
b16Low	1			;low byte of b16 (16-bit value)

.cseg

Swap
;swap var1 and var2
	LDD   var1		;get var1
	TAX			;and put it in X temporarily
	LDD   var2		;now get var2
	STD   var1		;and store it in var1
	TXA			;get original var1 back
	STD   var2		;and store it in var2


16RightShift
;16-bit logical right shift of a16
	LDD   a16High		;shift high byte first
	LSR			;do the shift (low bit is in carry now)
	STD   a16High		;store new high byte
	LDD   a16Low		;now shift the low byte in
	RRC			;need rotate to bring carry (low bit of high
                                ;   byte) into high bit of low byte
	STD   a16Low		;store the new low byte


16Subtract
;16-bit subtract (a16 <- a16 - b16)
	LDD   a16Low		;subtract low bytes first
	SUB   b16Low
	STD   a16Low		;and put result back in a
	LDD   a16High		;now subtract the high bytes
	SBB   b16High		;   propagating the borrow
	STD   a16High		;and store result back in a


16Compare
;16-bit unsigned compare of a16 and b16
	LDD   a16High		;compare high bytes first
	CMP   b16High
	JB    aLTb		;a < b
	LDD   a16Low		;get ready to compare low bytes in branch delay slot
	JA    aGTb		;a > b
	CMP   b16Low		;compare low bytes
	JB    aLTb		;a < b (only get here if high bytes equal)
	NOP			;branch delay slot
	JA    aGTb		;a > b (only get here if high bytes equal)
	NOP			;branch delay slot
	;JE   aEQb		;a = b (both high and low bytes equal)
aEQb    ;some code		;handle a = b case
        JMP   elsewhere
        NOP
aGTb 	;some code		;handle a > b case
        JMP   elsewhere
        NOP
aLTb 	;some code		;handle a < b case
        JMP   elsewhere
        NOP
elsewhere
	NOP
	NOP
	NOP
	JMP   .IP

