import os
from eventix.functions.eventix_client import EventixClient
from eventix.pydantic.task import EventixTaskStatusEnum
from fastapi import APIRouter, Query


router = APIRouter(prefix="", tags=["eventix"])


@router.get("/task/by_unique_key/{unique_key}")
def router_task_by_unique_key_for_namespace_get(
    unique_key: str, stati: list[EventixTaskStatusEnum] = Query(None)
):
    if stati is None:
        stati = [
            EventixTaskStatusEnum.scheduled.value,
            EventixTaskStatusEnum.retry.value,
        ]
    namespace = os.environ.get("EVENTIX_NAMESPACE", None)
    r = EventixClient.get_task_by_unique_key_and_namespace(
        unique_key, namespace=namespace, stati=stati
    )
    return r.json()
