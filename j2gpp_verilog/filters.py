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

# Log2 rounded up for bus width calculation
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

# Invert the direction
def invert(direction):
  if   direction=="input":  return "output"
  elif direction=="output": return "input"
  elif direction=="inout":  return "inout"
  else:
    throw_error(f"Invalid direction '{direction}' for filter 'invert'.")
    return direction
extra_filters['invert'] = invert

# Invert the direction if condition is true
def invert_if(direction, condition):
  if condition: return invert(direction)
  else: return direction
extra_filters['invert_if'] = invert_if



# ┌──────────────┐
# │ Block format │
# └──────────────┘

# Remove the comma at the end of the last non-commented non-empty line
def remove_last_comma(content):
  lines = content.split('\n')
  for idx, line in reversed(list(enumerate(lines))):
    line_strip = line.lstrip()
    if line_strip and line_strip[0] != '/':
      lines[idx] = line.replace(',', '', 1)
      break
  return '\n'.join(lines)
extra_filters['remove_last_comma'] = remove_last_comma
