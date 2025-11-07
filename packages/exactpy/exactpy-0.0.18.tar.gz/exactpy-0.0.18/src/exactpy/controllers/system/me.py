from exactpy.controllers.base import BaseController
from exactpy.models.system import MeModel


class MeController(BaseController):
    _resource = "current/Me"
    _model = MeModel

    def all(self):
        raise NotImplementedError("Method not implemented in this controller.")

    def show(self, **kwargs):
        r = self._client.get(
            resource=self._resource,
            include_division=False,
        )

        return self._model.model_validate(r.json()["d"]["results"][0])
