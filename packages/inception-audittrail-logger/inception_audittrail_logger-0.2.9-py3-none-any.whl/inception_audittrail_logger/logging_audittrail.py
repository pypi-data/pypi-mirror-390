import asyncio
import sys
from datetime import datetime
from inception_audittrail_logger.format_data import (
    format_audittrail_data,
    format_sys_error_data,
)
from inception_audittrail_logger.audittrail_mongo import insert_document
from inception_audittrail_logger.audittrail_elastic import (
    index_document,
    AUDITTRAIL_INDEX_NAME,
    SYSTEM_ERROR_INDEX_NAME,
)


async def log(
    data: dict, user: dict, correlation_id: str, user_agent_str: str, ip_address: str
):
    """
    Asynchronously format and log audit trail data to MongoDB and Elasticsearch.
    """
    try:
        formatted_data = await format_audittrail_data(
            data, user, correlation_id, user_agent_str, ip_address
        )
        es_doc = formatted_data.copy()
        es_doc.pop("_id")
        results = await asyncio.gather(
            insert_document(formatted_data),
            index_document(
                index_name=AUDITTRAIL_INDEX_NAME,
                document_id=formatted_data.get("_id"),
                body=es_doc,
            ),
        )

        if all(results):
            print("✅ Audit trail saved to both MongoDB and Elasticsearch")
        else:
            print("⚠️ One or more logging targets failed")
        print(results)

        return results
    except Exception as e:
        # Optional: Add logging here
        print(f"[ERROR] Audit trail logging failed: {e}", file=sys.stderr)
        return None


async def log_audittrail(
    data: dict, user: dict, correlation_id: str, user_agent_str: str, ip_address: str
):
    """
    Asynchronously format and log audit trail data to MongoDB and Elasticsearch.
    """
    try:
        if asyncio.get_event_loop().is_running():
            # If in an existing event loop, create a task
            asyncio.create_task(
                log(data, user, correlation_id, user_agent_str, ip_address)
            )
        else:
            asyncio.run(log(data, user, correlation_id, user_agent_str, ip_address))
    except RuntimeError as e:
        print(f"[ERROR] Unable to log audit trail: {e}", file=sys.stderr)


async def log_sys_error(
    data: dict, user: dict, correlation_id: str, user_agent_str: str, ip_address: str
):
    """
    Asynchronously format and log system error data to Elasticsearch.
    """
    try:
        formatted_data = await format_sys_error_data(
            data, user, correlation_id, user_agent_str, ip_address
        )

        document_id = formatted_data.get("_id")
        formatted_data.pop("_id")
        results = await index_document(
            index_name=SYSTEM_ERROR_INDEX_NAME,
            document_id=document_id,
            body=formatted_data,
        )
        return results
    except Exception as e:
        print(f"[ERROR] System error logging failed: {e}", file=sys.stderr)
        return None


def get_changed_fields(old_data, new_data):
    changed_fields = []
    for key, value in new_data.items():
        if old_data.get(key) != value:
            changed_fields.append(
                {
                    "field": key,
                    "old_value": old_data.get(key),
                    "new_value": value,
                }
            )
    return changed_fields
