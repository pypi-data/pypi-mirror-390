import src.ss_ord as ss_ord
import sys

status = False
if status == False:
    print("This file was disabled.")
    sys.exit(1)

user_string = input("Enter a string: ")
print("Coded string: ", ss_ord.SSORD1_code(user_string))
print("Coded string (with shift 15): ", ss_ord.SSORD1_code(user_string, 15))

coded_string_normal = ss_ord.SS1_code("This string coded normally.")
coded_string_s15 = ss_ord.SS1_code("This string coded with shift 15.", 15)

print("Decoded string: ", ss_ord.SS1_decode(coded_string_normal))
print("Decoded string (with shift 15): ", ss_ord.SS1_decode(coded_string_s15, 15))

print("SS-1 (SS-ORD) tests complete.")