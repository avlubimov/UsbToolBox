from enum import Enum, unique
from datetime import datetime

ANNOTATIONS = "__annotations__"


@unique
class TypeRecord(Enum):
    BaseRecord: int = 1
    WhoIs: int = 2
    IsAT: int = 3


class BaseRecord:
    """
    Базовый класс записи (строки) в таблице БД
    Каждое поле (столбец) объявляется в наследуемых классах вместе с типом
    Поля без указания типа не обрабатываются, но будут доступны в классах и подклассах для своих методов

    class Record(BaseRecord)
        __dbtable__ = "main"
        id: int
        name: str = "default"

    Возможны вложеные классы
    class Record(BaseRecord)
        class Json(BaseRecord):
            id:int
            type:int = 1
        id: int
        name: str = "default"
        json: Json

        Поле json при сериализации и десериализации будет обрабатываться рекурсивно,
        Добавляемый класс дожен быть наследником класса BaseRecord.

        При создании объекта можно использовать частичные и полные данные из классов и словарей

        print(Record({"id":4, "type":6})
        print(Record(**{"id":4, "type":6})
        print(Record({"id"=4, "type":6},data={"id":5})
        print(Record(id=4, type=6, data={"id":5})

        Базовый класс предоставляет методы as_dict для рекурсивной выгрузки всех данных экземрляра в словарь
        и метод __str__ возвращающий этот словарь в виде строки
    """

    def __init__(self, dict_or_obj=None, **kwargs):
        """
        Конструктор класса записи.
        Собирает все поля из структуры классов до уровня BaseRecord в поле self.br_fields
        и затем загружает переданные данные в экземпляр класса

        :param dict_or_obj: словарь или класс с частичными или полными  данными
        :param kwargs:  именованные  значения для отдельных полей  **{}
        Значения м аотрибуты структур с именами, которых нет в записи (строке) установлены не будут.
        """

        self.br_fields = self.br_fields_update()

        for k, t in self.br_fields.items():
            try:
                v = self.br_getattr(k, dict_or_obj)
                self.br_set_field_value(k, t, v)
            except (KeyError, AttributeError):
                pass

        for k in kwargs:
            if k in self.br_fields:
                t = self.br_fields[k]
                v = kwargs[k]
                self.br_set_field_value(k, t, v)

    @classmethod
    def br_fields_update(cls):
        fields = {}
        for c in cls.mro():
            fields = {**getattr(c, ANNOTATIONS, {}), **fields}
            if c == BaseRecord:
                break
        return fields

    @property
    def br_fields_exist(self):
        return dict(filter(lambda k: hasattr(self, k[0]), self.br_fields.items()))

    def br_set_field_value(self, k, t, v):
        if issubclass(t, BaseRecord):
            v = t(v)
        setattr(self, k, v)

    @staticmethod
    def br_getattr(key, dict_or_object):
        if issubclass(type(dict_or_object), dict):
            v = dict_or_object[key]
        else:
            v = getattr(dict_or_object, key)
        return v

    @property
    def br_values(self):
        return dict(map(lambda k: (k, getattr(self, k)), self.br_fields_exist))

    @property
    def br_as_dict(self):
        """
        Рекурсивно дампит свое содержимое по списку self._fields в словарь
        :return: словарь данных объекта
        """
        result = {}
        for k, v in self.br_values.items():
            if issubclass(type(v), BaseRecord):
                v = v.br_as_dict
            result[k] = v
        return result

    def br_as_dict_eq(self, other) -> bool:
        """
        Сравнивает дампы объектов
        :param self: BaseRecord
        :param other: BaseRecord
        :return: bool True если равны, False если нет
        """
        # Сравнение имеет смысл только для потомков BaseRecord
        if not isinstance(other, BaseRecord):
            return False

        def dict_loop(one: dict, two: dict) -> bool:
            """
            Рекурсианвя проверка на равенство двух словарей
            :param one: первый словарь
            :param two: второй словарь
            :return: True если равны, False если нет
            """
            for k in {**one, **two}:
                if (k not in one) and (k not in two):
                    # Значения для k нет в обоих дампах, это нормально
                    continue
                if (k not in one) or (k not in two):
                    # Значение для k есть только в одном дампе
                    return False
                # проверка на совпадение типов значений в обоих классах
                if type(one[k]) != type(two[k]):
                    return False
                # если подсловари, рекурсивно проверяем
                if isinstance(one[k], dict) and not dict_loop(one[k], two[k]):
                    return False
                elif one[k] != two[k]:
                    return False
            return True

        return dict_loop(self.br_as_dict, other.br_as_dict)

    def __str__(self):
        return str(self.br_as_dict)


class Record(BaseRecord):
    id: int
    type: int
    time: datetime


class WhoIs(Record):
    type = 7

    class Data(BaseRecord):
        hwsrc: str
        pdst: str

    data: Data


class Registry(dict):
    def add(self, tr: TypeRecord, br: BaseRecord):
        self[tr] = br


if __name__ == "__main__":
    class obj_src1:
        hwsrc = "12345"
        pdst = "333333"


    dict_src1 = {
        "hwsrc": "12345",
        "pdst": "333333"
    }


    class obj_src2:
        type = 4
        id = 1

        class data:
            hwsrc = "hw_src2"
            pdst = "pdst_src2"


    dict_src2 = {
        "type": 4,
        "id": 1,
        "data": {
            "hwsrc": "hw_src2",
            "pdst": "pdst_src2"
        }
    }

    obj = WhoIs(id=4, type=6, data={"hwsrc": "eeee"})
    print(WhoIs(dict_src2))
    print(WhoIs(obj_src2))
    print(WhoIs(id=5, data=dict_src1))
    print(WhoIs(id=6, data=obj_src1))

    # print("Стр", obj)
    # print("Fields", obj.br_fields)
    # print("br_fields_exist", obj.br_fields_exist)
    # print("br_values", obj.br_values)
    #
    # print(WhoIs(obj_src2).br_as_dict_eq(WhoIs(obj_src2)))

