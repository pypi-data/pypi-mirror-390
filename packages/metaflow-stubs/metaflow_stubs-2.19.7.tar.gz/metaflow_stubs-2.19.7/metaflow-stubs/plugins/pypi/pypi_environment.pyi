######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.19.7                                                                                 #
# Generated on 2025-11-10T21:30:23.032900                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.pypi.conda_environment

from .conda_environment import CondaEnvironment as CondaEnvironment

class PyPIEnvironment(metaflow.plugins.pypi.conda_environment.CondaEnvironment, metaclass=type):
    ...

