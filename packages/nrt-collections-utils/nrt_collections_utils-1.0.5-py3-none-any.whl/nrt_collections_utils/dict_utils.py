from typing import Union


class DictUtil:

    @staticmethod
    def get_value(dict_: dict, path: Union[str, list], default_value=None):

        if isinstance(path, str):
            return dict_.get(path, default_value)

        for key in path:
            if not isinstance(dict_, dict):
                return default_value

            dict_ = dict_.get(key)

        return dict_
