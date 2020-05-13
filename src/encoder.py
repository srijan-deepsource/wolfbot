""" encoder.py """
import json
import pickle
import sys
from typing import Any, Dict

from src import const
from src.roles import Player, get_role_obj
from src.statements import Statement
from src.stats import GameResult, SavedGame


class WolfBotEncoder(json.JSONEncoder):
    """ Encoder for all WolfBot objects. """

    def default(self, o: Any) -> Any:
        """ Overrides encoding method. """
        if isinstance(o, (Player, Statement, GameResult, SavedGame)):
            return o.json_repr()
        if isinstance(o, set):
            return {"type": "Set", "data": sorted(tuple(o))}
        if isinstance(o, frozenset):
            return {"type": "FrozenSet", "data": sorted(tuple(o))}
        return json.JSONEncoder.default(self, o)


class WolfBotDecoder(json.JSONDecoder):
    """ Decoder for all WolfBot objects. """

    def __init__(self) -> None:
        super().__init__(object_hook=self.json_to_objects)

    @staticmethod
    def json_to_objects(obj: Dict[str, Any]) -> Any:
        """ Implements decoding method. """
        obj_type = obj.pop("type", None)
        if obj_type == "Set":
            return set(obj["data"])
        if obj_type == "FrozenSet":
            return frozenset(obj["data"])
        if obj_type == "Statement":
            obj["knowledge"] = tuple([tuple(know) for know in obj["knowledge"]])
            obj["switches"] = tuple([tuple(switch) for switch in obj["switches"]])
            return get_object_initializer(obj_type)(**obj)
        if obj_type == "GameResult":
            return get_object_initializer(obj_type)(**obj)
        if obj_type == "SavedGame":
            obj["original_roles"] = tuple(obj["original_roles"])
            return get_object_initializer(obj_type)(**obj)
        if obj_type in const.ROLE_SET:
            return get_role_obj(obj_type)(**obj)
        return obj


def get_object_initializer(obj_name: str) -> Any:
    """ Retrieves class initializer from its string name. """
    return getattr(sys.modules[__name__], obj_name)


def convert_pkl_to_json(file_path: str) -> None:
    """ Backwards compatibility with pkl. """
    with open(file_path, "rb") as fpkl, open(f"{file_path[0:-4]}.json", "w") as fjson:
        data = pickle.load(fpkl)
        json.dump(data, fjson, cls=WolfBotEncoder)
