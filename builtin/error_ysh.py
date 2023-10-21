from __future__ import print_function

from _devbuild.gen.runtime_asdl import cmd_value, CommandStatus
from _devbuild.gen.syntax_asdl import loc
from core import error
from core.error import e_die, e_die_status, e_usage
from core import state
from core import vm
from frontend import flag_spec
from frontend import typed_args
#from mycpp.mylib import log

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core import ui
    from osh import cmd_eval


class Try(vm._Builtin):
    """Allows explicit handling of errors.

    Takes command argv, or a block:

    try ls /bad

    try {
      var x = 1 / 0

      ls | wc -l

      diff <(sort left.txt) <(sort right.txt)
    }

    TODO:
    - Set _error_str (e.UserErrorString())
    - Set _error_location
    - These could be used by a 'raise' builtin?  Or 'reraise'

    try foo
    if (_status != 0) {
      echo 'hello'
      raise  # reads _status, _error_str, and _error_location ?
    }
    """

    def __init__(
            self,
            mutable_opts,  # type: state.MutableOpts
            mem,  # type: state.Mem
            cmd_ev,  # type: cmd_eval.CommandEvaluator
            shell_ex,  # type: vm._Executor
            errfmt,  # type: ui.ErrorFormatter
    ):
        # type: (...) -> None
        self.mutable_opts = mutable_opts
        self.mem = mem
        self.shell_ex = shell_ex
        self.cmd_ev = cmd_ev
        self.errfmt = errfmt

    def Run(self, cmd_val):
        # type: (cmd_value.Argv) -> int
        _, arg_r = flag_spec.ParseCmdVal('try_',
                                         cmd_val,
                                         accept_typed_args=True)

        cmd = typed_args.OptionalCommand(cmd_val)
        if cmd:
            status = 0  # success by default
            try:
                with state.ctx_Try(self.mutable_opts):
                    unused = self.cmd_ev.EvalCommand(cmd)
            except error.Expr as e:
                status = e.ExitStatus()
            except error.ErrExit as e:
                status = e.ExitStatus()
            except error.UserError as e:
                status = e.ExitStatus()

            self.mem.SetTryStatus(status)
            return 0

        if arg_r.Peek() is None:
            e_usage('expects a block or command argv', loc.Missing)

        argv, locs = arg_r.Rest2()
        cmd_val2 = cmd_value.Argv(argv, locs, cmd_val.typed_args,
                                  cmd_val.pos_args, cmd_val.named_args)

        try:
            # Temporarily turn ON errexit, but don't pass a SPID because we're
            # ENABLING and not disabling.  Note that 'if try myproc' disables it and
            # then enables it!
            with state.ctx_Try(self.mutable_opts):
                # Pass do_fork=True.  Slight annoyance: the real value is a field of
                # command.Simple().  See _NoForkLast() in CommandEvaluator We have an
                # extra fork (miss out on an optimization) of code like ( status ls )
                # or forkwait { status ls }, but that is NOT idiomatic code.  status is
                # for functions.
                cmd_st = CommandStatus.CreateNull(
                    alloc_lists=True)  # TODO: take param
                status = self.shell_ex.RunSimpleCommand(cmd_val2, cmd_st, True)
                #log('st %d', status)
        except error.Expr as e:
            status = e.ExitStatus()
        except error.ErrExit as e:
            status = e.ExitStatus()

        # special variable
        self.mem.SetTryStatus(status)
        return 0


class Error(vm._Builtin):

    def __init__(self):
        # type: () -> None
        pass

    def Run(self, cmd_val):
        # type: (cmd_value.Argv) -> int
        rd = typed_args.ReaderForProc(cmd_val)
        message = rd.PosStr()
        status = rd.NamedInt('status', 1)
        rd.Done()

        if status == 0:
            e_die('Status must be a non-zero integer', cmd_val.arg_locs[0])

        if len(cmd_val.argv) > 1:
            raise error.TypeErrVerbose(
                'Expected 0 untyped arguments, but got %d' %
                (len(cmd_val.argv) - 1), loc.Missing)

        raise error.UserError(status, message, cmd_val.arg_locs[0])


class BoolStatus(vm._Builtin):

    def __init__(self, shell_ex, errfmt):
        # type: (vm._Executor, ui.ErrorFormatter) -> None
        self.shell_ex = shell_ex
        self.errfmt = errfmt

    def Run(self, cmd_val):
        # type: (cmd_value.Argv) -> int

        _, arg_r = flag_spec.ParseCmdVal('boolstatus', cmd_val)

        if arg_r.Peek() is None:
            e_usage('expected a command to run', loc.Missing)

        argv, locs = arg_r.Rest2()
        cmd_val2 = cmd_value.Argv(argv, locs, cmd_val.typed_args,
                                  cmd_val.pos_args, cmd_val.named_args)

        cmd_st = CommandStatus.CreateNull(alloc_lists=True)
        status = self.shell_ex.RunSimpleCommand(cmd_val2, cmd_st, True)

        if status not in (0, 1):
            e_die_status(status,
                         'boolstatus expected status 0 or 1, got %d' % status,
                         locs[0])

        return status