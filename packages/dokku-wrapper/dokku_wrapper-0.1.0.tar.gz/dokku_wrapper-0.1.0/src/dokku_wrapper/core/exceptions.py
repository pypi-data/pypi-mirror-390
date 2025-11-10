class DokkuError(Exception):
    """Erro base para o wrapper Dokku."""


class DokkuCommandError(DokkuError):
    def __init__(self, command, message):
        super().__init__(f"Erro executando {' '.join(command)}: {message}")
        self.command = command
        self.message = message


class AppAlreadyExists(DokkuError):
    def __init__(self, name: str):
        super().__init__(f"O app '{name}' já existe.")


class AppNotFound(DokkuError):
    def __init__(self, name: str):
        super().__init__(f"O app '{name}' não foi encontrado.")
