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
from j2gpp.filters import align, camel, pascal, snake, kebab
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

# Convert integer to Verilog hex literal
def to_hex(value, width=None):
  value = int(value)
  if width is None:
    return f"'h{value:X}"
  else:
    width = int(width)
    hex_digits = (width + 3) // 4
    return f"{width}'h{value:0{hex_digits}X}"
extra_filters['to_hex'] = to_hex

# Convert integer to Verilog binary literal
def to_bin(value, width=None):
  value = int(value)
  if width is None:
    return f"'b{value:b}"
  else:
    width = int(width)
    return f"{width}'b{value:0{width}b}"
extra_filters['to_bin'] = to_bin

# Convert integer to Verilog decimal literal
def to_dec(value, width=None):
  value = int(value)
  if width is None:
    return f"'d{value}"
  else:
    width = int(width)
    return f"{width}'d{value}"
extra_filters['to_dec'] = to_dec

# Generate a bitmask of N ones as a Verilog literal
def bitmask(width, hex=False):
  width = int(width)
  mask = (1 << width) - 1
  if hex:
    hex_digits = (width + 3) // 4
    return f"{width}'h{mask:0{hex_digits}X}"
  else:
    return f"{width}'b{'1' * width}"
extra_filters['bitmask'] = bitmask

# Generate a one-hot encoded Verilog literal
def onehot(index, width, hex=False):
  index = int(index)
  width = int(width)
  value = 1 << index
  if hex:
    hex_digits = (width + 3) // 4
    return f"{width}'h{value:0{hex_digits}X}"
  else:
    return f"{width}'b{value:0{width}b}"
extra_filters['onehot'] = onehot

# Generate one-hot decoder assign statements
def onehot_decode(signal, num_bits):
  num_bits = int(num_bits)
  num_outputs = 1 << num_bits
  lines = []
  for i in range(num_outputs):
    lines.append(f"assign decoded[{i}] § = ({signal} == {to_dec(i, num_bits)});")
  return align('\n'.join(lines))
extra_filters['onehot_decode'] = onehot_decode

# Generate priority encoder as nested ternary expression
def priority_encode(signals):
  if not signals:
    return "'0"
  if len(signals) == 1:
    name, value = next(iter(signals.items()))
    return value
  items = list(signals.items())
  expr = items[-1][1]
  for name, value in reversed(items[:-1]):
    expr = f"{name} ? {value} : ({expr})"
  return expr
extra_filters['priority_encode'] = priority_encode

# Generate bit-reversal concatenation expression
def bit_reverse(signal, width):
  width = int(width)
  bits = [f"{signal}[{i}]" for i in range(width)]
  return "{" + ", ".join(bits) + "}"
extra_filters['bit_reverse'] = bit_reverse

# Generate nibble swap concatenation expression (4-bit granularity)
def nibble_swap(signal, num_nibbles):
  num_nibbles = int(num_nibbles)
  slices = []
  for i in range(num_nibbles):
    lsb = i * 4
    msb = lsb + 3
    slices.append(f"{signal}[{msb}:{lsb}]")
  return "{" + ", ".join(slices) + "}"
extra_filters['nibble_swap'] = nibble_swap

# Generate endianness swap concatenation expression (8-bit granularity)
def byte_swap(signal, num_bytes):
  num_bytes = int(num_bytes)
  slices = []
  for i in range(num_bytes):
    lsb = i * 8
    msb = lsb + 7
    slices.append(f"{signal}[{msb}:{lsb}]")
  return "{" + ", ".join(slices) + "}"
extra_filters['byte_swap'] = byte_swap

# Generate word swap concatenation expression (16-bit granularity)
def word_swap(signal, num_words):
  num_words = int(num_words)
  slices = []
  for i in range(num_words):
    lsb = i * 16
    msb = lsb + 15
    slices.append(f"{signal}[{msb}:{lsb}]")
  return "{" + ", ".join(slices) + "}"
extra_filters['word_swap'] = word_swap

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

# Assign block to pack a list of signals into a vector signal
def pack_bus(bus_name, signals, signal_prefix="", signal_suffix="", signal_case=None):
  if len(signals) == 0: return ""
  lines = []
  all_sizes_are_numbers = all(isinstance(value, (int,float)) for value in signals.values())
  if all_sizes_are_numbers:
    idx_start = 0
    idx_end   = 0
    for signal_name, signal_size in signals.items():
      signal_name = format_signal(signal_name, signal_prefix, signal_suffix, signal_case)
      signal_size = int(signal_size)
      idx_end     = idx_start + signal_size
      if signal_size == 1:
        line = f"assign {bus_name} [§ §§ § {idx_start} §§ ] = {signal_name};"
      else:
        line = f"assign {bus_name} [§ {idx_end} §§ : §{idx_start} §§ ] = {signal_name};"
      lines.append(line)
      idx_start = idx_end
  else:
    idx_base = "0"
    for signal_name, signal_size in signals.items():
      signal_name = format_signal(signal_name, signal_prefix, signal_suffix, signal_case)
      line = f"assign {bus_name} [§ {idx_base} § +: §{signal_size} §§ ] = {signal_name};"
      lines.append(line)
      if idx_base == "0":
        idx_base = str(signal_size)
      else:
        idx_base = f"{idx_base}+{signal_size}"
  return align('\n'.join(lines))
extra_filters['pack_bus'] = pack_bus

def unpack_bus(bus_name, signals, signal_prefix="", signal_suffix="", signal_case=None):
  if len(signals) == 0: return ""
  lines = []
  all_sizes_are_numbers = all(isinstance(value, (int,float)) for value in signals.values())
  if all_sizes_are_numbers:
    idx_start = 0
    idx_end   = 0
    for signal_name, signal_size in signals.items():
      signal_name = format_signal(signal_name, signal_prefix, signal_suffix, signal_case)
      signal_size = int(signal_size)
      idx_end     = idx_start + signal_size
      if signal_size == 1:
        line = f"assign {signal_name} § = {bus_name} [§ §§ § {idx_start} §§ ];"
      else:
        line = f"assign {signal_name} § = {bus_name} [§ {idx_end} §§ : §{idx_start} §§ ];"
      lines.append(line)
      idx_start = idx_end
  else:
    idx_base = "0"
    for signal_name, signal_size in signals.items():
      signal_name = format_signal(signal_name, signal_prefix, signal_suffix, signal_case)
      line = f"assign {signal_name} § = {bus_name} [§ {idx_base} § +: §{signal_size} §§ ];"
      lines.append(line)
      if idx_base == "0":
        idx_base = str(signal_size)
      else:
        idx_base = f"{idx_base}+{signal_size}"
  return align('\n'.join(lines))
extra_filters['unpack_bus'] = unpack_bus

# Declare a list of wires
def declare_wires(signals, signal_prefix="", signal_suffix="", signal_case=None):
  if len(signals) == 0: return ""
  lines = []
  for signal_name, signal_size in signals.items():
    signal_name = format_signal(signal_name, signal_prefix, signal_suffix, signal_case)
    line = f"wire {array_width(signal_size)} {signal_name};"
    lines.append(line)
  return autoformat_signal_definitions('\n'.join(lines))
extra_filters['declare_wires'] = declare_wires

# Declare a list of registers
def declare_registers(signals, signal_prefix="", signal_suffix="", signal_case=None):
  if len(signals) == 0: return ""
  lines = []
  for signal_name, signal_size in signals.items():
    signal_name = format_signal(signal_name, signal_prefix, signal_suffix, signal_case)
    line = f"reg {array_width(signal_size)} {signal_name};"
    lines.append(line)
  return autoformat_signal_definitions('\n'.join(lines))
extra_filters['declare_registers'] = declare_registers

# Declare a list of logic signals/registers
def declare_logic(signals, signal_prefix="", signal_suffix="", signal_case=None):
  if len(signals) == 0: return ""
  lines = []
  for signal_name, signal_size in signals.items():
    signal_name = format_signal(signal_name, signal_prefix, signal_suffix, signal_case)
    line = f"logic {array_width(signal_size)} {signal_name};"
    lines.append(line)
  return autoformat_signal_definitions('\n'.join(lines))
extra_filters['declare_logic'] = declare_logic

# Declare a list of parameters
def declare_parameters(params):
  if len(params) == 0: return ""
  lines = []
  for param_name, param_value in params.items():
    line = f"parameter {param_name} § = § {param_value};"
    lines.append(line)
  return align('\n'.join(lines))
extra_filters['declare_parameters'] = declare_parameters

# Declare a list of localparams
def declare_localparams(params):
  if len(params) == 0: return ""
  lines = []
  for param_name, param_value in params.items():
    line = f"localparam {param_name} § = § {param_value};"
    lines.append(line)
  return align('\n'.join(lines))
extra_filters['declare_localparams'] = declare_localparams

# Generate a module instantiation
def instantiate(module_name, ports, instance_name=None, params=None, indent=2):
  if instance_name is None:
    instance_name = f"i_{module_name}"
  lines = []
  ind = " " * indent
  if params:
    lines.append(f"{module_name} #(")
    param_lines = []
    for pname, pvalue in params.items():
      param_lines.append(f"{ind}.{pname} ({pvalue})")
    for i, pline in enumerate(param_lines):
      comma = "," if i < len(param_lines) - 1 else ""
      lines.append(pline + comma)
    lines.append(f") {instance_name} (")
  else:
    lines.append(f"{module_name} {instance_name} (")
  port_lines = []
  for pname, connection in ports.items():
    port_lines.append(f"{ind}.{pname} ({connection})")
  for i, pline in enumerate(port_lines):
    comma = "," if i < len(port_lines) - 1 else ""
    lines.append(pline + comma)
  lines.append(");")
  return autoformat_instance_ports('\n'.join(lines), indent)
extra_filters['instantiate'] = instantiate


