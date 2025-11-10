"""Database manager module for SecureAPI."""

from typing import Optional, List, Dict, Any, Callable
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID


class DatabaseManager:
    """Manager for database operations with flexible database ID management."""
    
    def __init__(self, client: Client, default_database_id: Optional[str] = None):
        """
        Initialize DatabaseManager.
        
        Args:
            client: Appwrite client instance
            default_database_id: Optional default database ID to use
        """
        self.databases = Databases(client)
        self.default_database_id = default_database_id
    
    def _get_database_id(self, database_id: Optional[str] = None) -> str:
        """
        Get the database ID to use, either from parameter or default.
        
        Args:
            database_id: Optional database ID
            
        Returns:
            Database ID to use
            
        Raises:
            ValueError: If no database ID is provided
        """
        db_id = database_id or self.default_database_id
        if not db_id:
            raise ValueError(
                'Database ID must be provided either during initialization or method call'
            )
        return db_id
    
    def create_collection(
        self,
        name: str,
        collection_id: str,
        database_id: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        document_security: Optional[bool] = None,
        enabled: Optional[bool] = None
    ):
        """Create a collection."""
        return self.databases.create_collection(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            name=name,
            permissions=permissions,
            document_security=document_security,
            enabled=enabled
        )
    
    def list_collections(
        self,
        database_id: Optional[str] = None,
        queries: Optional[List[str]] = None,
        search: Optional[str] = None
    ):
        """List all collections."""
        return self.databases.list_collections(
            database_id=self._get_database_id(database_id),
            queries=queries,
            search=search
        )
    
    def get_collection(
        self,
        collection_id: str,
        database_id: Optional[str] = None
    ):
        """Get a collection."""
        return self.databases.get_collection(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id
        )
    
    def update_collection(
        self,
        name: str,
        collection_id: str,
        database_id: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        document_security: Optional[bool] = None,
        enabled: Optional[bool] = None
    ):
        """Update a collection."""
        return self.databases.update_collection(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            name=name,
            permissions=permissions,
            document_security=document_security,
            enabled=enabled
        )
    
    def delete_collection(
        self,
        collection_id: str,
        database_id: Optional[str] = None
    ):
        """Delete a collection."""
        return self.databases.delete_collection(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id
        )
    
    def create_document(
        self,
        collection_id: str,
        data: Dict[str, Any],
        database_id: Optional[str] = None,
        document_id: Optional[str] = None,
        permissions: Optional[List[str]] = None
    ):
        """Create a document."""
        return self.databases.create_document(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            document_id=document_id or ID.unique(),
            data=data,
            permissions=permissions
        )
    
    def list_documents(
        self,
        collection_id: str,
        database_id: Optional[str] = None,
        queries: Optional[List[str]] = None
    ):
        """List all documents."""
        return self.databases.list_documents(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            queries=queries
        )
    
    def get_document(
        self,
        collection_id: str,
        document_id: str,
        database_id: Optional[str] = None,
        queries: Optional[List[str]] = None
    ):
        """Get a document."""
        return self.databases.get_document(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            document_id=document_id,
            queries=queries
        )
    
    def update_document(
        self,
        collection_id: str,
        document_id: str,
        data: Dict[str, Any],
        database_id: Optional[str] = None,
        permissions: Optional[List[str]] = None
    ):
        """Update a document."""
        return self.databases.update_document(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            document_id=document_id,
            data=data,
            permissions=permissions
        )
    
    def delete_document(
        self,
        collection_id: str,
        document_id: str,
        database_id: Optional[str] = None
    ):
        """Delete a document."""
        return self.databases.delete_document(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            document_id=document_id
        )
    
    def create_index(
        self,
        collection_id: str,
        key: str,
        type: str,
        attributes: List[str],
        database_id: Optional[str] = None,
        orders: Optional[List[str]] = None,
        lengths: Optional[List[int]] = None
    ):
        """Create an index."""
        return self.databases.create_index(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            key=key,
            type=type,
            attributes=attributes,
            orders=orders,
            lengths=lengths
        )
    
    def list_indexes(
        self,
        collection_id: str,
        database_id: Optional[str] = None,
        queries: Optional[List[str]] = None
    ):
        """List all indexes."""
        return self.databases.list_indexes(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            queries=queries
        )
    
    def get_index(
        self,
        collection_id: str,
        key: str,
        database_id: Optional[str] = None
    ):
        """Get an index."""
        return self.databases.get_index(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            key=key
        )
    
    def delete_index(
        self,
        collection_id: str,
        key: str,
        database_id: Optional[str] = None
    ):
        """Delete an index."""
        return self.databases.delete_index(
            database_id=self._get_database_id(database_id),
            collection_id=collection_id,
            key=key
        )
    
    async def batch(self, operations: List[Callable]) -> 'BatchResult':
        """
        Execute multiple database operations in batch.
        
        Args:
            operations: List of callable operations to execute
            
        Returns:
            BatchResult with successful results and errors
        """
        import asyncio
        
        results = []
        errors = []
        
        async def execute_operation(index: int, operation: Callable):
            try:
                result = await operation() if asyncio.iscoroutinefunction(operation) else operation()
                results.append(result)
            except Exception as e:
                results.append(None)
                errors.append(BatchError(index=index, error=str(e)))
        
        # Execute all operations
        tasks = [execute_operation(i, op) for i, op in enumerate(operations)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return BatchResult(
            successful=[r for r in results if r is not None],
            errors=errors,
            total_operations=len(operations),
            success_count=len([r for r in results if r is not None]),
            error_count=len(errors)
        )


class BatchResult:
    """Result of a batch operation."""
    
    def __init__(
        self,
        successful: List[Any],
        errors: List['BatchError'],
        total_operations: int,
        success_count: int,
        error_count: int
    ):
        self.successful = successful
        self.errors = errors
        self.total_operations = total_operations
        self.success_count = success_count
        self.error_count = error_count
    
    @property
    def all_successful(self) -> bool:
        """Check if all operations were successful."""
        return self.error_count == 0
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return self.error_count > 0
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            'totalOperations': self.total_operations,
            'successCount': self.success_count,
            'errorCount': self.error_count,
            'errors': [e.to_json() for e in self.errors]
        }


class BatchError:
    """Error in a batch operation."""
    
    def __init__(self, index: int, error: str):
        self.index = index
        self.error = error
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            'index': self.index,
            'error': self.error
        }
