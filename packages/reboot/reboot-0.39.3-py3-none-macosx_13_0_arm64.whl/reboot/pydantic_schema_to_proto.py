#!/usr/bin/env python3

import aiofiles
import os
import typing
from importlib.util import module_from_spec, spec_from_file_location
from pydantic import BaseModel  # type: ignore[import]
from reboot.cli import terminal
from rebootdev.api import API, to_pascal_case
from typing import Dict, List, Optional, Union, get_args, get_origin


def get_field_tag(field_info) -> int:
    """Get the tag from a Pydantic field's json_schema_extra."""
    json_schema_extra = getattr(field_info, 'json_schema_extra', {})
    if isinstance(json_schema_extra, dict) and 'tag' in json_schema_extra:
        return json_schema_extra['tag']
    raise ValueError("Field does not have a valid 'tag'")


async def generate(
    proto,
    schema: typing.Union[
        typing.Type[BaseModel],
        typing.Type[dict],
        typing.Type[list],
    ],
    path: str,
    name: Optional[str] = None,
    state: bool = False,
):
    origin = get_origin(schema)
    args = get_args(schema)

    if isinstance(schema, type) and issubclass(schema, BaseModel):
        assert name is not None

        await proto.write(f"message {name} {{\n")

        if state:
            await proto.write("  option (rbt.v1alpha1.state) = {};\n")

        tags: Dict[int, str] = {}

        # Type assertion to help Pylance understand schema is a BaseModel
        # and do not complain.
        base_model_schema: typing.Type[BaseModel] = schema
        for field_name, field_info in base_model_schema.model_fields.items():
            field_type = field_info.annotation

            try:
                tag = get_field_tag(field_info)
            except ValueError:
                terminal.fail(
                    f"Missing tag for property '{field_name}' at '{path}'; "
                    f"all properties must be tagged for backwards compatibility"
                )

            if tag in tags:
                terminal.fail(
                    f"Trying to use tag {tag} with property '{field_name}' "
                    f"already used by '{tags[tag]}' at '{path}'"
                )

            tags[tag] = field_name

            proto_field_name = field_name

            inner_type = field_type

            field_origin = get_origin(field_type)
            field_args = get_args(field_type)

            # Get inner type for 'Optional[T]' if possible.
            if field_origin is Union and type(None) in field_args and len(
                field_args
            ) == 2:
                inner_type = next(
                    arg for arg in field_args if arg is not type(None)
                )

            # The 'inner_type' represents the actual type, i.e. 'list[list[...]]]',
            # '<class 'str'>', '<class 'int'>', etc. So we need to get
            # the real type to handle for complex structures. For primitive
            # types the 'inner_origin' will be 'None'.
            inner_origin = get_origin(inner_type)

            if inner_type == str:
                assert inner_origin is None
                await proto.write(
                    f"  optional string {proto_field_name} = {tag};\n"
                )
            elif inner_type == int:
                assert inner_origin is None
                await proto.write(
                    f"  optional int64 {proto_field_name} = {tag};\n"
                )
            elif inner_type == float:
                assert inner_origin is None
                await proto.write(
                    f"  optional double {proto_field_name} = {tag};\n"
                )
            elif inner_type == bool:
                assert inner_origin is None
                await proto.write(
                    f"  optional bool {proto_field_name} = {tag};\n"
                )
            elif inner_origin in (list, List):
                type_name = to_pascal_case(field_name) + "Array"
                await proto.write(f"  message {type_name} {{\n")
                await generate(proto, inner_type, f"{path}.{field_name}")
                await proto.write("  }\n")
                await proto.write(
                    f"  optional {type_name} {proto_field_name} = {tag};\n"
                )
            elif inner_origin in (dict, Dict):
                type_name = to_pascal_case(field_name) + "Record"
                await proto.write(f"  message {type_name} {{\n")
                await generate(proto, inner_type, f"{path}.{field_name}")
                await proto.write("  }\n")
                await proto.write(
                    f"  optional {type_name} {proto_field_name} = {tag};\n"
                )
            elif isinstance(inner_type,
                            type) and issubclass(inner_type, BaseModel):
                type_name = to_pascal_case(field_name)
                await generate(
                    proto,
                    inner_type,
                    f"{path}.{field_name}",
                    name=type_name,
                )
                await proto.write(
                    f"  optional {type_name} {proto_field_name} = {tag};\n"
                )
            elif not field_args and inner_origin is None:
                # Better error message for unparameterized generics.
                #
                # 'inner_origin' becomes 'None' there, since there is no
                # args specified (i.e. 'list' instead of 'list[str]').
                terminal.fail(
                    f"'{path}.{field_name}' has collection type '{inner_type}' "
                    "which doesn't have an element type specified. Please specify "
                    "the element type, e.g., 'list[str]' or 'dict[str, int]'."
                )
            else:
                terminal.fail(
                    f"'{path}.{field_name}' has type '{inner_type}' which is not "
                    f"(yet) supported, please reach out to the maintainers!"
                )

        await proto.write("}\n")
    elif origin in (dict, Dict):
        if len(args) >= 2:
            key_type = args[0]
            value_type = args[1]

            if key_type != str:
                terminal.fail(
                    f"Unexpected 'dict' key type '{key_type}' at '{path}'; "
                    f"only 'string' key types are currently supported for 'dict's"
                )

            value_origin = get_origin(value_type)

            if value_type == str:
                type_name = "string"
            elif value_type == int:
                type_name = "int64"
            elif value_type == float:
                type_name = "double"
            elif value_type == bool:
                type_name = "bool"
            elif value_origin in (list, List):
                type_name = "Value"
                await proto.write("  message Value {\n")
                await generate(proto, value_type, f"{path}.[value]")
                await proto.write("  }\n")
            elif value_origin in (dict, Dict):
                type_name = "Value"
                await proto.write("  message Value {\n")
                await generate(proto, value_type, f"{path}.[value]")
                await proto.write("  }\n")
            elif isinstance(value_type,
                            type) and issubclass(value_type, BaseModel):
                type_name = value_type.__name__
                await generate(
                    proto,
                    value_type,
                    f"{path}.[value]",
                    name=type_name,
                )
            else:
                terminal.fail(
                    f"Dictionary at '{path}' has value type '{value_type}' which is not "
                    f"(yet) supported"
                )

            await proto.write(f"    map<string, {type_name}> record = 1;\n")
        else:
            terminal.fail(
                f"Dictionary type at '{path}' must have key and value types, "
                f"e.g., dict[str, int]"
            )
    elif origin in (list, List):
        if args:
            element_type = args[0]
            element_origin = get_origin(element_type)

            if element_type == str:
                type_name = "string"
            elif element_type == int:
                type_name = "int64"
            elif element_type == float:
                type_name = "double"
            elif element_type == bool:
                type_name = "bool"
            elif element_origin in (list, List):
                type_name = "Element"
                await proto.write("  message Element {\n")
                await generate(proto, element_type, f"{path}.[element]")
                await proto.write("  }\n")
            elif element_origin in (dict, Dict):
                type_name = "Element"
                await proto.write("  message Element {\n")
                await generate(proto, element_type, f"{path}.[element]")
                await proto.write("  }\n")
            elif isinstance(element_type,
                            type) and issubclass(element_type, BaseModel):
                type_name = element_type.__name__
                await generate(
                    proto, element_type, f"{path}.[element]", name=type_name
                )
            else:
                terminal.fail(
                    f"List at '{path}' has element type '{element_type}' which is not "
                    f"(yet) supported"
                )

            await proto.write(f"    repeated {type_name} elements = 1;\n")
        else:
            terminal.fail(
                f"List type at '{path}' must have an element type, e.g., list[str]"
            )

    else:
        terminal.fail(f"Unexpected type '{schema}' at '{path}'")


async def generate_proto_file_from_api(
    filename: str,
    proto_directory: str,
    output_directory: str,
) -> Optional[str]:
    """Write the generated proto content to a file.
    Return the path to the generated proto file or None if file doesn't
    contain Pydantic API schema."""
    relative_file_path = os.path.join(proto_directory, filename)

    spec = spec_from_file_location("temp_module", relative_file_path)
    if spec is None or spec.loader is None:
        terminal.fail(f"Failed to load module from {relative_file_path}")

    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        terminal.fail(f"Failed to execute module {relative_file_path}: {e}")

    if not hasattr(module, 'api'):
        # It could be that the module does not define an API, but has some
        # shared code. In that case, we just skip it, but allow processing
        # further files.
        return None

    api: API = getattr(module, 'api')

    proto_file_name = filename.replace('.py', '.proto')
    proto_file_path = os.path.join(output_directory, proto_file_name)
    package_name = os.path.dirname(filename).replace(os.sep, '.')

    os.makedirs(os.path.dirname(proto_file_path), exist_ok=True)

    generated_errors_names = set()

    async with aiofiles.open(proto_file_path, 'w') as proto:
        await proto.write('syntax = "proto3";\n')
        await proto.write(f'package {package_name};\n')
        await proto.write('import "google/protobuf/empty.proto";\n')
        await proto.write('import "google/protobuf/struct.proto";\n')
        await proto.write('import "rbt/v1alpha1/options.proto";\n')
        await proto.write('import "rbt/v1alpha1/tasks.proto";\n')
        await proto.write(
            f"option (rbt.v1alpha1.file).pydantic = "
            f"\"{filename.rsplit('.py', 1)[0].replace(os.sep, '.')}\";\n"
        )
        await proto.write('\n')

        for type_name, type_obj in api.get_types().items():
            await generate(
                proto,
                type_obj.state,
                f"api.{type_name}.state",
                name=type_name,
                state=True,
            )
            await proto.write('\n')

            for method_name, method_spec in type_obj.methods.items():
                request_type_name = f"{type_name}{to_pascal_case(method_name)}Request"

                await generate(
                    proto,
                    method_spec.request,
                    f"api.{type_name}.methods.{method_name}.request",
                    name=request_type_name,
                )
                await proto.write('\n')

                if method_spec.response is not None:
                    response_type_name = f"{type_name}{to_pascal_case(method_name)}Response"

                    await generate(
                        proto,
                        method_spec.response,
                        f"api.{type_name}.methods.{method_name}.response",
                        name=response_type_name,
                    )
                    await proto.write('\n')

            for method_name, method_spec in type_obj.methods.items():
                if method_spec.errors:
                    for error_model in method_spec.errors:
                        error_type_name = error_model.__name__
                        if error_type_name in generated_errors_names:
                            continue
                        generated_errors_names.add(error_type_name)
                        await generate(
                            proto,
                            error_model,
                            f"api.{type_name}.methods.{method_name}.errors.{error_type_name}",
                            name=error_type_name,
                        )
                        await proto.write('\n')

            await proto.write(f"service {type_name}Methods {{\n")

            for method_name, method_spec in type_obj.methods.items():
                request_type_name = f"{type_name}{to_pascal_case(method_name)}Request"

                if method_spec.response is None:
                    response_type_name = "google.protobuf.Empty"
                else:
                    response_type_name = f"{type_name}{to_pascal_case(method_name)}Response"

                await proto.write(
                    f"  rpc {to_pascal_case(method_name)}({request_type_name})\n"
                )
                await proto.write(f"      returns ({response_type_name}) {{\n")
                await proto.write("    option (rbt.v1alpha1.method) = {\n")
                await proto.write(f"      {method_spec.kind.value}: {{\n")

                if method_spec.factory:
                    await proto.write("        constructor: {},\n")

                await proto.write("      },\n")

                if method_spec.errors:
                    error_names = [
                        f'"{error.__name__}"' for error in method_spec.errors
                    ]
                    await proto.write(
                        f"      errors: [{', '.join(error_names)}],\n"
                    )

                await proto.write("    };\n")
                await proto.write("  }\n")

            await proto.write("}\n\n")

    return proto_file_name
