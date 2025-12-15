from typing import Dict, Type, Optional, Any, Tuple
from pydantic import BaseModel, create_model


def extract_infra_fields(infra: BaseModel) -> Dict[str, Tuple[Any, Any]]:
    infra_dict = infra.model_dump(exclude_unset=False)
    fields = {}
    
    for field_name, field_info in infra.__class__.model_fields.items():
        if field_name in infra_dict and infra_dict[field_name] is not None:
            fields[field_name] = (Optional[field_info.annotation], infra_dict[field_name])
        else:
            fields[field_name] = (field_info.annotation, field_info)
    
    return fields


def extract_args_fields(args: Type[BaseModel]) -> Dict[str, Tuple[Any, Any]]:
    fields = {}
    
    for field_name, field_info in args.model_fields.items():
        fields[field_name] = (field_info.annotation, field_info)
    
    return fields


def create_schema_name(pipeline_name: str) -> str:
    return pipeline_name.title().replace("-", "").replace("_", "")


def build_pipeline_schema(
    name: str,
    args: Optional[Type[BaseModel]] = None,
    infra: Optional[BaseModel] = None
) -> Type[BaseModel]:
    schema_fields = {}
    
    if infra:
        schema_fields.update(extract_infra_fields(infra))
    
    if args:
        schema_fields.update(extract_args_fields(args))
    
    schema_name = create_schema_name(name)
    return create_model(schema_name, **schema_fields)
