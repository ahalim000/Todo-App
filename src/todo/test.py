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
