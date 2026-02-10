# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ Project:     j2gpp-verilog                                                ║
# ║ Author:      Louis Duret-Robert - louisduret@gmail.com                    ║
# ║ Website:     louis-dr.github.io                                           ║
# ║ License:     MIT License                                                  ║
# ║ File:        tests.py                                                     ║
# ╟───────────────────────────────────────────────────────────────────────────╢
# ║ Description: Additional tests ilters for Verilog and SystemVerilog.       ║
# ║                                                                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝



extra_tests = {}



extra_tests['power_of_two'] = lambda x : x & (x - 1) == 0
