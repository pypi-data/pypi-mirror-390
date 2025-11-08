#!/usr/bin/env python3
"""Filter OpenAPI spec to include only SDK-tagged endpoints.

This script extracts endpoints tagged with "SDK" from the OpenAPI specification
and creates a filtered spec that includes only those endpoints and their
referenced schemas.

Usage:
    python scripts/filter_sdk_endpoints.py <input.json> <output.json>
"""

import json
import sys
from pathlib import Path
from typing import Any


def collect_schema_refs(obj: Any, schemas: set[str], visited: set[int]) -> None:
    """Recursively collect schema references from an object.

    Args:
        obj: Object to scan for $ref references
        schemas: Set to collect schema names into
        visited: Set of visited object IDs to avoid infinite recursion
    """
    if obj is None:
        return

    obj_id = id(obj)
    if obj_id in visited:
        return
    visited.add(obj_id)

    if isinstance(obj, dict):
        # Check for $ref
        if "$ref" in obj:
            ref = obj["$ref"]
            if ref.startswith("#/components/schemas/"):
                schema_name = ref.split("/")[-1]
                schemas.add(schema_name)

        # Recurse into dict values
        for value in obj.values():
            collect_schema_refs(value, schemas, visited)

    elif isinstance(obj, list):
        # Recurse into list items
        for item in obj:
            collect_schema_refs(item, schemas, visited)


def collect_all_related_schemas(spec: dict[str, Any], initial_schemas: set[str]) -> set[str]:
    """Collect all schemas related to the initial set, including nested refs.

    Args:
        spec: Full OpenAPI specification
        initial_schemas: Set of initial schema names

    Returns:
        Complete set of all related schema names
    """
    all_schemas = spec.get("components", {}).get("schemas", {})
    collected = set(initial_schemas)
    to_process = list(initial_schemas)

    while to_process:
        schema_name = to_process.pop()
        if schema_name not in all_schemas:
            continue

        schema_def = all_schemas[schema_name]
        visited: set[int] = set()
        new_refs: set[str] = set()
        collect_schema_refs(schema_def, new_refs, visited)

        # Add new schemas to process
        for ref in new_refs:
            if ref not in collected:
                collected.add(ref)
                to_process.append(ref)

    return collected


def filter_sdk_endpoints(spec: dict[str, Any]) -> dict[str, Any]:
    """Filter OpenAPI spec to keep only SDK-tagged endpoints.

    Args:
        spec: Full OpenAPI specification

    Returns:
        Filtered OpenAPI specification with only SDK endpoints
    """
    filtered_paths: dict[str, Any] = {}
    used_schemas: set[str] = set()

    # Filter paths by SDK tag
    for path, methods in spec.get("paths", {}).items():
        filtered_methods: dict[str, Any] = {}

        for method, operation in methods.items():
            if not isinstance(operation, dict):
                continue

            tags = operation.get("tags", [])
            if "SDK" in tags:
                filtered_methods[method] = operation

                # Collect schemas from this operation
                visited: set[int] = set()
                collect_schema_refs(operation, used_schemas, visited)

        if filtered_methods:
            filtered_paths[path] = filtered_methods

    # Collect all related schemas (including nested references)
    all_related_schemas = collect_all_related_schemas(spec, used_schemas)

    # Build filtered spec
    filtered_spec = {
        "openapi": spec["openapi"],
        "info": spec["info"],
        "servers": spec.get("servers", []),
        "paths": filtered_paths,
        "components": {
            "schemas": {},
            "securitySchemes": spec.get("components", {}).get("securitySchemes", {}),
        },
    }

    # Add security if present
    if "security" in spec:
        filtered_spec["security"] = spec["security"]

    # Include only used schemas
    all_schemas = spec.get("components", {}).get("schemas", {})
    for schema_name in all_related_schemas:
        if schema_name in all_schemas:
            filtered_spec["components"]["schemas"][schema_name] = all_schemas[schema_name]

    # Filter tags to only include SDK and related tags
    relevant_tags = {"SDK", "OCR", "Upload", "Models"}
    if "tags" in spec:
        filtered_spec["tags"] = [t for t in spec["tags"] if t.get("name") in relevant_tags]

    return filtered_spec


def main() -> None:
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python filter_sdk_endpoints.py <input.json> <output.json>")
        print()
        print("Filters OpenAPI spec to include only SDK-tagged endpoints")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Load spec
    print(f"Loading OpenAPI spec from {input_path}...")
    with open(input_path) as f:
        spec = json.load(f)

    # Filter endpoints
    print("Filtering SDK endpoints...")
    filtered = filter_sdk_endpoints(spec)

    # Count results
    endpoint_count = sum(len(methods) for methods in filtered["paths"].values())
    schema_count = len(filtered["components"]["schemas"])

    # Save filtered spec
    print(f"Writing filtered spec to {output_path}...")
    with open(output_path, "w") as f:
        json.dump(filtered, f, indent=2)

    print()
    print(f"✓ Filtered {endpoint_count} SDK endpoints")
    print(f"✓ Included {schema_count} related schemas")
    print(f"✓ Saved to {output_path}")


if __name__ == "__main__":
    main()
