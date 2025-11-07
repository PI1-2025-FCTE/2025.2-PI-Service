from typing import Optional

class CustomException(Exception):
    """
    Classe base para todas as exceções customizadas da aplicação.

    Atributos:
        code (int): HTTP status code.
        message (str): Mensagem padrão do erro.
    """
    code: int = 500
    message: str = "Erro interno do servidor"

    def __init__(self, message: Optional[str] = None):
        if message is not None:
            self.message = message
        super().__init__(self.message)
