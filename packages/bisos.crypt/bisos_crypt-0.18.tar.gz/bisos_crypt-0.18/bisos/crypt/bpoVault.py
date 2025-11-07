# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for creating and managing BPO's vaults.
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/crypt/py3/bisos/crypt/bpoVault.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['bpoVault'], }
csInfo['version'] = '202209272423'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'bpoVault-Panel.org'
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
#from bis os.icm import fpath


#import logging

#import shutil

import pykeepass_cache
import pykeepass

####+BEGIN: b:py3:class/decl :className "BpoVault" :superClass "object" :comment "Run Bases of a Bpo" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /BpoVault/  superClass=object =Run Bases of a Bpo=  [[elisp:(org-cycle)][| ]]
#+end_org """
class BpoVault(object):
####+END:
    """
** Abstraction of the Vaults of BPOs (ByStar Portable Object)
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
*** TODO [[elisp:(org-cycle)][| *MethodDesc:* | ]] Rename vault, vaults ---  Confirm that ~bpoVaultsBaseDir~ exists and return that.
        #+end_org """

        bpoVaultsBaseDir = pathlib.Path(
            os.path.join(
                self.bpo.bpoBaseDir,
                'vault',
            )
        )
        if not os.path.exists(bpoVaultsBaseDir):
            bpoVaultsBaseDir.mkdir(parents=True, exist_ok=True)

        return bpoVaultsBaseDir

####+BEGIN: b:py3:cs:method/typing :methodName "vaultFilePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /vaultFilePath_obtain/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def vaultFilePath_obtain(
####+END:
            self,
            vault,
    ) -> pathlib.Path:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]]  Based on =vault= create BPO's {vault}.kdbx. Return that path.
        #+end_org """

        vaultFileName = f"{vault}.kdbx"
        repoBase = self.repoBasePath_obtain()

        return (
            pathlib.Path(
                os.path.join(
                    repoBase,
                    vaultFileName,
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "vaultCreate_wOp" :methodType "wOp" :retType "OpOutcome" :deco "default" :argsList "typed"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-wOp  [[elisp:(outline-show-subtree+toggle)][||]] /vaultCreate_wOp/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def vaultCreate_wOp(
####+END:
            self,
            vault,
            passwd,
            outcome: typing.Optional[b.op.Outcome] = None,
    ) -> b.op.Outcome:
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Create an empty database if it does not exist. Implemented with ph (passhole) as a command.
*** TODO dependence on ph is un-necessary. relevant part of passhole should be merged with pykeepass.
        #+end_org """

        if not outcome:
           outcome = b.op.Outcome()

        vaultFilePath = self.vaultFilePath_obtain(vault)

        if os.path.exists(vaultFilePath):
            b_io.ann.write(f"""{vaultFilePath} Exists. Creation Skipped""")
            return outcome
        else:
            b_io.ann.write(f"No database file found at {vaultFilePath}")
            b_io.ann.write("Creating it...")

        # DEBUG -- invkedBy=outcome
        if b.subProc.WOpW(log=1).bash(
                f"""ph init --name {vault} --database {vaultFilePath} --password {passwd}""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))

        print(vaultFilePath)

        return outcome

####+BEGIN: b:py3:cs:method/typing :methodName "vaultOpen" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /vaultOpen/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def vaultOpen(
####+END:
            self,
            vault,
            passwd,
    ):
    # ) -> typing.Optional[pykeepass.PyKeePass]:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]]  Open the vault and return a kp. vault must exist. passwd is mandatory.
        Thereafter, for a while actions can be performed without the password.
*** TODO Add passhole to panel.
        #+end_org """

        vaultFilePath = self.vaultFilePath_obtain(vault)

        if not os.path.exists(vaultFilePath):
            b_io.eh.problem_usageError(f"""Missing vault={vaultFilePath}""")
            return typing.cast(pykeepass.PyKeePass, None)

        if not passwd:
            b_io.eh.problem_usageError(f"""Missing passwd""")
            return typing.cast(pykeepass.PyKeePass, None)

        #kp = pykeepass_cache.PyKeePass(vaultFilePath, passwd, timeout=1000)
        kp = pykeepass_cache.PyKeePass(vaultFilePath, passwd)

        return typing.cast(pykeepass.PyKeePass, kp)

####+BEGIN: b:py3:cs:method/typing :methodName "vaultClose" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /vaultClose/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def vaultClose(
####+END:
            self,
            vault,
            passwd,
    ):
        """ #+begin_org
*** TODO [[elisp:(org-cycle)][| *MethodDesc:* | ]]  UnImplemented. Close the vault.
        #+end_org """

        return vault, passwd


####+BEGIN: b:py3:cs:method/typing :methodName "vaultGroupAdd" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /vaultGroupAdd/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def vaultGroupAdd(
####+END:
            self,
            vault,
            passwd,
            groupName,
    ):
        """ #+begin_org
*** TODO [[elisp:(org-cycle)][| *MethodDesc:* | ]]  Add =groupName= to specified vault. Becomes persistent only when =passwd= is provided.
        #+end_org """

        kp = self.vaultOpen(vault, passwd)

        group = kp.add_group(kp.root_group, groupName)

        if passwd:
            kp.save()
        else:
            b_io.ann.write(f"Group -- {groupName} updated but not saved")

        return group


####+BEGIN: b:py3:cs:method/typing :methodName "vaultEntryUpdate" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /vaultEntryUpdate/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def vaultEntryUpdate(
####+END:
            self,
            vault,
            passwd,
            group,
            entryName,
            entryValue,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]]  Create a new entry or update an exisiting one. Becomes persistent only when =passwd= is provided.
        #+end_org """

        kp = self.vaultOpen(vault, passwd)

        group = kp.find_groups(name=group, first=True)

        print(f"KKK {entryName}, {entryValue}")

        kp.add_entry(group, entryName, entryName, entryValue)
        #kp.add_entry(group, 'gmail', 'myusername', 'myPassw0rdXX')

        if passwd:
            kp.save()

        return kp

####+BEGIN: b:py3:cs:method/typing :methodName "vaultEntryRead" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /vaultEntryRead/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def vaultEntryRead(
####+END:
            self,
            vault,
            passwd,
            title,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]]  Return an entry given =title=.
        #+end_org """

        kp = self.vaultOpen(vault, passwd)

        entry = kp.find_entries(title=title, first=True)

        # print(f"NOTYET, vaultEntryRead should not use print {title} -- {entry} {entry.username} {entry.password}")

        return entry

####+BEGIN: b:py3:cs:method/typing :methodName "vaultEntriesList" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /vaultEntriesList/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def vaultEntriesList(
####+END:
            self,
            vault,
            passwd,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]]  List existing entries.
        #+end_org """

        kp = self.vaultOpen(vault, passwd)

        print(f"Entries == {kp.entries}")

        return kp.entries


####+BEGIN: b:py3:cs:method/typing :methodName "vaultEntryDelete" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /vaultEntryDelete/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def vaultEntryDelete(
####+END:
            self,
            vault,
            passwd,
            title,
    ):
        """ #+begin_org
*** TODO [[elisp:(org-cycle)][| *MethodDesc:* | ]]  UnImpelemted. Delete the entry specified by =title=
        #+end_org """

        kp = pykeepass_cache.PyKeePass(self.vaultFilePath_obtain(vault), passwd,)
        return title, kp

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
        parName='vault',
        parDescription="Vault Name -- uniq within bpo/vault",
        parDataType=None,
        parDefault='fpVault',
        parChoices=["any"],
        # parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--vault',
    )
    csParams.parDictAdd(
        parName='passwd',
        parDescription="Password (General Purpose)",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--passwd',
    )

####+BEGIN: bx:cs:py3:section :title "CS-Lib Examples"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Lib Examples*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "examples_csu" :comment "~CSU Specification~" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csu/  ~CSU Specification~ deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csu(
####+END:
        oneBpo,
        vault,
        passwd,
        sectionTitle=None,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* |]] Examples of Cmnds provided by this CSU-Lib
    #+end_org """

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
    # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

    if sectionTitle == "default":
        cs.examples.menuChapter('*Manage BPO Vault*')

    if not oneBpo:
        return

    cs.examples.menuChapter('*Primary Commands*')

    cmndName = "vaultCreate"
    cmndArgs = ""
    cps = cpsInit() ; cps['bpoId'] = oneBpo ; cps['vault'] = vault ; cps['passwd'] = passwd
    menuItem(verbosity='none')

    cmndName = "vaultOpen"
    cmndArgs = ""
    cps = cpsInit() ; cps['bpoId'] = oneBpo ; cps['vault'] = vault ; cps['passwd'] = passwd
    menuItem(verbosity='none')

    cmndName = "vaultClose"
    cmndArgs = ""
    cps = cpsInit() ; cps['bpoId'] = oneBpo ; cps['vault'] = vault ; cps['passwd'] = passwd
    menuItem(verbosity='none')

    cmndName = "vaultGroupAdd"
    cmndArgs = "bisos"
    cps = cpsInit() ; cps['bpoId'] = oneBpo ; cps['vault'] = vault ; cps['passwd'] = passwd
    menuItem(verbosity='none')

    cmndName = "vaultEntryUpdate"
    cmndArgs = "fpsKey=bpoFpsSecret"
    cps = cpsInit() ; cps['bpoId'] = oneBpo ; cps['vault'] = vault ; cps['passwd'] = passwd
    menuItem(verbosity='none')

    cmndName = "vaultEntryRead"
    cmndArgs = "fpsKey"
    cps = cpsInit() ; cps['bpoId'] = oneBpo ; cps['vault'] = vault ; cps['passwd'] = passwd
    menuItem(verbosity='none')

    cmndName = "vaultEntryDelete"
    cmndArgs = ""
    cps = cpsInit() ; cps['bpoId'] = oneBpo ; cps['vault'] = vault ; cps['passwd'] = passwd
    menuItem(verbosity='none')

    cs.examples.menuChapter('*Secondary Commands*')

    cmndName = "bpoVaultPrep"
    cmndArgs = ""
    cps = cpsInit() ; cps['bpoId'] = oneBpo ; cps['vault'] = vault ; cps['passwd'] = passwd
    menuItem(verbosity='none')

    cmndName = "databasesList"
    cmndArgs = ""
    cps = cpsInit() ; cps['bpoId'] = oneBpo ; cps['vault'] = vault ; cps['passwd'] = passwd
    menuItem(verbosity='none')

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

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vaultCreate" :parsMand "bpoId vault passwd" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vaultCreate>>  =verify= parsMand=bpoId vault passwd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vaultCreate(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'vault', 'passwd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             vault: typing.Optional[str]=None,  # Cs Mandatory Param
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'vault': vault, 'passwd': passwd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Wrpper around class method.
        #+end_org """)

        thisBpo = BpoVault(bpoId,)

        cmndOutcome = thisBpo.vaultCreate_wOp(vault, passwd, outcome=None)

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vaultOpen" :parsMand "bpoId vault passwd" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vaultOpen>>  =verify= parsMand=bpoId vault passwd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vaultOpen(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'vault', 'passwd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             vault: typing.Optional[str]=None,  # Cs Mandatory Param
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'vault': vault, 'passwd': passwd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Wrpper around class method.
        #+end_org """)

        thisBpo = BpoVault(bpoId,)

        thisBpo.vaultOpen(vault, passwd)

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vaultClose" :parsMand "" :parsOpt "vault" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vaultClose>>  =verify= parsOpt=vault ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vaultClose(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'vault', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             vault: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        callParamsDict = {'vault': vault, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]] UnImplemented -- Manually kill the server.
        #+end_org """)

        #pykeepass_cache.close()

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vaultGroupAdd" :parsMand "bpoId vault" :parsOpt "passwd" :argsMin 0 :argsMax 999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vaultGroupAdd>>  =verify= parsMand=bpoId vault parsOpt=passwd argsMax=999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vaultGroupAdd(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'vault', ]
    cmndParamsOptional = [ 'passwd', ]
    cmndArgsLen = {'Min': 0, 'Max': 999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             vault: typing.Optional[str]=None,  # Cs Mandatory Param
             passwd: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'vault': vault, 'passwd': passwd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Manually kill the server.
        #+end_org """)

        thisBpo = BpoVault(bpoId,)

        cmndArgs = self.cmndArgsGet("0&-1", cmndArgsSpecDict, argsList)

        # Any number of Name=Value can be passed as args
        for each in typing.cast(list, cmndArgs):
            group = thisBpo.vaultGroupAdd(vault, passwd, each)
            print(group)

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
            argDescription="A sequence of varName=varValue"
        )

        return typing.cast(dict, cmndArgsSpecDict)





####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vaultEntryUpdate" :parsMand "bpoId vault passwd" :parsOpt "" :argsMin 0 :argsMax 999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vaultEntryUpdate>>  =verify= parsMand=bpoId vault passwd argsMax=999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vaultEntryUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'vault', 'passwd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             vault: typing.Optional[str]=None,  # Cs Mandatory Param
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'vault': vault, 'passwd': passwd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Manually kill the server.
        #+end_org """)

        thisBpo = BpoVault(bpoId,)

        cmndArgs = self.cmndArgsGet("0&-1", cmndArgsSpecDict, argsList)

        # Any number of Name=Value can be passed as args
        for each in typing.cast(list, cmndArgs):
            varNameValue = each.split('=')
            parValue=varNameValue[1]
            print(f"{varNameValue} {parValue}")
            thisBpo.vaultEntryUpdate(vault, passwd, 'bisos', varNameValue[0], varNameValue[1])

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
            argDescription="A sequence of varName=varValue"
        )

        return cmndArgsSpecDict




####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vaultEntryRead" :parsMand "bpoId vault" :parsOpt "passwd" :argsMin 1 :argsMax 999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vaultEntryRead>>  =verify= parsMand=bpoId vault parsOpt=passwd argsMin=1 argsMax=999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vaultEntryRead(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'vault', ]
    cmndParamsOptional = [ 'passwd', ]
    cmndArgsLen = {'Min': 1, 'Max': 999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             vault: typing.Optional[str]=None,  # Cs Mandatory Param
             passwd: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'vault': vault, 'passwd': passwd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Manually kill the server.
        #+end_org """)

        # bpoId = bpo.effectiveId(bpoId)

        thisBpo = BpoVault(bpoId,)

        cmndArgs = self.cmndArgsGet("0&-1", cmndArgsSpecDict, argsList)
        if not cmndArgs:
            b_io.ann.write("Missing cmndArgs")

        # Any number of Name=Value can be passed as args
        for each in typing.cast(list, cmndArgs):
            entry = thisBpo.vaultEntryRead(vault, passwd, each)
            print(f" {entry} {entry.username} {entry.password}")

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
            argDescription="A sequence of varName=varValue"
        )

        return cmndArgsSpecDict

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vaultEntriesList" :parsMand "bpoId vault" :parsOpt "passwd" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vaultEntriesList>>  =verify= parsMand=bpoId vault parsOpt=passwd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vaultEntriesList(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'vault', ]
    cmndParamsOptional = [ 'passwd', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             vault: typing.Optional[str]=None,  # Cs Mandatory Param
             passwd: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'vault': vault, 'passwd': passwd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Manually kill the server.
        #+end_org """)

        thisBpo = BpoVault(bpoId,)

        thisBpo.vaultEntriesList(vault, passwd)

        return cmndOutcome





####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vaultEntryDelete" :parsMand "" :parsOpt "vault" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vaultEntryDelete>>  =verify= parsOpt=vault ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vaultEntryDelete(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'vault', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             vault: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        callParamsDict = {'vault': vault, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Manually kill the server.
        #+end_org """)

        #pykeepass_cache.close()

        return cmndOutcome




####+BEGIN: bx:cs:py3:section :title "Secondary Command Services"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Secondary Command Services*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "bpoVaultPrep" :parsMand "bpoId vault passwd" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<bpoVaultPrep>>  =verify= parsMand=bpoId vault passwd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class bpoVaultPrep(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'vault', 'passwd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             vault: typing.Optional[str]=None,  # Cs Mandatory Param
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'vault': vault, 'passwd': passwd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Wrpper around class method.
        #+end_org """)

        b_io.ann.write("NOTYET, Here we should do all that necessary to set fpsKey up.")

        return cmndOutcome



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "databasesList" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<databasesList>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class databasesList(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Get a dictionary of currently cached databases.
        #+end_org """)

        # Should open the data bases first.
        dataBases = pykeepass_cache.cached_databases()

        print(dataBases)

        return cmndOutcome

####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
