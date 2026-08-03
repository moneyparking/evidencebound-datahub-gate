"""Deterministic, fail-closed verification core for DataHub agent actions."""

from __future__ import annotations

import ast
import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any, Final

SCHEMA_VERSION: Final = "evidencebound-datahub-candidate/1.0"
RECEIPT_SCHEMA_VERSION: Final = "evidencebound-datahub-receipt/1.0"
POLICY_VERSION: Final = "evidencebound-datahub-policy/1.0"
MAX_SOURCE_BYTES: Final = 8_192
MAX_AST_NODES: Final = 256
MAX_FUEL: Final = 512

BLOCKED_NODES: Final = (
    ast.Import,
    ast.ImportFrom,
    ast.Attribute,
    ast.AsyncFunctionDef,
    ast.Await,
    ast.ClassDef,
    ast.Delete,
    ast.Global,
    ast.Lambda,
    ast.Nonlocal,
    ast.Raise,
    ast.Try,
    ast.While,
    ast.With,
    ast.Yield,
    ast.YieldFrom,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)
ALLOWED_CALLS: Final[dict[str, Callable[..., Any]]] = {
    "abs": abs,
    "len": len,
    "max": max,
    "min": min,
}


class GateInputError(ValueError):
    """Raised when candidate or context input is malformed."""


class DeterministicRuntimeError(RuntimeError):
    """Raised when the restricted runtime cannot safely evaluate source."""


@dataclass(frozen=True)
class GateReceipt:
    schema_version: str
    policy_version: str
    candidate_id: str
    dataset_urn: str
    verdict: str
    reasons: tuple[str, ...]
    candidate_sha256: str
    source_sha256: str
    schema_sha256: str
    lineage_sha256: str
    runtime_result_sha256: str | None
    evidence_refs: tuple[str, ...]
    human_approval_required: bool
    promotion_authorized: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def normalize_schema_fields(fields: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for field in fields:
        field_path = field.get("fieldPath") or field.get("field_path") or field.get("name")
        if not isinstance(field_path, str) or not field_path.strip():
            continue
        native_type = field.get("nativeDataType") or field.get("native_data_type") or "unknown"
        normalized.append(
            {"fieldPath": field_path.strip(), "nativeDataType": str(native_type).strip()}
        )
    normalized.sort(key=lambda item: (item["fieldPath"], item["nativeDataType"]))
    return normalized


def _extract_urns(value: Any) -> set[str]:
    urns: set[str] = set()
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key == "urn" and isinstance(nested, str) and nested.startswith("urn:li:"):
                urns.add(nested)
            urns.update(_extract_urns(nested))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for nested in value:
            urns.update(_extract_urns(nested))
    return urns


def normalize_context(raw_context: Mapping[str, Any]) -> dict[str, Any]:
    dataset_urn = raw_context.get("dataset_urn")
    if not isinstance(dataset_urn, str) or not dataset_urn.startswith("urn:li:dataset:"):
        raise GateInputError("context.dataset_urn must be a DataHub dataset URN")

    schema_source = raw_context.get("schema_fields", [])
    if not isinstance(schema_source, Sequence) or isinstance(schema_source, (str, bytes)):
        raise GateInputError("context.schema_fields must be a list")
    schema_fields = normalize_schema_fields(schema_source)

    lineage_source = raw_context.get("lineage", {})
    lineage_urns = sorted(urn for urn in _extract_urns(lineage_source) if urn != dataset_urn)

    return {
        "dataset_urn": dataset_urn,
        "schema_fields": schema_fields,
        "lineage_urns": lineage_urns,
    }


def context_digests(context: Mapping[str, Any]) -> tuple[str, str]:
    normalized = normalize_context(context)
    return (
        sha256_json(normalized["schema_fields"]),
        sha256_json(normalized["lineage_urns"]),
    )


def _validate_candidate_shape(candidate: Mapping[str, Any]) -> None:
    if candidate.get("schema_version") != SCHEMA_VERSION:
        raise GateInputError(f"candidate.schema_version must equal {SCHEMA_VERSION}")
    for key in ("candidate_id", "dataset_urn", "source_code"):
        if not isinstance(candidate.get(key), str) or not str(candidate[key]).strip():
            raise GateInputError(f"candidate.{key} must be a non-empty string")
    if not str(candidate["dataset_urn"]).startswith("urn:li:dataset:"):
        raise GateInputError("candidate.dataset_urn must be a DataHub dataset URN")
    if candidate.get("human_approval_required") is not True:
        raise GateInputError("candidate.human_approval_required must be true")
    if not isinstance(candidate.get("required_fields"), list):
        raise GateInputError("candidate.required_fields must be a list")
    if not isinstance(candidate.get("claims"), list):
        raise GateInputError("candidate.claims must be a list")
    if not isinstance(candidate.get("runtime_fixture"), dict):
        raise GateInputError("candidate.runtime_fixture must be an object")


def _validate_ast(source: str) -> tuple[ast.Module | None, list[str], set[str]]:
    reasons: list[str] = []
    referenced_fields: set[str] = set()
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        return None, ["SOURCE_SIZE_LIMIT_EXCEEDED"], referenced_fields
    try:
        tree = ast.parse(source, mode="exec")
    except SyntaxError:
        return None, ["SOURCE_SYNTAX_INVALID"], referenced_fields

    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_AST_NODES:
        reasons.append("AST_NODE_LIMIT_EXCEEDED")
    for node in nodes:
        if isinstance(node, BLOCKED_NODES):
            reasons.append(f"AST_NODE_BLOCKED:{type(node).__name__}")
        if isinstance(node, ast.Call) and (
            not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_CALLS
        ):
            reasons.append("CALL_NOT_ALLOWED")
        if isinstance(node, ast.Assign) and any(
            not isinstance(target, ast.Name) for target in node.targets
        ):
            reasons.append("MUTATION_TARGET_BLOCKED")
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "row"
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            referenced_fields.add(node.slice.value)

    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    if len(tree.body) != 1 or len(functions) != 1 or functions[0].name != "transform":
        reasons.append("ENTRYPOINT_MUST_BE_SINGLE_TRANSFORM_FUNCTION")
    else:
        function = functions[0]
        if [arg.arg for arg in function.args.args] != ["row"] or function.args.vararg:
            reasons.append("TRANSFORM_SIGNATURE_INVALID")
        if function.args.kwarg or function.args.kwonlyargs:
            reasons.append("TRANSFORM_SIGNATURE_INVALID")
        if not function.body or not isinstance(function.body[-1], ast.Return):
            reasons.append("TRANSFORM_FINAL_RETURN_REQUIRED")
        elif not isinstance(function.body[-1].value, ast.Dict):
            reasons.append("TRANSFORM_RETURN_MUST_BE_DICT")

    return tree, sorted(set(reasons)), referenced_fields


class _Interpreter:
    def __init__(self, row: Mapping[str, Any]) -> None:
        self.env: dict[str, Any] = {"row": dict(row)}
        self.fuel = MAX_FUEL

    def _burn(self) -> None:
        self.fuel -= 1
        if self.fuel < 0:
            raise DeterministicRuntimeError("RUNTIME_FUEL_EXHAUSTED")

    def expression(self, node: ast.expr) -> Any:
        self._burn()
        if isinstance(node, ast.Constant):
            if isinstance(node.value, float):
                raise DeterministicRuntimeError("FLOAT_LITERAL_BLOCKED")
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in self.env:
                raise DeterministicRuntimeError(f"NAME_UNBOUND:{node.id}")
            return self.env[node.id]
        if isinstance(node, ast.Dict):
            result: dict[str, Any] = {}
            for key_node, value_node in zip(node.keys, node.values, strict=True):
                if key_node is None:
                    raise DeterministicRuntimeError("DICT_UNPACK_BLOCKED")
                key = self.expression(key_node)
                if not isinstance(key, str):
                    raise DeterministicRuntimeError("OUTPUT_KEY_MUST_BE_STRING")
                if key in result:
                    raise DeterministicRuntimeError("DUPLICATE_OUTPUT_KEY")
                result[key] = self.expression(value_node)
            return result
        if isinstance(node, ast.List):
            return [self.expression(item) for item in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(self.expression(item) for item in node.elts)
        if isinstance(node, ast.Subscript):
            container = self.expression(node.value)
            key = self.expression(node.slice)
            try:
                return container[key]
            except (KeyError, IndexError, TypeError) as exc:
                raise DeterministicRuntimeError("SUBSCRIPT_LOOKUP_FAILED") from exc
        if isinstance(node, ast.UnaryOp):
            value = self.expression(node.operand)
            if isinstance(node.op, ast.Not):
                return not bool(value)
            if isinstance(node.op, ast.USub) and isinstance(value, int):
                return -value
            if isinstance(node.op, ast.UAdd) and isinstance(value, int):
                return value
            raise DeterministicRuntimeError("UNARY_OPERATION_BLOCKED")
        if isinstance(node, ast.BinOp):
            left = self.expression(node.left)
            right = self.expression(node.right)
            if not isinstance(left, int) or not isinstance(right, int):
                raise DeterministicRuntimeError("ARITHMETIC_REQUIRES_INTEGERS")
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.FloorDiv):
                if right == 0:
                    raise DeterministicRuntimeError("DIVISION_BY_ZERO")
                return left // right
            if isinstance(node.op, ast.Mod):
                if right == 0:
                    raise DeterministicRuntimeError("MODULO_BY_ZERO")
                return left % right
            raise DeterministicRuntimeError("BINARY_OPERATION_BLOCKED")
        if isinstance(node, ast.Compare):
            left = self.expression(node.left)
            for operation, comparator_node in zip(node.ops, node.comparators, strict=True):
                right = self.expression(comparator_node)
                if isinstance(operation, ast.Eq):
                    passed = left == right
                elif isinstance(operation, ast.NotEq):
                    passed = left != right
                elif isinstance(operation, ast.Lt):
                    passed = left < right
                elif isinstance(operation, ast.LtE):
                    passed = left <= right
                elif isinstance(operation, ast.Gt):
                    passed = left > right
                elif isinstance(operation, ast.GtE):
                    passed = left >= right
                else:
                    raise DeterministicRuntimeError("COMPARISON_BLOCKED")
                if not passed:
                    return False
                left = right
            return True
        if isinstance(node, ast.BoolOp):
            values = [bool(self.expression(item)) for item in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            if isinstance(node.op, ast.Or):
                return any(values)
            raise DeterministicRuntimeError("BOOLEAN_OPERATION_BLOCKED")
        if isinstance(node, ast.IfExp):
            branch = node.body if bool(self.expression(node.test)) else node.orelse
            return self.expression(branch)
        if isinstance(node, ast.Call):
            assert isinstance(node.func, ast.Name)
            function = ALLOWED_CALLS.get(node.func.id)
            if function is None or node.keywords:
                raise DeterministicRuntimeError("CALL_NOT_ALLOWED")
            return function(*(self.expression(argument) for argument in node.args))
        raise DeterministicRuntimeError(f"EXPRESSION_BLOCKED:{type(node).__name__}")

    def run(self, function: ast.FunctionDef) -> dict[str, Any]:
        for statement in function.body:
            self._burn()
            if isinstance(statement, ast.Assign):
                if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
                    raise DeterministicRuntimeError("ASSIGNMENT_TARGET_BLOCKED")
                self.env[statement.targets[0].id] = self.expression(statement.value)
                continue
            if isinstance(statement, ast.Return):
                result = self.expression(statement.value) if statement.value is not None else None
                if not isinstance(result, dict):
                    raise DeterministicRuntimeError("RUNTIME_RESULT_MUST_BE_DICT")
                return result
            raise DeterministicRuntimeError(f"STATEMENT_BLOCKED:{type(statement).__name__}")
        raise DeterministicRuntimeError("RUNTIME_RETURN_MISSING")


def _claim_evidence(
    candidate: Mapping[str, Any], schema_fields: set[str], lineage_urns: set[str]
) -> tuple[list[str], set[str]]:
    reasons: list[str] = []
    evidence_refs: set[str] = set()
    seen_claim_ids: set[str] = set()
    for raw_claim in candidate["claims"]:
        if not isinstance(raw_claim, Mapping):
            reasons.append("CLAIM_INVALID")
            continue
        claim_id = raw_claim.get("claim_id")
        refs = raw_claim.get("evidence_refs")
        if not isinstance(claim_id, str) or not claim_id:
            reasons.append("CLAIM_ID_INVALID")
            continue
        if claim_id in seen_claim_ids:
            reasons.append(f"CLAIM_ID_DUPLICATE:{claim_id}")
        seen_claim_ids.add(claim_id)
        if not isinstance(refs, list) or not refs:
            reasons.append(f"CLAIM_UNBOUND:{claim_id}")
            continue
        for ref in refs:
            if not isinstance(ref, str):
                reasons.append(f"EVIDENCE_REF_INVALID:{claim_id}")
                continue
            evidence_refs.add(ref)
            if ref.startswith("schema:"):
                if ref.removeprefix("schema:") not in schema_fields:
                    reasons.append(f"EVIDENCE_REF_MISSING:{ref}")
            elif ref.startswith("lineage:"):
                if ref.removeprefix("lineage:") not in lineage_urns:
                    reasons.append(f"EVIDENCE_REF_MISSING:{ref}")
            else:
                reasons.append(f"EVIDENCE_REF_CLASS_INVALID:{ref}")
    return reasons, evidence_refs


def evaluate_candidate(candidate: Mapping[str, Any], raw_context: Mapping[str, Any]) -> GateReceipt:
    """Evaluate one candidate against observed DataHub context without network access."""

    _validate_candidate_shape(candidate)
    context = normalize_context(raw_context)
    candidate_sha256 = sha256_json(candidate)
    source = str(candidate["source_code"])
    source_sha256 = sha256_bytes(source.encode("utf-8"))
    schema_sha256 = sha256_json(context["schema_fields"])
    lineage_sha256 = sha256_json(context["lineage_urns"])
    reasons: list[str] = []

    if candidate["dataset_urn"] != context["dataset_urn"]:
        reasons.append("DATASET_IDENTITY_MISMATCH")
    if candidate.get("expected_schema_sha256") != schema_sha256:
        reasons.append("SCHEMA_MISMATCH")
    if candidate.get("expected_lineage_sha256") != lineage_sha256:
        reasons.append("LINEAGE_MISMATCH")

    tree, ast_reasons, referenced_fields = _validate_ast(source)
    reasons.extend(ast_reasons)
    available_fields = {field["fieldPath"] for field in context["schema_fields"]}
    required_fields = {str(field) for field in candidate["required_fields"]}
    for field in sorted(required_fields - available_fields):
        reasons.append(f"REQUIRED_FIELD_MISSING:{field}")
    for field in sorted(referenced_fields - available_fields):
        reasons.append(f"SOURCE_FIELD_MISSING:{field}")

    claim_reasons, evidence_refs = _claim_evidence(
        candidate, available_fields, set(context["lineage_urns"])
    )
    reasons.extend(claim_reasons)

    runtime_result_sha256: str | None = None
    if not reasons and tree is not None:
        try:
            function = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
            runtime_result = _Interpreter(candidate["runtime_fixture"]).run(function)
            runtime_result_sha256 = sha256_json(runtime_result)
        except (DeterministicRuntimeError, StopIteration) as exc:
            reasons.append(str(exc) or "RUNTIME_BLOCKED")

    normalized_reasons = tuple(sorted(set(reasons)))
    verdict = "VERIFIED" if not normalized_reasons else "BLOCKED"
    return GateReceipt(
        schema_version=RECEIPT_SCHEMA_VERSION,
        policy_version=POLICY_VERSION,
        candidate_id=str(candidate["candidate_id"]),
        dataset_urn=str(candidate["dataset_urn"]),
        verdict=verdict,
        reasons=normalized_reasons,
        candidate_sha256=candidate_sha256,
        source_sha256=source_sha256,
        schema_sha256=schema_sha256,
        lineage_sha256=lineage_sha256,
        runtime_result_sha256=runtime_result_sha256,
        evidence_refs=tuple(sorted(evidence_refs)),
        human_approval_required=True,
        promotion_authorized=False,
    )
