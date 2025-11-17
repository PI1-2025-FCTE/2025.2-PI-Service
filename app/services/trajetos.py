from app.repositories.trajetos import TrajetoRepository
from app.schemas import TrajetoUpdate

class TrajetoService:
    def __init__(self, repo: TrajetoRepository):
        self.repo = repo

    def create_trajeto(self, comandos_enviados: str):
        return self.repo.create(comandos_enviados)

    def update_trajeto(self, trajeto_id: int, data: dict):
        update_data = TrajetoUpdate.model_validate(data, strict=False).model_dump(exclude_unset=True)
        return self.repo.update(trajeto_id, update_data)

    def list_trajetos(self):
        return self.repo.list_all()

    def get_trajeto(self, trajeto_id: int):
        return self.repo.get(trajeto_id)

    def delete_trajeto(self, trajeto_id: int):
        self.repo.delete(trajeto_id)
