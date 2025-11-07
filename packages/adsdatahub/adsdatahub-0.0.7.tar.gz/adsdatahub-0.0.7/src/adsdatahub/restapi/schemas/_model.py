from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    pass


class ExtraAllowModel(Model):
    model_config = ConfigDict(extra="allow")


class ExtraForbidModel(Model):
    model_config = ConfigDict(extra="forbid")
