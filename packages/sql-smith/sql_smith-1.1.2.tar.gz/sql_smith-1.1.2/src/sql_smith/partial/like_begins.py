from sql_smith.interfaces import StatementInterface


class LikeBegins(StatementInterface):
    def __init__(self, value: str):
        self._value = value

    def sql(self, engine: "EngineInterface") -> str:
        return engine.get_parameter_placeholder()

    def params(self, engine: "EngineInterface") -> tuple:
        value = engine.escape_like(self._value)
        return (value + "%",)
