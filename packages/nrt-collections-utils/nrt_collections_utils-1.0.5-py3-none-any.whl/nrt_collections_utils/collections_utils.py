

class CollectionsUtil:

    @classmethod
    def deep_args_to_list(cls, *args) -> list:
        args_list = []

        for arg in args:
            args_list.extend(cls.__args_to_list_recursive(arg))

        return args_list

    @staticmethod
    def is_iter(element) -> bool:
        try:
            iter(element)
        except TypeError:
            return False

        return True

    @classmethod
    def object_to_deep_collection(cls, obj):
        if hasattr(obj, '__dict__'):
            return cls.object_to_deep_collection(obj.__dict__)

        if isinstance(obj, dict):
            return {k: cls.object_to_deep_collection(v) for k, v in obj.items()}

        if isinstance(obj, list):
            return [cls.object_to_deep_collection(e) for e in obj]

        if isinstance(obj, tuple):
            return tuple(cls.object_to_deep_collection(e) for e in obj)

        if isinstance(obj, set):
            return {cls.object_to_deep_collection(e) for e in obj}

        return obj

    @classmethod
    def __args_to_list_recursive(cls, arg):
        args_list = []

        if cls.is_iter(arg) and not isinstance(arg, str):
            for a in arg:
                args_list.extend(cls.__args_to_list_recursive(a))
        else:
            args_list.append(arg)

        return args_list
