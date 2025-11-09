# -*- coding: utf-8 -*-
"""\
* *[Summary]* :: A /library/ for additions to pathlib library.
"""

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-u
#+end_org """
####+END:


####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

from pathlib import Path
from typing import Union

import logging
logger = logging.getLogger(__name__)

def symlink_update( target_path: str | Path, symlink_path: str | Path,) -> None:
    """
    Update a symlink to point to a new target. If the symlink exists, it will be replaced.

    Raises:
        FileNotFoundError: If the target_path does not exist.
        ValueError: If symlink_path and target_path are the same.
    """
    symlink = Path(symlink_path)
    target = Path(target_path)

    if not target.exists():
        raise FileNotFoundError(f"Target path does not exist: {target}")

    # if symlink.resolve() == target.resolve():
        # raise ValueError("Symlink path and target path must not be the same.")

    # Remove existing symlink or file
    if symlink.is_symlink():
        symlink.unlink()

    if symlink.exists():
        logger.warning(f"{symlink} exists and is not a symlink. Not Updated")
        raise FileExistsError(f"{symlink} exists but is not a symlink. Manual intervention required.")
    else:
        # Create new symlink
        symlink.symlink_to(target)
        logger.info(f"Updated symlink: {symlink} -> {target}")


def whichOrDefaultBinPath (
        progName: str,
        defaultPath: Path,
) -> Path | None:
    """ Ignore the one here and locate *progName*. If none found return  *defaultPath*.
Sometimes we may be running this script in the cwd -- shutil.which  does not do the equivalent of -a
    """

    result: Path | None = None

    cmndOutcome = b.subProc.WOpW(invedBy=None, log=0).bash(
        f"""set -o pipefail; which -a {progName} | grep -v '\./{progName}' | head -1""",
    )
    if cmndOutcome.isProblematic():
        if defaultPath.exists():
            result = defaultPath
        else:
            result = None
    else:
         result = Path(cmndOutcome.stdout.strip())

    return result


def whichBinPath (
        progName: str,
) -> Path | None:
    """ Ignore the one here and locate *progName*.
Sometimes we may be running this script in the cwd -- shutil.which  does not do the equivalent of -a
    """

    result: Path | None = None

    cmndOutcome = b.subProc.WOpW(invedBy=None, log=0).bash(
        f"""set -o pipefail; which -a {progName} | grep -v '\./{progName}' | head -1""",
    )
    if cmndOutcome.isProblematic():
        result = None
    else:
         result = Path(cmndOutcome.stdout.strip())

    return result
