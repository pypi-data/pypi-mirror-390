# -*- coding: utf-8 -*-

""" #+begin_org
* *[Summary]* :: A =CmndLib= for providing currents configuration to CS-s.
#+end_org """

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
** This File: /bisos/git/auth/bxRepos/bisos-pip/currents/py3/bisos/currents/currentsConfig.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['currentsConfig'], }
csInfo['version'] = '202209290819'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'currentsConfig-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* /[[elisp:(org-cycle)][| Description |]]/ :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
Module description comes here.
** Relevant Panels:
** Status: In use with blee3
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

import os
import collections
#import enum

import shutil

import sys
import pathlib

####+BEGIN: blee:bxPanel:foldingSection :outLevel 1 :title "Obtain Package Bases"  :extraInfo ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*       [[elisp:(outline-show-subtree+toggle)][| *Obtain Package Bases:* |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "configBaseDir_obtain" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /configBaseDir_obtain/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def configBaseDir_obtain(
####+END:

) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """


    outcome =  b.subProc.WOpW(invedBy=None, log=0).bash(
        f"""usgBpos.sh -i usgBpos_usageEnvs_fullUse_bxoPath""")

    if outcome.isProblematic():
        outcome =  b.subProc.WOpW(invedBy=None, log=0).bash(
            f"""/bisos/core/bsip/bin/usgBpos.sh -i usgBposUsageEnvs_bisosDev_bxoPath""")
        if outcome.isProblematic():
                #b_io.ann("Both Failed: usgBpos.sh -i {usgBposUsageEnvs_bisosDev_bxoPath,usgBposUsageEnvs_bisosDev_bxoPath}")
                b_io.write("Both Failed: usgBpos.sh -i {usgBposUsageEnvs_bisosDev_bxoPath}")
                b_io.eh.badOutcome(outcome)
                return ""

    retVal = outcome.stdout.rstrip('\n')

    return retVal


####+BEGIN: bx:cs:python:func :funcName "configUsgCursBaseDir_obtain" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "configBaseDir"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /configUsgCursBaseDir_obtain/ retType=bool argsList=(configBaseDir)  [[elisp:(org-cycle)][| ]]
#+end_org """
def configUsgCursBaseDir_obtain(
    configBaseDir,
):
####+END:
    if not configBaseDir:
        configBaseDir = configBaseDir_obtain()

    return os.path.abspath(os.path.join(configBaseDir, "control/currents"))


####+BEGIN: bx:cs:python:func :funcName "configUsgCursFpBaseDir_obtain" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "configBaseDir"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /configUsgCursFpBaseDir_obtain/ retType=bool argsList=(configBaseDir)  [[elisp:(org-cycle)][| ]]
#+end_org """
def configUsgCursFpBaseDir_obtain(
    configBaseDir,
):
####+END:
    if not configBaseDir:
        configBaseDir = configBaseDir_obtain()

    return os.path.abspath(os.path.join(configBaseDir,"control/currents/fp"))



####+BEGIN: blee:bxPanel:foldingSection :outLevel 1 :title "File Parameters Obtain"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*       [[elisp:(outline-show-subtree+toggle)][| *File Parameters Obtain:* |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:cs:python:func :funcName "bxoId_fpObtain" :comment "Configuration Parameter" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "configBaseDir"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /bxoId_fpObtain/ =Configuration Parameter= retType=bool argsList=(configBaseDir)  [[elisp:(org-cycle)][| ]]
#+end_org """
def bxoId_fpObtain(
    configBaseDir,
):
####+END:
    if not configBaseDir:
        configBaseDir = configBaseDir_obtain()

    return(
        b.fp.FileParamValueReadFrom(
            parRoot= os.path.abspath("{}/usgCurs/fp".format(configBaseDir)),
            parName="bxoId")
    )


####+BEGIN: bx:cs:python:func :funcName "sr_fpObtain" :comment "Configuration Parameter" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "configBaseDir"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /sr_fpObtain/ =Configuration Parameter= retType=bool argsList=(configBaseDir)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sr_fpObtain(
    configBaseDir,
):
####+END:
    if not configBaseDir:
        configBaseDir = configBaseDir_obtain()

    return(
        b.fp.FileParamValueReadFrom(
            parRoot= os.path.abspath("{}/usgCurs/fp".format(configBaseDir)),
            parName="sr")
    )


####+BEGIN: blee:bxPanel:foldingSection :outLevel 1 :title "Common Command Parameter Specification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*       [[elisp:(outline-show-subtree+toggle)][| *Common Command Parameter Specification:* |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


####+BEGIN: bx:cs:python:func :funcName "commonParamsSpecify" :funcType "void" :retType "bool" :deco "" :argsList "csParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-void     [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ retType=bool argsList=(csParams)  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    csParams,
):
####+END:

    csParams.parDictAdd(
        parName='configBaseDir',
        parDescription="Root Of usgCurs/fp from which file parameters will be read",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--configBaseDir',
    )

    csParams.parDictAdd(
        parName='bxoId',
        parDescription="BISOS Default UserName",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--bxoId',
    )

    csParams.parDictAdd(
        parName='sr',
        parDescription="BISOS Default GroupName",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--sr',
    )

####+BEGIN: blee:bxPanel:foldingSection :outLevel 1 :title "Common Command Examples Sections"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*       [[elisp:(outline-show-subtree+toggle)][| *Common Command Examples Sections:* |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


####+BEGIN: bx:cs:python:func :funcName "examples_usgCursParsFull" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "configBaseDir"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /examples_usgCursParsFull/ retType=bool argsList=(configBaseDir)  [[elisp:(org-cycle)][| ]]
#+end_org """
def examples_usgCursParsFull(
    configBaseDir,
):
####+END:
    """
** Auxiliary examples to be commonly used.
"""

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity,
                             comment='none', icmWrapper=None, icmName=None) # verbosity: 'little' 'basic' 'none'
    def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

    cs.examples.menuChapter(' =FP Values=  *usgCurs Clear InfoBase --- Deletes All FPs*')

    cmndName = "usgCursParsDelete" ; cmndArgs = "" ;
    cps = collections.OrderedDict() ;  cps['configBaseDir'] = configBaseDir
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "usgCursParsDelete" ; cmndArgs = "" ; cps=cpsInit(); menuItem(verbosity='none')

    cmndName = "usgCursParsDelete" ; cmndArgs = "anyName" ;
    cps = collections.OrderedDict() ;
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper="echo", verbosity='little')

    cs.examples.menuChapter(' =FP Values=  *usgCurs Get Parameters*')

    cmndName = "usgCursParsGet" ; cmndArgs = "" ;
    cps = collections.OrderedDict() ;  cps['configBaseDir'] = configBaseDir
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "usgCursParsGet" ; cmndArgs = "" ; cps=cpsInit(); menuItem(verbosity='none')

    cs.examples.menuChapter(' =FP Values=  *UsgCurs Defaults ParsSet  --*')

    cmndName = "usgCursParsDefaultsSet" ; cmndArgs = "bxoPolicy /" ;
    cpsInit(); menuItem('none')

    cmndName = "usgCursParsDefaultsSet" ; cmndArgs = "bxoPolicy /tmp" ;
    cpsInit(); menuItem('none')

    cs.examples.menuChapter(' =FP Values=  *UsgCurs ParsSet -- Set Parameters Explicitly*')

    cmndOutcome = b.op.Outcome()
    curParsGetAsDictValue_wOp("", cmndOutcome)
    results = cmndOutcome.results
    for eachKey in results:
        cs.examples.execInsert(execLine=f"bx-currents.cs -v 20 -i usgCursParsSet {eachKey}={results[eachKey]}")

    # cmndName = "usgCursParsSet" ; cmndArgs = "" ;
    # cps = collections.OrderedDict() ;  cps['bpoId'] = "BPOID"
    # cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    # cmndName = "usgCursParsSet" ; cmndArgs = "" ;
    # cps = collections.OrderedDict() ;  cps['bxoId'] = "ea-59043"
    # cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    # cmndName = "usgCursParsSet" ; cmndArgs = "" ;
    # cps = collections.OrderedDict() ;  cps['sr'] = "marme/dsnProc"
    # cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    # cmndName = "usgCursParsSet" ; cmndArgs = "" ;
    # cps = collections.OrderedDict() ;  cps['sr'] = "apache2/plone3"
    # cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    # # cmndName = "usgCursParsSet" ; cmndArgs = "" ;
    # # cps = collections.OrderedDict() ;  cps['configBaseDir'] = configBaseDir ; cps['platformControlBaseDir'] = "${HOME}/bisosControl"
    # # cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "usgCursParsSet" ; cmndArgs = "anyName=anyValue" ;
    cps = collections.OrderedDict() ;
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "usgCursParsSet" ; cmndArgs = "anyName=anyValue" ;
    cps = collections.OrderedDict() ;
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper="echo", verbosity='little')


####+BEGIN: blee:bxPanel:foldingSection :outLevel 1 :title "File Parameters Get/Set -- Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*       [[elisp:(outline-show-subtree+toggle)][| *File Parameters Get/Set -- Commands:* |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


####+BEGIN: bx:cs:python:func :funcName "FP_readTreeAtBaseDir_CmndOutput" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "interactive fpBaseDir cmndOutcome"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /FP_readTreeAtBaseDir_CmndOutput/ retType=bool argsList=(interactive fpBaseDir cmndOutcome)  [[elisp:(org-cycle)][| ]]
#+end_org """
def FP_readTreeAtBaseDir_CmndOutput(
    interactive,
    fpBaseDir,
    cmndOutcome,
):
####+END:
    """Invokes FP_readTreeAtBaseDir.cmnd as interactive-output only."""
    #
    # Interactive-Output + Chained-Outcome Command Invokation
    #
    FP_readTreeAtBaseDir = icm.FP_readTreeAtBaseDir()
    FP_readTreeAtBaseDir.cmndLineInputOverRide = True
    FP_readTreeAtBaseDir.cmndOutcome = cmndOutcome

    return FP_readTreeAtBaseDir.cmnd(
        interactive=interactive,
        FPsDir=fpBaseDir,
    )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "usgCursParsDelete" :comment "" :parsMand "" :parsOpt "configBaseDir" :argsMin 0 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<usgCursParsDelete>>  =verify= parsOpt=configBaseDir argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class usgCursParsDelete(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'configBaseDir', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             configBaseDir: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'configBaseDir': configBaseDir, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Remove The entire infoBaseDir
        #+end_org """)

        if not configBaseDir:
            configBaseDir = configUsgCursFpBaseDir_obtain(None)

        cmndArgs = self.cmndArgsGet("0&-1", cmndArgsSpecDict, argsList)

        if len(cmndArgs) == 0:
            try:
                shutil.rmtree(configBaseDir)
            except OSError as e:
                print(f"Error: {configBaseDir} : {e.strerror}")
            b.dir.createIfNotThere(configBaseDir)

        else:
            for each in cmndArgs:
                parNameFullPath = os.path.join(
                        configBaseDir,
                        each
                )
                try:
                    shutil.rmtree(parNameFullPath)
                except OSError as e:
                    print(f"Error: {parNameFullPath} : {e.strerror}")


        return cmndOutcome

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&-1",
            argName="cmndArgs",
            argDefault=None,
            argChoices='any',
            argDescription="A sequence of parNames"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:func/typing :funcName "curParsGetAsDictValue" :funcType "WOp" :retType "extTyped" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-WOp    [[elisp:(outline-show-subtree+toggle)][||]] /curParsGetAsDictValue/   [[elisp:(org-cycle)][| ]]
#+end_org """
def curParsGetAsDictValue(
####+END:
        parNamesList: list,
) -> typing.Dict[str, typing.Any]:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] A function returning a dictionary of values.
    if not ~parNamesList~, get all the values.
    #+end_org """

    configBaseDir = configUsgCursFpBaseDir_obtain(None)

    return (
        b.fp.parsGetAsDictValue(parNamesList, configBaseDir,)
    )


####+BEGIN: b:py3:cs:func/typing :funcName "curParsGetAsDictValue_wOp" :funcType "WOp" :retType "extTyped" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-WOp    [[elisp:(outline-show-subtree+toggle)][||]] /curParsGetAsDictValue_wOp/   [[elisp:(org-cycle)][| ]]
#+end_org """
def curParsGetAsDictValue_wOp(
####+END:
        parNamesList: list,
        outcome: b.op.Outcome = None,
) -> b.op.Outcome:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] A Wrapped Operation with results being a dictionary of values.
    if not ~parNamesList~, get all the values.
    #+end_org """

    configBaseDir = configUsgCursFpBaseDir_obtain(None)

    try:
        if not pathlib.Path(configBaseDir).exists():
            b_io.stderr(f"ALERT: Missing {configBaseDir}")
            outcome.results = {}
            return outcome
            #return None
    except:
        print("NOTYET -- exception")
        return None

    return (
        #FP_parsGetAsDictValue_wOp(parNamesList, configBaseDir, outcome)
        b.fp.parsGetAsDictValue_wOp(parNamesList, configBaseDir, outcome)
    )

####+BEGIN: b:py3:cs:func/typing :funcName "FP_parsGetAsDictValue_wOp_Obsoleted" :funcType "wOp" :retType "OpOutcome" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-wOp    [[elisp:(outline-show-subtree+toggle)][||]] /FP_parsGetAsDictValue_wOp_Obsoleted/   [[elisp:(org-cycle)][| ]]
#+end_org """
def FP_parsGetAsDictValue_wOp_Obsoleted(
####+END:
        parNamesList: list,
        configBaseDir,
        outcome: b.op.Outcome = None,
) -> b.op.Outcome:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] A Wrapped Operation with results being a dictionary of values.
    if not ~parNamesList~, get all the values.
*** TODO --- NOTYET This needs to be moved to
    #+end_org """



    return b.fp.parsGetAsDictValue_wOp(parNamesList, configBaseDir, outcome=outcome)

    print(f"NOTREACHED {configBaseDir}")

    if not outcome:
        outcome = b.op.Outcome()

    FP_readTreeAtBaseDir_CmndOutput(
        interactive=False,
        fpBaseDir=configBaseDir,
        cmndOutcome=outcome,
    )

    results = outcome.results

    opResults = dict()
    opErrors = ""

    if parNamesList:
        for each in parNamesList:
            # NOTYET, If no results[each], we need to record it in opErrors
            opResults[each] = results[each].parValueGet()
            #print(f"{each} {eachFpValue}")

    else:
        for eachFpName in results:
            opResults[eachFpName] = results[eachFpName].parValueGet()
            #print(f"{eachFpName} {eachFpValue}")

    return outcome.set(
        opError=b.OpError.Success,
        opResults=opResults,
    )



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "usgCursParsGet" :comment "" :parsMand "" :parsOpt "configBaseDir" :argsMin 0 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<usgCursParsGet>>  =verify= parsOpt=configBaseDir argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class usgCursParsGet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'configBaseDir', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             configBaseDir: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'configBaseDir': configBaseDir, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  it reads from ../usgCurs/fp.
        #+end_org """)

        if not configBaseDir:
            configBaseDir = configUsgCursFpBaseDir_obtain(None)

        cmndArgs = self.cmndArgsGet("0&-1", cmndArgsSpecDict, argsList)

        curParsGetAsDictValue_wOp(cmndArgs, cmndOutcome)
        results = cmndOutcome.results

        if rtInv.outs:
            configBaseDir = configUsgCursFpBaseDir_obtain(None)
            print(f"Obtained From: configBaseDir={configBaseDir}")
            for eachKey in results:
                print(f"{eachKey}: {results[eachKey]}")

        return cmndOutcome

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&-1",
            argName="cmndArgs",
            argDefault=None,
            argChoices='any',
            argDescription="A sequence of parNames"
        )

        return cmndArgsSpecDict




####+BEGIN: b:py3:cs:cmnd/classHeadNOT :cmndName "usgCursParsSet" :comment "" :parsMand "" :parsOpt "configBaseDir bxoId sr" :argsMin 0 :argsMax 1000 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<usgCursParsSet>>  =verify= parsOpt=configBaseDir bxoId sr argsMax=1000 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class usgCursParsSet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'configBaseDir', 'bxoId', 'sr', ]
    cmndArgsLen = {'Min': 0, 'Max': 1000,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             configBaseDir: typing.Optional[str]=None,  # Cs Optional Param
             bxoId: typing.Optional[str]=None,  # Cs Optional Param
             sr: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        #callParamsDict = {'configBaseDir': configBaseDir, 'bxoId': bxoId, 'sr': sr, }
        #if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            #return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Args are in the form of a list of varName=varValue. Well known pars can also be set.
=configBaseDir= defaults to ~configBaseDir_obtain()~
        #+end_org """)

        if not configBaseDir:
            configBaseDir = configBaseDir_obtain()

        cmndArgs = self.cmndArgsGet("0&-1", cmndArgsSpecDict, argsList)

        parNameFullPath = ""

        def createPathAndFpWrite(
                fpPath,
                valuePath,
        ):
            valuePath = os.path.abspath(valuePath)
            try:
                os.makedirs(valuePath)
            except OSError:
                if not os.path.isdir(valuePath):
                    raise

            b.fp.b.fp.FileParamWriteToPath(
                parNameFullPath=fpPath,
                parValue=valuePath,
            )
            parNameFullPath = fpPath

        # Any number of Name=Value can be passed as args
        for each in cmndArgs:
            varNameValue = each.split('=')
            parNameFullPath = os.path.join(
                    configUsgCursFpBaseDir_obtain(configBaseDir=configBaseDir),
                    varNameValue[0],
            )
            b.fp.b.fp.FileParamWriteToPath(
                parNameFullPath=parNameFullPath,
                parValue=varNameValue[1],
            )


        if bxoId:
             parNameFullPath = b.fp.b.fp.FileParamWriteToPath(
                parNameFullPath=os.path.join(
                    configUsgCursFpBaseDir_obtain(configBaseDir=configBaseDir),
                    "bxoId",
                ),
                parValue=bxoId,
            )

        if sr:
             parNameFullPath = b.fp.b.fp.FileParamWriteToPath(
                parNameFullPath=os.path.join(configUsgCursFpBaseDir_obtain(configBaseDir=configBaseDir),
                             "sr",
                ),
                parValue=sr,
            )

        if rtInv.outs:
            parValue = b.fp.FileParamValueReadFromPath(parNameFullPath)
            b_io.ann.here("usgCursParsSet: {parValue} at {parNameFullPath}".
                         format(parValue=parValue, parNameFullPath=parNameFullPath))


        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=True,
        )

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&-1",
            argName="cmndArgs",
            argDefault=None,
            argChoices='any',
            argDescription="A sequence of varName=varValue"
        )

        return cmndArgsSpecDict




####+BEGIN: b:prog:file/endOfFile :extraParams nil
""" #+begin_org
* *[[elisp:(org-cycle)][| END-OF-FILE |]]* :: emacs and org variables and control parameters
#+end_org """
### local variables:
### no-byte-compile: t
### end:
####+END:
