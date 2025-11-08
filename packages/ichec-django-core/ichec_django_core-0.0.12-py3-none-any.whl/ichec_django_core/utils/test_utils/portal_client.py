import logging

from pydantic import BaseModel

from .rest_client import RestClient
from .models import (
    get_path_from_item,
    get_path_from_type,
    get_type,
    Resource,
    Timestamped,
)

logger = logging.getLogger(__name__)


class Paginated(BaseModel, frozen=True):

    count: int = 0
    next: str | None = None
    previous: str | None = None
    results: list[Timestamped] = []


class PortalClient(RestClient):

    def get_items(self, item_t, page: int = 1) -> Paginated:
        path = get_path_from_type(item_t)
        return_t = get_type(path, "list")

        ret_json = self.get(path)
        if ret_json:
            return Paginated(
                count=ret_json["count"],
                next=ret_json["next"],
                previous=ret_json["previous"],
                results=[return_t(**item) for item in ret_json["results"]],
            )
        else:
            return Paginated()

    def get_item(self, id, item_t) -> Timestamped:
        path = get_path_from_type(item_t)
        return_t = get_type(path, "detail")
        return_json = self.get(f"{path}/{id}")
        return return_t(**return_json)

    def create_item(self, resource: BaseModel) -> Timestamped:
        path = get_path_from_item(resource)
        print(resource.model_dump(mode="json"))
        create_json = self.post(path, resource.model_dump(mode="json"))
        return get_type(path, "detail")(**create_json)

    def create_items(self, resources: list[BaseModel]) -> list[Timestamped]:
        return [self.create_item(item) for item in resources]

    def delete_item(self, resource: Resource):
        self.delete(f"{get_path_from_item(resource)}/{resource.id}/")
