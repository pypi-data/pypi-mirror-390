from .services.apps import Apps


class Dokku:
    """Interface principal para interação com o Dokku."""

    def __init__(self):
        self.apps = Apps()
