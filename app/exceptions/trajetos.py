from app.exceptions.base import CustomException

class TrajetoNotFoundException(CustomException):
    code = 404
    message = "Trajeto não encontrado"
