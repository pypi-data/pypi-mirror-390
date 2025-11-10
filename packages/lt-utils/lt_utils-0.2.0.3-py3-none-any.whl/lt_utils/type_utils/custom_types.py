__all__ = ["UniDict"]
from lt_utils.common import *
from lt_utils.misc_utils import updateDict


class _NOT_FOUND:
    def __init__(self):
        pass


class UniDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redefine_attrs()
        self.___notfound_instance = _NOT_FOUND()

    def _check(self, fn_inst: str):
        if hasattr(self, "_frozen_state"):
            if self._frozen_state:
                raise RuntimeError(
                    f"You cannot use ``{fn_inst}`` on a {self.__class__.__name__} instance while '_frozen_state' is set to True."
                )

    def _setup_value(self, value):
        if isinstance(value, (list, tuple, set)):
            if not value:
                return value
            nv = [self._setup_value(v) for v in value]
            if isinstance(value, list):
                return nv
            elif isinstance(value, tuple):
                return tuple(nv)
            return set(nv)
        elif isinstance(value, dict):
            return UniDict(**value)
        return value

    def __delitem__(self, key: str):
        self._check("__delitem__")
        super().__delitem__(key)

    def __setitem__(self, key, value):
        needs_redefine = False
        self._check("__setitem__")
        if key not in self:
            value = self._setup_value(value)
            needs_redefine = True
        super().__setitem__(key, value)
        super().__setattr__(str(key), value)
        if needs_redefine:
            self._redefine_attrs()

    def __setattr__(self, name, value):
        if name != "_frozen_state":
            self._check("__setattr__")
            if name not in self:
                value = self._setup_value(value)
        super().__setattr__(str(name), value)

    def _redefine_attrs(self):
        data = self.copy()
        if not hasattr(self, "_frozen_state"):
            self._frozen_state = False
            froozen = False
        else:
            froozen = self._frozen_state

        updateDict(self, {str(k): v for k, v in data.items()})

        self._frozen_state = froozen

    def setdefault(self, key: Any, default: None = None):
        self._check("setdefault")
        super().setdefault(key, default)

    def unfreeze_dict(self):
        try:
            self._frozen_state = False
        except:
            pass
        for k, v in self.items():
            try:
                if isinstance(v, UniDict):
                    v.unfreeze_dict()

                elif isinstance(v, dict):
                    self.force_set(k, UniDict(**v))

                elif isinstance(v, (list, tuple, set)):
                    for _, v2 in v:
                        if isinstance(v2, UniDict):
                            v2.unfreeze_dict()
            except Exception as e:
                print(e)

    def freeze_dict(self):
        try:
            self._frozen_state = False
        except:
            pass
        for k, v in self.items():
            try:
                if isinstance(v, UniDict):
                    v.freeze_dict()
                elif isinstance(v, dict):
                    self.force_set(k, UniDict(**v))
                    self[k].freeze_dict()
                elif isinstance(v, (list, tuple, set)):
                    for _, v2 in v:
                        if isinstance(v2, UniDict):
                            v2.freeze_dict()
            except Exception as e:
                print(e)
        self._frozen_state = True

    def pop(self, key: Any, default: Optional[Any] = None):
        self._check("pop")
        super().pop(key, default)
        super().__delattr__(key, None)

    def force_set(self, name, value):
        """Ignores the frozen state"""
        super().__setitem__(name, value)
        self._redefine_attrs()

    def _process_update_args(*args, **kwargs):
        if args:
            for arg in args:
                assert isinstance(
                    arg, dict
                ), f"{arg} is not a valid arg, it should be a valid dictionary"
                kwargs.update({k: v for k, v in arg.items()})
        return kwargs

    def update(self, *args: Dict[str, Any], **kwargs):
        self._check("update")
        super().update(self._process_update_args(*args, **kwargs))

    def force_update(self, *args: Dict[str, Any], **kwargs):
        super().update(self._process_update_args(*args, **kwargs))

    def copy(self, deep: bool = False):
        if deep:
            from copy import deepcopy

            if self._frozen_state:
                self.unfreeze_dict()
                results = deepcopy(dict(self))
                self.freeze_dict()
            else:
                results = deepcopy(dict(self))
            return results
        return dict(self).copy()

    def find(self, item: object, total: int = -1, *, verbose_exceptions: bool = False):
        """
        Find objects by value, accepting also values
        with the same type if the cannot be compared
        """
        matching = []

        for k, v in self.items():
            try:
                if v == item:
                    current = {"key": k, "value": v}
                    if total > 0:
                        if total == 1:
                            return current
                        matching.append(current)
                        if len(matching) >= total:
                            return matching[:total]
                    else:
                        matching.append(current)
            except Exception as e:
                if verbose_exceptions:
                    print(e)
                pass

        if not matching:
            return None
        if total > 0:
            return matching[:total]
        return matching

    def _update(self, **kwargs):
        """Same as the original update, but this version
        returns the class itself. Very circumstantial use-cases"""
        self.update(**kwargs)
        return self

    def save_state(self, location: Union[str, Path], *args, **kwargs):
        path = Path(location)
        assert "." in path.name, "Cannot process without any specific extension"
        if path.name.endswith((".npy", ".pkl")):
            from lt_utils.file_ops import save_pickle

            save_pickle(path, self.copy(True), *args, **kwargs)
        elif path.name.endswith(".json"):
            from lt_utils.file_ops import save_json

            save_json(path, self.copy(True), *args, **kwargs)
        elif path.name.endswith((".yaml", ".yml")):
            from lt_utils.file_ops import save_yaml

            save_yaml(path, self.copy(True), *args, **kwargs)
        else:
            raise ValueError(
                f"No valid extension has been provided to '{path.name}'. It must be either 'npy', 'pkl', 'json', 'yaml' or 'yml'."
            )

    def load_state(self, location: Union[str, Path], *args, **kwargs):
        path = Path(location)
        assert "." in path.name, "Cannot process without any specific extension"
        if path.name.endswith((".npy", ".pkl")):
            from lt_utils.file_ops import load_pickle
            from numpy import ndarray

            previous_state = load_pickle(str(path), *args, **kwargs)
            if isinstance(previous_state, ndarray):
                previous_state = previous_state.tolist()
        elif path.name.endswith(".json"):
            from lt_utils.file_ops import load_json

            previous_state = load_json(str(path), *args, **kwargs)
        elif path.name.endswith((".yml", ".yaml")):
            from lt_utils.file_ops import load_yaml

            previous_state = load_yaml(str(path), *args, **kwargs)
        else:
            raise ValueError(
                f"No valid extension has been provided to '{path.name}'. It must be either 'npy', 'pkl', 'json', 'yaml' or 'yml'."
            )
        assert isinstance(
            previous_state, (UniDict, dict)
        ), f"The state loaded from '{str(path)}' are not a valid dictionary."
        self.force_update(**previous_state)
        self._redefine_attrs()

    @classmethod
    def load_from_file(cls, location: Union[str, Path], *args, **kwargs):
        path = Path(location)
        assert "." in path.name, "Cannot process without any specific extension"
        if path.name.endswith((".npy", ".pkl")):
            from lt_utils.file_ops import load_pickle
            from numpy import ndarray

            previous_state = load_pickle(str(path), *args, **kwargs)
            if isinstance(previous_state, ndarray):
                previous_state = previous_state.tolist()
        elif path.name.endswith(".json"):
            from lt_utils.file_ops import load_json

            previous_state = load_json(str(path), *args, **kwargs)
        elif path.name.endswith((".yml", ".yaml")):
            from lt_utils.file_ops import load_yaml

            previous_state = load_yaml(str(path), *args, **kwargs)
        else:
            raise ValueError(
                f"No valid extension has been provided to '{path.name}'. It must be either 'npy', 'pkl', 'json', 'yaml' or 'yml'."
            )
        assert isinstance(
            previous_state, (UniDict, dict)
        ), f"The state loaded from '{str(path)}' are not a valid dictionary."
        return cls(**previous_state)
