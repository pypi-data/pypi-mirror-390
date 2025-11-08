#!/usr/bin/env python

""" #+begin_org
* ~[Summary]~ :: A =PlantedCmnds= (Pkged, seed=bx-gpg-sym.cs)  Spread-Plant for encryption of current dir.
#+end_org """

from bisos import b
from bisos.b import b_io
from bisos.b import cs
import collections

from bisos.crypt import bxGpgSym_seed
from bisos.b import cmndsSeed

from bisos.crypt import gpgSym

import pathlib

import ast
import typing


cmndsSeed.setup(
    seedType="common",
    kwSeedInfo={'unused': "NOTYET"}
)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "makePasswd" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<makePasswd>>  =verify= argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class makePasswd(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

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
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        self.captureRunStr(""" #+begin_org
*** Run Results
#+begin_src sh :results output :session shared
planted-bx-gpg-sym.cs -i makePasswd /etc/motd
  #+end_src
#+RESULTS:
:

        #+end_org """)

        cmndArg = self.cmndArgsGet("0", self.cmndArgsSpec(), argsList)

        if not (resStr := b.subProc.Op(outcome=cmndOutcome, log=0,).bash(
           f"""\
privPolicy.cs --policy_hash="P11"  -i policyHash {cmndArg}""",
           stdin="",
        ).stdout):  return(b_io.eh.badOutcome(cmndOutcome))

        resValue = ast.literal_eval(resStr)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=resValue,
        )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "isLocalHere" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<isLocal>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class isLocalHere(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        self.captureRunStr(""" #+begin_org
*** Run Results
#+begin_src sh :results output :session shared
planted-bx-gpg-sym.cs -i isLocal
  #+end_src
#+RESULTS:
:

        #+end_org """)

        # If the file /bisos/var/sites/selected is a symlink, return True, else False
        try:
            target_path = pathlib.Path("/bisos/var/sites/selected")
            resValue = target_path.is_symlink()

        except Exception as e:
            # return a bad outcome with the exception message
            return b_io.eh.badOutcome(cmndOutcome, comment=str(e))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=resValue,
        )



def examples_csu() -> None:

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter
    literal = cs.examples.execInsert

    csName = "bx-gpg-sym.cs"
    cmndOutcome = b.op.Outcome()

    #  -v 1 --callTrackings monitor+ --callTrackings invoke+
    pars_debug_full = od([('verbosity', "1"), ('callTrackings', "monitor+"), ('callTrackings', "invoke+"), ])

    # cmnd('targetRun', csName=csName, pars=(pars_debug_full | pars_upload), comment=f"""# DEBUG Small Batch""",)

    if not (isLocal := isLocalHere(cmndOutcome=cmndOutcome).pyCmnd().results): return(1)


    localPasswd = "sometthingLocal"
    remotePasswd = "somethingRemote"

    if isLocal == True:
        if not (passwds := makePasswd(cmndOutcome=cmndOutcome).pyCmnd(argsList=[localPasswd]).results): return(1)        
        pars_passwdEncrypt = od([('passwd', passwds[0]),])
        if not (passwds := makePasswd(cmndOutcome=cmndOutcome).pyCmnd(argsList=[remotePasswd]).results): return(1)        
        pars_passwdDecrypt = od([('passwd', passwds[0]),])
    else:
        if not (passwds := makePasswd(cmndOutcome=cmndOutcome).pyCmnd(argsList=[remotePasswd]).results): return(1)        
        pars_passwdEncrypt = od([('passwd', passwds[0]),])
        if not (passwds := makePasswd(cmndOutcome=cmndOutcome).pyCmnd(argsList=[localPasswd]).results): return(1)        
        pars_passwdDecrypt = od([('passwd', passwds[0]),])

    pars_passwdWeak = od([('passwd', "N0tStrong_"),])

    # pars_gpgTextOutFalse = od([('gpgTextOut', 'False'),])  # False is now default

    outFileCipher = "/tmp/gpgSymEx1.tar.gz.gpg"
    pars_outFileCipher = od([('outFile', outFileCipher),])

    outFileElf = "/tmp/gpgSymEx1.tar.gz.gpg.elf"
    pars_outFileElf= od([('outFile', outFileElf),])

    outFileClear = "/tmp/gpgSymEx1.tar.gz"
    pars_outFileClear = od([('outFile', outFileClear),])

    pars_elfDeleteInDataFile = od([('elfDeleteInDataFile', "True"),])

    cs.examples.menuChapter(f'*Seed Extensions*')

    cs.examples.menuSection('*Make Password*')

    cmnd('makePasswd', args="/etc/motd")
    cmnd('isLocalHere', args="")    

    cs.examples.menuSection('*GPG Symmetric Encryption Of BaseDirs*')

    cmnd('gpg_symEncrypt_baseDirs', csName=csName, pars=(pars_passwdWeak | pars_outFileCipher | pars_elfDeleteInDataFile), args=".")
    cmnd('gpg_symEncrypt_baseDirs_elfbin', csName=csName, pars=(pars_passwdWeak | pars_outFileElf | pars_elfDeleteInDataFile), args=".")

    cmnd('gpg_symEncrypt_baseDirs', csName=csName, pars=(pars_passwdEncrypt | pars_outFileCipher | pars_elfDeleteInDataFile), args=".")
    cmnd('gpg_symEncrypt_baseDirs_elfbin', csName=csName, pars=(pars_passwdEncrypt | pars_outFileElf | pars_elfDeleteInDataFile), args=".")

    cs.examples.menuSection('*GPG Symmetric Decryption of .tar.gz*')

    cmnd('gpg_symDecrypt', csName=csName, pars=(pars_passwdWeak | pars_outFileClear), args=f"{outFileCipher}")
    cmnd('gpg_symDecrypt_elfbin', csName=csName, pars=(pars_passwdWeak | pars_outFileClear), args=f"{outFileElf}")

    cmnd('gpg_symDecrypt', pars=(pars_passwdDecrypt | pars_outFileClear), args=f"{outFileCipher}")
    cmnd('gpg_symDecrypt_elfbin', pars=(pars_passwdDecrypt | pars_outFileClear), args=f"{outFileElf}")

    return
