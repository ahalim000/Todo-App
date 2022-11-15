import time
import inspect


class Flask:
    def __init__(self, name):
        self.name = name
        self.routes = {}

    def route(self, path: str):
        def outer(f):
            self.routes[path] = f
            return f

        return outer

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


class PersonBuilder:
    def __init__(self):
        self._first_name = None
        self._last_name = None
        self._age = None

    def first_name(self, first_name):
        self._first_name = first_name
        return self

    def last_name(self, last_name):
        self._last_name = last_name
        return self

    def age(self, age):
        self._age = age
        return self

    def execute(self):
        if self._first_name is None or self._last_name is None or self._age is None:
            raise Exception("Missing required attributes")

        return Person2(first_name=self._first_name, last_name=self._last_name, age=self._age)


builder = PersonBuilder()
person = builder.first_name("Jules").last_name("Skrill").age(27).execute()
print(person.first_name, person.last_name, person.age)
