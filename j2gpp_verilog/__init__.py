# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ Project:     j2gpp-verilog                                                ║
# ║ Author:      Louis Duret-Robert - louisduret@gmail.com                    ║
# ║ Website:     louis-dr.github.io                                           ║
# ║ License:     MIT License                                                  ║
# ║ File:        __init__.py                                                  ║
# ╟───────────────────────────────────────────────────────────────────────────╢
# ║ Description: J2GPP extension for Verilog and SystemVerilog.               ║
# ║                                                                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝



from importlib.metadata import version

from j2gpp_verilog.filters import extra_filters
from j2gpp_verilog.tests   import extra_tests
from j2gpp_verilog.globals import extra_globals



# ┌───────────────────────┐
# │ Extension Entry Point │
# └───────────────────────┘

try:
  extension_version = version('j2gpp')
except Exception:
  extension_version = "error"

j2gpp_extension = {
  "name": "example",
  "version": extension_version,
  "dependencies": [],
  "filters": extra_filters,
  "tests":   extra_tests,
  "globals": extra_globals,
}
