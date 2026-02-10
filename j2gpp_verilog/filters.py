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
from j2gpp.utils import throw_error



extra_filters = {}



# ┌───────────────┐
# │ Basic filters │
# └───────────────┘

extra_filters['clog2'] = lambda x : ceil(log2(x))

# Vector or array declaration size
def array_width(width, str_len=0):
  if width is None: return "".rjust(str_len)
  elif isinstance(width, str):
    if width == "": return "".rjust(str_len)
    else: return f"[{width}-1:0]".rjust(str_len)
  else:
    try:
      width = int(width)
    except Exception as exc:
      throw_error(f"Exception occured in filter 'array_width' width width '{width}' : \n  {type(exc).__name__}\n{intend_text(exc)}")
      return ""
    if width <= 0:
      throw_error(f"Invalid zero or negative width '{width}' for filter 'array_width'.")
      return ""
    elif width == 1: return "".rjust(str_len)
    else: return f"[{width-1}:0]".rjust(str_len)
extra_filters['array_width'] = array_width
extra_filters['arr']         = array_width # Alias
