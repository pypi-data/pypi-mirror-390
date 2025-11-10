from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from loguru import logger

try:
    from azure.data.tables import TableServiceClient
    from azure.core.exceptions import (
        ResourceNotFoundError,
        ResourceExistsError,
        ClientAuthenticationError,
        HttpResponseError,
    )
except Exception:  # pragma: no cover
    TableServiceClient = None  # type: ignore
    ResourceNotFoundError = None  # type: ignore
    ResourceExistsError = None  # type: ignore
    ClientAuthenticationError = None  # type: ignore
    HttpResponseError = None  # type: ignore


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AzureTableService:
    connection_string: Optional[str] = None

    def __init__(self, connection_string: Optional[str] = None) -> None:
        # Constructor injection preferred; fallback to env only if not provided
        self.connection_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    def _get_client(self) -> "TableServiceClient":
        if not self.connection_string:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not configured")
        if TableServiceClient is None:
            raise RuntimeError("azure-data-tables not installed; install to use table operations")
        clean = self.connection_string.strip().strip('"').strip("'")
        return TableServiceClient.from_connection_string(conn_str=clean)

    def ensure_table(self, table_name: str) -> None:
        client = self._get_client()
        try:
            client.create_table_if_not_exists(table_name=table_name)
        except Exception as e:
            logger.warning("ensure_table(%s) warning: %s", table_name, e)

    def list_tables(self) -> List[str]:
        """List all tables in the storage account.

        Returns:
            List of table names
        """
        client = self._get_client()
        try:
            tables = [table.name for table in client.list_tables()]
            logger.info("Listed %d tables", len(tables))
            return tables
        except Exception as exc:
            logger.error("Failed to list tables: %s", exc)
            return []

    def delete_table(self, table_name: str) -> bool:
        """Delete a table.

        Args:
            table_name: Name of the table to delete

        Returns:
            True if deleted successfully or table doesn't exist, False on other errors
        """
        client = self._get_client()
        try:
            client.delete_table(table_name=table_name)
            logger.info("Deleted table: %s", table_name)
            return True
        except ResourceNotFoundError:
            # Table already deleted or doesn't exist - this is still success
            logger.info(f"Table {table_name} already deleted or doesn't exist")
            return True
        except ClientAuthenticationError as exc:
            logger.error("Authentication failed deleting table %s: %s", table_name, exc)
            return False
        except HttpResponseError as exc:
            logger.error("Azure service error deleting table %s: %s", table_name, exc.message)
            return False
        except Exception as exc:
            logger.error("Unexpected error deleting table %s: %s", table_name, exc)
            return False

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists.

        Args:
            table_name: Name of the table

        Returns:
            True if table exists, False otherwise
        """
        return table_name in self.list_tables()

    def put_entity(self, table_name: str, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new entity into a table.

        Args:
            table_name: Name of the table
            entity: Entity dictionary with PartitionKey and RowKey

        Returns:
            Dict with etag and timestamp

        Raises:
            RuntimeError: If entity already exists or other errors occur
        """
        client = self._get_client()
        table = client.get_table_client(table_name)
        try:
            res = table.create_entity(entity=entity)
            logger.info(
                "Inserted entity into %s: PK=%s RK=%s",
                table_name,
                entity.get("PartitionKey"),
                entity.get("RowKey"),
            )
            return {"etag": getattr(res, "etag", None), "ts": _now_iso()}
        except ResourceExistsError as e:
            pk, rk = entity.get("PartitionKey"), entity.get("RowKey")
            logger.error(f"Entity already exists in {table_name}: PK={pk} RK={rk}")
            raise RuntimeError(f"Entity already exists: {e}") from e
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed inserting entity into {table_name}: {e}")
            raise RuntimeError(f"Authentication failed: {e}") from e
        except HttpResponseError as e:
            logger.error(f"Azure service error inserting entity into {table_name}: {e.message}")
            raise RuntimeError(f"Failed to insert entity: {e.message}") from e

    def upsert_entity(self, table_name: str, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update an entity in a table.

        Args:
            table_name: Name of the table
            entity: Entity dictionary with PartitionKey and RowKey

        Returns:
            Dict with etag and timestamp

        Raises:
            RuntimeError: If authentication or service errors occur
        """
        client = self._get_client()
        table = client.get_table_client(table_name)
        try:
            res = table.upsert_entity(entity=entity, mode="merge")
            logger.info(
                "Upserted entity into %s: PK=%s RK=%s",
                table_name,
                entity.get("PartitionKey"),
                entity.get("RowKey"),
            )
            return {"etag": getattr(res, "etag", None), "ts": _now_iso()}
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed upserting entity into {table_name}: {e}")
            raise RuntimeError(f"Authentication failed: {e}") from e
        except HttpResponseError as e:
            logger.error(f"Azure service error upserting entity into {table_name}: {e.message}")
            raise RuntimeError(f"Failed to upsert entity: {e.message}") from e

    def delete_entity(self, table_name: str, partition_key: str, row_key: str) -> bool:
        """Delete an entity from a table.

        Args:
            table_name: Name of the table
            partition_key: Partition key of the entity
            row_key: Row key of the entity

        Returns:
            True if deleted successfully or entity doesn't exist, False on other errors

        Note:
            Azure Tables delete_entity doesn't fail if entity doesn't exist
        """
        client = self._get_client()
        table = client.get_table_client(table_name)
        try:
            table.delete_entity(partition_key=partition_key, row_key=row_key)
            logger.info("Deleted entity in %s (%s/%s)", table_name, partition_key, row_key)
            return True
        except ResourceNotFoundError:
            # Entity already deleted or doesn't exist - this is still success
            logger.info(
                f"Entity in {table_name} ({partition_key}/{row_key}) already deleted or doesn't exist"
            )
            return True
        except ClientAuthenticationError as exc:
            logger.error("Authentication failed deleting entity in %s: %s", table_name, exc)
            return False
        except HttpResponseError as exc:
            logger.error("Azure service error deleting entity in %s: %s", table_name, exc.message)
            return False
        except Exception as exc:
            logger.error("Unexpected error deleting entity in %s: %s", table_name, exc)
            return False

    def get_entity(
        self, table_name: str, partition_key: str, row_key: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a single entity by partition and row key.

        Args:
            table_name: Name of the table
            partition_key: Partition key of the entity
            row_key: Row key of the entity

        Returns:
            Entity dict if found, None otherwise (including on auth/service errors)
        """
        client = self._get_client()
        table = client.get_table_client(table_name)
        try:
            entity = table.get_entity(partition_key=partition_key, row_key=row_key)
            logger.info("Retrieved entity from %s: PK=%s RK=%s", table_name, partition_key, row_key)
            return dict(entity)
        except ResourceNotFoundError:
            logger.info("Entity not found in %s (%s/%s)", table_name, partition_key, row_key)
            return None
        except ClientAuthenticationError as exc:
            logger.error("Authentication failed retrieving entity from %s: %s", table_name, exc)
            return None
        except HttpResponseError as exc:
            logger.error(
                "Azure service error retrieving entity from %s: %s", table_name, exc.message
            )
            return None
        except Exception as exc:
            logger.error("Unexpected error retrieving entity from %s: %s", table_name, exc)
            return None

    def entity_exists(self, table_name: str, partition_key: str, row_key: str) -> bool:
        """Check if an entity exists without retrieving it.

        Args:
            table_name: Name of the table
            partition_key: Partition key of the entity
            row_key: Row key of the entity

        Returns:
            True if entity exists, False otherwise
        """
        return self.get_entity(table_name, partition_key, row_key) is not None

    def batch_insert_entities(
        self, table_name: str, entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Insert multiple entities in a batch operation.

        Note: All entities must have the same PartitionKey for batch operations.

        Args:
            table_name: Name of the table
            entities: List of entity dictionaries to insert

        Returns:
            Dict with count of successful operations and any errors
        """
        if not entities:
            return {"success": 0, "errors": []}

        client = self._get_client()
        table = client.get_table_client(table_name)

        # Group by partition key (batch requirement)
        from collections import defaultdict

        by_partition: defaultdict[str, List[Dict[str, Any]]] = defaultdict(list)
        for entity in entities:
            pk = entity.get("PartitionKey")
            if not pk:
                logger.error("Entity missing PartitionKey, skipping")
                continue
            by_partition[pk].append(entity)

        success_count = 0
        errors = []

        for partition_key, partition_entities in by_partition.items():
            # Process in chunks of 100 (Azure limit)
            for i in range(0, len(partition_entities), 100):
                chunk = partition_entities[i : i + 100]
                operations = [("create", entity) for entity in chunk]

                try:
                    table.submit_transaction(operations)
                    success_count += len(chunk)
                    logger.info(
                        "Batch inserted %d entities into %s (PK=%s)",
                        len(chunk),
                        table_name,
                        partition_key,
                    )
                except Exception as exc:
                    error_msg = f"Batch insert failed for PK={partition_key}: {exc}"
                    logger.error(error_msg)
                    errors.append(error_msg)

        return {"success": success_count, "errors": errors, "ts": _now_iso()}

    def batch_upsert_entities(
        self, table_name: str, entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Upsert multiple entities in a batch operation.

        Note: All entities must have the same PartitionKey for batch operations.

        Args:
            table_name: Name of the table
            entities: List of entity dictionaries to upsert

        Returns:
            Dict with count of successful operations and any errors
        """
        if not entities:
            return {"success": 0, "errors": []}

        client = self._get_client()
        table = client.get_table_client(table_name)

        # Group by partition key
        from collections import defaultdict

        by_partition: defaultdict[str, List[Dict[str, Any]]] = defaultdict(list)
        for entity in entities:
            pk = entity.get("PartitionKey")
            if not pk:
                logger.error("Entity missing PartitionKey, skipping")
                continue
            by_partition[pk].append(entity)

        success_count = 0
        errors = []

        for partition_key, partition_entities in by_partition.items():
            # Process in chunks of 100
            for i in range(0, len(partition_entities), 100):
                chunk = partition_entities[i : i + 100]
                operations = [("upsert", entity, {"mode": "merge"}) for entity in chunk]

                try:
                    table.submit_transaction(operations)
                    success_count += len(chunk)
                    logger.info(
                        "Batch upserted %d entities into %s (PK=%s)",
                        len(chunk),
                        table_name,
                        partition_key,
                    )
                except Exception as exc:
                    error_msg = f"Batch upsert failed for PK={partition_key}: {exc}"
                    logger.error(error_msg)
                    errors.append(error_msg)

        return {"success": success_count, "errors": errors, "ts": _now_iso()}

    def batch_delete_entities(self, table_name: str, keys: List[tuple[str, str]]) -> Dict[str, Any]:
        """Delete multiple entities in a batch operation.

        Note: All entities must have the same PartitionKey for batch operations.

        Args:
            table_name: Name of the table
            keys: List of (partition_key, row_key) tuples

        Returns:
            Dict with count of successful operations and any errors
        """
        if not keys:
            return {"success": 0, "errors": []}

        client = self._get_client()
        table = client.get_table_client(table_name)

        # Group by partition key
        from collections import defaultdict

        by_partition: defaultdict[str, List[tuple[str, str]]] = defaultdict(list)
        for pk, rk in keys:
            by_partition[pk].append((pk, rk))

        success_count = 0
        errors = []

        for partition_key, partition_keys in by_partition.items():
            # Process in chunks of 100
            for i in range(0, len(partition_keys), 100):
                chunk = partition_keys[i : i + 100]
                operations = [("delete", {"PartitionKey": pk, "RowKey": rk}) for pk, rk in chunk]

                try:
                    table.submit_transaction(operations)
                    success_count += len(chunk)
                    logger.info(
                        "Batch deleted %d entities from %s (PK=%s)",
                        len(chunk),
                        table_name,
                        partition_key,
                    )
                except Exception as exc:
                    error_msg = f"Batch delete failed for PK={partition_key}: {exc}"
                    logger.error(error_msg)
                    errors.append(error_msg)

        return {"success": success_count, "errors": errors, "ts": _now_iso()}

    def query(self, table_name: str, filter_query: str) -> Iterable[Dict[str, Any]]:
        """Query entities with a filter.

        Args:
            table_name: Name of the table
            filter_query: OData filter query string

        Yields:
            Entity dictionaries matching the filter
        """
        client = self._get_client()
        table = client.get_table_client(table_name)
        for entity in table.query_entities(filter=filter_query):
            yield dict(entity)

    def query_with_options(
        self,
        table_name: str,
        filter_query: Optional[str] = None,
        select: Optional[List[str]] = None,
        top: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        """Query entities with advanced options.

        Args:
            table_name: Name of the table
            filter_query: Optional OData filter query string
            select: Optional list of property names to return (projection)
            top: Optional maximum number of entities to return

        Yields:
            Entity dictionaries matching the criteria
        """
        client = self._get_client()
        table = client.get_table_client(table_name)

        kwargs: Dict[str, Any] = {}
        if filter_query:
            kwargs["filter"] = filter_query
        if select:
            kwargs["select"] = select
        if top:
            kwargs["results_per_page"] = top

        for entity in table.query_entities(**kwargs):
            yield dict(entity)

    def query_all(
        self,
        table_name: str,
        filter_query: Optional[str] = None,
        select: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Query all entities and return as a list.

        Warning: This loads all results into memory. Use query() for large result sets.

        Args:
            table_name: Name of the table
            filter_query: Optional OData filter query string
            select: Optional list of property names to return

        Returns:
            List of entity dictionaries
        """
        return list(self.query_with_options(table_name, filter_query, select))

    def count_entities(self, table_name: str, filter_query: Optional[str] = None) -> int:
        """Count entities matching a filter.

        Args:
            table_name: Name of the table
            filter_query: Optional OData filter query string

        Returns:
            Count of matching entities
        """
        count = 0
        for _ in self.query_with_options(table_name, filter_query):
            count += 1
        return count
