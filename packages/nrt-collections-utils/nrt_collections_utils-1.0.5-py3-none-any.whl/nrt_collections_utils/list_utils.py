

class ListUtil:
    @staticmethod
    def compare_lists(list_1: list, list_2: list) -> bool:
        if len(list_1) != len(list_2):
            return False

        for item in list_1:
            if item not in list_2:
                return False

        for item in list_2:
            if item not in list_1:
                return False

        return True

    @staticmethod
    def get_common_elements(list_1: list, list_2: list) -> list:
        return [item for item in list_1 if item in list_2]

    @staticmethod
    def remove_none(list_: list):
        return [o for o in list_ if o is not None]

    @staticmethod
    def remove_empty(list_: list):
        return [o for o in list_ if o or isinstance(o, (int, float))]

    @staticmethod
    def remove_duplicates(list_: list):
        return list(set(list_))

    @staticmethod
    def get_intersection_list(list_1: list, list_2: list) -> list:
        return list(set(list_1) & set(list_2))
