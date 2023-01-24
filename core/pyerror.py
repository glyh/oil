"""
pyerror.py -- Wrappers for raising exceptions.

Like pyutil.py, this code is only needed in Python.  In C++ they have different
implementations.  This file has fewer deps than pyutil.py.
"""
from __future__ import print_function

import sys

try:
  from core import error
except ImportError:
  # HACK because many files 'from core.pyerror import log', but this module
  # depends on _devbuild.gen.syntax_asdl, which may not be ready
  error = None

from typing import NoReturn, Any, TYPE_CHECKING

if TYPE_CHECKING:
  from _devbuild.gen.syntax_asdl import loc_t


def log(msg, *args):
  # type: (str, *Any) -> None
  if args:
    msg = msg % args
  print(msg, file=sys.stderr)


def e_usage(msg, *pos_args, **kwargs):
  # type: (str, *Any, **Any) -> NoReturn
  """Convenience wrapper for arg parsing / validation errors.

  Usually causes a builtin to fail with status 2, but the script can continue
  if 'set +o errexit'.  Main programs like bin/oil also use this.

  Caught by

  - RunAssignBuiltin and RunBuiltin, with optional LOCATION INFO
  - various main() programs, without location info

  Probably should separate these two cases?

  - builtins pass Token() or loc::Missing()
  - tool interfaces don't pass any location info
  """
  raise error.Usage(msg, *pos_args, **kwargs)


def e_strict(msg, location):
  # type: (str, loc_t) -> NoReturn
  """Convenience wrapper for strictness errors.

  Like e_die(), except the script MAY continue executing after these errors.

  TODO: This could have a level too?
  """
  raise error.Strict(msg, location)


def p_die(msg, *args, **kwargs):
  # type: (str, *Any, **Any) -> NoReturn
  """Convenience wrapper for parse errors.

  Exits with status 2.  See core/main_loop.py.
  """
  raise error.Parse(msg, *args, **kwargs)


def e_die(msg, *args, **kwargs):
  # type: (str, *Any, **Any) -> NoReturn
  """Convenience wrapper for fatal runtime errors.

  Usually exits with status 1.  See osh/cmd_eval.py.
  """
  assert 'status' not in kwargs, 'Use e_die_status'
  raise error.FatalRuntime(msg, *args, **kwargs)


def e_die_status(status, msg, **kwargs):
  # type: (int, str, **Any) -> NoReturn
  """Wrapper for C++ semantics
  
  To avoid confusing e_die(int span_id) and e_die(int status)!

  Note that it doesn't take positional args, so you should use % formatting.
  """
  kwargs['status'] = status
  raise error.FatalRuntime(msg, **kwargs)
