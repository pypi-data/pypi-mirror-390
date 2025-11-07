# -*- coding: utf-8 -*-
"""\
* *[Summary]* ::  A /library/ to support icmsPkg facilities
"""

####+BEGIN: bx:cs:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
""" #+begin_org
*  This file:/bisos/git/auth/bxRepos/bisos-pip/namespace/py3/bisos/currents/bxCurrentsConfig.py :: [[elisp:(org-cycle)][| ]]
 is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
 *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
 A Python Interactively Command Module (PyICM).
 Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
 *WARNING*: All edits wityhin Dynamic Blocks may be lost.
#+end_org """
####+END:


"""
*  [[elisp:(org-cycle)][| *Lib-Module-INFO:* |]] :: Author, Copyleft and Version Information
"""

####+BEGIN: bx:global:lib:name-py :style "fileName"
__libName__ = "bxCurrentsConfig"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "202502123000"
####+END:

####+BEGIN: bx:global:icm:status-py :status "Production"
__status__ = "Production"
####+END:

__credits__ = [""]

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/csInfo-mbNedaGpl.py"

####+END:

####+BEGIN: bx:cs:python:topControls 
""" #+begin_org
*  [[elisp:(org-cycle)][|/Controls/| ]] :: [[elisp:(org-show-subtree)][|=]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
#+end_org """
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/pyWorkBench.org"

####+END:

####+BEGIN: bx:cs:python:section :title "ContentsList"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ContentsList*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:dblock:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =Imports=  [[elisp:(outline-show-subtree+toggle)][||]] *IMPORTS*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGINNOT: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
** Imports Based On Classification=cs-u
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:

import os
import collections
#import enum

import typing

from bisos.common import bisosPolicy
from bisos.currents import bxCurrentsThis

####+BEGIN: bx:dblock:python:section :title "Library Description (Overview)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Library Description (Overview)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:cs:python:section :title "Obtain Package Bases"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Obtain Package Bases*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:cs:python:func :funcName "configBaseDir_obtain" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /configBaseDir_obtain/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def configBaseDir_obtain():
####+END:
    return bxCurrentsThis.pkgBase_configDir()

####+BEGIN: bx:cs:python:func :funcName "configPkgInfoBaseDir_obtain" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "configBaseDir"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /configPkgInfoBaseDir_obtain/ retType=bool argsList=(configBaseDir)  [[elisp:(org-cycle)][| ]]
#+end_org """
def configPkgInfoBaseDir_obtain(
    configBaseDir,
):
####+END:
    if not configBaseDir:
        configBaseDir = configBaseDir_obtain()

    return os.path.abspath(
        "{}/pkgInfo".format(configBaseDir)
    )


####+BEGIN: bx:cs:python:func :funcName "configPkgInfoFpBaseDir_obtain" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "configBaseDir"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /configPkgInfoFpBaseDir_obtain/ retType=bool argsList=(configBaseDir)  [[elisp:(org-cycle)][| ]]
#+end_org """
def configPkgInfoFpBaseDir_obtain(
    configBaseDir,
):
####+END:
    if not configBaseDir:
        configBaseDir = configBaseDir_obtain()

    return os.path.abspath(
        "{}/pkgInfo/fp".format(configBaseDir)
    )

    
####+BEGIN: bx:dblock:python:section :title "File Parameters Obtain"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *File Parameters Obtain*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
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
            parRoot= os.path.abspath("{}/pkgInfo/fp".format(configBaseDir)),
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
            parRoot= os.path.abspath("{}/pkgInfo/fp".format(configBaseDir)),
            parName="sr")
    )


####+BEGIN: bx:dblock:python:section :title "Common Command Parameter Specification"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Command Parameter Specification*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
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
        parDescription="Root Of pkgInfo/fp from which file parameters will be read",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--configBaseDir',
    )
    
    csParams.parDictAdd(
        parName='bxoId',
        parDescription="BISOS Default UserName",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--bxoId',
    )
    
    csParams.parDictAdd(
        parName='sr',
        parDescription="BISOS Default GroupName",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--sr',
    )

####+BEGIN: bx:dblock:python:section :title "Common Command Examples Sections"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Command Examples Sections*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:cs:python:func :funcName "examples_pkgInfoParsFull" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "configBaseDir"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /examples_pkgInfoParsFull/ retType=bool argsList=(configBaseDir)  [[elisp:(org-cycle)][| ]]
#+end_org """
def examples_pkgInfoParsFull(
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
    
    cs.examples.menuChapter(' =FP Values=  *pkgInfo Get Parameters*')

    cmndName = "pkgInfoParsGet" ; cmndArgs = "" ;
    cps = collections.OrderedDict() ;  cps['configBaseDir'] = configBaseDir 
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "pkgInfoParsGet" ; cmndArgs = "" ; cps=cpsInit(); menuItem(verbosity='none')

    cs.examples.menuChapter(' =FP Values=  *PkgInfo Defaults ParsSet  --*')

    cmndName = "pkgInfoParsDefaultsSet" ; cmndArgs = "bxoPolicy /" ;
    cpsInit(); menuItem('none')

    cmndName = "pkgInfoParsDefaultsSet" ; cmndArgs = "bxoPolicy /tmp" ;
    cpsInit(); menuItem('none')
    
    cs.examples.menuChapter(' =FP Values=  *PkgInfo ParsSet -- Set Parameters Explicitly*')
     
    cmndName = "pkgInfoParsSet" ; cmndArgs = "" ;
    cps = collections.OrderedDict() ;  cps['bxoId'] = "mcm"
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "pkgInfoParsSet" ; cmndArgs = "" ;
    cps = collections.OrderedDict() ;  cps['bxoId'] = "ea-59043"
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "pkgInfoParsSet" ; cmndArgs = "" ;
    cps = collections.OrderedDict() ;  cps['sr'] = "marme/dsnProc"
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "pkgInfoParsSet" ; cmndArgs = "" ;
    cps = collections.OrderedDict() ;  cps['sr'] = "apache2/plone3"
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')
    
    # cmndName = "pkgInfoParsSet" ; cmndArgs = "" ;
    # cps = collections.OrderedDict() ;  cps['configBaseDir'] = configBaseDir ; cps['platformControlBaseDir'] = "${HOME}/bisosControl"
    # cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')
    
    cmndName = "pkgInfoParsSet" ; cmndArgs = "anyName=anyValue" ;
    cps = collections.OrderedDict() ; 
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "pkgInfoParsSet" ; cmndArgs = "anyName=anyValue" ;
    cps = collections.OrderedDict() ;
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper="echo", verbosity='little')
    

####+BEGIN: bx:dblock:python:section :title "File Parameters Get/Set -- Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *File Parameters Get/Set -- Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
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
    FP_readTreeAtBaseDir = b.fp.FP_readTreeAtBaseDir()
    FP_readTreeAtBaseDir.cmndLineInputOverRide = True
    FP_readTreeAtBaseDir.cmndOutcome = cmndOutcome
        
    return FP_readTreeAtBaseDir.cmnd(
        interactive=interactive,
        FPsDir=fpBaseDir,
    )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "pkgInfoParsGet" :comment "" :parsMand "" :parsOpt "configBaseDir" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<pkgInfoParsGet>>  =verify= parsOpt=configBaseDir ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class pkgInfoParsGet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'configBaseDir', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             configBaseDir: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'configBaseDir': configBaseDir, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        configBaseDir = csParam.mappedValue('configBaseDir', configBaseDir)
####+END:

        if not configBaseDir:
            configBaseDir = configBaseDir_obtain()

        FP_readTreeAtBaseDir_CmndOutput(
            interactive=interactive,
            fpBaseDir=configPkgInfoFpBaseDir_obtain(
                configBaseDir=configBaseDir,
            ),
            cmndOutcome=cmndOutcome,
        )

        return cmndOutcome


    def cmndDesc(): """
** Without --configBaseDir, it reads from ../pkgInfo/fp.
"""


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "pkgInfoParsSet" :comment "" :parsMand "" :parsOpt "configBaseDir bxoId sr" :argsMin 0 :argsMax 1000 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<pkgInfoParsSet>>  =verify= parsOpt=configBaseDir bxoId sr argsMax=1000 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class pkgInfoParsSet(cs.Cmnd):
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

        failed = b_io.eh.badOutcome
        callParamsDict = {'configBaseDir': configBaseDir, 'bxoId': bxoId, 'sr': sr, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        configBaseDir = csParam.mappedValue('configBaseDir', configBaseDir)
        bxoId = csParam.mappedValue('bxoId', bxoId)
        sr = csParam.mappedValue('sr', sr)
####+END:
        if not configBaseDir:
            configBaseDir = configBaseDir_obtain()

        cmndArgs = self.cmndArgsGet("0&-1", cmndArgsSpecDict, argsList)

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
            
            icm.b.fp.FileParamWriteToPath(
                parNameFullPath=fpPath,
                parValue=valuePath,
            )

        def processEachArg(argStr):
            varNameValue=argStr.split('=')
            icm.b.fp.FileParamWriteToPath(
                parNameFullPath=os.path.join(
                    configPkgInfoFpBaseDir_obtain(configBaseDir=configBaseDir),
                    varNameValue[0],
                ),
                parValue=varNameValue[1],
            )

        # Any number of Name=Value can be passed as args
        for each in cmndArgs:
            processEachArg(each)

        if bxoId:
             parNameFullPath = icm.b.fp.FileParamWriteToPath(
                parNameFullPath=os.path.join(
                    configPkgInfoFpBaseDir_obtain(configBaseDir=configBaseDir),
                    "bxoId",
                ),
                parValue=bxoId,
            )

        if sr:
             parNameFullPath = icm.b.fp.FileParamWriteToPath(
                parNameFullPath=os.path.join(configPkgInfoFpBaseDir_obtain(configBaseDir=configBaseDir),
                             "sr",
                ),
                parValue=sr,
            )
            
        if rtInv.outs:
            parValue = b.fp.FileParamValueReadFromPath(parNameFullPath)
            b_io.ann.here("pkgInfoParsSet: {parValue} at {parNameFullPath}".
                         format(parValue=parValue, parNameFullPath=parNameFullPath))


        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
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

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "pkgInfoParsDefaultsSet" :comment "" :parsMand "" :parsOpt "configBaseDir bisosUserName bisosGroupName rootDir_bisos rootDir_bxo rootDir_deRun rootDir_foreignBxo" :argsMin 0 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<pkgInfoParsDefaultsSet>>  =verify= parsOpt=configBaseDir bisosUserName bisosGroupName rootDir_bisos rootDir_bxo rootDir_deRun rootDir_foreignBxo argsMax=2 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class pkgInfoParsDefaultsSet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'configBaseDir', 'bisosUserName', 'bisosGroupName', 'rootDir_bisos', 'rootDir_bxo', 'rootDir_deRun', 'rootDir_foreignBxo', ]
    cmndArgsLen = {'Min': 0, 'Max': 2,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             configBaseDir: typing.Optional[str]=None,  # Cs Optional Param
             bisosUserName: typing.Optional[str]=None,  # Cs Optional Param
             bisosGroupName: typing.Optional[str]=None,  # Cs Optional Param
             rootDir_bisos: typing.Optional[str]=None,  # Cs Optional Param
             rootDir_bxo: typing.Optional[str]=None,  # Cs Optional Param
             rootDir_deRun: typing.Optional[str]=None,  # Cs Optional Param
             rootDir_foreignBxo: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'configBaseDir': configBaseDir, 'bisosUserName': bisosUserName, 'bisosGroupName': bisosGroupName, 'rootDir_bisos': rootDir_bisos, 'rootDir_bxo': rootDir_bxo, 'rootDir_deRun': rootDir_deRun, 'rootDir_foreignBxo': rootDir_foreignBxo, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        configBaseDir = csParam.mappedValue('configBaseDir', configBaseDir)
        bisosUserName = csParam.mappedValue('bisosUserName', bisosUserName)
        bisosGroupName = csParam.mappedValue('bisosGroupName', bisosGroupName)
        rootDir_bisos = csParam.mappedValue('rootDir_bisos', rootDir_bisos)
        rootDir_bxo = csParam.mappedValue('rootDir_bxo', rootDir_bxo)
        rootDir_deRun = csParam.mappedValue('rootDir_deRun', rootDir_deRun)
        rootDir_foreignBxo = csParam.mappedValue('rootDir_foreignBxo', rootDir_foreignBxo)
####+END:
        if not configBaseDir:
            configBaseDir = configBaseDir_obtain()

        basesPolicy = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        rootPrefix = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)

        if basesPolicy == "bxoPolicy":
            if not bisosUserName:
                bisosUserName = bisosPolicy.bisosAccountName()
                
            if not bisosGroupName:
                bisosGroupName = bisosPolicy.bisosGroupName()

            if not rootDir_bisos:
                rootDir_bisos = os.path.join(rootPrefix, bisosPolicy.rootDir_bisos())

            if not rootDir_bxo:
                rootDir_bxo = os.path.join(rootPrefix, bisosPolicy.rootDir_bxo())

            if not rootDir_deRun:
                rootDir_deRun = os.path.join(rootPrefix, bisosPolicy.rootDir_deRun())

                
        elif basesPolicy == "foreignBxoPolicy":
            if not bisosUserName:
                return b_io.eh.problem_usageError("Missing bisosUserName")                

            if not bisosGroupName:
                return b_io.eh.problem_usageError("Missing bisosGroupName")

            if not rootDir_foreignBxo:
                return b_io.eh.problem_usageError("Missing rootDir_foreignBxo")

            if not rootDir_bisos:
                rootDir_bisos = os.path.join(rootPrefix, bisosPolicy.rootDir_bisos())

            if not rootDir_bxo:
                rootDir_bxo = os.path.join(rootPrefix, bisosPolicy.rootDir_bxo())

            if not rootDir_deRun:
                rootDir_deRun = os.path.join(rootPrefix, bisosPolicy.rootDir_deRun())
            
            
        elif basesPolicy == "externalPolicy":
            if not bisosUserName:
                return b_io.eh.problem_usageError("Missing bisosUserName")                

            if not bisosGroupName:
                return b_io.eh.problem_usageError("Missing bisosGroupName")

            if not rootDir_foreignBxo:
                return b_io.eh.problem_usageError("Missing rootDir_foreignBxo")

            if not rootDir_bisos:
                return b_io.eh.problem_usageError("Missing rootDir_bisos")

            if not rootDir_bxo:
                return b_io.eh.problem_usageError("Missing rootDir_bxo")                

            if not rootDir_deRun:
                return b_io.eh.problem_usageError("Missing rootDir_deRun")                
            
            
        else:
            return b_io.eh.critical_oops("basesPolicy={}".format(basesPolicy))

        pkgInfoParsSet().cmnd(
            interactive=False,
            configBaseDir=configBaseDir,
            bisosUserName=bisosUserName,
            bisosGroupName=bisosGroupName,
            rootDir_foreignBxo=rootDir_foreignBxo,
            rootDir_bisos=rootDir_bisos,
            rootDir_bxo=rootDir_bxo,
            rootDir_deRun=rootDir_deRun,
        )

    def cmndDesc(): """
** Set File Parameters at ../pkgInfo/fp -- By default
** TODO NOTYET auto detect marme.dev -- marme.control and decide where they should be, perhaps in /var/
"""

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec():
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="basesPolicy",
            argDefault="bxoPolicy",
            argChoices=['bxoPolicy', 'foreignBxoPolicy', 'externalPolicy'],
            argDescription="bxoPolicy: rundirs are per bxo/foreign. externalPolicy: Un-ByStar."
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="rootPrefix",
            argDefault="/",            
            argChoices='any',
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict
    
    

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :title " ~End Of Editable Text~ "
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _ ~End Of Editable Text~ _: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"

####+END:
