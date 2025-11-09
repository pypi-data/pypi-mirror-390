from __future__ import annotations

from typing import TYPE_CHECKING

from exactpy.controllers.system import DivisionController, MeController
from exactpy.namespaces.base import Namespace

if TYPE_CHECKING:
    from exactpy.client import Client


class SystemNamespace(Namespace):
    me: MeController
    divisions: DivisionController

    def __init__(self, client: Client):
        super().__init__(client=client)

        self.me = MeController(self._client)
        self.divisions = DivisionController(self._client)
