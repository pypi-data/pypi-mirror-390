from aitrados_api.trade_middleware.request import FrontendRequest, AsyncFrontendRequest

from aitrados_broker.trade_middleware_service.trade_middleware_rpc_service import AitradosBrokerBackendService


def broker_request(fun_name,*args,**kwargs):
    result = FrontendRequest.call_sync(
        AitradosBrokerBackendService.IDENTITY.backend_identity,
        fun_name, *args, **kwargs,
    )
    return result

async def a_broker_request(fun_name,*args,**kwargs):
    result = await AsyncFrontendRequest.call_sync(
        AitradosBrokerBackendService.IDENTITY.backend_identity,
        fun_name, *args, **kwargs,
    )
    return result