# SS-ORD
SS-ORD it's a library for SS-ORD coding algorythm.

It supports all SS-ORD versions (because it's only one heh)
## How it work?
In for cycle, library receive current symbol Unicode number

And performs the action described by the formula:

SymbolUnicodeNumber - Shift

Shift defaulty 10, but in functions (code and decode) you can indicate the shift.

## How use it?
Coding example:

coded_string = ss_ord.SS1_code("This string will be coded with SS-ORD algorythm.") # Normally coding

coded_string_s15 = ss_ord.SS1_code("This string will be coded with SS-ORD algorythm with shift 15.", 15) # Indicating the shift (in this case, 15)

Decoding example:

coded_string = SS1_code("This string will be decoded.")

coded_string_s15 = SS1_code("This string will be decoded with shift 15.", 15)

print(ss_ord.SS1_decode(coded_string))

print(ss_ord.SS1_decode(coded_string_s15))