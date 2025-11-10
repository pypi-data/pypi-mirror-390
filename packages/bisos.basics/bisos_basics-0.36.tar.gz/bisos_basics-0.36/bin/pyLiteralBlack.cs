#!/bin/env python
# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CmndSvc= processing pyLiteral. It should be renamed to pyLiteralTo.cs. It should become a bisos-pip package.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-mu"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-mu
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-mu") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-mu
#+end_org """
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of BISOS ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Neda Communications, Inc. Subject to AGPL.
** It is part of BISOS (ByStar Internet Services OS)
** Best read and edited  with Blee in Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/core/bpip/examples/pyLiteralToBash.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['pyLiteralToBash'], }
csInfo['version'] = '202402104344'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'pyLiteralToBash-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos-pip/bisos.cs/_nodeBase_/fullUsagePanel-en.org][BISOS CmndSvcs Panel]]   [[elisp:(org-cycle)][| ]]

This a =CmndSvc= for running CS examples individually or collectively.
It can also be used as a regression tester.
It works closely with the bisos.examples package.

** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO pyRoInv examples module should be merged with pyInv and cmnds module.
*** TODO Create an examples panel to which this points.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]

#+end_org """
####+END:

####+BEGIN: b:py3:file/workbench :outLevel 1
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
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-mu=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

import ast
import black

""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~csuList emacs-list Specifications~  [[elisp:(blee:org:code-block/above-run)][ /Eval Below/ ]] [[elisp:(org-cycle)][| ]]
#+BEGIN_SRC emacs-lisp
(setq  b:py:cs:csuList
  (list
   "bisos.b.cs.ro"
   ;; "bisos.csPlayer.bleep"
 ))
#+END_SRC
#+RESULTS:
| bisos.b.cs.ro |
#+end_org """

####+BEGIN: b:py3:cs:framework/csuListProc :pyImports t :csuImports t :csuParams t
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~Process CSU List~ with /1/ in csuList pyImports=t csuImports=t csuParams=t
#+end_org """

from bisos.b.cs import ro

csuList = [ 'bisos.b.cs.ro', ]

g_importedCmndsModules = cs.csuList_importedModules(csuList)

def g_extraParams():
    csParams = cs.param.CmndParamDict()
    cs.csuList_commonParamsSpecify(csuList, csParams)
    cs.argsparseBasedOnCsParams(csParams)

####+END:

####+BEGIN: b:py3:cs:main/exposedSymbols :classes ()
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~Exposed Symbols List Specification~ with /0/ in Classes List
#+end_org """
####+END:

cs.invOutcomeReportControl(cmnd=True, ro=True)

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples" :extent "verify" :ro "noCli" :comment "FrameWrk: CS-Main-Examples" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples>>  *FrameWrk: CS-Main-Examples*  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:
        """FrameWrk: CS-Main-Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        od = collections.OrderedDict
        cmnd = cs.examples.cmndEnter

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())
        cs.examples.commonBrief()
        # bleep.examples_csBasic()

        cs.examples.menuChapter('*Convert Python Literal Syntax To Equivalent In Bash*')
        cmnd('stdinToBash')

        print("""echo "{'key1': 'value 1.2AA', 'key2': 'value2' }" | pyLiteralTo.cs -i stdinToBash""")
        print("""echo "[{'key1': 'value 1.2AA', 'key2': 'value2' }]" | pyLiteralTo.cs -i stdinToBash""")
        print("""echo "[{'key1': 'value 1.2AA', 'key2': 'value2' }]" | pyLiteralBash.cs""")

        cs.examples.menuChapter('*stdinToBlack: Format Python Literal Syntax*')
        cmnd('stdinToBlack')

        print("""echo "{'key1': 'value 1.2AA', 'key2': 'value2' }" | pyLiteralTo.cs -i stdinToBlack""")
        print("""echo "[{'key1': 'value 1.2AA', 'key2': 'value2' }]" | pyLiteralTo.cs -i stdinToBlack""")
        print("""echo "[{'key1': 'value 1.2AA', 'key2': 'value2' }]" | pyLiteralBlack.cs""")

        cs.examples.menuChapter('*Bash Examples of Py Input*')
        cmnd('bashDictExample')
        cmnd('bashListDictExample')

        return(cmndOutcome)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "noCmndProcessor" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<noCmndProcessor>>  =verify= argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class noCmndProcessor(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        cmndOutcome = self.getOpOutcome()

        csMuName = cs.G.icmMyName()

        if "pyLiteralBlack.cs"  ==  csMuName:
            stdinToBlack().pyWCmnd(cmndOutcome,)
            print(cmndOutcome.results)
        elif "pyLiteralBash.cs"  ==  csMuName:
            stdinToBash().pyWCmnd(cmndOutcome,)
            print(cmndOutcome.results)
        else:
            examples().pyWCmnd(cmndOutcome,)

        return(cmndOutcome)


####+BEGIN: b:py3:cs:orgItem/section :title "Conversion Functions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Conversion Functions*   [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "bashProcList" :funcType "extTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /bashProcList/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def bashProcList(
####+END:
        pyList: list,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Convert a python list to a bash list.
    #+end_org """

    result = "( "
    for each in pyList:
        if isCompoundDataType(each) == True:
            # print(f"AA{each}BB")
            eachProced = pyProcStr(f"{each}\n")
            result += f'''"{eachProced}" '''
        else:
            result += f"{each} "
    result += " )"
    return result

####+BEGIN: b:py3:cs:func/typing :funcName "bashProcDict" :funcType "extTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /bashProcDict/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def bashProcDict(
####+END:
        pyDict: dict,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    result = "( "
    for eachKey, eachValue  in pyDict.items():
       if isCompoundDataType(eachValue) == True:
            # print(f"AA{eachValue}BB")
            eachProced = pyProcStr(f"{eachValue}\n")
            result += f"[{eachKey}]='{eachProced}' "
       else:
           result += f"[{eachKey}]='{eachValue}' "
    result += " )"
    return result

####+BEGIN: b:py3:cs:func/typing :funcName "bashProcTuple" :funcType "extTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /bashProcTuple/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def bashProcTuple(
####+END:
        pyTuple: tuple,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    result = ""
    for each in pyTuple:
        result += f"{each} "
    return result

####+BEGIN: b:py3:cs:func/typing :funcName "bashProcSet" :funcType "extTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /bashProcSet/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def bashProcSet(
####+END:
        pySet: set,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    result = ""
    for each in pySet:
        result += f"{each} "
    return result

####+BEGIN: b:py3:cs:func/typing :funcName "bashProcBool" :funcType "extTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /bashProcBool/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def bashProcBool(
####+END:
        pyBool: bool,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    return f"{pyBool}"

####+BEGIN: b:py3:cs:func/typing :funcName "bashProcInt" :funcType "extTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /bashProcInt/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def bashProcInt(
####+END:
        pyInt: int,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    return f"(({pyInt}))"

####+BEGIN: b:py3:cs:func/typing :funcName "bashProcStr" :funcType "extTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /bashProcStr/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def bashProcStr(
####+END:
        pyStr: str,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    return f"{pyStr}"

####+BEGIN: b:py3:cs:func/typing :funcName "pyProcStr" :funcType "extTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /pyProcStr/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def pyProcStr(
####+END:
        pyStr: str,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    #print(f"CC{pyStr}DD")
    pyInput = ast.literal_eval(pyStr)

    if isinstance(pyInput, list):
        result = bashProcList(pyInput)
    elif isinstance(pyInput, dict):
        result = bashProcDict(pyInput)
    elif isinstance(pyInput, tuple):
        result = bashProcTuple(pyInput)
    elif isinstance(pyInput, set):
        result = bashProcSet(pyInput)

    elif isinstance(pyInput, bool):
        result = bashProcBool(pyInput)
    elif isinstance(pyInput, int):
        result = bashProcInt(pyInput)
    elif isinstance(pyInput, str):
        result = bashProcStr(pyInput)
    else:
        result = f"Unsupported type {type(pyInput)}"

    return result


####+BEGIN: b:py3:cs:func/typing :funcName "isCompoundDataType" :funcType "extTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /isCompoundDataType/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def isCompoundDataType(
####+END:
        pyInput,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    if isinstance(pyInput, list):
        result = True
    elif isinstance(pyInput, dict):
        result = True
    elif isinstance(pyInput, tuple):
        result = True
    elif isinstance(pyInput, set):
        result = True
    else:
        result = False

    return result

####+BEGIN: b:py3:cs:func/typing :funcName "isSimpleDataType" :funcType "extTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /isSimpleDataType/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def isSimpleDataType(
####+END:
        pyStr: str,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    if isinstance(pyInput, bool):
        result = True
    elif isinstance(pyInput, int):
        result = True
    elif isinstance(pyInput, str):
        result = True
    else:
        result = False

    return result




####+BEGIN: b:py3:cs:orgItem/section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*   [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "stdinToBlack" :extent "verify" :comment "stdin as input" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "methodInvokeArg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<stdinToBlack>>  *stdin as input*  =verify= ro=cli pyInv=methodInvokeArg   [[elisp:(org-cycle)][| ]]
#+end_org """
class stdinToBlack(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             methodInvokeArg: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as input"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Given a string of literals on stdin, converts it to bash syntax.

This implementation is incomplete, as it does not deal with nested collections.
        #+end_org """)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  echo "[ 'some List', 'second entry' ]" | pyLiteralTo.cs -i stdinToBlack
#+end_src
#+RESULTS:
:
: some List second entry

#+end_org """)

        if self.justCaptureP(): return cmndOutcome

        if not methodInvokeArg:
            methodInvokeArg = b_io.stdin.read()

        # print(black.format_str(repr(factValue), mode=black.Mode()))
        result = black.format_str(methodInvokeArg, mode=black.Mode())

        return cmndOutcome.set(opResults=result)



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "stdinToBash" :extent "verify" :comment "stdin as input" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "methodInvokeArg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<stdinToBash>>  *stdin as input*  =verify= ro=cli pyInv=methodInvokeArg   [[elisp:(org-cycle)][| ]]
#+end_org """
class stdinToBash(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             methodInvokeArg: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as input"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Given a string of literals on stdin, converts it to bash syntax.

This implementation is incomplete, as it does not deal with nested collections.
        #+end_org """)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  echo "[ 'some List', 'second entry' ]" | pyLiteralToBash.cs -i stdinToBash
#+end_src
#+RESULTS:
:
: some List second entry
#+begin_src sh :results output :session shared
  echo "{'key1': ['value1.1', 'value 1.2'], 'key2': 'value2' }" | pyLiteralToBash.cs -i stdinToBash
#+end_src
#+RESULTS:
:
: ( [key1]='['value1.1', 'value 1.2']' [key2]='value2'  )
#+begin_src sh :results output :session shared
  echo "{'key1': ['value1.1', 'value 1.2'], 'key2': 'value2' }" | pyLiteralToBash.cs -i stdinToBash
#+end_src
#+RESULTS:
:
: ( [key1]='['value1.1', 'value 1.2']' [key2]='value2'  )

#+begin_src sh :results output :session shared
  echo "222" | pyLiteralToBash.cs -i stdinToBash
#+end_src
#+RESULTS:
:
: Unsupported type <class 'int'>
#+begin_src sh :results output :session shared
  echo "'222'" | pyLiteralToBash.cs -i stdinToBash
#+end_src
#+RESULTS:
:
: Unsupported type <class 'str'>
#+begin_src sh :results output :session shared
  echo "True" | pyLiteralToBash.cs -i stdinToBash
#+end_src
#+RESULTS:
:
: Unsupported type <class 'bool'>
#+begin_src sh :results output :session shared
  echo "('tuple1', 'tuple2', 'tuple3')" | pyLiteralToBash.cs -i stdinToBash
#+end_src
#+RESULTS:
:
: Unsupported type <class 'tuple'>
#+begin_src sh :results output :session shared
  echo "{'set1', 'set2', 'set3'}" | pyLiteralToBash.cs -i stdinToBash
#+end_src
#+RESULTS:
:
: Unsupported type <class 'set'>

#+end_org """)

        if self.justCaptureP(): return cmndOutcome

        if not methodInvokeArg:
            methodInvokeArg = b_io.stdin.read()

        # print(f"ZZ{methodInvokeArg}YY")
        result = pyProcStr(methodInvokeArg)

        return cmndOutcome.set(opResults=result)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "bashDictExample" :extent "verify" :comment "stdin as input" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<bashDictExample>>  *stdin as input*  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class bashDictExample(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:
        """stdin as input"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Bash example of using -i stdinToBash to bring in pyDict as bash dict.
        #+end_org """)

        if not (resStr := b.subProc.WOpW(invedBy=self, log=0).bash("""
declare  -A gotPyDict=$( echo "{'key1': 'value 1.2AA', 'key2': 'value2' }" | pyLiteralToBash.cs -i stdinToBash )

echo ${gotPyDict[@]} -- ${!gotPyDict[@]} --- ${gotPyDict['key1']}

for each in "${!gotPyDict[@]}"; do
    echo "$each - ${gotPyDict[$each]}"
done
""",
        ).stdout):  return(io.eh.badOutcome(cmndOutcome))

        return cmndOutcome.set(opResults=resStr)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "bashListDictExample" :extent "verify" :comment "stdin as input" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<bashListDictExample>>  *stdin as input*  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class bashListDictExample(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:
        """stdin as input"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Bash example of using -i stdinToBash to bring in pyDict as bash dict.
        #+end_org """)

        if not (resStr := b.subProc.WOpW(invedBy=self, log=0).bash("""
pythonInput="[{'key1': 'value 1.2AA', 'key2': 'value2' }, {'key5': 'VALUE 5BB'}]"
echo "pythonInput=${pythonInput}"
        
eval declare -a listOfDicts="$( echo ${pythonInput} | pyLiteralToBash.cs -i stdinToBash )"        

echo "bashInput=( ${listOfDicts[@]} )"

echo "------"
if [ "${#listOfDicts[@]}" == "0" ] ; then
        echo "Empty List"
fi
for eachDictStr in "${listOfDicts[@]}" ; do
        echo "########"

        echo "eachDictStr=${eachDictStr}"

        declare -A eachDict="${eachDictStr}"
        
        echo ${eachDict[@]} -- ${!eachDict[@]} --- ${eachDict['key1']}

        echo "+++++++"
        
        for eachKey in "${!eachDict[@]}"; do
            echo "$eachKey - ${eachDict[$eachKey]}"
        done
        
        echo "~~~~~~~"
done
""",
        ).stdout):  return(b_io.eh.badOutcome(cmndOutcome))

        return cmndOutcome.set(opResults=resStr)



####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Main" :anchor ""  :extraInfo "Framework DBlock"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Main_: |]]  Framework DBlock  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/main :csInfo "csInfo" :noCmndEntry "noCmndProcessor" :extraParamsHook "g_extraParams" :importedCmndsModules "g_importedCmndsModules"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =g_csMain= (csInfo, _noCmndProcessor_, g_extraParams, g_importedCmndsModules)
#+end_org """

if __name__ == '__main__':
    cs.main.g_csMain(
        csInfo=csInfo,
        noCmndEntry=noCmndProcessor,  # specify a Cmnd name
        extraParamsHook=g_extraParams,
        importedCmndsModules=g_importedCmndsModules,
    )

####+END:

####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
