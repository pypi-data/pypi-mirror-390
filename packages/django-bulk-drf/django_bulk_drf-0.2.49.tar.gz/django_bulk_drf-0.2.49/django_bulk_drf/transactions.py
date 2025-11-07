"""
Transaction management for bulk operations.

Handles atomic operations and failure strategies.
"""

from django.db import transaction
from contextlib import contextmanager
import logging

from .settings import PartialFailureStrategy


logger = logging.getLogger(__name__)


class BulkTransactionManager:
    """
    Manages transactions and rollback for bulk operations.
    """

    def __init__(self, atomic=True, savepoints=True, failure_strategy=None):
        """
        Configure transaction behavior.

        Args:
            atomic: Wrap operations in transaction.atomic()
            savepoints: Use savepoints for partial rollback
            failure_strategy: PartialFailureStrategy enum value
        """
        self.atomic = atomic
        self.savepoints = savepoints
        self.failure_strategy = failure_strategy or PartialFailureStrategy.ROLLBACK_ALL

    @contextmanager
    def execute(self):
        """
        Execute operation within transaction context.

        Yields:
            None

        Example:
            with manager.execute():
                # perform database operations
                pass
        """
        if not self.atomic:
            # No transaction management
            yield
            return

        try:
            with transaction.atomic():
                yield
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise

    @contextmanager
    def execute_with_savepoint(self):
        """
        Execute with savepoint support.

        Yields:
            None
        """
        if not self.atomic or not self.savepoints:
            yield
            return

        try:
            with transaction.atomic():
                sid = transaction.savepoint()
                try:
                    yield
                    transaction.savepoint_commit(sid)
                except Exception:
                    transaction.savepoint_rollback(sid)
                    raise
        except Exception as e:
            logger.error(f"Transaction with savepoint failed: {e}")
            raise

    def handle_partial_failure(self, successful, failed, errors):
        """
        Handle cases where some records succeed, others fail.

        Args:
            successful: List of successful instances
            failed: List of failed items
            errors: Dict of errors by index

        Returns:
            Tuple of (successful, failed, should_commit)

        Raises:
            Exception: If strategy is ROLLBACK_ALL
        """
        if self.failure_strategy == PartialFailureStrategy.ROLLBACK_ALL:
            # Default: all-or-nothing
            logger.warning(f"Partial failure detected: {len(successful)} succeeded, {len(failed)} failed. Rolling back all changes.")
            # Raise exception to trigger rollback
            from .exceptions import PartialBulkError

            raise PartialBulkError(successful, failed, errors)

        elif self.failure_strategy == PartialFailureStrategy.COMMIT_SUCCESSFUL:
            # Commit successful, return errors
            return successful, failed, True

        elif self.failure_strategy == PartialFailureStrategy.CONTINUE:
            # Continue processing, no transactions
            return successful, failed, True

        # Default: rollback
        from .exceptions import PartialBulkError

        raise PartialBulkError(successful, failed, errors)

    def rollback_on_error(self):
        """
        Rollback current transaction.

        Note: This is typically handled automatically by Django's
        transaction.atomic() context manager.
        """
        if transaction.get_autocommit():
            logger.warning("Cannot rollback - not in a transaction")
            return

        try:
            transaction.set_rollback(True)
            logger.info("Transaction marked for rollback")
        except Exception as e:
            logger.error(f"Failed to mark transaction for rollback: {e}")

    def commit_successful(self):
        """
        Commit transaction.

        Note: This is typically handled automatically by Django's
        transaction.atomic() context manager when the block exits cleanly.

        Returns:
            True if commit would succeed
        """
        if transaction.get_autocommit():
            logger.debug("Not in a transaction - nothing to commit")
            return True

        # Check if transaction is marked for rollback
        if transaction.get_rollback():
            logger.warning("Transaction is marked for rollback")
            return False

        return True


def execute_in_transaction(func, atomic=True, failure_strategy=None):
    """
    Execute a function within a transaction.

    Args:
        func: Function to execute
        atomic: Whether to use atomic transaction
        failure_strategy: PartialFailureStrategy enum value

    Returns:
        Result of func()
    """
    manager = BulkTransactionManager(atomic=atomic, failure_strategy=failure_strategy)

    with manager.execute():
        return func()


@contextmanager
def bulk_atomic(using=None, savepoint=True):
    """
    Context manager for bulk operations with atomic transactions.

    Args:
        using: Database alias
        savepoint: Whether to use savepoints

    Yields:
        None

    Example:
        with bulk_atomic():
            # perform bulk operations
            pass
    """
    with transaction.atomic(using=using, savepoint=savepoint):
        yield


def is_in_transaction():
    """
    Check if currently in a transaction.

    Returns:
        True if in transaction, False otherwise
    """
    return not transaction.get_autocommit()
