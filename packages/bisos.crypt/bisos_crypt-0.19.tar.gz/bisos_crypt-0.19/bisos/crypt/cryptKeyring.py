# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CmndSvc= for
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
** This File: /bisos/git/bxRepos/bisos-pip/crypt/py3/bisos/crypt/cryptKeyring.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['cryptKeyring'], }
csInfo['version'] = '202502113531'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'cryptKeyring-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
Module description comes here.
** Relevant Panels:
** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
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
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:


import os
import collections
import enum

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import binascii
import base64

import json
import keyring
import getpass

#from cryptography.hazmat.primitives.ciphers.aead import AESGCM
#import binascii
import os
import errno

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

import pickle

from bisos.crypt import symCrypt


####+BEGIN: b:py3:cs:orgItem/section :title "CSU-Lib Examples" :comment "-- Providing examples_csu"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CSU-Lib Examples* -- Providing examples_csu  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:icm:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:dblock:python:section :title "Library Description (Overview)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Library Description (Overview)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


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
        parName='rsrc',
        parDescription="Resource",
        parDataType=None,
        parDefault=None,
        parChoices=["someResource", "UserInput"],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--rsrc',
        )
    

    csParams.parDictAdd(
        parName='cryptoPolicy',
        parDescription="Encryption Policy",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--cryptoPolicy',
        )

    csParams.parDictAdd(
        parName='passwdPolicy',
        parDescription="Policy For Setting Passwd In Keyring",
        parDataType=None,
        parDefault=None,
        parChoices=['prompt', 'default',],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--passwdPolicy',
        )

    csParams.parDictAdd(
        parName='system',
        parDescription="System Name",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--system',
        )
    
    csParams.parDictAdd(
        parName='user',
        parDescription="User Name",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--user',
        )

    csParams.parDictAdd(
        parName='passwd',
        parDescription="Pass Word",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--passwd',
        )
     


####+BEGIN: bx:dblock:python:section :title "Common Command Examples Sections"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Command Examples Sections*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:cs:python:func :funcName "examples_libModuleCmnds" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "keyring=None system=None user=None"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /examples_libModuleCmnds/ retType=bool argsList=(keyring=None system=None user=None)  [[elisp:(org-cycle)][| ]]
#+end_org """
def examples_libModuleCmnds(
    keyring=None,
    system=None,
    user=None,
):
####+END:
    """
** Auxiliary examples to be commonly used.x2
"""
    def cpsInit(): return collections.OrderedDict()
    def menuItemVerbose(): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')
    def menuItemTerse(): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')            
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity)            
    def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

    if not keyring:
        keyring="keyring"

    if not system:
        system="sysEx1"
        
    if not user:
        user="userEx1"
        
    rsrcPath = """{keyring}/{system}/{user}""".format(keyring=keyring, system=system, user=user)        

    cs.examples.menuChapter('*Prepare Crypto Keyring*')

    cmndName = "prepare"

    def thisBlock():
        cmndArgs = "";
        cps = cpsInit();  cps['rsrc'] = 'keyring'
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', comment="# One time initialization")
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='full')                        
    thisBlock()


####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "Set Password In Crypto Keyring"

####+END:

    cs.examples.menuChapter('*Set Password In Crypto Keyring*')

    cmndName = "cryptPasswdSet"
    
    def thisBlock():
        cmndArgs = "";
        cps = cpsInit();  cps['rsrc'] = rsrcPath;  cps['passwdPolicy'] = 'prompt'
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='full')                        
    thisBlock()
    

    def thisBlock():
        cmndArgs = "somePasswd";
        cps = cpsInit();  cps['rsrc'] = rsrcPath; 
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')
    thisBlock()


    cs.examples.menuChapter('*Get Password From Crypto Keyring (Decrypted)*')

    cmndName = "clearPasswdGet"
    def thisBlock():
        cmndArgs = "";
        cps = cpsInit();  cps['rsrc'] = rsrcPath
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')
    thisBlock()

    
####+BEGINNOT: bx:cs:python:cmnd:subSection :context "func-1" :context "func-1" :title "Get Password From Keyring (Encrypted)"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Get Password From Crypto Keyring*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    cs.examples.menuChapter('*Get Password From Keyring (Encrypted)*')

    cmndName = "keyringPasswdGet"
    def thisBlock():
        cmndArgs = "";
        cps = cpsInit();  cps['rsrc'] = rsrcPath
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')
    thisBlock()



####+BEGINNOT: bx:cs:python:cmnd:subSection :context "func-1" :context "func-1" :title "Delete Password From Crypto Keyring"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Delete Password From Crypto Keyring*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    cs.examples.menuChapter('*Delete Password From Crypto Keyring*')

    cmndName = "passwdDelete"

    def thisBlock():
        cmndArgs = "";
        cps = cpsInit();  cps['rsrc'] = rsrcPath
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')
    thisBlock()
    

    return


####+BEGIN: bx:dblock:python:section :title "Lib Module Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Lib Module Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:



####+BEGIN: bx:cs:python:section :title "ICM-Commands: CryptPasswd Prepare"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM-Commands: CryptPasswd Prepare*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "prepare" :comment "" :parsMand "rsrc" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<prepare>>  =verify= parsMand=rsrc ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class prepare(cs.Cmnd):
    cmndParamsMandatory = [ 'rsrc', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             rsrc: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'rsrc': rsrc, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        rsrc = csParam.mappedValue('rsrc', rsrc)
####+END:
        opError=b.OpError.Success

        rsrcPath = os.path.normpath(rsrc)
        rsrcParts = rsrcPath.split(os.sep)

        rsrcBase = rsrcParts[0]
        
        cryptoKeyring = CryptoKeyring()

        opError = cryptoKeyring.prepare()

        return cmndOutcome.set(
            opError=opError,
            opResults=None,
        )

####+BEGIN: bx:cs:python:section :title "ICM-Commands: CryptPasswd Set"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM-Commands: CryptPasswd Set*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cryptPasswdSet" :comment "" :parsMand "rsrc" :parsOpt "passwdPolicy" :argsMin 0 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cryptPasswdSet>>  =verify= parsMand=rsrc parsOpt=passwdPolicy argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cryptPasswdSet(cs.Cmnd):
    cmndParamsMandatory = [ 'rsrc', ]
    cmndParamsOptional = [ 'passwdPolicy', ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             rsrc: typing.Optional[str]=None,  # Cs Mandatory Param
             passwdPolicy: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'rsrc': rsrc, 'passwdPolicy': passwdPolicy, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        rsrc = csParam.mappedValue('rsrc', rsrc)
        passwdPolicy = csParam.mappedValue('passwdPolicy', passwdPolicy)
####+END:
        opError=b.OpError.Success

        rsrcPath = os.path.normpath(rsrc)
        rsrcParts = rsrcPath.split(os.sep)

        rsrcBase = rsrcParts[0]
        system = rsrcParts[1]
        user = rsrcParts[2]                

        
        passwd=None
        
        cmndArgs = self.cmndArgsGet("0&1", cmndArgsSpecDict, argsList)
        for each in cmndArgs:
            passwd = each                      

        if not passwd:
            
            if not passwdPolicy:
                passwd = "clear"
            elif passwdPolicy == "prompt":
                # Prompt for password
                passwd = getpass.getpass()
            else:
                return (
                    b_io.eh.problem_usageError("Bad passwdPolicy={}".passwdPolicy)
                )

            
        
        cryptoKeyring = CryptoKeyring(
            system=system,
            user=user,
        )

        cryptedPasswd = cryptoKeyring.passwdSet(passwd)

        if rtInv.outs:
            print(("cryptedPasswd={}".format(cryptedPasswd)))

        return cmndOutcome.set(
            opError=opError,
            opResults=cryptedPasswd,
        )

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification  -- Each As Any.
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&1",
            argName="passwd",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict



####+BEGIN: bx:cs:python:section :title "ICM-Commands: CryptPasswd Get"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM-Commands: CryptPasswd Get*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "clearPasswdGet" :comment "" :parsMand "rsrc" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<clearPasswdGet>>  =verify= parsMand=rsrc ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class clearPasswdGet(cs.Cmnd):
    cmndParamsMandatory = [ 'rsrc', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             rsrc: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'rsrc': rsrc, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        rsrc = csParam.mappedValue('rsrc', rsrc)
####+END:
        opError=b.OpError.Success

        rsrcPath = os.path.normpath(rsrc)
        rsrcParts = rsrcPath.split(os.sep)
        
        rsrcBase = rsrcParts[0]
        system = rsrcParts[1]
        user = rsrcParts[2]                

        cryptoKeyring = CryptoKeyring(
            system=system,
            user=user,
        )

        clearPasswd = cryptoKeyring.passwdGet()

        if rtInv.outs:        
            print(clearPasswd)

        return cmndOutcome.set(
            opError=opError,
            opResults=clearPasswd,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "keyringPasswdGet" :comment "" :parsMand "rsrc" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<keyringPasswdGet>>  =verify= parsMand=rsrc ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class keyringPasswdGet(cs.Cmnd):
    cmndParamsMandatory = [ 'rsrc', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             rsrc: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'rsrc': rsrc, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        rsrc = csParam.mappedValue('rsrc', rsrc)
####+END:
        opError=b.OpError.Success

        rsrcPath = os.path.normpath(rsrc)
        rsrcParts = rsrcPath.split(os.sep)

        rsrcBase = rsrcParts[0]
        system = rsrcParts[1]
        user = rsrcParts[2]                

        keyringPasswd = keyring.get_password(system, user)

        if rtInv.outs:
            if keyringPasswd:
                print(keyringPasswd)
            else:
                print(("No Passwd Found For: system={system} user={user}".format(system=system, user=user)))

        return cmndOutcome.set(
            opError=opError,
            opResults=keyringPasswd,
        )


####+BEGIN: bx:cs:python:section :title "ICM-Commands: CryptPasswd Delete"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM-Commands: CryptPasswd Get*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "passwdDelete" :comment "" :parsMand "rsrc system user" :parsOpt "passwdPolicy cryptoPolicy" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<passwdDelete>>  =verify= parsMand=rsrc system user parsOpt=passwdPolicy cryptoPolicy ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class passwdDelete(cs.Cmnd):
    cmndParamsMandatory = [ 'rsrc', 'system', 'user', ]
    cmndParamsOptional = [ 'passwdPolicy', 'cryptoPolicy', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             rsrc: typing.Optional[str]=None,  # Cs Mandatory Param
             system: typing.Optional[str]=None,  # Cs Mandatory Param
             user: typing.Optional[str]=None,  # Cs Mandatory Param
             passwdPolicy: typing.Optional[str]=None,  # Cs Optional Param
             cryptoPolicy: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'rsrc': rsrc, 'system': system, 'user': user, 'passwdPolicy': passwdPolicy, 'cryptoPolicy': cryptoPolicy, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        rsrc = csParam.mappedValue('rsrc', rsrc)
        system = csParam.mappedValue('system', system)
        user = csParam.mappedValue('user', user)
        passwdPolicy = csParam.mappedValue('passwdPolicy', passwdPolicy)
        cryptoPolicy = csParam.mappedValue('cryptoPolicy', cryptoPolicy)
####+END:
        opError=b.OpError.Success

        
        cryptoKeyring = CryptoKeyring(
            system=system,
            user=user,
        )

        opError = cryptoKeyring.passwdSet()

        #cryptoKeyring.save()        

        return cmndOutcome.set(
            opError=opError,
            opResults=None,
        )


####+BEGIN: bx:cs:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: b:py3:class/decl :className "CryptoKeyring" :superClass "" :comment "" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Class-basic    :: /CryptoKeyring/ object  [[elisp:(org-cycle)][| ]]
"""
class CryptoKeyring(object):
####+END:
    """ 
    """

    ucryptKeyringBackend = "placeholder"
    ucryptKeyringSystem = "ucrypt"    
    ucryptPolicy = "cryptoKeyring"
    ucryptKeyPasswdPolicy = "prompt"

####+BEGIN: b:py3:cs:method/args :methodName "__init__" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self system=None user=None"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /__init__/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(self, system=None, user=None, ):
####+END:
        """ 
        system = (string) 
        user = (string)
        """
        
        self.system = system
        self.user = user
        

####+BEGIN: b:py3:cs:method/args :methodName "load" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /load/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def load(self, ):
####+END:
        f = open(self.pickleFile, 'rb')
        tmp_dict = pickle.load(f)
        f.close()          

        self.__dict__.update(tmp_dict) 

####+BEGIN: b:py3:cs:method/args :methodName "save" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /save/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def save(self, ):
####+END:
        f = open(self.pickleFile, 'wb')
        pickle.dump(self.__dict__, f, 2)
        f.close()        


####+BEGIN: b:py3:cs:method/args :methodName "prepare" :methodType "anyOrNone" :retType "passwd string" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /prepare/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def prepare(self, ):
####+END:
        """ create ucrypt policy. 
"""
        outcome = symCrypt.createEncryptionPolicy().cmnd(
            interactive=False,
            rsrc="policy",
            policy=self.__class__.ucryptPolicy,
            keyringPolicy=self.__class__.ucryptKeyPasswdPolicy,
            #argsList=[],
        ).log()
        if outcome.isProblematic(): return(io.eh.badOutcome(outcome))

        print((outcome.results))



####+BEGIN: b:py3:cs:method/args :methodName "passwdSet" :methodType "anyOrNone" :retType "passwd string" :deco "default" :argsList "self passwd"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /passwdSet/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def passwdSet(self, passwd, ):
####+END:
        """ Return passwd string from keyring.
"""

        outcome = symCrypt.encrypt().cmnd(        
            interactive=False,
            rsrc="policy/{}".format(self.__class__.ucryptPolicy),            
            clearText=passwd,
        ).log()
        if outcome.isProblematic(): return(io.eh.badOutcome(outcome))

        cipheredPasswd = outcome.results

        keyring.set_password(self.system, self.user, cipheredPasswd)        
            
        keyringPasswd = keyring.get_password(self.system, self.user)

        b_io.tm.here(keyringPasswd)
        
        return keyringPasswd

    
####+BEGIN: b:py3:cs:method/args :methodName "passwdGet" :methodType "anyOrNone" :retType "binary" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /passwdGet/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def passwdGet(self, ):
####+END:
        """ Return passwd."""

        keyringPasswd = keyring.get_password(self.system, self.user)

        if not keyringPasswd:
            return None
        
        outcome = symCrypt.decrypt().cmnd(        
            interactive=False,
            rsrc="policy/{}".format(self.__class__.ucryptPolicy),            
            cipherText=keyringPasswd,
        ).log()
        if outcome.isProblematic(): return(io.eh.badOutcome(outcome))

        clearPasswd = outcome.results

        b_io.tm.here(clearPasswd)
        
        return clearPasswd


    
####+BEGIN: b:py3:cs:method/args :methodName "passwdDelete" :methodType "anyOrNone" :retType "binary" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /passwdDelete/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def passwdDelete(self, ):
####+END:
        """ Return passwd."""
        return 
    



####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :title " ~End Of Editable Text~ "
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
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


