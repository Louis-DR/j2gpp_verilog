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



import re
from math import ceil, log2
from j2gpp.utils import throw_error
from j2gpp.filters import align
from jinja2.filters import do_indent



extra_filters = {}



# ┌─────────────────────┐
# │ Regular expressions │
# └─────────────────────┘

# Module Port Definition (stopping after name)
# Matches: "input wire [7:0] name" or "output reg name"
regex_portDefinition_noArray_noComma = re.compile(r"""
  ^\s*
  (?P<dir>input|output|inout)               # Direction
  (?:\s+(?P<type>[a-zA-Z_]\w*))?            # Optional net type (wire/reg/logic)
  (?:
    \s+
    (?P<packed>\[\s*[^:]*\s*:\s*[^:]*\s*\]) # Optional packed dimension [MSB:LSB]
  )?
  \s+
  (?P<name>[a-zA-Z_]\w*)                    # Port name
""", re.VERBOSE)

# Instance Port Connection
# Matches: ".port_name ( connection_expression ),"
regex_portConnection = re.compile(r"""
  ^\s*
  \.(?P<port_name>[a-zA-Z_]\w*)             # Port name
  \s*
  \(
  \s*
  (?P<connection>[^)]*)                     # Connection expression
  \s*
  \)
  \s*
  ,?                                        # Optional comma
""", re.VERBOSE)

# Wire/Signal Definition (stopping after name)
# Matches: "wire [7:0] name" or "logic name"
regex_wireDefinition_noArray_noComma = re.compile(r"""
  ^\s*
  (?P<type>wire|logic|reg|bit|int)          # Signal type
  (?:
    \s+
    (?P<packed>\[\s*[^:]*\s*:\s*[^:]*\s*\]) # Optional packed dim [MSB:LSB]
  )?
  \s+
  (?P<name>[a-zA-Z_]\w*)                    # Signal name
""", re.VERBOSE)

# Assign Statement
# Matches: "assign x = y;"
regex_assignStatement = re.compile(r"""
  ^\s*
  assign\s+
  (?P<lhs>[^=]*[^=\s])                      # Left-hand side
  \s*=\s*
  (?P<rhs>[^;]*[^;\s])                      # Right-hand side
  \s*;
""", re.VERBOSE)

# Parameter Definition
# Matches: "parameter type [p:p] name [u:u] = value;"
regex_parameterDefinition = re.compile(r"""
  ^\s*
  (?P<keyword>parameter|localparam|specparam)
  \s+
  (?:                                       # Optional type block
    (?P<type>(?:(?!\[).)*?)                 # Type: match until first bracket (lazy)
    \s*
    (?P<packed>(?:\[[^\]]*\]\s*)+)?         # Packed: one or more [ ... ]
  )?
  \s*
  (?P<name>[a-zA-Z_]\w*)                    # Parameter name
  \s*
  (?P<unpacked>(?:\[[^\]]*\]\s*)*)?         # Unpacked: zero or more [ ... ]
  \s*
  (?:=\s*(?P<value>.*?))?                   # Optional value (lazy)
  \s*
  (?P<terminator>[,;])                      # Terminator
""", re.VERBOSE)



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

def autoformat_module_ports(content, indent=2):
  lines = content.split('\n')
  for idx, line in enumerate(lines):
    line_strip = line.strip()
    if line_strip and line_strip.startswith('/'):
      lines[idx] = line_strip
      continue
    line_split = line_strip.split('//', 1)
    line_func = line_split[0]
    line_comm = ('§ // ' + line_split[1].strip()) if len(line_split) == 2 else ""
    line_func = regex_portDefinition_noArray_noComma.sub(
      r"\g<dir> § \g<type> § \g<packed> §§ \g<name>",
      line_func
    )
    lines[idx] = line_func + line_comm
  return do_indent(align('\n'.join(lines)), indent, True).strip('\n')
extra_filters['autoformat_module_ports'] = autoformat_module_ports

def autoformat_instance_ports(content, indent=2):
  lines = content.split('\n')
  for idx, line in enumerate(lines):
    line_strip = line.strip()
    if line_strip and line_strip.startswith('/'):
      lines[idx] = line_strip
      continue
    line_split = line_strip.split('//', 1)
    line_func = line_split[0]
    line_comm = ('§ // ' + line_split[1].strip()) if len(line_split) == 2 else ""
    line_func = line_func.replace('(', '§(§', 1).replace(')', ' §)', 1)
    lines[idx] = line_func + line_comm
  return do_indent(align('\n'.join(lines)), indent, True).strip('\n')
extra_filters['autoformat_instance_ports'] = autoformat_instance_ports

def autoformat_signal_definitions(content, indent=0):
  lines = content.split('\n')
  for idx, line in enumerate(lines):
    line_strip = line.strip()
    if line_strip and line_strip.startswith('/'):
      lines[idx] = line_strip
      continue
    line_split = line_strip.split('//', 1)
    line_func = line_split[0]
    line_comm = ('§ // ' + line_split[1].strip()) if len(line_split) == 2 else ""
    line_func = regex_wireDefinition_noArray_noComma.sub(
      r"\g<type> § \g<packed> §§ \g<name>",
      line_func
    )
    lines[idx] = line_func + line_comm
  return do_indent(align('\n'.join(lines)), indent, True).strip('\n')
extra_filters['autoformat_signal_definitions'] = autoformat_signal_definitions

def autoformat_assign_statements(content, indent=0):
  lines = content.split('\n')
  for idx, line in enumerate(lines):
    line_strip = line.strip()
    if line_strip and line_strip.startswith('/'):
      lines[idx] = line_strip
      continue
    line_split = line_strip.split('//', 1)
    line_func = line_split[0]
    line_comm = ('§ // ' + line_split[1].strip()) if len(line_split) == 2 else ""
    line_func = regex_assignStatement.sub(
      r"assign \g<lhs> § = § \g<rhs>;",
      line_func
    )
    lines[idx] = line_func + line_comm
  return do_indent(align('\n'.join(lines)), indent, True).strip('\n')
extra_filters['autoformat_assign_statements'] = autoformat_assign_statements

def autoformat_parameter_list(content, indent=0):
  lines = content.split('\n')
  for idx, line in enumerate(lines):
    line_strip = line.strip()
    if line_strip and line_strip.startswith('/'):
      lines[idx] = line_strip
      continue
    line_split = line_strip.split('//', 1)
    line_func = line_split[0]
    line_comm = ('§ // ' + line_split[1].strip()) if len(line_split) == 2 else ""
    line_func = regex_parameterDefinition.sub(
      r"\g<keyword> § \g<type> § \g<packed> §§ \g<name>\g<unpacked> § = § \g<value>\g<terminator>",
      line_func
    )
    lines[idx] = line_func + line_comm
  return do_indent(align('\n'.join(lines)), indent, True).strip('\n')
extra_filters['autoformat_parameter_list'] = autoformat_parameter_list



# ┌───────────────┐
# │ Block filters │
# └───────────────┘

# Filter out duplicated ports from module port definition list
def remove_duplicate_module_ports(content, reverse=False):
  lines = content.split('\n')
  if reverse:
    lines = lines[::-1]
  filtered_lines = []
  ports_seen = set()
  for line in lines:
    line_strip = line.strip()
    # If line is not blank and not commented
    if line_strip and not line_strip.startswith('/'):
      # Uses regex_portDefinition_noArray_noComma from previous context
      line_match = regex_portDefinition_noArray_noComma.match(line)
      if line_match:
        port_name = line_match.group('name')
        if port_name in ports_seen:
          continue
        else:
          ports_seen.add(port_name)
    filtered_lines.append(line)
  if reverse:
    filtered_lines = filtered_lines[::-1]
  return '\n'.join(filtered_lines)
extra_filters['remove_duplicate_module_ports'] = remove_duplicate_module_ports

# Filter out duplicated ports from instance port connection list
def remove_duplicate_instance_ports(content, reverse=False):
  lines = content.split('\n')
  if reverse:
    lines = lines[::-1]
  filtered_lines = []
  ports_seen = set()
  for line in lines:
    line_strip = line.strip()
    # If line is not blank and not commented
    if line_strip and not line_strip.startswith('/'):
      line_match = regex_portConnection.match(line)
      if line_match:
        port_name = line_match.group('port_name')
        if port_name in ports_seen:
          continue
        else:
          ports_seen.add(port_name)
    filtered_lines.append(line)
  if reverse:
    filtered_lines = filtered_lines[::-1]
  return '\n'.join(filtered_lines)
extra_filters['remove_duplicate_instance_ports'] = remove_duplicate_instance_ports

# Filter out listed ports from module port definition list
def exclude_list_module_ports(content, excludeList=[]):
  lines = content.split('\n')
  filtered_lines = []
  for line in lines:
    line_strip = line.strip()
    # If line is not blank and not commented
    if line_strip and not line_strip.startswith('/'):
      line_match = regex_portDefinition_noArray_noComma.match(line)
      if line_match:
        port_name = line_match.group('name')
        if port_name in excludeList:
          continue
    filtered_lines.append(line)
  return '\n'.join(filtered_lines)
extra_filters['exclude_list_module_ports'] = exclude_list_module_ports

# Filter out listed ports from instance port connection list
def exclude_list_instance_ports(content, excludeList=[]):
  lines = content.split('\n')
  filtered_lines = []
  for line in lines:
    line_strip = line.strip()
    # If line is not blank and not commented
    if line_strip and not line_strip.startswith('/'):
      line_match = regex_portConnection.match(line)
      if line_match:
        port_name = line_match.group('port_name')
        if port_name in excludeList:
          continue
    filtered_lines.append(line)
  return '\n'.join(filtered_lines)
extra_filters['exclude_list_instance_ports'] = exclude_list_instance_ports



# ┌───────────────────┐
# │ Signals and buses │
# └───────────────────┘

# Format a signal name
def format_signal(signal_name, signal_prefix="", signal_suffix="", signal_case=None):
  match signal_case:
    case "lower":      signal_case = signal_case.lower()
    case "upper":      signal_case = signal_case.upper()
    case "title":      signal_case = signal_case.title()
    case "capitalize": signal_case = signal_case.capitalize()
    case "casefold":   signal_case = signal_case.casefold()
    case "swapcase":   signal_case = signal_case.swapcase()
    case "camel":      signal_case = camel  (signal_case)
    case "pascal":     signal_case = pascal (signal_case)
    case "snake":      signal_case = snake  (signal_case)
    case "kebab":      signal_case = kebab  (signal_case)
  signal_name = signal_prefix + signal_name + signal_suffix
  return signal_name
extra_filters['format_signal'] = format_signal
