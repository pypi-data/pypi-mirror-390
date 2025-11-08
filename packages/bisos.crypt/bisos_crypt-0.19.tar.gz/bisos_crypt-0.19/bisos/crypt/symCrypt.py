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
** This File: /bisos/git/bxRepos/bisos-pip/crypt/py3/bisos/crypt/symCrypt.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['symCrypt'], }
csInfo['version'] = '202502110208'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'symCrypt-Panel.org'
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


import sys
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

####+BEGIN: bx:icm:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: bx:dblock:python:section :title "Common Command Parameter Specification"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Command Parameter Specification*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:cs:python:func :funcName "commonParamsSpecify" :funcType "void" :retType "bool" :deco "" :argsList "csParams"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-void      :: /commonParamsSpecify/ retType=bool argsList=(csParams)  [[elisp:(org-cycle)][| ]]
"""
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
        parName='inFile',
        parDescription="Input File",
        parDataType=None,
        parDefault=None,
        parChoices=["someFile", "UserInput"],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--inFile',
        )

    csParams.parDictAdd(
        parName='baseDir',
        parDescription="Base Directory Name",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--baseDir',
        )

    csParams.parDictAdd(
        parName='policy',
        parDescription="Encryption Policy",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--policy',
        )

    csParams.parDictAdd(
        parName='keyringPolicy',
        parDescription="Policy For Setting Passwd In Keyring",
        parDataType=None,
        parDefault=None,
        parChoices=['prompt', 'default',],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--keyringPolicy',
        )

    csParams.parDictAdd(
        parName='alg',
        parDescription="Symetric Encryption Algorithem",
        parDataType=None,
        parDefault=None,
        parChoices=['default', 'someAlg',],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--alg',
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

    csParams.parDictAdd(
        parName='seed',
        parDescription="Seed or Salt",
        parDataType=None,
        parDefault=None,
        parChoices=[],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--seed',
        )
    


####+BEGIN: bx:dblock:python:section :title "Common Command Examples Sections"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Command Examples Sections*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:cs:python:func :funcName "examples_libModuleCmnds" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /examples_libModuleCmnds/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def examples_libModuleCmnds():
####+END:
    """
** Auxiliary examples to be commonly used.x2
"""
    def cpsInit(): return collections.OrderedDict()
    def menuItemVerbose(): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')
    def menuItemTerse(): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')            
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity)            
    def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "Generate Seed (genseed)"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Generate Seed (genseed)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    cs.examples.menuChapter('*Generate Seed (genseed)*')
        
    cmndName = "genseed"

    def thisBlock1():
        cps = cpsInit() ; cmndArgs = "";
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')            
    thisBlock1()

    def thisBlock():
        cps = cpsInit() ; cmndArgs = "hex";
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')            
    thisBlock()
    

####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "Generate Key (genkey)"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Generate Key (genkey)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    cs.examples.menuChapter('*Generate Key (genkey)*')

    cmndName = "genkey"

    def thisBlock2(): # type: ignore [no-redef]
        cps = cpsInit() ; cmndArgs = "";
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='full')                        
    thisBlock2()

    def thisBlock3(): # type: ignore [no-redef]
        cps = cpsInit() ; cmndArgs = "hex";
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')
    thisBlock3()


####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "List Encryption Policy"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *List Encryption Policy*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    cs.examples.menuSection('*listEncryptionPolicy*')

    cmndName = "listEncryptionPolicy"
    def setRsrc(cps):
        cps['rsrc'] = "policy";        

    cps = cpsInit() ; setRsrc(cps)
    cmndArgs = ""
    cps['baseDir'] = "~/.ucrypt" ; menuItem(verbosity='none')        
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='full')        

    def thisBlock4():
        cps = cpsInit() ; setRsrc(cps) 
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')            
    thisBlock4()


####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "Create Encryption Policy"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Create Encryption Policy*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    cs.examples.menuSection('*createEncryptionPolicy*')

    cmndName = "createEncryptionPolicy"
    def setRsrc(cps):
        cps['rsrc'] = "policy";        


    cps = cpsInit() ; setRsrc(cps) ; cps['policy'] = "example"
    cmndArgs = ""; menuItem(verbosity='none')

    cps['keyringPolicy'] = "default" ; cps['baseDir'] = "~/.ucrypt" ; menuItem(verbosity='none')        
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='full')        

    def thisBlock():
        cps = cpsInit() ; setRsrc(cps) ; cps['policy'] = "weak"; cps['alg'] = "clear" ;
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')            
    thisBlock()

####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "Show Encryption Policy"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Create Encryption Policy*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    cs.examples.menuSection('*createEncryptionPolicy*')

    cmndName = "describeEncryptionPolicy"
    def setRsrc(cps):
        cps['rsrc'] = "policy/example";        


    def thisBlock():
        cps = cpsInit() ; setRsrc(cps)
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')            
    thisBlock()

    execLineEx("""keyring get ucrypt example""")
    

####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "Encrypt"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Encrypt*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    cs.examples.menuSection('*Encrypt*')

    cmndName = "encrypt"

    def setRsrc(cps):
        cps['rsrc'] = "policy/example";        

    cps = cpsInit(); setRsrc(cps)
    cmndArgs = "clearTextComesHere"; menuItem(verbosity='none')
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='full')

    def thisBlock():
        cps = cpsInit() ; cps['inFile'] = "/etc/passwd"; setRsrc(cps); cmndArgs = ""
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')            
    thisBlock()

    def thisBlock():
        icmWrapper = "echo HereComes Some ClearText | "
        cps = cpsInit();  setRsrc(cps); cmndArgs = ""
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)
    thisBlock()

    def setRsrc(cps):
        cps['rsrc'] = "policy/weak";        

    def thisBlock():
        icmWrapper = "echo HereComes Some ClearText | "
        cps = cpsInit();  setRsrc(cps); cmndArgs = ""
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)
    thisBlock()


####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "Decrypt"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Decrypt*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    cs.examples.menuSection('*Decrypt*')

    cmndName = "decrypt"

    cps = cpsInit() 

    cmndArgs = "cipherText"; menuItem(verbosity='none')

    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='full')        

    def thisBlock():
        clearText = "Some Secret"
        encryptCmnd = """ucrypt.py --rsrc="policy/weak"  -i encrypt"""
        icmWrapper = """echo {clearText} | {encryptCmnd} | """.format(
            clearText=clearText,
            encryptCmnd=encryptCmnd,
        )
        cps = cpsInit();  cps['rsrc'] = "policy/weak"; cmndArgs = ""
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)
    thisBlock()

    def thisBlock():
        clearText = "Some Secret"
        encryptCmnd = """"""
        argCmnd = """$( ucrypt.py --rsrc="policy/weak"  -i encrypt "{clearText}" )""".format(
            clearText=clearText,
        )
        cps = cpsInit();  cps['rsrc'] = "policy/weak"; cmndArgs = argCmnd
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')
    thisBlock()


    # ucrypt.py --rsrc="policy/weak"  -i decrypt $(echo Some Secret | ucrypt.py --rsrc=policy/weak  -i encrypt)        


        
####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "Remain In Sycn With Template"
    """
**   [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]          *Remain In Sycn With Template*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

    def thisBlock():
        cs.examples.menuChapter('*Remain In Sycn With Template*')

        templateFile = "/bisos/git/bxRepos/bisos-pip/examples/dev/bisos/examples/icmLibPkgBegin.py"
        thisFile = __file__

        execLineEx("""diff {thisFile} {templateFile}""".format(thisFile=thisFile, templateFile=templateFile))
        execLineEx("""cp {thisFile} {templateFile}""".format(thisFile=thisFile, templateFile=templateFile))
        execLineEx("""cp {templateFile} {thisFile}""".format(thisFile=thisFile, templateFile=templateFile))                
    #thisBlock()
        
    return


####+BEGIN: bx:dblock:python:section :title "Lib Module Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Lib Module Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:cs:python:section :title "ICM-Commands: Common Encryption Facilities"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM-Commands: Common Encryption Facilities*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "genseed" :comment "Generates seed often used as salt" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<genseed>>  *Generates seed often used as salt*  =verify= argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class genseed(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """Generates seed often used as salt"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:


        choices = self.cmndArgsGet("0&1", cmndArgsSpecDict, argsList)

        allChoices=False
        if choices[0] == "all":
            allChoices=True        
            cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&1")
            argChoices = cmndArgsSpec.argChoicesGet()
            argChoices.pop(0)
            choices = argChoices


        opResult = list()
        opError = b.OpError.Success
        
        def processEachResult(eachChoice, eachResult):
            opResult.append(eachResult)
            if rtInv.outs:
                separator = ""
                choiceString = ""
                if allChoices:
                    separator = ":"
                    choiceString = eachChoice
                print(("""{eachChoice}{separator}{eachResult}"""
                      .format(eachChoice=choiceString, separator=separator, eachResult=eachResult)))

        salt = generate_seed()
        
        for eachChoice in choices:
            if eachChoice == "hex":
                eachResult = binascii.hexlify(bytearray(salt))
                processEachResult(eachChoice, eachResult)
                
            else:
                b_io.eh.problem_usageError(
                """Bad Choice: {eachChoice}"""
                    .format(eachChoice=eachChoice,))
                opError = icm.OpError.Fail

            hex_data = eachResult.decode("hex")

            #print(salt)
            #print(hex_data)
                
        return cmndOutcome.set(
            opError=opError,
            opResults=salt,
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
            argPosition="0&1",
            argName="choices",
            argDefault='all',
            argChoices=['all', 'hex',],
            argDescription="Output formats.",
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "genkey" :comment "" :parsMand "" :parsOpt "passwd seed" :argsMin 0 :argsMax 4 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<genkey>>  =verify= parsOpt=passwd seed argsMax=4 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class genkey(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'passwd', 'seed', ]
    cmndArgsLen = {'Min': 0, 'Max': 4,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             passwd: typing.Optional[str]=None,  # Cs Optional Param
             seed: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'passwd': passwd, 'seed': seed, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        passwd = csParam.mappedValue('passwd', passwd)
        seed = csParam.mappedValue('seed', seed)
####+END:
        choices = self.cmndArgsGet("0&4", cmndArgsSpecDict, argsList)

        allChoices=False
        if choices[0] == "all":
            allChoices=True        
            cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&4")
            argChoices = cmndArgsSpec.argChoicesGet()
            argChoices.pop(0)
            choices = argChoices


        opResult = list()
        opError = b.OpError.Success
        
        def processEachResult(eachChoice, eachResult):
            opResult.append(eachResult)
            if rtInv.outs:
                separator = ""
                choiceString = ""
                if allChoices:
                    separator = ":"
                    choiceString = eachChoice
                print(("""{eachChoice}{separator}{eachResult}"""
                      .format(eachChoice=choiceString, separator=separator, eachResult=eachResult)))

        key = generate_key()
        keyhex = binascii.hexlify(key)
        
        for eachChoice in choices:
            if eachChoice == "hex":
                eachResult = keyhex
                processEachResult(eachChoice, eachResult)
                
            elif eachChoice == "utf-8":
                eachResult = keyhex.decode('utf-8')
                processEachResult(eachChoice, eachResult)
                
            elif eachChoice == "base64":
                eachResult = base64.b64encode(key)
                processEachResult(eachChoice, eachResult)

            elif eachChoice == "base64url":
                # we will also print the base64url version which uses a few different 
                # characters so it can be used in an HTTP URL safely
                # '+' replaced by '-' and  '/'  replaced by '_' 
                # The padding characters == are sometime left off base64url

                eachResult = base64.urlsafe_b64encode(key)
                processEachResult(eachChoice, eachResult)
                
            else:
                b_io.eh.problem_usageError(
                """Bad Choice: {eachChoice}"""
                    .format(eachChoice=eachChoice,))
                opError = icm.OpError.Fail

                
        return cmndOutcome.set(
            opError=opError,
            opResults=opResult,
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
            argPosition="0&4",
            argName="choices",
            argDefault='all',
            argChoices=['all', 'hex', 'utf-8', 'base64', 'base64url',],
            argDescription="Output formats.",
        )

        return cmndArgsSpecDict



####+BEGIN: bx:cs:python:section :title "ICM-Commands: Encryption Policy"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM-Commands: Encryption Policy*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "listEncryptionPolicy" :comment "" :parsMand "rsrc" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<listEncryptionPolicy>>  =verify= parsMand=rsrc ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class listEncryptionPolicy(cs.Cmnd):
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

        if rsrc != "policy":
            return  b_io.eh.problem_usageError(
                "Bad Resource={rsrc}".format(rsrc=rsrc)
                )

        #
        # This is Temporary -- We should go to the Class and build path
        #
        
        outcome = icm.subProc_bash("""\
        ls ~/.ucrypt/policy"""
        ).log()
        if outcome.isProblematic(): return(io.eh.badOutcome(outcome))
        stdOut = outcome.stdout; stdErr = outcome.stderr; stdExit = outcome.error

        print(stdOut)
        
        return outcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "createEncryptionPolicy" :comment "" :parsMand "rsrc policy" :parsOpt "baseDir alg keyringPolicy" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<createEncryptionPolicy>>  =verify= parsMand=rsrc policy parsOpt=baseDir alg keyringPolicy ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class createEncryptionPolicy(cs.Cmnd):
    cmndParamsMandatory = [ 'rsrc', 'policy', ]
    cmndParamsOptional = [ 'baseDir', 'alg', 'keyringPolicy', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             rsrc: typing.Optional[str]=None,  # Cs Mandatory Param
             policy: typing.Optional[str]=None,  # Cs Mandatory Param
             baseDir: typing.Optional[str]=None,  # Cs Optional Param
             alg: typing.Optional[str]=None,  # Cs Optional Param
             keyringPolicy: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'rsrc': rsrc, 'policy': policy, 'baseDir': baseDir, 'alg': alg, 'keyringPolicy': keyringPolicy, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        rsrc = csParam.mappedValue('rsrc', rsrc)
        policy = csParam.mappedValue('policy', policy)
        baseDir = csParam.mappedValue('baseDir', baseDir)
        alg = csParam.mappedValue('alg', alg)
        keyringPolicy = csParam.mappedValue('keyringPolicy', keyringPolicy)
####+END:
        opError=b.OpError.Success

        if rsrc != "policy":
            return  b_io.eh.problem_usageError(
                "Bad Resource={rsrc}".format(rsrc=rsrc)
                )

        if not alg:
            alg="default"
        
        ucrypt = EncryptionPolicy(
            policy=policy,
            baseDir=baseDir,
            keyringPolicy=keyringPolicy,
            keyringAlg=alg,            
            alg=alg,
        )

        opError = ucrypt.policyKeyCreate()

        ucrypt.save()        

        return cmndOutcome.set(
            opError=opError,
            opResults=None,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "describeEncryptionPolicy" :comment "" :parsMand "rsrc" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<describeEncryptionPolicy>>  =verify= parsMand=rsrc ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class describeEncryptionPolicy(cs.Cmnd):
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

        policy=os.path.basename(rsrc)
            
        ucrypt = EncryptionPolicy(
            policy= policy,
        )

        ucrypt.load()

        clearHexKey = ucrypt.policyKeyGet()
        passwdFromKeyring = keyring.get_password("ucrypt", ucrypt.policy)

        with open(ucrypt.keyPath, 'r') as thisFile:
            encryptedHexKey = thisFile.read()
        
        
        print(("""\
keyringSystemName =ucrypt       # Class Variable
keyringBackend=default          # Class Variable
------------                    # Instance Variables
policy={policy}
policyPath={policyPath}
keyringPolicy={keyringPolicy}   # How are passwds created (e.g., prompt)
keyringAlg={keyringAlg}         # Key encryption algorithem
alg={alg}                       # clearText encryption algorithem
keyPath={keyPath}
pickleFile={pickleFile}
saltForEncryptionofKey={salt}
------------                    # Derived Information
passwdFromKeyring={passwdFromKeyring}
encryptedHexKey={encryptedHexKey}
clearHexKey={clearHexKey}\
"""
              .format(
                  policy=ucrypt.policy,
                  policyPath=ucrypt.policyPath,
                  keyringPolicy=ucrypt.keyringPolicy,
                  keyringAlg=ucrypt.keyringAlg,
                  alg=ucrypt.alg,
                  keyPath=ucrypt.keyPath,
                  pickleFile=ucrypt.pickleFile,
                  salt=binascii.hexlify(ucrypt.salt),
                  passwdFromKeyring=passwdFromKeyring,
                  encryptedHexKey=encryptedHexKey,
                  clearHexKey=clearHexKey,
              )
        ))

        return cmndOutcome.set(
            opError=opError,
            opResults=None,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "encrypt" :comment "Input is arg1 or inFile or stdin" :parsMand "rsrc" :parsOpt "inFile" :argsMin 0 :argsMax 1 :pyInv "clearText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<encrypt>>  *Input is arg1 or inFile or stdin*  =verify= parsMand=rsrc parsOpt=inFile argsMax=1 ro=cli pyInv=clearText   [[elisp:(org-cycle)][| ]]
#+end_org """
class encrypt(cs.Cmnd):
    cmndParamsMandatory = [ 'rsrc', ]
    cmndParamsOptional = [ 'inFile', ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             rsrc: typing.Optional[str]=None,  # Cs Mandatory Param
             inFile: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             clearText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """Input is arg1 or inFile or stdin"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'rsrc': rsrc, 'inFile': inFile, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        rsrc = csParam.mappedValue('rsrc', rsrc)
        inFile = csParam.mappedValue('inFile', inFile)
####+END:

        def readFromStdin():
            """Reads stdin. Returns a string. -- Uses mutable list."""
    
            msgAsList = []
            for line in sys.stdin:
                msgAsList.append(str(line))
                
            return (
                str("".join(msgAsList),)
            )
            
        def readFromFile(fileName):
            """Reads file. Returns an email msg object.  -- Uses mutable list."""
                
            return (
                open(fileName, 'r').read()
            )
        
        if not clearText:
            clearText = ""
            if effectiveArgsList:
                for each in effectiveArgsList:
                    clearText = clearText + each
                
            elif inFile:
                clearText = readFromFile(inFile)
            else:
                # Stdin then
                clearText = readFromStdin()

        b_io.tm.here("""clearText={clearText}""".format(clearText=clearText))
        b_io.tm.here("""rsrc={rsrc}""".format(rsrc=rsrc))

        policy=os.path.basename(rsrc)
            
        ucrypt = EncryptionPolicy(
            policy= policy,
        )

        ucrypt.load()

        cypherText = ucrypt.encrypt(clearText)

        if rtInv.outs:
            print(cypherText)
                
        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=cypherText,
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
            argPosition="0",
            argName="clearText",
            argDefault=None,
            argChoices=[ ],
            argDescription="Exec all or those specified as functions.",
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "decrypt" :comment "Input is arg1 or inFile or stdin" :parsMand "rsrc" :parsOpt "inFile" :argsMin 0 :argsMax 1 :pyInv "cipherText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<decrypt>>  *Input is arg1 or inFile or stdin*  =verify= parsMand=rsrc parsOpt=inFile argsMax=1 ro=cli pyInv=cipherText   [[elisp:(org-cycle)][| ]]
#+end_org """
class decrypt(cs.Cmnd):
    cmndParamsMandatory = [ 'rsrc', ]
    cmndParamsOptional = [ 'inFile', ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             rsrc: typing.Optional[str]=None,  # Cs Mandatory Param
             inFile: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             cipherText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """Input is arg1 or inFile or stdin"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'rsrc': rsrc, 'inFile': inFile, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        rsrc = csParam.mappedValue('rsrc', rsrc)
        inFile = csParam.mappedValue('inFile', inFile)
####+END:

        def readFromStdin():
            """Reads stdin. Returns a string. -- Uses mutable list."""
    
            msgAsList = []
            for line in sys.stdin:
                msgAsList.append(str(line))
                
            return (
                str("".join(msgAsList),)
            )
            
        def readFromFile(fileName):
                """Reads file. Returns an email msg object.  -- Uses mutable list."""
                
                return (
                    open(fileName, 'r').read()
                )
        
        if not cipherText:
            cipherText = ""
            if effectiveArgsList:
                for each in effectiveArgsList:
                    cipherText = cipherText + each
                
            elif inFile:
                cipherText = readFromFile(inFile)
            else:
                # Stdin then
                cipherText = readFromStdin()

        policy=os.path.basename(rsrc)
            
        ucrypt = EncryptionPolicy(
            policy= policy,
        )

        ucrypt.load()

        clearText = ucrypt.decrypt(cipherText)

        if rtInv.outs:
            print(("""{clearText}""".format(clearText=clearText)))
                
        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=clearText,
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
            argPosition="0",
            argName="cipherText",
            argDefault=None,
            argChoices=[ ],
            argDescription="Exec all or those specified as functions.",
        )

        return cmndArgsSpecDict


####+BEGIN: bx:cs:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:cs:python:func :funcName "generate_seed" :funcType "anyOrNone" :retType "binary" :deco "" :argsList "type=None size=None" :comment "Generates seed used as salt"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-anyOrNone :: /generate_seed/ =Generates seed used as salt= retType=binary argsList=(type=None size=None)  [[elisp:(org-cycle)][| ]]
"""
def generate_seed(
    type=None,
    size=None,
):
####+END:

    return (
        os.urandom(16)
        )


####+BEGIN: bx:cs:python:func :funcName "generate_key" :funcType "anyOrNone" :retType "binary" :deco "" :argsList "passwd=None salt=None" :comment "Create a new key or based on passwd"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-anyOrNone :: /generate_key/ =Create a new key or based on passwd= retType=binary argsList=(passwd=None salt=None)  [[elisp:(org-cycle)][| ]]
"""
def generate_key(
    passwd=None,
    salt=None,
):
####+END:
    """  Generate an AES key, 128 bits long """

    if not passwd:
        key = AESGCM.generate_key(bit_length=128)
    else:
        backend = default_backend()

        # derive
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=backend
        )

        key = kdf.derive(passwd.encode('utf-8'))

    return key


####+BEGIN: bx:cs:python:func :funcName "symEncrypt" :funcType "anyOrNone" :retType "cipherText" :deco "" :argsList "algorithm hexkey clearText" :comment "Symetric Encryption"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-anyOrNone :: /symEncrypt/ =Symetric Encryption= retType=cipherText argsList=(algorithm hexkey clearText)  [[elisp:(org-cycle)][| ]]
"""
def symEncrypt(
    algorithm,
    hexkey,
    clearText,
):
####+END:
    b_io.tm.here("Encryping ClearText -- Algorithm={}".format(algorithm))

    key_forsecrets = hexkey

    b_io.tm.here(key_forsecrets)

    secret = clearText

    b_io.tm.here(secret)
        
    encrypted_secret = None
    # Generate a random Nonce 12 bytes long
    nonce = os.urandom(12)
    aesgcm = AESGCM(binascii.unhexlify(key_forsecrets))
    extra_associated_data = None
    secret_bytes = secret.encode('utf-8')  # string to bytes
    encrypted_secret = aesgcm.encrypt(nonce, secret_bytes, extra_associated_data)
    # encrypted_secret has cipher text + a 16 byte tag appended to the end

    # We will prepend the nonce and turn to hex and decode from bytes to string
    encrypted_secret_withnonce_hex = binascii.hexlify(nonce + encrypted_secret).decode('utf-8')

    b_io.tm.here("nonce= [" + str(binascii.hexlify(nonce)) + "]")
    b_io.tm.here("encrypted_secret= [" + str(binascii.hexlify(encrypted_secret)) + "]")
    b_io.tm.here("encrypted_secret_withnonce_hex= [" + encrypted_secret_withnonce_hex + "]")
        
    return encrypted_secret_withnonce_hex



####+BEGIN: bx:cs:python:func :funcName "symDecrypt" :funcType "anyOrNone" :retType "clearText" :deco "" :argsList "algorithm key cipherText" :comment "Symetric Encryption"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Func-anyOrNone :: /symDecrypt/ =Symetric Encryption= retType=clearText argsList=(algorithm key cipherText)  [[elisp:(org-cycle)][| ]]
"""
def symDecrypt(
    algorithm,
    key,
    cipherText,
):
####+END:
    b_io.tm.here("Decrypting -- Algorithm={}".format(algorithm))

    key_forsecrets = key

    b_io.tm.here(cipherText)
        
    encrypted_secret = cipherText.strip()
    #encrypted_secret = cipherText

    # get the bytes instead of hex string
    encrypted_secret_bytes = binascii.unhexlify(encrypted_secret)
    #encrypted_secret_bytes = encrypted_secret.decode('hex')

    # we should receive 12 bytes nonce + encrypted data + 16 byte tag
    # Grab the 12 byte Nonce at the beginning
    nonce = encrypted_secret_bytes[:12]

    # Grab the the 16 byte tag at the end (but we don't need it)
    # tag = encrypted_secret_bytes[-16:]
    # if we wanted just the ciphertext
    # just_ciphertext = encrypted_secret_bytes[12:-16]

    # skip the first 12 bytes where the Nonce is
    encrypted_secret_bytes_plustag = encrypted_secret_bytes[12:]
    extra_associated_data = None
    aesgcm = AESGCM(binascii.unhexlify(key_forsecrets))
    secret_bytes = aesgcm.decrypt(nonce, encrypted_secret_bytes_plustag, extra_associated_data)

    b_io.tm.here(secret_bytes)
        
    return secret_bytes



####+BEGIN: b:py3:class/decl :className "EncryptionPolicy" :superClass "" :comment "" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]] [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(bx:orgm:indirectBufOther)][|>]] [[elisp:(bx:orgm:indirectBufMain)][|I]] [[elisp:(blee:ppmm:org-mode-toggle)][|N]] [[elisp:(org-top-overview)][|O]] [[elisp:(progn (org-shifttab) (org-content))][|C]] [[elisp:(delete-other-windows)][|1]]  Class-basic    :: /EncryptionPolicy/ object  [[elisp:(org-cycle)][| ]]
"""
class EncryptionPolicy(object):
####+END:
    """ policyKeyCreate() creates an encrypted key. encrypt() and decrypt() use the key through policyKeyGet(). 
    """

    saltAsHexStringObsolete = "597229074e499e5442994d3643a3e7f7"   # generated with os.urandom(16)
    #saltObsolete = saltAsHexStringObsolete.decode("hex")

    keyringSystemName = "ucrypt"
    keyringBackend = "default"

####+BEGIN: b:py3:cs:method/args :methodName "__init__" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "policy=None baseDir=None keyringPolicy=None keyringAlg=None alg=None"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /__init__/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(policy=None, baseDir=None, keyringPolicy=None, keyringAlg=None, alg=None, ):
####+END:
        """ 
        policy = (string) name of persistent directory.
        baseDir = (path) alternative to ~/.ucrypt.
        keyringPolicy = (enum) how to determine passwd that derives the key -- clear, samePlus, prompt, default
        keyringAlg = (enum) how to encrypt the key
        alg = (enum) how to encrypt clearText
        """
        if not baseDir:
            baseDir = os.path.expanduser("~/.ucrypt")
        else:
            baseDir = os.path.expanduser(baseDir)            
        

        policyBaseDir = os.path.join(baseDir, "policy")
            
        try:
            os.makedirs(policyBaseDir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        if not policy:
            b_io.eh.problem_usageError("")
            return

        policyPath =  os.path.join(policyBaseDir, policy)

        b_io.tm.here(policyPath)
            
        if not os.path.exists(policyPath):
            os.makedirs(policyPath)

        #
        # NOTYET, this is wrong -- it should be 
        #
        if alg == 'clear':
            keyPath =  os.path.join(policyPath, "clearKey")
        else:
            keyPath =  os.path.join(policyPath, "encryptedKey")

        pickleFile =  os.path.join(policyPath, "EncryptionPolicy.pickle")

        
        self.policyPath = policyPath
        self.policy = policy
        self.keyringPolicy = keyringPolicy
        self.keyringAlg = keyringAlg        
        self.alg = alg
        self.keyPath = keyPath   # fullPathName of where the key resides
        self.pickleFile = pickleFile  # fullPathName of where the pickleFile resides
        
        

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


####+BEGIN: b:py3:cs:method/args :methodName "_policyPasswdCreate" :methodType "anyOrNone" :retType "passwd string" :deco "default" :argsList "self passwd=None"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /_policyPasswdCreate/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def _policyPasswdCreate(self, passwd=None, ):
####+END:
        """ Sets policy as user in keyring. If passwd is provided, it is used otherwise created based on keyringPolicy.
"""

        serviceName = "ucrypt"
        userName = self.policy

        def samePlusPasswd(userName):
            return (
                "ucrypt-" + userName
                )

        if not passwd:
            
            if self.keyringPolicy == "clear":
                passwd = "clear"
            elif self.keyringPolicy == "default":
                passwd = samePlusPasswd(userName)
            elif self.keyringPolicy == "samePlus":
                passwd = samePlusPasswd(userName)
            elif self.keyringPolicy == "prompt":
                # Prompt for password
                passwd = getpass.getpass()
            else:
                return (
                    b_io.eh.problem_usageError("Bad keyringPolicy={}".format(self.keyringPolicy))
                )
            
        keyring.set_password(serviceName, userName, passwd)
        keyringPasswd = keyring.get_password(serviceName, userName)

        b_io.tm.here(keyringPasswd)
        
        return keyringPasswd

    

####+BEGIN: b:py3:cs:method/args :methodName "_policyPasswdGet" :methodType "anyOrNone" :retType "passwd string" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /_policyPasswdGet/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def _policyPasswdGet(self, ):
####+END:
        """ Return passwd string from keyring.
"""

        serviceName = "ucrypt"
        userName = self.policy

        keyringPasswd = keyring.get_password(serviceName, userName)

        return keyringPasswd

    
####+BEGIN: b:py3:cs:method/args :methodName "_ucryptSaltGet" :methodType "anyOrNone" :retType "binary" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /_ucryptSaltGet/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def _ucryptSaltGet(self, ):
####+END:
        """ Return a 16 byte number."""
        #return self.__class__.salt
        return self.salt        


####+BEGIN: b:py3:cs:method/args :methodName "_hexkeyForPolicyKeyEncryption" :methodType "anyOrNone" :retType "hex string" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /_hexkeyForPolicyKeyEncryption/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def _hexkeyForPolicyKeyEncryption(self, ):
####+END:
        """ Get salt, get passwd, create keyForPolicyKeyEncryption.

 # https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/

"""

        salt = self._ucryptSaltGet()
        
        passwd = self._policyPasswdGet()

        key = generate_key(
            passwd=passwd,
            salt=salt,
            )

        return binascii.hexlify(key)

    
####+BEGIN: b:py3:cs:method/args :methodName "_policyKeyEncrypt" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self hexkeyForPolicyKeyEncryption clearKey"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /_policyKeyEncrypt/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def _policyKeyEncrypt(self, hexkeyForPolicyKeyEncryption, clearKey, ):
####+END:
        """ Encrypt the key.
"""

        cipherText = symEncrypt(
            self.keyringAlg,
            hexkeyForPolicyKeyEncryption,
            clearKey,
        )

        return cipherText

####+BEGIN: b:py3:cs:method/args :methodName "_policyKeyDecrypt" :methodType "anyOrNone" :retType "clearText" :deco "default" :argsList "self hexkeyForPolicyKeyEncryption encryptedKey"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /_policyKeyDecrypt/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def _policyKeyDecrypt(self, hexkeyForPolicyKeyEncryption, encryptedKey, ):
####+END:
        """ Decrypt the key.
"""

        clearText = symDecrypt(
            self.keyringAlg,
            hexkeyForPolicyKeyEncryption,
            encryptedKey,
        )

        return clearText

        
    
####+BEGIN: b:py3:cs:method/args :methodName "policyKeyCreate" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /policyKeyCreate/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def policyKeyCreate(self, ):
####+END:
        """ If policy directory and file exist do nothing. 
 - Use baseDir to create policy
 - based on 
 - Use genkey to create key.
 - Encrypt key with passwd of policy domain
 - store encrypted key
"""

        b_io.tm.here("{policyPath} -- {policy} {keyPath}".format(policyPath=self.policyPath, policy=self.policy,  keyPath=self.keyPath))

        if not os.path.exists(self.policyPath):
            b_io.eh.critical_oops("Missing {policyPath}".format(policyPath=self.policyPath))
            return

        if not self.policy:
            b_io.eh.critical_oops("Missing {policy}".format(policy=self.policy))
            return

        
        keyPath = self.keyPath

        if os.path.exists(keyPath):
            b_io.tm.here("EXISTS: {keyPath}".format(keyPath=self.keyPath))        
            return

        b_io.tm.here("CREATING: {policyPath} -- {policy} {keyPath}".format(policyPath=self.policyPath, policy=self.policy,  keyPath=self.keyPath))        


        outcome = genkey().cmnd(
             interactive=False,
             argsList=['hex'],
        )
        
        results = outcome.results
        clearKey = results[0]


        b_io.tm.here(clearKey)

        self.salt = generate_seed()

        if self.keyringAlg == 'clear':
            self._policyPasswdCreate(
                passwd='clear'
            )
            with open(keyPath, 'w') as thisFile:
                thisFile.write(clearKey)
            return
        
        elif self.keyringAlg == 'default':
            self._policyPasswdCreate()

            hexkeyForPolicyKeyEncryption = self._hexkeyForPolicyKeyEncryption()

            encryptedKey = self._policyKeyEncrypt(
                hexkeyForPolicyKeyEncryption,
                clearKey,
            )
            with open(keyPath, 'w') as thisFile:
                thisFile.write(encryptedKey)

            return
        
        else:
            return (
                b_io.eh.problem_usageError("bad keyringAlg={}".format(self.keyringAlg))
            )


####+BEGIN: b:py3:cs:method/args :methodName "policyKeyGet" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /policyKeyGet/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def policyKeyGet(self, ):
####+END:
        """ If directory and file exist do nothing. 
 - Read encryptedKey
 - Read keyring passwd
 - Get Salt
 - Create Key For Decription Of Key from 
 - decode encryotedKey with keyring passwd
"""
        if not os.path.exists(self.policyPath):
            b_io.eh.critical_oops("Missing {policyPath}".format(policyPath=self.policyPath))
            return

        if not self.policy:
            b_io.eh.critical_oops("Missing {policy}".format(policy=self.policy))
            return

        keyPath = self.keyPath
        b_io.tm.here(keyPath)
        

        if self.keyringAlg == 'clear':
            with open(keyPath, 'r') as thisFile:
                clearKey = thisFile.read()
            b_io.tm.here(clearKey)                
            return clearKey

        elif self.keyringAlg == 'default':
            with open(keyPath, 'r') as thisFile:
                encryptedKey = thisFile.read()
            b_io.tm.here(encryptedKey)

            hexkeyForPolicyKeyEncryption = self._hexkeyForPolicyKeyEncryption()

            clearKey = self._policyKeyDecrypt(
                hexkeyForPolicyKeyEncryption,
                encryptedKey,
            )
            
            return clearKey

        else:
            return (
                b_io.eh.problem_usageError("bad keyringAlg={}".format(self.keyringAlg))
            )

        

####+BEGIN: b:py3:cs:method/args :methodName "encrypt" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self clearText"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /encrypt/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def encrypt(self, clearText, ):
####+END:
        """ 
 - Make sure policy exists as directory. 
 - Get encrypted key.
 - Decrypt the key.
 - encrypt clearText with that key.
"""
        return (
            symEncrypt(
                self.alg,
                self.policyKeyGet(),
                clearText,
            )
        )

    
####+BEGIN: b:py3:cs:method/args :methodName "decrypt" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self cipherText"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /decrypt/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def decrypt(self, cipherText, ):
####+END:
        """ If directory and file exist do nothing. 
 - Get key.
 - decrypt with that key
"""
        return (
            symDecrypt(
                self.alg,
                self.policyKeyGet(),
                cipherText,
            )
        )





####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :title " ~End Of Editable Text~ "
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
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
