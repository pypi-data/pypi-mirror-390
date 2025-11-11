# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any
from importlib.resources import files
import jsonschema
import json

import pytest


def test_schema():
    print("Testing schema")
    import os

    def _load_schema() -> dict[str, Any]:
        schema_path = files("pristy.schema").joinpath("node_injector.schema.json")
        with schema_path.open("r") as schema_file:
            content = json.load(schema_file)
        return content

    schema = _load_schema()

    test_dir = os.path.dirname(__file__)
    sample_file = os.path.join(test_dir, "sample_nodes.json")

    with open(sample_file, "rb") as f:
        node = f.read()
        print(node)
    node_json = json.loads(node)
    for node in node_json:
        print(node)
        jsonschema.validate(node, schema=schema)


def test_fail_schema():
    print("Testing schema")
    import os

    def _load_schema() -> dict[str, Any]:
        schema_path = files("pristy.schema").joinpath("node_injector.schema.json")
        with schema_path.open("r") as schema_file:
            content = json.load(schema_file)
        return content

    schema = _load_schema()

    test_dir = os.path.dirname(__file__)
    sample_file = os.path.join(test_dir, "sample_fail_nodes.json")

    with open(sample_file, "rb") as f:
        node = f.read()
        print(node)
    node_json = json.loads(node)
    for node in node_json:
        print(node)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(node, schema=schema)
