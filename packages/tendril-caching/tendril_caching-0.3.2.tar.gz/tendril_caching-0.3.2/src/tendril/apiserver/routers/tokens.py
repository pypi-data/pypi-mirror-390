

from fastapi import APIRouter
from fastapi import Depends

from tendril.apiserver.security import security
from tendril.apiserver.security import swagger_auth
from tendril.caching.tokens import GenericTokenTModel
from tendril.caching.tokens import read

from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


tokens_router = APIRouter(prefix='/tokens',
                          tags=["Tokens API"],
                          dependencies=[Depends(swagger_auth),
                                        security(scopes=['interests:common'])]
                          )


@tokens_router.get("/{namespace}/{key}",
                   response_model=GenericTokenTModel)
async def get_token(namespace: str, key: str):
    return read(namespace=namespace, key=key)


routers = [
    tokens_router
]
