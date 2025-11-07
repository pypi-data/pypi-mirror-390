class EdgeLambdaConfiguration:
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __init__(self, **kwargs) -> None:

        self._values = kwargs

        for key, value in kwargs.items():
            self[key] = value
