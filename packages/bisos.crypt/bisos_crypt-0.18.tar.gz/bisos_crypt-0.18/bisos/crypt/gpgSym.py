# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for creating and managing symetric gpg  encryption/decryption.
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
** This File: /bisos/git/bxRepos/bisos-pip/crypt/py3/bisos/crypt/gpgSym.py
** File True Name: /bisos/git/auth/bxRepos/bisos-pip/crypt/py3/bisos/crypt/gpgSym.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['gpgSym'], }
csInfo['version'] = '202511025105'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'gpgSym-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos.crypt/_nodeBase_/fullUsagePanel-en.org][PyFwrk bisos.crypt Panel]]
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
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:

import sys
import collections
import gnupg

import ast
import tempfile
import os
from pathlib import Path


####+BEGIN: bx:cs:py3:section :title "Common Parameters Specification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common Parameters Specification*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:cs:python:func :funcName "commonParamsSpecify" :funcType "ParSpec" :retType "" :deco "" :argsList "csParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-ParSpec  [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ retType= argsList=(csParams)  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    csParams,
):
####+END:
    csParams.parDictAdd(
        parName='gpgTextOut',
        parDescription="In GPG Maps to armor -- Deciding on text or bin output",
        parDataType=None,
        parDefault='True',
        parChoices=["True", "False"],
        # parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--gpgTextOut',
    )
    csParams.parDictAdd(
        parName='outFile',
        parDescription="NOTYET",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--outFile',
    )



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples_csu" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples_csu>>  =verify= ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples_csu(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Basic example command.
        #+end_org """)

        self.captureRunStr(""" #+begin_org
*** Run Results
#+begin_src sh :results output :session shared
facterModule.cs -i examples
#+end_src
        #+end_org """)

        def cpsInit(): return collections.OrderedDict()
        od = collections.OrderedDict
        cmnd = cs.examples.cmndEnter
        literal = cs.examples.execInsert

        #  -v 1 --callTrackings monitor+ --callTrackings invoke+
        pars_debug_verbosity = od([('verbosity', "1"),])
        pars_debug_monitor = od([('callTrackings', "monitor+"),])
        pars_debug_invoke = od([('callTrackings', "invoke+"),])
        pars_debug_full = (pars_debug_verbosity | pars_debug_monitor | pars_debug_invoke)

        passwd = "MISSING"

        if pyKwArgs:
            if pyKwArgs.get('passwd'):
                passwd =  pyKwArgs['passwd']
            else:
                return failed(cmndOutcome)
        else:
            return failed(cmndOutcome)

        pars_passwd = od([('passwd', passwd),])
        pars_gpgTextOutFalse = od([('gpgTextOut', 'False'),])

        clearFile = "/tmp/gpgSymEx1"
        cipherFile = "/tmp/gpgSymEx1.gpg"

        outFileClear = "/tmp/gpgSymEx1.tar.gz"
        pars_outFileClear = od([('outFile', outFileClear),])

        outFileCipher = "/tmp/gpgSymEx1.tar.gz.gpg"
        pars_outFileCipher = od([('outFile', outFileCipher),])

        outFileElf = "/tmp/gpgSymEx1.tar.gz.gpg.elf"
        pars_outFileElf= od([('outFile', outFileElf),])

        cs.examples.menuSection('*GPG Symmetric Encryption*')
        
        literal(f"""cp /etc/motd {clearFile}""")

        cmnd('gpg_symEncrypt', pars=(pars_passwd), args=f"{clearFile}")
        cmnd('gpg_symEncrypt', pars=(pars_passwd | pars_gpgTextOutFalse), args=f"{clearFile}")        

        cmnd('gpg_symEncrypt', pars=(pars_passwd), args="",
             wrapper="echo HereComes Some ClearText | ",)
        cmnd('gpg_symEncrypt', pars=(pars_passwd | pars_gpgTextOutFalse), args="",
             wrapper="echo HereComes Some ClearText | ",)

        cs.examples.menuSection('*GPG Symmetric Decryption*')

        cmnd('gpg_symDecrypt', pars=(pars_passwd), args=f"{cipherFile}")
        cmnd('gpg_symDecrypt', pars=(pars_passwd | pars_outFileClear), args=f"{cipherFile}")

        cmnd('gpg_symDecrypt', pars=(pars_passwd), args="",
             wrapper=f"cat {cipherFile} | ",)

        cs.examples.menuSection('*GPG Symmetric Encryption and Decryption*')

        def cmndStdinEncrypt(cmndName): # type: ignore
            icmWrapper = "echo HereComes Some ClearText | "
            cps = cpsInit() ; cps['passwd'] = passwd ; cmndArgs = ""
            return cs.examples.csCmndLine(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)
        encryptCmndStr = cmndStdinEncrypt("gpg_symEncrypt")
        # print(f"TTT{encryptCmndStr}")

        cmnd('gpg_symDecrypt', pars=(pars_passwd), args="",
             wrapper=f"{encryptCmndStr} | ",)


        cs.examples.menuSection('*GPG Symmetric Encryption Of BaseDirs*')
        
        cmnd('gpg_symEncrypt_baseDirs', pars=(pars_passwd | pars_outFileCipher | pars_gpgTextOutFalse), args=".")
        cmnd('gpg_symEncrypt_baseDirs_elfbin', pars=(pars_passwd | pars_outFileElf | pars_gpgTextOutFalse), args=".")

        cs.examples.menuSection('*GPG Symmetric Decryption of .tar.gz*')

        # cmnd('gpg_symDecrypt', pars=(pars_passwd), args=f"{cipherFile}")
        cmnd('gpg_symDecrypt', pars=(pars_passwd | pars_outFileClear ), args=f"{outFileCipher}")
        cmnd('gpg_symDecrypt_elfbin', pars=(pars_passwd | pars_outFileClear ), args=f"{outFileElf}")


        # cs.examples.menuChapter('*GPG Commands*')

        # literal(f"""sudo apt -y install gnupg""")
        # literal(f"""gpg --list-key  # Includes keyId""")
        # literal(f"""env | grep -i gpg""")
        # literal(f"""gpg --send-key [keyId]""")
        # literal(f"""gpg -e -r first.last@example.com -o /bxo/usg/bystar/.password-store/anotherVar.gpg --quiet --yes --compress-algo=none --no-encrypt-to""")
        # literal(f"""gpg -d --quiet --yes --compress-algo=none --no-encrypt-to /bxo/usg/bystar/.password-store/myPass.gpg""")

        return(cmndOutcome)



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples_seed" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples_seed>>  =verify= ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples_seed(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  pyKwArgs 'upload' is mandatory
        #+end_org """)

        return(cmndOutcome)


####+BEGIN: b:py3:class/decl :className "GpgSym" :superClass "object" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /GpgSym/  superClass=object  [[elisp:(org-cycle)][| ]]
#+end_org """
class GpgSym(object):
####+END:
    """ #+begin_org
** This is really a namespace not a class. All methods are static.
    #+end_org """

####+BEGIN: b:py3:cs:method/typing :methodName "__init__" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /__init__/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(
####+END:
            self,
            alg=""
    ):
        self.alg = alg  # Unused, placeholder

####+BEGIN: b:py3:cs:method/typing :methodName "encryptBytes" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /encryptBytes/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def encryptBytes(
####+END:
            clearText: str,
            symKey: str,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]] Returns gpgOutcome. Usage: cipheredText = gpgOutcome.data
        #+end_org """

        gpg = gnupg.GPG()

        #
        # This is the interface to python-gnupg-0.5.4 package
        # Which is very different from gnupg package.
        # Make sure that you are using pip install python-gnupg
        #
        gpgOutcome = gpg.encrypt(
            clearText,
            recipients=None,
            symmetric='AES256',
            passphrase=symKey,
            #armor=False,
        )
        #cipheredText = gpgOutcome.data
        return gpgOutcome

####+BEGIN: b:py3:cs:method/typing :methodName "decryptBytes" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /decryptBytes/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def decryptBytes(
####+END:
            cipherText: str,
            symKey: str,
            armor: bool=True,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]] Returns gpgOutcome. Usage: clearText = gpgOutcome.data
        #+end_org """

        gpg = gnupg.GPG()

        gpgOutcome = gpg.decrypt(
            cipherText,
            passphrase=symKey,
            armor=armor,
        )
        #clearText = gpgOutcome.data
        return gpgOutcome

####+BEGIN: b:py3:cs:method/typing :methodName "encryptFile" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /encryptFile/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def encryptFile(
####+END:
            clearFilePath: str,
            symKey: str,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]] Returns gpgOutcome. Usage: cipheredText = gpgOutcome.data
        #+end_org """

        gpg = gnupg.GPG()

        with open(clearFilePath, "rb") as fileObj:
            gpgOutcome = gpg.encrypt_file(
                fileObj,
                recipients=None,
                symmetric='AES256',
                passphrase=symKey,
                #armor=False,
                output=f"{clearFilePath}.gpg"
            )
            b_io.tm.here(f"""Processed File={clearFilePath}""")

            return gpgOutcome

####+BEGIN: b:py3:cs:method/typing :methodName "decryptFile" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /decryptFile/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def decryptFile(
####+END:
            cipherFilePath: str,
            symKey: str,
            output: str | None=None,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]] Returns gpgOutcome. Usage: clearText = gpgOutcome.data
        #+end_org """

        gpg = gnupg.GPG()

        with open(cipherFilePath, "rb") as fileObj:
            gpgOutcome = gpg.decrypt_file(
                fileObj,
                passphrase=symKey,
                output=output,
                #armor=False,
            )
        # NOTYET, write the clean text
        return gpgOutcome

    
####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:cs:py3:section :title "Primary Command Services"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Primary Command Services*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpgSymEncryptDecyptExample" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpgSymEncryptDecyptExample>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpgSymEncryptDecyptExample(cs.Cmnd):
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
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] A simple example showing encrpyt and decrypt.
        #+end_org """)

        gpg = gnupg.GPG()
        data = 'the quick brown fow jumps over the laxy dog.'
        passphrase='12345'
        crypt = gpg.encrypt(
            data,
            recipients=None,
            symmetric='AES256',
            passphrase=passphrase,
            armor=False,
        )
        print(crypt.data)

        clear = gpg.decrypt(
            crypt.data,
            passphrase=passphrase,
        )

        print(clear)

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpg_symEncrypt" :comment "stdin as clearText" :parsMand "passwd" :parsOpt "gpgTextOut" :argsMin 0 :argsMax 9999 :pyInv "clearText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpg_symEncrypt>>  *stdin as clearText*  =verify= parsMand=passwd parsOpt=gpgTextOut argsMax=9999 ro=cli pyInv=clearText   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpg_symEncrypt(cs.Cmnd):
    cmndParamsMandatory = [ 'passwd', ]
    cmndParamsOptional = [ 'gpgTextOut', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
             gpgTextOut: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             clearText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as clearText"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'passwd': passwd, 'gpgTextOut': gpgTextOut, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        passwd = csParam.mappedValue('passwd', passwd)
        gpgTextOut = csParam.mappedValue('gpgTextOut', gpgTextOut)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        gpg = gnupg.GPG()

        results = []

        cmndArgs = self.cmndArgsGet("0&9999", self.cmndArgsSpec(), argsList)

        gpgTextOut_pyLit = ast.literal_eval(gpgTextOut) if gpgTextOut is not None else True   

        filesProcessed = False
        for each in typing.cast(list, cmndArgs):
            filesProcessed = True
            with open(each, "rb") as fileObj:
                gpgStatus = gpg.encrypt_file(
                    fileObj,
                    recipients=None,
                    symmetric='AES256',
                    passphrase=passwd,
                    armor=gpgTextOut_pyLit,
                    output=f"{each}.gpg"
                )
                b_io.tm.here(f"""Processed File={each}""")
                results.append(f"{each}.gpg")

        if not clearText:
            clearText = b_io.stdin.read()

        if not clearText and not filesProcessed:
            b_io.eh.problem_usageError(f"noFiles and no clearText")
            return cmndOutcome

        if clearText:
            gpgStatus = gpg.encrypt(
                clearText,
                recipients=None,
                symmetric='AES256',
                passphrase=passwd,
                armor=gpgTextOut_pyLit,
            )

            cipheredText = gpgStatus.data

            b_io.tm.here(f"""clearText={clearText}""")
            b_io.tm.here(f"""cipheredText={cipheredText}""")

            sys.stdout.buffer.write(cipheredText)  # print does not work.

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=results,
        )

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]]
        #+end_org """
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpg_symDecrypt" :extent "verify" :comment "stdin as cipherText" :parsMand "passwd" :parsOpt "outFile" :argsMin 0 :argsMax 9999 :pyInv "cipherText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpg_symDecrypt>>  *stdin as cipherText*  =verify= parsMand=passwd parsOpt=outFile argsMax=9999 ro=cli pyInv=cipherText   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpg_symDecrypt(cs.Cmnd):
    cmndParamsMandatory = [ 'passwd', ]
    cmndParamsOptional = [ 'outFile', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
             outFile: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             cipherText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as cipherText"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'passwd': passwd, 'outFile': outFile, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        passwd = csParam.mappedValue('passwd', passwd)
        outFile = csParam.mappedValue('outFile', outFile)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        gpg = gnupg.GPG()

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        result = []

        if outFile:
            if len(cmndArgs) != 1:
                b_io.eh.problem_usageError(f"outFile={outFile} was specified but not just one cmndArgs")
                return cmndOutcome

        filesProcessed = False
        for each in typing.cast(list, cmndArgs):
            filesProcessed = True
            # print(f"outFile={outFile} each={each}")
            with open(each, "rb") as fileObj:
                gpgStatus = gpg.decrypt_file(
                    fileObj,
                    passphrase=passwd,
                    output=outFile
                )

        if not cipherText:
            cipherText = b_io.stdin.read()

        if not cipherText and not filesProcessed:
            b_io.eh.problem_usageError(f"noFiles and no cipheredText")
            return cmndOutcome

        if cipherText:
            gpgStatus = gpg.decrypt(
                cipherText,
                passphrase=passwd,
                #armor=False,
            )

            clearText = gpgStatus.data

            b_io.tm.here(f"""clearText={clearText}""")
            b_io.tm.here(f"""cipheredText={cipherText}""")

            sys.stdout.buffer.write(clearText)  # print does not work.

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
        """  #+begin_org
** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]]
        #+end_org """
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpg_symEncrypt_baseDirs" :comment "outFile is encrypted compressed tar file" :parsMand "passwd" :parsOpt "gpgTextOut outFile" :argsMin 0 :argsMax 9999 :pyInv "clearText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpg_symEncrypt_baseDirs>>  *stdin as clearText*  =verify= parsMand=passwd outFile parsOpt=gpgTextOut argsMax=9999 ro=cli pyInv=clearText   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpg_symEncrypt_baseDirs(cs.Cmnd):
    cmndParamsMandatory = [ 'passwd', 'outFile', ]
    cmndParamsOptional = [ 'gpgTextOut', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
             outFile: typing.Optional[str]=None,  # Cs Mandatory Param
             gpgTextOut: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             clearText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as clearText"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'passwd': passwd, 'outFile': outFile, 'gpgTextOut': gpgTextOut, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        passwd = csParam.mappedValue('passwd', passwd)
        outFile = csParam.mappedValue('outFile', outFile)
        gpgTextOut = csParam.mappedValue('gpgTextOut', gpgTextOut)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)


        cmndArgs = self.cmndArgsGet("0&9999", self.cmndArgsSpec(), argsList)
        cmndArgsStr = " ".join(typing.cast(list, cmndArgs))

        gpgTextOut_pyLit = ast.literal_eval(gpgTextOut) if gpgTextOut is not None else True

        fd, path = tempfile.mkstemp(suffix=".tgz", prefix="gpgSym_")


        if b.subProc.Op(outcome=cmndOutcome, log=1).bash(
                f"""\
tar --exclude-vcs -czf {path} {cmndArgsStr}\
"""
        ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))

        if not (result := gpg_symEncrypt(cmndOutcome=cmndOutcome).pyCmnd(
                passwd=passwd,
                gpgTextOut=gpgTextOut,
                argsList=[path],
        ).results): return(b_io.eh.badOutcome(cmndOutcome))

        if outFile:
            # result[0] is the generated encrypted tar file; rename it to the
            # value provided by the caller in `outFile` and update the results
            src = result[0]
            try:
                src_path = Path(src)
                dest_path = Path(outFile)
                # use Path.replace to atomically move/replace
                src_path.replace(dest_path)
                # replace the entry in result list to reflect new name
                result[0] = str(dest_path)
                b_io.tm.here(f"Renamed {src} -> {outFile}")
            except Exception as e:
                b_io.eh.problem_runtimeError(f"Failed to move {src} to {outFile}: {e}")
                return b_io.eh.badOutcome(cmndOutcome)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=result,
        )

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]]
        #+end_org """
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpg_symEncrypt_baseDirs_elfbin" :comment "outFile is in elf-bin format" :parsMand "passwd outFile" :parsOpt "gpgTextOut" :argsMin 0 :argsMax 9999 :pyInv "clearText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpg_symEncrypt_baseDirs_elfbin>>  *outFile is in elf-bin format*  =verify= parsMand=passwd outFile parsOpt=gpgTextOut argsMax=9999 ro=cli pyInv=clearText   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpg_symEncrypt_baseDirs_elfbin(cs.Cmnd):
    cmndParamsMandatory = [ 'passwd', 'outFile', ]
    cmndParamsOptional = [ 'gpgTextOut', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
             outFile: typing.Optional[str]=None,  # Cs Mandatory Param
             gpgTextOut: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             clearText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """outFile is in elf-bin format"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'passwd': passwd, 'outFile': outFile, 'gpgTextOut': gpgTextOut, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        passwd = csParam.mappedValue('passwd', passwd)
        outFile = csParam.mappedValue('outFile', outFile)
        gpgTextOut = csParam.mappedValue('gpgTextOut', gpgTextOut)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        cmndArgs = self.cmndArgsGet("0&9999", self.cmndArgsSpec(), argsList)
        cmndArgsStr = " ".join(typing.cast(list, cmndArgs))

        if not (result := gpg_symEncrypt_baseDirs(cmndOutcome=cmndOutcome).pyCmnd(
                passwd=passwd,
                gpgTextOut=gpgTextOut,
                argsList=[cmndArgsStr],
        ).results): return(b_io.eh.badOutcome(cmndOutcome))


        if b.subProc.Op(outcome=cmndOutcome, log=1).bash(
                f"""\
elfbin.cs --elfFile="{outFile}" --inDataFile={result[0]}  -i dataInElf\
"""
        ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=outFile,
        )

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]]
        #+end_org """
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpg_symEncrypt_baseDirs_elfbin" :comment "outFile is in elf-bin format" :parsMand "passwd outFile" :parsOpt "gpgTextOut" :argsMin 0 :argsMax 9999 :pyInv "clearText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpg_symEncrypt_baseDirs_elfbin>>  *outFile is in elf-bin format*  =verify= parsMand=passwd outFile parsOpt=gpgTextOut argsMax=9999 ro=cli pyInv=clearText   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpg_symDecrypt_elfbin(cs.Cmnd):
    cmndParamsMandatory = [ 'passwd', 'outFile', ]
    cmndParamsOptional = [ 'gpgTextOut', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
             outFile: typing.Optional[str]=None,  # Cs Mandatory Param
             gpgTextOut: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             clearText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """outFile is in elf-bin format"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'passwd': passwd, 'outFile': outFile, 'gpgTextOut': gpgTextOut, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        passwd = csParam.mappedValue('passwd', passwd)
        outFile = csParam.mappedValue('outFile', outFile)
        gpgTextOut = csParam.mappedValue('gpgTextOut', gpgTextOut)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        cmndArg = self.cmndArgsGet("0", self.cmndArgsSpec(), argsList)

        fd, path = tempfile.mkstemp(suffix=".gpg", prefix="gpgSym_")


        if b.subProc.Op(outcome=cmndOutcome, log=1).bash(
                f"""\
elfbin.cs --elfFile="{cmndArg}" --outDataFile="{path}"  -i dataOutElf\
"""
        ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))

        gpg_symDecrypt(cmndOutcome=cmndOutcome).pyCmnd(
                passwd=passwd,
                outFile=outFile,
                argsList=[path],
        )

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=outFile,
        )

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]]
        #+end_org """
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&1",
            argName="cmndArg",
            argChoices=[],
            argDescription="CmndArg To Be Processed."
        )

        return cmndArgsSpecDict





####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
