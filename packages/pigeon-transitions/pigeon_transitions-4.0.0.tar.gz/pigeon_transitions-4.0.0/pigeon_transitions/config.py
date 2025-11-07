from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import Optional, Mapping, Any
from importlib import import_module
import yaml


def get_machine(name, subclass=None):
    *package_path, class_name = name.split(".")
    package_name = ".".join(package_path)
    package = import_module(package_name)
    machine = getattr(package, class_name)
    assert subclass is None or issubclass(machine, subclass)
    return machine


class MachineConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    config: Optional[Mapping[str, Any]] = {}
    replace: Optional[str] = None

    @field_validator("replace")
    @classmethod
    def get_machines(cls, replacement):
        from .base import BaseMachine

        return get_machine(replacement, BaseMachine)

    @model_validator(mode="after")
    def validate_extra(self):
        for key, val in self.__pydantic_extra__.items():
            setattr(self, key, self.__class__(**val))
        return self


class PigeonTransitionsConfig(BaseModel):
    root: str
    machines: Optional[MachineConfig] = MachineConfig()

    @field_validator("root")
    @classmethod
    def get_machine(cls, root: str):
        from .root import RootMachine

        return get_machine(root, RootMachine)

    @classmethod
    def load(cls, data):
        return cls(**yaml.safe_load(data))

    @classmethod
    def load_file(cls, file):
        with open(file) as f:
            return cls.load(f.read())
