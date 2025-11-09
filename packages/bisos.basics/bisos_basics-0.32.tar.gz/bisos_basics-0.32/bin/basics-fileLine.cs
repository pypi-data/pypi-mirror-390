#!/bin/env python
# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CmndSvc= CS for verification, regression testing and as examples of fileLineLib.
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
** This File: /bisos/git/bxRepos/bisos-pip/facter/py3/bin/facter-active.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['facter-active'], }
csInfo['version'] = '202409222627'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'facter-active-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos-pip/bisos.cs/_nodeBase_/fullUsagePanel-en.org][BISOS CmndSvcs Panel]]   [[elisp:(org-cycle)][| ]]

This a =CmndSvc= for running the equivalent of facter in py and remotely with rpyc.
With BISOS, it is used in CMDB remotely.

** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO Convert all ICMs to CSs
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

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-mu=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

from bisos.basics import basics

import pathlib

""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~csuList emacs-list Specifications~  [[elisp:(blee:org:code-block/above-run)][ /Eval Below/ ]] [[elisp:(org-cycle)][| ]]
#+BEGIN_SRC emacs-lisp
(setq  b:py:cs:csuList
  (list
   "bisos.b.cs.ro"
   ;; "bisos.csPlayer.bleep"
   "bisos.basics.basicsCmndParams"
 ))
#+END_SRC
#+RESULTS:
| bisos.b.cs.ro | bisos.basics.basicsCmndParams |
#+end_org """

####+BEGIN: b:py3:cs:framework/csuListProc :pyImports t :csuImports t :csuParams t :csmuParams nil
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~Process CSU List~ with /2/ in csuList pyImports=t csuImports=t csuParams=t
#+end_org """

from bisos.b.cs import ro
from bisos.basics import basicsCmndParams

csuList = [ 'bisos.b.cs.ro', 'bisos.basics.basicsCmndParams', ]

g_importedCmndsModules = cs.csuList_importedModules(csuList)

def g_extraParams():
    csParams = cs.param.CmndParamDict()
    cs.csuList_commonParamsSpecify(csuList, csParams)
    cs.argsparseBasedOnCsParams(csParams)

####+END:

####+BEGIN: b:py3:cs:main/exposedSymbols :classes ()
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~CS Controls and Exposed Symbols List Specification~ with /0/ in Classes List
#+end_org """
####+END:

cs.invOutcomeReportControl(cmnd=True, ro=True)

userExFile = "/tmp/fontMime.user"
rootExFile = "/tmp/fontMime.root"

lineRegExp = "font/ttf"
lineToAppend = "'New Line To Be Appended'"


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
        self.cmndDocStr(f""" #+begin_org
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Conventional top level example.
        #+end_org """)

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())
        cs.examples.commonBrief()

        od = collections.OrderedDict
        cmnd = cs.examples.cmndEnter
        literal = cs.examples.execInsert

        runAsRootParam = od([('runAsRoot', 'True'),])
        safeKeepParam = od([('safeKeep', 'True'),])
        runAsRootAndSafeKeepParams = od([('runAsRoot', 'True'),('safeKeep', 'True'),])

        cs.examples.menuChapter('=Prep For Validation=')

        cmnd('prepForValidation', args="", pars=od(), comment=f" # ")

        cs.examples.menuChapter('=FileLine Python Library Commands -- User or Root Passive=')

        cmnd('fileLine', args=f"grep {userExFile} {lineRegExp}", pars=od(), comment=f" # basics.FileLine.grep(filePath, lineRegExp)")
        cmnd('fileLine', args=f"grep {rootExFile} {lineRegExp}", pars=od(), comment=f" # Will Fail {rootExFile} is not readbale")
        cmnd('fileLine', args=f"grep {rootExFile} {lineRegExp}", pars=runAsRootParam, comment=f" # Will Fail {rootExFile} is not readbale")
        cmnd('fileLine', args=f"grepDashv {userExFile} {lineRegExp}", pars=od(), comment=f" # basics.FileLine.grepDashv(filePath, lineRegExp)")
        cmnd('fileLine', args=f"isIn {userExFile} {lineRegExp}", pars=od(), comment=f" # basics.FileLine.isIn(filePath, lineRegExp)")

        cs.examples.menuChapter('=FileLine Python Library Commands=')

        cs.examples.menuSection('=FileLine append Commands=')

        cmnd('fileLine', args=f"append {userExFile} {lineToAppend}", pars=safeKeepParam, comment=f" # basics.FileLine.grep(filePath, lineRegExp)")
        cmnd('fileLine', args=f"append {rootExFile} {lineToAppend}", pars=runAsRootParam, comment=f" # basics.FileLine.grep(filePath, lineRegExp)")
        cmnd('fileLine', args=f"append {rootExFile} {lineToAppend}", pars=runAsRootAndSafeKeepParams, comment=f" # basics.FileLine.grep(filePath, lineRegExp)")

        cs.examples.menuSection('=FileLine remove Commands=')

        cmnd('fileLine', args=f"remove {userExFile} {lineRegExp}", pars=safeKeepParam, comment=f" # basics.FileLine.grep(filePath, lineRegExp)")
        cmnd('fileLine', args=f"remove {rootExFile} {lineRegExp}", pars=runAsRootParam, comment=f" # basics.FileLine.grep(filePath, lineRegExp)")
        cmnd('fileLine', args=f"remove {rootExFile} {lineRegExp}", pars=runAsRootAndSafeKeepParams, comment=f" # basics.FileLine.grep(filePath, lineRegExp)")

        cs.examples.menuChapter('=Verify / Validate=')

        literal(f"ls -l {userExFile}* {rootExFile}*")

        return(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "prepForValidation" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<prepForValidation>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class prepForValidation(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  facter.cs -i factName networking.primary os.distro.id
#+end_src
#+RESULTS:
: [{'networking.primary': 'eno1'}, {'os.distro.id': 'Debian'}]
        #+end_org """)

        if b.subProc.WOpW(invedBy=self, log=1).bash(
                f"""\
rm {userExFile}
sudo rm {rootExFile}
egrep ^font /etc/mime.types > {userExFile}
egrep ^font  /etc/mime.types > {rootExFile}
sudo chown root:root  {rootExFile}
sudo chmod 600 {rootExFile}
sudo ls -l {userExFile} {rootExFile}
""",
        ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fileLine" :comment "" :noMapping "t" :extent "verify" :ro "cli" :parsMand "" :parsOpt "runAsRoot safeKeep" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fileLine>>  =verify= parsOpt=runAsRoot safeKeep argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fileLine(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'runAsRoot', 'safeKeep', ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             runAsRoot: typing.Optional[str]=None,  # Cs Optional Param
             safeKeep: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'runAsRoot': runAsRoot, 'safeKeep': safeKeep, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  facter.cs -i factName networking.primary os.distro.id
#+end_src
#+RESULTS:
: [{'networking.primary': 'eno1'}, {'os.distro.id': 'Debian'}]
        #+end_org """)

        cmndArg = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        restArgs = self.cmndArgsGet("1&9999", cmndArgsSpecDict, argsList)

        result: typing.Any = None
        perhapsAsRoot = False
        perhapsSafeKeep = False

        if runAsRoot == 'True':
            perhapsAsRoot = True

        if safeKeep == 'True':
            perhapsSafeKeep = True

        if cmndArg == 'grep':
            filePath = pathlib.Path(restArgs[0])
            lineRegExp = restArgs[1]
            result = basics.FileLine.grep(filePath, lineRegExp, perhapsAsRoot=perhapsAsRoot,)
        elif cmndArg == 'grepDashv':
            filePath = pathlib.Path(restArgs[0])
            lineRegExp = restArgs[1]
            result = basics.FileLine.grepDashv(filePath, lineRegExp, perhapsAsRoot=perhapsAsRoot,)
        elif cmndArg == 'isIn':
            filePath = pathlib.Path(restArgs[0])
            lineRegExp = restArgs[1]
            result = basics.FileLine.isIn(filePath, lineRegExp, perhapsAsRoot=perhapsAsRoot,)
        elif cmndArg == 'append':
            filePath = pathlib.Path(restArgs[0])
            lineToAppend = restArgs[1]
            result = basics.FileLine.appendIfNotThere(filePath, lineToAppend, perhapsAsRoot=perhapsAsRoot, perhapsSafeKeep=perhapsSafeKeep,)
        elif cmndArg == 'remove':
            filePath = pathlib.Path(restArgs[0])
            lineRegExp = restArgs[1]
            result = basics.FileLine.remove(filePath, lineRegExp, perhapsAsRoot=perhapsAsRoot, perhapsSafeKeep=perhapsSafeKeep,)
        else:
            b_io.eh.critical_usageError(f"Unknown cmndArg={cmndArg}")

        return(cmndOutcome.set(opResults=result))


####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]]
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="cmndArg",
            argChoices=[],
            argDescription="Command which may need restOfArgs"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&9999",
            argName="restOfArgs",
            argChoices=[],
            argDescription="Rest of args which may be specific to each command"
        )
        return cmndArgsSpecDict

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Main" :anchor ""  :extraInfo "Framework DBlock"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Main_: |]]  Framework DBlock  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/main :csInfo "csInfo" :noCmndEntry "examples" :extraParamsHook "g_extraParams" :importedCmndsModules "g_importedCmndsModules"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =g_csMain= (csInfo, _examples_, g_extraParams, g_importedCmndsModules)
#+end_org """

if __name__ == '__main__':
    cs.main.g_csMain(
        csInfo=csInfo,
        noCmndEntry=examples,  # specify a Cmnd name
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
