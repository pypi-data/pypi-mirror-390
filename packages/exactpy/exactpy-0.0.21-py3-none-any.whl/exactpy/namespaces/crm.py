from __future__ import annotations

from typing import TYPE_CHECKING

from exactpy.controllers.crm import AccountController
from exactpy.namespaces.base import Namespace

if TYPE_CHECKING:
    from exactpy.client import Client


class CRMNamespace(Namespace):
    accounts: AccountController

    def __init__(self, client: Client):
        super().__init__(client=client)

        self.accounts = AccountController(self._client)
