# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ Project:     j2gpp-verilog                                                ║
# ║ Author:      Louis Duret-Robert - louisduret@gmail.com                    ║
# ║ Website:     louis-dr.github.io                                           ║
# ║ License:     MIT License                                                  ║
# ║ File:        filters.py                                                   ║
# ╟───────────────────────────────────────────────────────────────────────────╢
# ║ Description: Additional filters for Verilog and SystemVerilog.            ║
# ║                                                                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝



from math import ceil, log2



extra_filters = {}



extra_filters['clog2'] = lambda x : ceil(log2(x))
