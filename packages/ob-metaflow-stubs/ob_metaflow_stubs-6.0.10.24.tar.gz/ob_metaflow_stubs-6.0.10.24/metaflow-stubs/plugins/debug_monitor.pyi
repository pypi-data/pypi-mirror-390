######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.19.5.1+obcheckpoint(0.2.8);ob(v1)                                                    #
# Generated on 2025-11-10T18:36:23.733731                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.monitor


class DebugMonitor(metaflow.monitor.NullMonitor, metaclass=type):
    @classmethod
    def get_worker(cls):
        ...
    ...

class DebugMonitorSidecar(object, metaclass=type):
    def __init__(self):
        ...
    def process_message(self, msg):
        ...
    ...

