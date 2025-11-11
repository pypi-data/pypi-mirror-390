import json
import logging
from collections.abc import Awaitable, Callable
from contextlib import AsyncExitStack
from decimal import Decimal
from typing import TypedDict, cast

import aioboto3
from types_aiobotocore_dynamodb import DynamoDBServiceResource
from types_aiobotocore_dynamodb.service_resource import Table as DynamoTable

StartupCallable = Callable[[], Awaitable[None]]
ShutdownCallable = Callable[[], Awaitable[None]]
GetResourceCallable = Callable[[], Awaitable[DynamoDBServiceResource]]
DynamoContext = tuple[StartupCallable, ShutdownCallable, GetResourceCallable]

SESSION = aioboto3.Session()

TABLE_RESOURCES: dict[str, DynamoTable] = {}


def create_dynamo_context() -> DynamoContext:
    context_stack = None
    resource = None

    async def _startup() -> None:
        nonlocal context_stack, resource

        context_stack = AsyncExitStack()
        resource = await context_stack.enter_async_context(
            SESSION.resource(
                service_name="dynamodb",
                use_ssl=True,
                verify=True,
            ),
        )
        if context_stack:
            await context_stack.aclose()

    async def _shutdown() -> None:
        if context_stack:
            await context_stack.aclose()

    async def _get_resource() -> DynamoDBServiceResource:
        if resource is None:
            await dynamo_startup()

        return cast(DynamoDBServiceResource, resource)

    return _startup, _shutdown, _get_resource


dynamo_startup, dynamo_shutdown, get_resource = create_dynamo_context()


async def get_table(table_name: str) -> DynamoTable:
    if table_name not in TABLE_RESOURCES:
        resource = await get_resource()
        TABLE_RESOURCES[table_name] = await resource.Table(table_name)
    return TABLE_RESOURCES[table_name]


class PredictionResult(TypedDict):
    PREDICTION_LABEL: str | None
    PREDICTION_SCORE: float
    code_hash: str | None
    version: str | None
    created_at: str | None


class LambdaPredictionResult(TypedDict):
    label: str
    score: float
    index: int


async def get_prediction_by_snippet_hash(
    code_hash: str,
    version: str,
) -> PredictionResult | None:
    """Get prediction data for a snippet hash from DynamoDB."""
    table = await get_table("sifts_state")

    pk = f"HASH#{code_hash}"
    sk = f"PREDICTION#{version}"

    response = await table.get_item(Key={"pk": pk, "sk": sk})

    item = response.get("Item")
    if item is None:
        return None

    prediction_label: str | None = item.get("prediction_label")  # type: ignore[assignment]
    if prediction_label == "UNKNOWN":
        prediction_label = item.get("subcategory")  # type: ignore[assignment]

    if prediction_label is None or prediction_label == "UNKNOWN":
        return None

    prediction_score = item.get("prediction_score")
    if isinstance(prediction_score, (Decimal, int, float)):
        score_float = float(prediction_score)
    else:
        score_float = 0.0

    return PredictionResult(
        PREDICTION_LABEL=prediction_label,
        PREDICTION_SCORE=score_float,
        code_hash=cast(str, item.get("code_hash")),
        version=cast(str, item.get("version")),
        created_at=cast(str, item.get("created_at")),
    )


async def get_prediction_from_lambda(snippet_content: str) -> LambdaPredictionResult | None:
    """Get prediction from Lambda function when not available in DynamoDB."""
    logger = logging.getLogger(__name__)

    payload = json.dumps({"texts": [snippet_content]})

    logger.debug("Invoking Lambda function for prediction")

    async with SESSION.client("lambda") as lambda_client:
        response = await lambda_client.invoke(
            FunctionName="arn:aws:lambda:us-east-1:205810638802:function:sifts-model-consumer",
            InvocationType="RequestResponse",
            Payload=payload,
        )

        # Check for Lambda errors
        if "FunctionError" in response:
            error_payload = await response["Payload"].read()
            logger.error("Lambda function error: %s", error_payload.decode("utf-8"))
            return None

        # Parse the response
        payload_data = await response["Payload"].read()
        result = json.loads(payload_data.decode("utf-8"))

        if result and len(result) > 0:
            logger.debug("Lambda prediction result: %s", result[0])
            return LambdaPredictionResult(
                label=result[0]["label"], score=result[0]["score"], index=result[0]["index"]
            )

        logger.debug("No prediction result from Lambda")
        return None
