# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for Managing Lines in a file.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, b-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-mu
#+end_org """
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of Blee ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Libre-Halaal Foundation. Subject to AGPL.
** It is not part of Emacs. It is part of Blee.
** Best read and edited  with Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: NOTYET
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['ro'], }
csInfo['version'] = '202209130210'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'ro-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos-pip/bisos.cs/_nodeBase_/fullUsagePanel-en.org][PyFwrk bisos.b.cs Panel For RO]] ||
Module description comes here.
** Relevant Panels:
** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
#+end_org """
####+END:

####+BEGIN: b:python:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:orgItem/basic :type "=PyImports= " :title "*Py Library IMPORTS*" :comment "-- with classification based framework/imports"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS* -- with classification based framework/imports  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
** Imports Based On Classification=cs-u
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

# from bisos.currents import currentsConfig
from bisos.basics import pyRunAs
# from bisos.basics import basics

import pathlib
import re
import datetime
import os

####+BEGIN: bx:cs:py3:section :title "Public Classes"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Public Functions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:class/decl :className "Date" :superClass "object" :comment "Abstraction of a File" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /Date/  superClass=object =Abstraction of a File=  [[elisp:(org-cycle)][| ]]
#+end_org """
class Date(object):
####+END:
    """
** Abstraction of a Line in a File
"""

    def __init__(
            self,
    ):
        pass

####+BEGIN: b:py3:cs:method/typing :methodName "timeTag" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /timeTag/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def timeTag(
####+END:
    )-> str:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """

        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


####+BEGIN: b:py3:class/decl :className "File" :superClass "object" :comment "Abstraction of a File" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /File/  superClass=object =Abstraction of a File=  [[elisp:(org-cycle)][| ]]
#+end_org """
class File(object):
####+END:
    """
** Abstraction of a Line in a File
"""

    def __init__(
            self,
    ):
        pass


####+BEGIN: b:py3:cs:method/typing :methodName "readAsStr" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /readAsStr/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def readAsStr(
####+END:
            filePath: pathlib.Path,
            perhapsAsRoot: bool = False,
    )-> str:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        if perhapsAsRoot == True:
            fileContent = pyRunAs.as_root_readFromFile(filePath)
        else:
           with open(filePath, "r") as thisFile:
               fileContent = thisFile.read()
        return fileContent

####+BEGIN: b:py3:cs:method/typing :methodName "writeWithStr" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /writeWithStr/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def writeWithStr(
####+END:
            filePath: pathlib.Path,
            content: str,
            perhapsSafeKeep: bool = False,
            perhapsAsRoot: bool = False,
    )-> pathlib.Path:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        if perhapsSafeKeep == True:
            safeKeepFile = pathlib.Path(str(filePath)+Date.timeTag())
            if perhapsAsRoot == True:
                pyRunAs.as_root_renameFile(filePath, safeKeepFile)
            else:
               os.rename(filePath, safeKeepFile)

        if perhapsAsRoot == True:
            pyRunAs.as_root_writeToFile(filePath, content)
        else:
            with open(filePath, "w") as thisFile:
                thisFile.write(content + '\n')

        return filePath

####+BEGIN: b:py3:cs:method/typing :methodName "appendWithStr" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /appendWithStr/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def appendWithStr(
####+END:
            filePath: pathlib.Path,
            toBeAppended: str,
            perhapsSafeKeep: bool = False,
            perhapsAsRoot: bool = False,
    )-> pathlib.Path:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        fileContent = File.readAsStr(filePath, perhapsAsRoot=perhapsAsRoot)
        fileContent = fileContent + toBeAppended
        File.writeWithStr(filePath, fileContent, perhapsAsRoot=perhapsAsRoot, perhapsSafeKeep=perhapsSafeKeep)

        return filePath

####+BEGIN: b:py3:class/decl :className "FileLine" :superClass "object" :comment "Abstraction of Line in a File" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /FileLine/  superClass=object =Abstraction of Line in a File=  [[elisp:(org-cycle)][| ]]
#+end_org """
class FileLine(object):
####+END:
    """
** Abstraction of a Line in a File
"""

    def __init__(
            self,
    ):
        pass

####+BEGIN: b:py3:cs:method/typing :methodName "grep" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /grep/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def grep(
####+END:
            filePath: pathlib.Path,
            lineRegExp: str,
            perhapsAsRoot: bool = False,
    )-> list[str]:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        result: list[str] = []

        fileContent = File.readAsStr(filePath, perhapsAsRoot=perhapsAsRoot)
        lines = fileContent.splitlines()

        for line in lines:
            pattern  = re.compile(lineRegExp)
            if pattern.search(line):
                result.append(line)

        return result

####+BEGIN: b:py3:cs:method/typing :methodName "grepDashv" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /grepDashv/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def grepDashv(
####+END:
            filePath: pathlib.Path,
            lineRegExp: str,
            perhapsAsRoot: bool = False,
    )-> list[str]:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        result: list[str] = []

        fileContent = File.readAsStr(filePath, perhapsAsRoot=perhapsAsRoot)
        lines = fileContent.splitlines()

        for line in lines:
            pattern  = re.compile(lineRegExp)
            if not pattern.search(line):
                result.append(line)

        return result

####+BEGIN: b:py3:cs:method/typing :methodName "isIn" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /isIn/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def isIn(
####+END:
            filePath: pathlib.Path,
            lineRegExp: str,
            perhapsAsRoot: bool = False,
    )-> bool:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        gotVal = FileLine.grep(filePath, lineRegExp, perhapsAsRoot=perhapsAsRoot)
        if len(gotVal) == 0:
            return False
        else:
            return True

####+BEGIN: b:py3:cs:method/typing :methodName "replace" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /replace/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def replace(
####+END:
            filePath: pathlib.Path,
            lineRegExp: typing.Match[str],
            perhapsSafeKeep: bool = False,
            perhapsAsRoot: bool = False,
    )-> bool:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        return True

####+BEGIN: b:py3:cs:method/typing :methodName "remove" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /remove/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def remove(
####+END:
            filePath: pathlib.Path,
            lineRegExp: str,
            perhapsSafeKeep: bool = False,
            perhapsAsRoot: bool = False,
    )-> bool:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        if not FileLine.isIn(filePath, lineRegExp, perhapsAsRoot=perhapsAsRoot,):
            b_io.log.info(f"{filePath} does not contain {lineRegExp}, removal skipped")
            return False

        linesList  = FileLine.grepDashv(filePath, lineRegExp, perhapsAsRoot=perhapsAsRoot,)
        content = '\n'.join(linesList)

        File.writeWithStr(filePath, content, perhapsAsRoot=perhapsAsRoot, perhapsSafeKeep=perhapsSafeKeep)

        return True

####+BEGIN: b:py3:cs:method/typing :methodName "removeBlock" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /removeBlock/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def removeBlock(
####+END:
            filePath: pathlib.Path,
            lineRegExp: typing.Match[str],
            perhapsSafeKeep: bool = False,
            perhapsAsRoot: bool = False,
    )-> bool:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        print("NOTYET")
        return True

####+BEGIN: b:py3:cs:method/typing :methodName "replaceOrAdd" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /replaceOrAdd/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def replaceOrAdd(
####+END:
            filePath: pathlib.Path,
            lineRegExp: typing.Match[str],
            perhapsSafeKeep: bool = False,
            perhapsAsRoot: bool = False,
    )-> bool:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        return True

####+BEGIN: b:py3:cs:method/typing :methodName "appendIfNotThere" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /appendIfNotThere/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def appendIfNotThere(
####+END:
            filePath: pathlib.Path,
            toBeAppended: str,
            perhapsSafeKeep: bool = False,
            perhapsAsRoot: bool = False,
    )-> bool:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns True if line matching regExp is in filePath. Equivalent of FN_lineIsInFile
        #+end_org """

        if FileLine.isIn(filePath, toBeAppended, perhapsAsRoot=perhapsAsRoot,):
            b_io.log.info(f"{filePath} already contains {toBeAppended}, addition skipped")
            return False

        File.appendWithStr(filePath, toBeAppended, perhapsAsRoot=perhapsAsRoot, perhapsSafeKeep=perhapsSafeKeep)

        return True

####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* *[[elisp:(org-cycle)][| ~End-Of-Editable-Text~ |]]* :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
