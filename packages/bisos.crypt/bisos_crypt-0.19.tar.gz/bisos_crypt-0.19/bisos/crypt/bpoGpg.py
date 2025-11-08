# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for creating and managing BPO's gpg and encryption/decryption.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, b-lib, pyLibPure
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/crypt/py3/bisos/crypt/bpoGpg.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['bpoGpg'], }
csInfo['version'] = '202210043620'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'bpoGpg-Panel.org'
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
import sys
#import select

# import pwd
# import grp
# import collections
# import enum
#

#import traceback

import collections

import pathlib

# from bisos.platform import bxPlatformConfig
# from bisos.platform import bxPlatformThis

# from bisos.basics import pattern

from bisos.bpo import bpo
#from bisos.pals import palsSis
#NOTYET from bis os.icm import fpath

from bisos import b
from bisos.b import cs
from bisos.b import b_io

import gnupg

#import logging

#import shutil

import pykeepass_cache
import pykeepass

####+BEGIN: b:py3:class/decl :className "BpoGpg" :superClass "object" :comment "Run Bases of a Bpo" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /BpoGpg/  superClass=object =Run Bases of a Bpo=  [[elisp:(org-cycle)][| ]]
#+end_org """
class BpoGpg(object):
####+END:
    """
** Abstraction of the Gpgs of BPOs (ByStar Portable Object)
"""
####+BEGIN: b:py3:cs:method/typing :methodName "__init__" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /__init__/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(
####+END:
            self,
            bpoId,
    ):
        self.bpoId = bpoId
        self.bpo = bpo.EffectiveBpos.givenBpoIdObtainBpo(bpoId, bpo.Bpo)

####+BEGIN: b:py3:cs:method/typing :methodName "repoBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /repoBasePath_obtain/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def repoBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        """ #+begin_org
*** TODO [[elisp:(org-cycle)][| *MethodDesc:* | ]] Rename vault, vaults ---  Confirm that ~bpoGpgsBaseDir~ exists and return that.
        #+end_org """

        bpoGpgsBaseDir = pathlib.Path(
            os.path.join(
                self.bpo.bpoBaseDir,
                'gpgKeys',
            )
        )
        if not os.path.isdir(bpoGpgsBaseDir):
            bpoGpgsBaseDir.mkdir(parents=True, exist_ok=True)

        return bpoGpgsBaseDir

####+BEGIN: b:py3:cs:method/typing :methodName "keysFilePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /keysFilePath_obtain/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def keysFilePath_obtain(
####+END:
            self,
            gpgBaseName,
    ) -> pathlib.Path:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]]  Based on =vault= create BPO's {vault}.kdbx. Return that path.
        #+end_org """

        repoBase = self.repoBasePath_obtain()

        gpgBaseDir = pathlib.Path(
            os.path.join(
                repoBase,
                gpgBaseName,
            )
        )

        if not os.path.isdir(gpgBaseDir):
            gpgBaseDir.mkdir(parents=True, exist_ok=True)

        return gpgBaseDir


####+BEGIN: b:py3:cs:method/typing :methodName "pkcsFileEncript" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /pkcsFileEncript/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def pkcsFileEncript(
####+END:
            self,
            gpgFileName,
            nameEmail,
            passphrase,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Generate Key.
        #+end_org """
        keysBaseDir = self.keysFilePath_obtain(gpgFileName,)

        gpg = gnupg.GPG(gnupghome=keysBaseDir)
        # generate key
        input_data = gpg.gen_key_input(
            name_email=nameEmail,
            passphrase=passphrase,
        )
        key = gpg.gen_key(input_data)
        print(key)


####+BEGIN: b:py3:cs:method/typing :methodName "pkcsEncryptFile" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /pkcsEncryptFile/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def pkcsEncryptFile(
####+END:
            self,
            gpgFileName,
            nameEmail,
            passphrase,
            fileObj,
            output,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Generate Key.
        #+end_org """
        keysBaseDir = self.keysFilePath_obtain(gpgFileName,)

        gpg = gnupg.GPG(gnupghome=keysBaseDir)

        status = gpg.encrypt_file(
            fileObj,
            recipients=[nameEmail],
            passphrase=passphrase,
            output=output,
        )
        print("ok: ", status.ok)
        print("status: ", status.status)
        print("stderr: ", status.stderr)

####+BEGIN: b:py3:cs:method/typing :methodName "pkcsEncrypt" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /pkcsEncrypt/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def pkcsEncrypt(
####+END:
            self,
            keysBase,
            keyName,
            passphrase,
            data,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Generate Key.
        #+end_org """

        keysBaseDir = self.keysFilePath_obtain(keysBase,)

        gpg = gnupg.GPG(gnupghome=keysBaseDir)

        status = gpg.encrypt(
            data,
            recipients=[keyName],
            passphrase=passphrase,
        )
        b_io.tm.here(f"ok: {status.ok}")
        b_io.tm.here(f"status: {status.status}")
        b_io.tm.here(f"stderr: {status.stderr}")
        b_io.tm.here(f"data: {status.data}")

        return status

####+BEGIN: b:py3:cs:method/typing :methodName "pkcsDecryptFile" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /pkcsDecryptFile/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def pkcsDecryptFile(
####+END:
            self,
            gpgFileName,
            fileObj,
            output,
            passphrase,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Generate Key.
        #+end_org """
        keysBaseDir = self.keysFilePath_obtain(gpgFileName,)

        gpg = gnupg.GPG(gnupghome=keysBaseDir)

        status = gpg.decrypt_file(
            fileObj,
            passphrase=passphrase,
            output=output,
        )
        print("ok: ", status.ok)
        print("status: ", status.status)
        print("stderr: ", status.stderr)

        return status

####+BEGIN: b:py3:cs:method/typing :methodName "pkcsDecrypt" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /pkcsDecrypt/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def pkcsDecrypt(
####+END:
            self,
            keysBase,
            passphrase,
            data,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Generate Key.
        #+end_org """
        keysBaseDir = self.keysFilePath_obtain(keysBase,)

        gpg = gnupg.GPG(gnupghome=keysBaseDir)

        print(data)

        status = gpg.decrypt(
            data,
            passphrase=passphrase,
        )
        print("ok: ", status.ok)
        print("status: ", status.status)
        print("stderr: ", status.stderr)
        print("data: ", status.data)

        return status


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
        parName='keysBase',
        parDescription="NOTYET",
        parDataType=None,
        parDefault='bisos',
        parChoices=["any"],
        # parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--keysBase',
    )
    csParams.parDictAdd(
        parName='keyName',
        parDescription="NOTYET",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--keyName',
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



####+BEGIN: bx:cs:py3:section :title "CS-Lib Examples"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Lib Examples*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: bx:dblock:python:func :funcName "examples_bpo_gpg" :comment "Show/Verify/Update For relevant PBDs" :funcType "examples" :retType "none" :deco "" :argsList "bpoId keysBase keyName passwd sectionTitle=None"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-examples [[elisp:(outline-show-subtree+toggle)][||]] /examples_bpo_gpg/ =Show/Verify/Update For relevant PBDs= retType=none argsList=(bpoId keysBase keyName passwd sectionTitle=None)  [[elisp:(org-cycle)][| ]]
#+end_org """
def examples_bpo_gpg(
    bpoId,
    keysBase,
    keyName,
    passwd,
    sectionTitle=None,
):
####+END:
    """
** Common examples.
"""

    if sectionTitle == "default":
        cs.examples.menuChapter('*Manage BPO Gpg -- Generate Keys, Encypt and Decrypt*')

    if not bpoId:
        return

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
    #def menuItemVerbose(): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')
    #def menuItemTerse(): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')
    def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

    def cmndCommonParsWithArgs(cmndName, cmndArgs=""): # type: ignore
        cps = cpsInit() ; cps['bpoId'] = bpoId ; cps['keysBase'] = keysBase ;
        cps['keyName'] = keyName ; cps['passwd'] = passwd ;
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')

    cs.examples.menuSection('*Generate PKCS Keys*')

    cmndCommonParsWithArgs(cmndName="gpg_genKey")

    cs.examples.menuSection('*GPG PKCS Encryption*')

    clearFile = "/tmp/gpgPkcsEx1"
    cipherFile = "/tmp/gpgPkcsEx1.gpg"

    execLineEx(f"""cp /etc/motd {clearFile}""")

    cmndCommonParsWithArgs(cmndName="gpg_pkcsEncrypt", cmndArgs=f"{clearFile}")

    def cmndStdinEncrypt(cmndName): # type: ignore
        icmWrapper = "echo HereComes Some ClearText | "
        cps = cpsInit() ; cps['bpoId'] = bpoId ; cps['keysBase'] = keysBase ;
        cps['keyName'] = keyName ; cps['passwd'] = passwd ; cmndArgs = ""
        return cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)
    encryptCmndStr = cmndStdinEncrypt("gpg_pkcsEncrypt")
    #print(f"{encryptCmndStr}")

####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "Decrypt"

####+END:

    cs.examples.menuSection('*GPG Symmetric Decryption*')

    cmndCommonParsWithArgs(cmndName="gpg_pkcsDecrypt", cmndArgs=f"{cipherFile}")

    def cmndStdinDecrypt(cmndName, icmWrapper): # type: ignore
        cps = cpsInit() ; cps['bpoId'] = bpoId ; cps['keysBase'] = keysBase ;
        cps['keyName'] = keyName ; cps['passwd'] = passwd ; cmndArgs = ""
        return cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)

    cmndStdinDecrypt("gpg_pkcsDecrypt", icmWrapper=f"cat {cipherFile} | ")

    cmndStdinDecrypt("gpg_pkcsDecrypt", icmWrapper=f"{encryptCmndStr} | ")

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:cs:py3:section :title "Keys Generation"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Keys Generation*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpg_genKey" :comment "" :parsMand "bpoId keysBase keyName passwd" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpg_genKey>>  =verify= parsMand=bpoId keysBase keyName passwd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpg_genKey(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'keysBase', 'keyName', 'passwd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             keysBase: typing.Optional[str]=None,  # Cs Mandatory Param
             keyName: typing.Optional[str]=None,  # Cs Mandatory Param
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'keysBase': keysBase, 'keyName': keyName, 'passwd': passwd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        # if b.subProc.WOpW(invedBy=self,).bash(
        #         f"""gpg --generate-key""",
        # ).isProblematic():  return(io.eh.badOutcome(cmndOutcome))

        thisBpo = BpoGpg(bpoId,)

        #thisBpo.genKey('bisos', 'bisos@example.com' , 'passphrase')
        thisBpo.genKey(keysBase, keyName, passwd)


        return cmndOutcome

####+BEGIN: bx:cs:py3:section :title "PKCS Encrypt/Decrypt"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *PKCS Encrypt/Decrypt*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpg_pkcsEncrypt" :comment "stdin as clearText" :parsMand "bpoId keysBase keyName passwd" :parsOpt "outFile" :argsMin 0 :argsMax 9999 :pyInv "clearText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpg_pkcsEncrypt>>  *stdin as clearText*  =verify= parsMand=bpoId keysBase keyName passwd parsOpt=outFile argsMax=9999 ro=cli pyInv=clearText   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpg_pkcsEncrypt(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'keysBase', 'keyName', 'passwd', ]
    cmndParamsOptional = [ 'outFile', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             keysBase: typing.Optional[str]=None,  # Cs Mandatory Param
             keyName: typing.Optional[str]=None,  # Cs Mandatory Param
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
             outFile: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             clearText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as clearText"""
        callParamsDict = {'bpoId': bpoId, 'keysBase': keysBase, 'keyName': keyName, 'passwd': passwd, 'outFile': outFile, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        thisBpo = BpoGpg(bpoId,)

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        filesProcessed = False
        for each in typing.cast(list, cmndArgs):
            filesProcessed = True
            with open(each, "rb") as fileObj:
                thisBpo.pkcsEncryptFile(
                    keysBase,
                    keyName,
                    passwd,
                    fileObj,
                    f"{each}.gpg"
                )
                print(f"{each}.gpg")


        if not clearText:
            clearText = b_io.stdin.read()

        if not clearText and not filesProcessed:
            b_io.eh.problem_usageError(f"noFiles and no clearText")
            return cmndOutcome

        if clearText:
            gpgStatus = thisBpo.pkcsEncrypt(
                keysBase,
                keyName,
                passwd,
                clearText,
            )

            cipheredText = gpgStatus.data

            b_io.tm.here(f"""clearText={clearText}""")
            b_io.tm.here(f"""cipheredText={cipheredText}""")

            sys.stdout.buffer.write(cipheredText)  # print does not work.

        return cmndOutcome

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


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpg_pkcsDecrypt" :comment "stdin as cipherText" :parsMand "bpoId keysBase keyName passwd" :parsOpt "outFile" :argsMin 0 :argsMax 9999 :pyInv "cipherText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpg_pkcsDecrypt>>  *stdin as cipherText*  =verify= parsMand=bpoId keysBase keyName passwd parsOpt=outFile argsMax=9999 ro=cli pyInv=cipherText   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpg_pkcsDecrypt(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'keysBase', 'keyName', 'passwd', ]
    cmndParamsOptional = [ 'outFile', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             keysBase: typing.Optional[str]=None,  # Cs Mandatory Param
             keyName: typing.Optional[str]=None,  # Cs Mandatory Param
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
             outFile: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             cipherText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as cipherText"""
        callParamsDict = {'bpoId': bpoId, 'keysBase': keysBase, 'keyName': keyName, 'passwd': passwd, 'outFile': outFile, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        thisBpo = BpoGpg(bpoId,)

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        filesProcessed = False
        for each in typing.cast(list, cmndArgs):
            filesProcessed = True
            with open(each, "rb") as fileObj:
                thisBpo.pkcsDecryptFile(
                    keysBase,
                    fileObj,
                    f"{each}.clear",
                    passwd,
                )

        if not cipherText:
            cipherText = io.stdin.read()

        if not cipherText and not filesProcessed:
            b_io.eh.problem_usageError(f"noFiles and no cipheredText")
            return cmndOutcome

        gpgStatus = thisBpo.pkcsDecrypt(
            keysBase,
            passwd,
            cipherText,
        )

        clearText = gpgStatus.data

        b_io.tm.here(f"""clearText={clearText}""")
        b_io.tm.here(f"""cipherText={cipherText}""")

        sys.stdout.buffer.write(clearText)  # print does not work.

        return cmndOutcome


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

####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
