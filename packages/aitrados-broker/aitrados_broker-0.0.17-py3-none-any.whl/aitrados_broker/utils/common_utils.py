import dataclasses
from aitrados_api.common_lib.response_format import ErrorResponse, UnifiedResponse

def broker_data_to_dict(data:any):
    if isinstance(data, list):
        return [dataclasses.asdict(item) for item in data]
    else:
        return dataclasses.asdict(data)

def  broker_data_to_json(data:any):
    new_data=broker_data_to_dict(data)
    return UnifiedResponse(result=new_data).model_dump_json()




