######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.19.6                                                                                 #
# Generated on 2025-11-06T21:18:29.125764                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.pypi.conda_environment

from .conda_environment import CondaEnvironment as CondaEnvironment

class PyPIEnvironment(metaflow.plugins.pypi.conda_environment.CondaEnvironment, metaclass=type):
    ...

