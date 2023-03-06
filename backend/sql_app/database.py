from contextvars import ContextVar
import peewee

HOST = 'db'
USER = 'postgres'
PASS = 'postgres'
PORT = 5432
DB = 'default'

db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


db = peewee.PostgresqlDatabase(
    DB, user=USER, password=PASS, host=HOST, port=PORT
)

db._state = PeeweeConnectionState()