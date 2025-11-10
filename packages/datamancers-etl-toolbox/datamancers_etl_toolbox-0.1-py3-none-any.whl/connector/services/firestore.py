"""
Firestore API wrapper for ETL operations.

This module provides a simplified interface for interacting with Google Cloud Firestore,
including reading data based on queries and batch writing multiple documents.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from google.api_core.exceptions import GoogleAPIError
from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter, Query
from google.oauth2 import service_account


class FirestoreClient:
    """
    A wrapper class for Google Cloud Firestore operations.

    This class provides simplified methods for common Firestore operations
    including querying collections and batch writing documents.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        credentials_path: Optional[str] = None,
        database: Optional[str] = None,
    ):
        """
        Initialize the Firestore client.

        Args:
            project_id: Google Cloud project ID. If None, uses default project.
            credentials_path: Path to service account credentials JSON file.
                            If None, uses default credentials.
        """
        self.logger = logging.getLogger(__name__)

        try:
            if credentials_path:
                # Initialize with specific credentials
                self.db = firestore.Client(
                    project=project_id,
                    credentials=service_account.Credentials.from_service_account_file(
                        credentials_path
                    ),
                    database=database,
                )
            else:
                # Use default credentials
                self.db = firestore.Client(project=project_id)

            self.logger.info(
                f"Firestore client initialized for project: {project_id or 'default'}"
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize Firestore client: {str(e)}")
            raise

    def read_collection_with_query(
        self,
        collection_name: str,
        filters: Optional[List[Dict[str, Any]]] = None,
        order_by: Optional[List[Dict[str, Any]]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Read data from a Firestore collection based on query parameters.

        Args:
            collection_name: Name of the Firestore collection
            filters: List of filter dictionaries with keys:
                   - field: Field name to filter on
                   - operator: Operator ('==', '!=', '<', '<=', '>', '>=', 'in', 'not-in', 'array-contains')
                   - value: Value to filter by
            order_by: List of ordering dictionaries with keys:
                    - field: Field name to order by
                    - direction: 'ASCENDING' or 'DESCENDING' (default: 'ASCENDING')
            limit: Maximum number of documents to return

        Returns:
            List of dictionaries containing document data with document ID included as '_id'

        Example:
            filters = [
                {'field': 'status', 'operator': '==', 'value': 'active'},
                {'field': 'created_at', 'operator': '>=', 'value': datetime(2023, 1, 1)}
            ]
            order_by = [{'field': 'created_at', 'direction': 'DESCENDING'}]
            data = client.read_collection_with_query('users', filters, order_by, 10)
        """
        try:
            self.logger.info(
                f"Querying collection '{collection_name}' with filters: {filters}"
            )

            # Start with collection reference
            query = self.db.collection(collection_name)

            # Apply filters
            if filters:
                for filter_dict in filters:
                    field = filter_dict["field"]
                    operator = filter_dict["operator"]
                    value = filter_dict["value"]

                    query = query.where(filter=FieldFilter(field, operator, value))

            # Apply ordering
            if order_by:
                for order_dict in order_by:
                    field = order_dict["field"]
                    direction = order_dict.get("direction", "ASCENDING")

                    if direction.upper() == "DESCENDING":
                        query = query.order_by(field, direction=Query.DESCENDING)
                    else:
                        query = query.order_by(field, direction=Query.ASCENDING)

            # Apply limit
            if limit:
                query = query.limit(limit)

            # Execute query
            docs = query.stream()

            # Convert to list of dictionaries
            results = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data["_id"] = doc.id  # Include document ID
                results.append(doc_data)

            self.logger.info(
                f"Successfully retrieved {len(results)} documents from '{collection_name}'"
            )
            return results

        except GoogleAPIError as e:
            self.logger.error(
                f"Google API error while querying collection '{collection_name}': {str(e)}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error while querying collection '{collection_name}': {str(e)}"
            )
            raise

    def set_multiple_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]],
        document_id_field: Optional[str] = None,
        merge: bool = False,
    ) -> Dict[str, Any]:
        """
        Set multiple documents in a Firestore collection using batch operations.

        Args:
            collection_name: Name of the Firestore collection
            documents: List of dictionaries containing document data
            document_id_field: Field name to use as document ID. If None, auto-generates IDs.
            merge: If True, merge with existing documents. If False, overwrite.

        Returns:
            Dictionary with operation results:
            - success_count: Number of successfully written documents
            - failed_count: Number of failed documents
            - errors: List of error messages for failed documents

        Example:
            documents = [
                {'name': 'John', 'email': 'john@example.com', 'status': 'active'},
                {'name': 'Jane', 'email': 'jane@example.com', 'status': 'inactive'}
            ]
            result = client.set_multiple_documents('users', documents, 'email')
        """
        try:
            self.logger.info(
                f"Setting {len(documents)} documents in collection '{collection_name}'"
            )

            if not documents:
                self.logger.warning("No documents provided for batch operation")
                return {"success_count": 0, "failed_count": 0, "errors": []}

            # Initialize batch
            batch = self.db.batch()
            success_count = 0
            failed_count = 0
            errors = []

            # Process documents in batches of 500 (Firestore limit)
            batch_size = 500
            total_batches = (len(documents) + batch_size - 1) // batch_size

            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min((batch_num + 1) * batch_size, len(documents))
                batch_documents = documents[start_idx:end_idx]

                current_batch = self.db.batch()

                for doc_data in batch_documents:
                    try:
                        # Determine document ID
                        if document_id_field and document_id_field in doc_data:
                            doc_id = str(doc_data[document_id_field])
                            # Remove the ID field from document data to avoid duplication
                            doc_data_clean = {
                                k: v
                                for k, v in doc_data.items()
                                if k != document_id_field
                            }
                        else:
                            doc_id = None  # Auto-generate ID
                            doc_data_clean = doc_data.copy()

                        # Get document reference
                        if doc_id:
                            doc_ref = self.db.collection(collection_name).document(
                                doc_id
                            )
                        else:
                            doc_ref = self.db.collection(collection_name).document()

                        # Add to batch
                        if merge:
                            current_batch.set(doc_ref, doc_data_clean, merge=True)
                        else:
                            current_batch.set(doc_ref, doc_data_clean)

                    except Exception as e:
                        failed_count += 1
                        error_msg = f"Failed to prepare document: {str(e)}"
                        errors.append(error_msg)
                        self.logger.error(error_msg)

                # Commit current batch
                try:
                    current_batch.commit()
                    batch_success = len(batch_documents) - (
                        failed_count - success_count
                    )
                    success_count += batch_success
                    self.logger.info(
                        f"Batch {batch_num + 1}/{total_batches} committed successfully with {batch_success} documents"
                    )

                except GoogleAPIError as e:
                    batch_failed = len(batch_documents)
                    failed_count += batch_failed
                    error_msg = f"Batch {batch_num + 1} failed: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)

            result = {
                "success_count": success_count,
                "failed_count": failed_count,
                "errors": errors,
            }

            self.logger.info(
                f"Batch operation completed. Success: {success_count}, Failed: {failed_count}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Unexpected error during batch operation: {str(e)}")
            raise

    def get_document(
        self, collection_name: str, document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single document by ID.

        Args:
            collection_name: Name of the Firestore collection
            document_id: ID of the document to retrieve

        Returns:
            Dictionary containing document data with '_id' field, or None if not found
        """
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc = doc_ref.get()

            if doc.exists:
                doc_data = doc.to_dict()
                doc_data["_id"] = doc.id
                return doc_data
            else:
                return None

        except Exception as e:
            self.logger.error(
                f"Error retrieving document '{document_id}' from '{collection_name}': {str(e)}"
            )
            raise

    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """
        Delete a single document by ID.

        Args:
            collection_name: Name of the Firestore collection
            document_id: ID of the document to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc_ref.delete()
            self.logger.info(
                f"Document '{document_id}' deleted from '{collection_name}'"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error deleting document '{document_id}' from '{collection_name}': {str(e)}"
            )
            return False

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists by attempting to read from it.

        Args:
            collection_name: Name of the Firestore collection

        Returns:
            True if collection exists, False otherwise
        """
        try:
            # Try to get one document from the collection
            docs = self.db.collection(collection_name).limit(1).stream()
            # If we can iterate, collection exists (even if empty)
            list(docs)
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking collection existence '{collection_name}': {str(e)}"
            )
            return False


# Example usage and utility functions
def create_firestore_client(
    project_id: Optional[str] = None, credentials_path: Optional[str] = None
) -> FirestoreClient:
    """
    Factory function to create a Firestore client instance.

    Args:
        project_id: Google Cloud project ID
        credentials_path: Path to service account credentials JSON file

    Returns:
        FirestoreClient instance
    """
    return FirestoreClient(project_id=project_id, credentials_path=credentials_path)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Initialize client
    client = create_firestore_client()

    # Example: Read data with query
    filters = [{"field": "status", "operator": "==", "value": "active"}]
    order_by = [{"field": "created_at", "direction": "DESCENDING"}]

    try:
        # Read data from collection
        data = client.read_collection_with_query(
            collection_name="users", filters=filters, order_by=order_by, limit=10
        )
        print(f"Retrieved {len(data)} documents")

        # Example: Set multiple documents
        documents = [
            {"name": "John Doe", "email": "john@example.com", "status": "active"},
            {"name": "Jane Smith", "email": "jane@example.com", "status": "inactive"},
        ]

        result = client.set_multiple_documents(
            collection_name="users",
            documents=documents,
            document_id_field="email",
            merge=True,
        )

        print(f"Batch operation result: {result}")

    except Exception as e:
        print(f"Error: {str(e)}")
