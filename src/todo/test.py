import time
import inspect
import string


class Flask:
    def __init__(self, name):
        self.name = name
        self.routes = {}

    def route(self, path: str):
        def decorator(f):
            self.routes[path] = f
            return f

        return decorator

    def dispatch(self, path: str):
        return self.routes[path]()


fake_app = Flask(__name__)


@fake_app.route("/")
def helloworld():
    return "Hello"


class Person:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self._age = None

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    @property
    def age(self):
        if self._age is None:
            time.sleep(3)  # Expensive calculation/operation
            self._age = 27

        return self._age

    @age.setter
    def age(self, val):
        self._age = val


person = Person("Jules", "Skrill")
# print(person.name)
# print(person.age)
# print(person.age)
# person.age = 30
# print(person.age)
# print(person.age)
# print(person.age)


class Person2:
    first_name = "John"
    last_name = "Doe"
    age = 7
    height = "5ft"

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self.__class__, key):
                raise Exception(f'Invalid Keyword arg "{key}"')
            setattr(self, key, val)

    @classmethod
    def get_class_attributes(cls):
        res = {}
        for key, val in vars(cls).items():
            if not key.startswith("__") and not inspect.isfunction(val) and not isinstance(val, classmethod):
                res[key] = val

        return res


person = Person2(first_name="Jules", last_name="Skrill", age=27)
# print(person.first_name)
# print(person.last_name)
# print(person.age)
# print(person.get_class_attributes, inspect.ismethod(person.get_class_attributes))
# from pprint import pprint

# pprint(dict(person.get_class_attributes()))


class Person3:
    def __init__(self, first_name, last_name, age):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age


class PersonBuilder:
    def __init__(self):
        self._first_name = None
        self._last_name = None
        self._age = None

    def set_first_name(self, first_name):
        self._first_name = first_name
        return self

    def set_last_name(self, last_name):
        self._last_name = last_name
        return self

    def set_age(self, age):
        self._age = age
        return self

    def execute(self):
        if self._first_name is None or self._last_name is None or self._age is None:
            raise Exception("Missing required attributes")

        return Person3(first_name=self._first_name, last_name=self._last_name, age=self._age)


class Query:
    def __init__(self, model, joins=None, filters=None):
        self.model = model
        self.joins = joins if joins is not None else []
        self.filters = filters if filters is not None else []

    def filter_by(self, filter_obj):
        self.filters.append(filter_obj)
        return self

    def join(self, db_class):
        self.joins.append(db_class)
        return self

    def clone(self):
        return Query(self.model, self.joins, self.filters)


builder = PersonBuilder()
person = builder.set_first_name("Jules").set_last_name("Skrill").set_age(27).execute()
print(person.first_name, person.last_name, person.age)


def convert_base(
    num_s: str,
    target_base: int,
    current_base: int = 10,
    current_alphabet: str = "0123456789" + string.ascii_uppercase,
    target_alphabet: str = "0123456789" + string.ascii_uppercase,
) -> str:

    base_10 = 0
    digit = len(num_s) - 1
    for character in num_s:
        character_val = current_alphabet.index(character)
        base_10 += (current_base**digit) * character_val
        digit -= 1

    converted_num = ""
    floored_quotient = base_10
    while floored_quotient != 0:
        converted_num = target_alphabet[floored_quotient % target_base] + converted_num
        floored_quotient //= target_base

    if converted_num == "":
        converted_num = target_alphabet[0]

    return converted_num


def get_lexical_average(string1: str, string2: str) -> str:
    base10_string1 = int(convert_base(string1, 10, 26, string.ascii_lowercase))
    base10_string2 = int(convert_base(string2, 10, 26, string.ascii_lowercase))

    avg = (base10_string1 + base10_string2) // 2

    return convert_base(str(avg), 26, 10, target_alphabet=string.ascii_lowercase)


# @app.route("/api/todos/<int:id>/reorder", methods=["PUT"])
# def reorder_todo(id):
#     todo = db.session.query(Todo).filter_by(id=id).one()
#     request_data = request.get_json()
#     todo_item_id = request_data["todo_item_id"]
#     todo_item = db.session.query(TodoItem).filter_by(id=todo_item_id).filter_by(todo_id=id).one()

#     insert_idx = request_data["insert_idx"]
#     above_idx = insert_idx - 1
#     above_todo_item = todo.todo_items[above_idx]
#     insert_position = todo.todo_items[insert_idx].position
#     above_position = todo.todo_items[above_idx].position

#     lex_avg = get_lexical_rank(insert_position, above_position)
#     todo_item.position = lex_avg

#     db.session.add(todo_item)
#     db.session.commit()

#     return Response(status=201)


def get_lexical_rank(string1, string2):
    string1 = string1.lstrip("a")
    if string1 == "":
        string1 = "a"

    string2 = string2.lstrip("a")
    if string2 == "":
        string2 = "a"

    max_len = max(len(string1), len(string2))

    while len(string1) < max_len:
        string1 += "a"

    while len(string2) < max_len:
        string2 += "a"

    lex_avg = get_lexical_average(string1, string2)

    if lex_avg == string1:
        lex_avg += "n"

    return lex_avg


# for str1, str2 in [("ba", "babc"), ("b", "c"), ("c", "caab"), ("aaa", "c")]:
#     ave = get_lexical_rank(str1, str2)
#     assert str1 < ave
#     assert ave < str2
#     print(ave)


class Shape:
    smiles = {"very": "happy"}


class Square(Shape):
    pass


class Circle(Shape):
    pass
