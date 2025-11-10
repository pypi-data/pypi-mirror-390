from typing import List, Optional, Union
from uuid import UUID

from ..core import paginate
from .base_models import ImageConnection
from .base_models import ImagePresigned as ImagePresignedType
from .gql_client import HLClient

__all__ = [
    "get_presigned_url",
    "get_presigned_urls",
]


def get_presigned_url(
    client: HLClient,
    id: int,
):
    """Return a single ImagePresignedType BaseModel
    for the given file id
    """
    result = client.image(
        return_type=ImagePresignedType,
        id=id,
    )
    return result


def get_presigned_urls(
    client,
    ids: List[int],
    uuids: List[Union[UUID, str]],
):
    """Return a generator of ImagePresignedType GQLBaseModels
    for the given list of file ids
    """
    kwargs = {}
    if ids:
        kwargs["id"] = ids
    if uuids:
        kwargs["uuid"] = uuids

    return paginate(
        client.imageConnection,
        ImageConnection,
        **kwargs,
    )
