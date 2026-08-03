"""DataHub MCP read and write-back adapter."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


class McpDependencyError(RuntimeError):
    """Raised when the optional FastMCP dependency is unavailable."""


class McpContractError(RuntimeError):
    """Raised when required DataHub MCP tools are missing or malformed."""


@dataclass(frozen=True)
class DataHubReadResult:
    context: dict[str, Any]
    raw: dict[str, Any]


class DataHubMcp:
    def __init__(self, *, gms_url: str, token: str | None = None) -> None:
        try:
            from fastmcp import Client
        except ImportError as exc:
            raise McpDependencyError(
                "Install the datahub extra: pip install -e '.[datahub]'"
            ) from exc
        env = {
            key: os.environ[key]
            for key in ("PATH", "HOME", "VIRTUAL_ENV", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE")
            if key in os.environ
        }
        env.update(
            {
                "DATAHUB_GMS_URL": gms_url,
                "TOOLS_IS_MUTATION_ENABLED": "true",
            }
        )
        if token:
            env["DATAHUB_GMS_TOKEN"] = token
        self._client = Client(
            {
                "mcpServers": {
                    "datahub": {
                        "transport": "stdio",
                        "command": "mcp-server-datahub",
                        "args": [],
                        "env": env,
                    }
                }
            }
        )

    @classmethod
    def from_env(cls) -> DataHubMcp:
        gms_url = os.environ.get("DATAHUB_GMS_URL", "http://localhost:8080")
        token = os.environ.get("DATAHUB_GMS_TOKEN") or None
        return cls(gms_url=gms_url, token=token)

    @staticmethod
    def _data(result: Any) -> Any:
        if getattr(result, "data", None) is not None:
            return result.data
        content = getattr(result, "content", None)
        if content and getattr(content[0], "text", None):
            import json

            return json.loads(content[0].text)
        raise McpContractError("MCP_RESULT_DATA_MISSING")

    async def _tool_names(self) -> set[str]:
        return {tool.name for tool in await self._client.list_tools()}

    @staticmethod
    def _resolve(tool_names: set[str], base_name: str) -> str:
        for candidate in (f"datahub_{base_name}", base_name):
            if candidate in tool_names:
                return candidate
        raise McpContractError(f"MCP_TOOL_MISSING:{base_name}")

    async def read_context(self, dataset_urn: str) -> DataHubReadResult:
        async with self._client:
            names = await self._tool_names()
            get_entities = self._resolve(names, "get_entities")
            list_schema = self._resolve(names, "list_schema_fields")
            get_lineage = self._resolve(names, "get_lineage")
            entity_result = self._data(
                await self._client.call_tool(get_entities, {"urns": dataset_urn})
            )
            schema_result = self._data(
                await self._client.call_tool(
                    list_schema, {"urn": dataset_urn, "limit": 100, "offset": 0}
                )
            )
            lineage_bounds = {"max_hops": 1, "max_results": 5}
            upstream_result = self._data(
                await self._client.call_tool(
                    get_lineage,
                    {
                        "urn": dataset_urn,
                        "upstream": True,
                        **lineage_bounds,
                    },
                )
            )
            upstream_urns = self._dataset_urns(upstream_result) - {dataset_urn}
            if upstream_urns:
                downstream_result: Any = {
                    "status": "NOT_QUERIED_UPSTREAM_LINEAGE_PRESENT",
                    "searchResults": [],
                }
            else:
                downstream_result = self._data(
                    await self._client.call_tool(
                        get_lineage,
                        {
                            "urn": dataset_urn,
                            "upstream": False,
                            **lineage_bounds,
                        },
                    )
                )
        raw = {
            "mcp_tools": sorted(names),
            "entity": entity_result,
            "schema": schema_result,
            "upstream": upstream_result,
            "downstream": downstream_result,
            "lineage_bounds": lineage_bounds,
        }
        fields = schema_result.get("fields", []) if isinstance(schema_result, Mapping) else []
        return DataHubReadResult(
            context={
                "dataset_urn": dataset_urn,
                "schema_fields": fields,
                "lineage": {"upstream": upstream_result, "downstream": downstream_result},
            },
            raw=raw,
        )

    async def discover_datasets(self, query: str = "*") -> list[str]:
        async with self._client:
            names = await self._tool_names()
            search = self._resolve(names, "search")
            result = self._data(
                await self._client.call_tool(
                    search,
                    {
                        "query": query,
                        "filter": "entity_type = dataset",
                        "num_results": 25,
                        "offset": 0,
                    },
                )
            )
        urns = sorted(self._dataset_urns(result))
        if not urns:
            raise McpContractError("DATASET_DISCOVERY_EMPTY")
        return urns

    @classmethod
    def _dataset_urns(cls, value: Any) -> set[str]:
        urns: set[str] = set()
        if isinstance(value, Mapping):
            urn = value.get("urn")
            if isinstance(urn, str) and urn.startswith("urn:li:dataset:"):
                urns.add(urn)
            for nested in value.values():
                urns.update(cls._dataset_urns(nested))
        elif isinstance(value, list):
            for nested in value:
                urns.update(cls._dataset_urns(nested))
        return urns

    async def write_receipt(self, *, dataset_urn: str, markdown: str) -> dict[str, Any]:
        async with self._client:
            names = await self._tool_names()
            update_description = self._resolve(names, "update_description")
            result = await self._client.call_tool(
                update_description,
                {
                    "entity_urn": dataset_urn,
                    "operation": "append",
                    "description": markdown,
                    "column_path": None,
                },
            )
            data = self._data(result)
        if not isinstance(data, Mapping) or data.get("success") is not True:
            raise McpContractError("MCP_WRITE_BACK_FAILED")
        return dict(data)
