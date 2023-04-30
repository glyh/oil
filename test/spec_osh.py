#!/usr/bin/env python2
"""
spec_osh.py
"""
from __future__ import print_function

def Define(sp):
  # Isolate it in its own test suite because of job control issue
  sp.OshFile('interactive', tags=['interactive', 'dev-minimal'])

  # Also uses $SH -i quite a bit
  sp.OshFile('sh-options', tags=['interactive'])
  sp.OshFile('sh-usage', tags=['interactive'])

  # one cases uses -i
  sp.OshFile('var-num', tags=['interactive'])

  sp.OshFile('builtin-history', tags=['interactive'])

  sp.OshFile('smoke', tags=['dev-minimal'])

  #
  # suite osh
  #

  sp.OshFile('alias')

  sp.OshFile('append')

  sp.OshFile('arith')

  sp.OshFile('arith-context')

  sp.OshFile('array')

  sp.OshFile('array-compat')

  sp.OshFile('assign')

  sp.OshFile('assign-deferred')

  sp.OshFile('assign-dialects')

  sp.OshFile('assign-extended')

  sp.OshFile('assoc')

  sp.OshFile('assoc-zsh')

  sp.OshFile('background')

  sp.OshFile('ble-features')

  sp.OshFile('ble-idioms')

  sp.OshFile('blog1')

  sp.OshFile('blog2')

  sp.OshFile('brace-expansion')

  sp.OshFile('bugs')

  sp.OshFile('builtin-bash')

  sp.OshFile('builtin-bracket')

  sp.OshFile('builtin-completion')

  sp.OshFile('builtin-dirs')

  sp.OshFile('builtin-eval-source')

  sp.OshFile('builtin-getopts')

  sp.OshFile('builtin-io')

  sp.OshFile('builtin-printf')

  sp.OshFile('builtins')

  sp.OshFile('builtins2')

  sp.OshFile('builtin-special')

  sp.OshFile('builtin-times')

  sp.OshFile('builtin-trap')

  sp.OshFile('builtin-trap-bash')

  sp.OshFile('builtin-vars')

  sp.OshFile('case_')

  sp.OshFile('command_')

  sp.OshFile('command-parsing')

  sp.OshFile('command-sub')

  sp.OshFile('comments')

  sp.OshFile('dbracket')

  sp.OshFile('dparen')

  sp.OshFile('empty-bodies')

  sp.OshFile('errexit')

  sp.OshFile('errexit-oil')

  sp.OshFile('exit-status')

  sp.OshFile('explore-parsing')

  sp.OshFile('extglob-files')

  sp.OshFile('extglob-match')

  sp.OshFile('fatal-errors')

  sp.OshFile('for-expr')

  sp.OshFile('func-parsing')

  sp.OshFile('glob')

  sp.OshFile('here-doc')

  sp.OshFile('if_')

  sp.OshFile('introspect')

  sp.OshFile('let')

  sp.OshFile('loop')

  sp.OshFile('nameref')

  sp.OshFile('nix-idioms')

  sp.OshFile('nocasematch-match')

  sp.OshFile('nul-bytes')

  sp.OshFile('osh-only')

  sp.OshFile('parse-errors')

  sp.OshFile('pipeline')

  sp.OshFile('posix')

  sp.OshFile('process-sub')

  sp.OshFile('prompt')

  sp.OshFile('quote')

  sp.OshFile('redirect')

  sp.OshFile('regex')

  sp.OshFile('serialize')

  sp.OshFile('sh-func')

  sp.OshFile('strict-options')

  sp.OshFile('subshell')

  sp.OshFile('tilde')

  sp.OshFile('TODO-deprecate')

  sp.OshFile('toysh')

  sp.OshFile('toysh-posix')

  sp.OshFile('type-compat')

  sp.OshFile('var-op-bash')

  sp.OshFile('var-op-len')

  sp.OshFile('var-op-patsub')

  sp.OshFile('var-op-slice')

  sp.OshFile('var-op-strip')

  sp.OshFile('var-op-test')

  sp.OshFile('var-ref')

  sp.OshFile('vars-bash')

  sp.OshFile('vars-special')

  sp.OshFile('var-sub')

  sp.OshFile('var-sub-quote')

  sp.OshFile('word-eval')

  sp.OshFile('word-split')

  sp.OshFile('xtrace')
