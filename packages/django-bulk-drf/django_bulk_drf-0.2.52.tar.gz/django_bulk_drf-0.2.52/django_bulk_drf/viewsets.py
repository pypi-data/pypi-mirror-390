"""
ViewSet layer for bulk operations.

Provides:
- BulkOperationMixin: Configuration and context injection
- BulkModelViewSet: Complete viewset with bulk operations
"""

import logging
from rest_framework import status, viewsets
from rest_framework.response import Response

from .operations import BulkDeleteOperation
from .queries import build_filter_for_delete
from .settings import bulk_settings
from .transactions import BulkTransactionManager
from .validators import validate_bulk_request, validate_for_delete

logger = logging.getLogger(__name__)


class BulkOperationMixin:
    """
    Configuration and context injection for bulk operations.
    Includes hybrid serialization optimization (auto-detection + manual override).
    """

    # Class attributes (can be overridden)
    unique_fields = ["id"]  # Fields for upsert matching
    batch_size = None  # Records per database batch (uses settings default if None)
    allow_singular = None  # Allow single-object requests (uses settings default if None)

    # Serialization optimization (hybrid approach)
    auto_optimize_serialization = True  # Enable auto-detection (default: True)
    select_related_fields = None  # Manual override for select_related
    prefetch_related_fields = None  # Manual override for prefetch_related

    def get_unique_fields(self):
        """
        Get unique fields for this request.
        Can be overridden to support per-request configuration.

        Returns:
            List of unique field names
        """
        return self.unique_fields

    def get_batch_size(self):
        """
        Get batch size for this request.
        Respects MAX_BATCH_SIZE setting.

        Returns:
            Batch size integer
        """
        batch_size = self.batch_size
        if batch_size is None:
            batch_size = bulk_settings.default_batch_size

        # Ensure doesn't exceed max
        max_batch_size = bulk_settings.max_batch_size
        return min(batch_size, max_batch_size)

    def get_allow_singular(self):
        """
        Get whether singular requests are allowed.

        Returns:
            Boolean
        """
        if self.allow_singular is not None:
            return self.allow_singular
        return bulk_settings.allow_singular

    def get_consistent_response_format(self):
        """
        Get whether to use consistent response format for single operations.

        Returns:
            Boolean
        """
        if hasattr(self, 'consistent_response_format'):
            return self.consistent_response_format
        return bulk_settings.consistent_response_format

    def get_serializer_context(self):
        """
        Inject bulk configuration into serializer context.

        Returns:
            Dict with context
        """
        context = super().get_serializer_context()

        # Add bulk-specific context
        context.update(
            {
                "unique_fields": self.get_unique_fields(),
                "batch_size": self.get_batch_size(),
                "operation": self._detect_operation(),
                "prefer_minimal": self._get_prefer_minimal(),
            }
        )

        return context

    def _detect_operation(self):
        """
        Map HTTP method to operation type.

        Returns:
            Operation type string
        """
        method = self.request.method if hasattr(self, "request") else None

        mapping = {
            "POST": "create",
            "PUT": "update",
            "PATCH": "upsert",
            "DELETE": "delete",
        }

        return mapping.get(method, "unknown")

    def _get_prefer_minimal(self):
        """
        Check if minimal response is preferred.
        Checks Prefer header and settings.

        Returns:
            Boolean
        """
        if not hasattr(self, "request"):
            return bulk_settings.prefer_minimal_response

        # Check Prefer header
        prefer_header = self.request.headers.get("Prefer", "")
        if "minimal" in prefer_header.lower():
            return True

        return bulk_settings.prefer_minimal_response

    def _is_bulk_request(self):
        """
        Determine if request is bulk or single.

        Returns:
            Boolean
        """
        # Check if detail endpoint (has lookup field in kwargs)
        if self.kwargs.get(self.lookup_field):
            return False

        # Check if data is a list
        if hasattr(self, "request") and isinstance(self.request.data, list):
            return True

        return False

    def _check_bulk_or_single(self, request):
        """
        Enforce request shape based on configuration.

        Args:
            request: HTTP request

        Raises:
            ValidationError: If request shape not allowed
        """
        is_list = isinstance(request.data, list)
        allow_singular = self.get_allow_singular()

        if not is_list and not allow_singular:
            # Single request provided but only bulk allowed
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Single-object requests not allowed on this endpoint")

    def _build_delete_queryset(self, data):
        """
        Build queryset for bulk delete from request data.

        Args:
            data: List of dicts with unique field values

        Returns:
            Filtered queryset
        """
        model = self.get_queryset().model
        unique_fields = self.get_unique_fields()

        q_filter = build_filter_for_delete(model, unique_fields, data)
        return self.get_queryset().filter(q_filter)

    def optimize_instances_for_serialization(self, instances):
        """
        Optimize instances for serialization to prevent N+1 queries.
        Uses hybrid approach: manual config overrides auto-detection.

        Args:
            instances: List of model instances to optimize

        Returns:
            list: Optimized instances with related data pre-loaded

        Flow:
            1. Try manual configuration first (explicit wins)
            2. Fall back to auto-detection if enabled
            3. No optimization - warn and return as-is
        """

        if not instances:
            return instances

        # 1. Manual configuration takes precedence
        if self.select_related_fields or self.prefetch_related_fields:
            return self._optimize_manual(instances)

        # 2. Auto-detection if enabled
        if self.auto_optimize_serialization:
            return self._optimize_auto(instances)

        # 3. No optimization - warn
        logger.warning(
            f"{self.__class__.__name__}: No serialization optimization configured! "
            f"This may cause N+1 queries. Set select_related_fields/prefetch_related_fields "
            f"or enable auto_optimize_serialization."
        )
        return instances

    def _optimize_manual(self, instances):
        """
        Apply manual select_related/prefetch_related configuration.

        Args:
            instances: List of model instances

        Returns:
            list: Re-fetched instances with optimizations applied (preserves order)
        """
        model = instances[0].__class__
        pks = [inst.pk for inst in instances]

        # Preserve original order by using pk__in with preserved_order
        queryset = model.objects.filter(pk__in=pks)

        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        # Preserve original order by creating a pk→instance lookup and rebuilding the list
        fetched = {obj.pk: obj for obj in queryset}
        result = [fetched[pk] for pk in pks if pk in fetched]
        return result

    def _optimize_auto(self, instances):
        """
        Auto-detect FK/M2M fields from serializer and apply optimizations.

        Args:
            instances: List of model instances

        Returns:
            list: Re-fetched instances with auto-detected optimizations applied (preserves order)
        """
        from .queries import QueryOptimizer

        serializer_class = self.get_serializer_class()
        optimizer = QueryOptimizer(serializer_class)

        select_related = optimizer.get_select_related_fields()
        prefetch_related = optimizer.get_prefetch_related_fields()

        # Re-fetch with detected optimizations
        model = instances[0].__class__
        pks = [inst.pk for inst in instances]
        queryset = model.objects.filter(pk__in=pks)

        if select_related:
            queryset = queryset.select_related(*select_related)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        # Preserve original order by creating a pk→instance lookup and rebuilding the list
        fetched = {obj.pk: obj for obj in queryset}
        optimized = [fetched[pk] for pk in pks if pk in fetched]
        return optimized


class BulkModelViewSet(BulkOperationMixin, viewsets.ModelViewSet):
    """
    Complete viewset with bulk operations on collection endpoints.
    Detail endpoints remain standard DRF behavior.
    """

    def get_serializer(self, *args, **kwargs):
        """
        Auto-detect many=True from request data structure.
        Injects serializer context with bulk configuration.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Serializer instance
        """
        # Auto-detect many=True for bulk operations
        if self._is_bulk_request() and "many" not in kwargs:
            kwargs["many"] = True

        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        POST /items/

        Handles both:
        - Single: {"name": "Item"}
        - Bulk: [{"name": "Item 1"}, {"name": "Item 2"}]

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        # Enforce request shape based on allow_singular setting
        self._check_bulk_or_single(request)

        is_bulk = self._is_bulk_request()

        if is_bulk:
            return self._handle_bulk_create(request)
        else:
            # Standard DRF single create
            try:
                response = super().create(request, *args, **kwargs)

                # Wrap in consistent format if enabled
                if self.get_consistent_response_format():
                    return Response({
                        "created": 1,
                        "updated": 0,
                        "failed": 0,
                        "data": [response.data]
                    }, status=response.status_code)

                return response
            except Exception as e:
                if self.get_consistent_response_format():
                    # Format any error consistently
                    from .results import BulkResponseFormatter
                    error_data = BulkResponseFormatter.format_error({"0": str(e)})
                    return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    # Re-raise for standard Django error handling
                    raise

    def update(self, request, *args, **kwargs):
        """
        PUT /items/ or PUT /items/{id}/

        Collection (no lookup): Bulk update
        Detail (with lookup): Standard single update

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        # Enforce request shape based on allow_singular setting
        self._check_bulk_or_single(request)

        is_bulk = self._is_bulk_request()

        if is_bulk:
            # Collection endpoint - bulk update
            return self._handle_bulk_update(request, partial=False)
        else:
            # Detail endpoint - standard update
            try:
                response = super().update(request, *args, **kwargs)

                # Wrap in consistent format if enabled
                if self.get_consistent_response_format():
                    return Response({
                        "created": 0,
                        "updated": 1,
                        "failed": 0,
                        "data": [response.data]
                    }, status=response.status_code)

                return response
            except Exception as e:
                if self.get_consistent_response_format():
                    # Format any error consistently
                    from .results import BulkResponseFormatter
                    error_data = BulkResponseFormatter.format_error({"0": str(e)})
                    return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    # Re-raise for standard Django error handling
                    raise

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /items/ or PATCH /items/{id}/

        Collection (no pk): Bulk upsert
        Detail (with pk): Standard single partial update

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        # Enforce request shape based on allow_singular setting
        self._check_bulk_or_single(request)

        is_bulk = self._is_bulk_request()

        if is_bulk:
            # Collection endpoint - bulk upsert
            return self._handle_bulk_upsert(request)
        else:
            # Detail endpoint - standard partial update
            try:
                response = super().partial_update(request, *args, **kwargs)

                # Wrap in consistent format if enabled
                if self.get_consistent_response_format():
                    return Response({
                        "created": 0,
                        "updated": 1,
                        "failed": 0,
                        "data": [response.data]
                    }, status=response.status_code)

                return response
            except Exception as e:
                if self.get_consistent_response_format():
                    # Format any error consistently
                    from .results import BulkResponseFormatter
                    error_data = BulkResponseFormatter.format_error({"0": str(e)})
                    return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    # Re-raise for standard Django error handling
                    raise

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /items/ or DELETE /items/{id}/

        Collection: Bulk delete by unique_fields
        Detail: Standard single delete

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        # Enforce request shape based on allow_singular setting
        self._check_bulk_or_single(request)

        is_bulk = self._is_bulk_request()

        if is_bulk:
            # Collection endpoint - bulk delete
            return self._handle_bulk_destroy(request)
        else:
            # Detail endpoint - standard delete
            return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Hook for custom create logic.
        Called after validation, before save.

        Args:
            serializer: Serializer instance
        """
        serializer.save()

    def perform_update(self, serializer):
        """
        Hook for custom update logic.

        Args:
            serializer: Serializer instance
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Hook for custom delete logic.

        Args:
            instance: Instance to delete (or queryset for bulk)
        """
        if hasattr(instance, "delete"):
            instance.delete()

    def _handle_bulk_create(self, request):
        """
        Internal handler for bulk create operations.

        Args:
            request: HTTP request

        Returns:
            Response
        """
        from .results import BulkResponseFormatter

        try:
            # Validate batch size
            validate_bulk_request(request.data, self.get_unique_fields(), bulk_settings.max_batch_size)

            # Get serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Execute with transaction
            transaction_manager = BulkTransactionManager(
                atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
            )

            with transaction_manager.execute():
                self.perform_create(serializer)

            # Format response using BulkOperationResult if available
            result = getattr(serializer, "bulk_result", None)
            prefer_minimal = self._get_prefer_minimal()

            if result is not None:
                # Only optimize instances if we're going to serialize them (not minimal)
                optimized_instances = None
                if not prefer_minimal:
                    all_instances = result.get_all_instances()
                    optimized_instances = self.optimize_instances_for_serialization(all_instances)

                data = BulkResponseFormatter.format_success(
                    result,
                    serializer=self.get_serializer if not prefer_minimal else None,
                    prefer_minimal=prefer_minimal,
                    optimized_instances=optimized_instances,
                )
                return Response(data, status=status.HTTP_201_CREATED)

            # Fallback to counts from serializer
            instances = serializer.instance if isinstance(serializer.instance, list) else [serializer.instance]
            optimized_instances = self.optimize_instances_for_serialization(instances)
            data = {
                "created": len(instances),
                "updated": 0,
                "failed": 0,
                "data": self.get_serializer(optimized_instances, many=True).data if not prefer_minimal else None,
            }
            if prefer_minimal and "data" in data:
                del data["data"]
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Format any unexpected error consistently
            error_data = BulkResponseFormatter.format_error({"bulk_error": str(e)})
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_bulk_update(self, request, partial=False):
        """
        Internal handler for bulk update operations.

        Args:
            request: HTTP request
            partial: Whether this is a partial update

        Returns:
            Response
        """
        from .results import BulkResponseFormatter

        try:
            if not isinstance(request.data, list):
                from rest_framework.exceptions import ValidationError

                raise ValidationError("Bulk update requires a list of objects")

            # Validate bulk request
            validate_bulk_request(request.data, self.get_unique_fields(), bulk_settings.max_batch_size)

            # Get serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Execute update
            transaction_manager = BulkTransactionManager(
                atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
            )

            with transaction_manager.execute():
                # Call serializer's update method (for bulk)
                if hasattr(serializer, "update"):
                    instances = serializer.update(serializer.validated_data)
                else:
                    instances = serializer.save()

            # Format response using BulkOperationResult if available
            result = getattr(serializer, "bulk_result", None)
            prefer_minimal = self._get_prefer_minimal()

            if result is not None:
                # Only optimize instances if we're going to serialize them (not minimal)
                optimized_instances = None
                if not prefer_minimal:
                    all_instances = result.get_all_instances()
                    optimized_instances = self.optimize_instances_for_serialization(all_instances)

                if result.has_errors() and result.has_successes():
                    data = BulkResponseFormatter.format_partial_success(
                        result,
                        serializer=self.get_serializer if not prefer_minimal else None,
                        prefer_minimal=prefer_minimal,
                        optimized_instances=optimized_instances,
                    )
                    return Response(data, status=status.HTTP_207_MULTI_STATUS)
                elif result.has_errors() and not result.has_successes():
                    data = BulkResponseFormatter.format_error(result.errors)
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data = BulkResponseFormatter.format_success(
                        result,
                        serializer=self.get_serializer if not prefer_minimal else None,
                        prefer_minimal=prefer_minimal,
                        optimized_instances=optimized_instances,
                    )
                    return Response(data, status=status.HTTP_200_OK)

            # Fallback to instance counts
            instances = instances if isinstance(instances, list) else [instances]
            if prefer_minimal:
                data = {"created": 0, "updated": len(instances), "failed": 0}
                return Response(data, status=status.HTTP_200_OK)
            optimized_instances = self.optimize_instances_for_serialization(instances)
            response_serializer = self.get_serializer(optimized_instances, many=True)
            data = {"created": 0, "updated": len(instances), "failed": 0, "data": response_serializer.data}
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            # Format any unexpected error consistently
            error_data = BulkResponseFormatter.format_error({"bulk_error": str(e)})
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_bulk_upsert(self, request):
        """
        Internal handler for bulk upsert.

        Args:
            request: HTTP request

        Returns:
            Response
        """
        from .results import BulkResponseFormatter

        try:
            if not isinstance(request.data, list):
                from rest_framework.exceptions import ValidationError

                raise ValidationError("Bulk upsert requires a list of objects")

            # Validate bulk request
            validate_bulk_request(request.data, self.get_unique_fields(), bulk_settings.max_batch_size)

            # Get serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Execute upsert
            transaction_manager = BulkTransactionManager(
                atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
            )

            with transaction_manager.execute():
                # Call serializer's upsert method
                if hasattr(serializer, "upsert"):
                    instances = serializer.upsert(serializer.validated_data)
                else:
                    instances = serializer.save()

            # Format response using BulkOperationResult if available
            result = getattr(serializer, "bulk_result", None)
            prefer_minimal = self._get_prefer_minimal()

            if result is not None:
                # Only optimize instances if we're going to serialize them (not minimal)
                optimized_instances = None
                if not prefer_minimal:
                    all_instances = result.get_all_instances()
                    optimized_instances = self.optimize_instances_for_serialization(all_instances)

                if result.has_errors() and result.has_successes():
                    data = BulkResponseFormatter.format_partial_success(
                        result,
                        serializer=self.get_serializer if not prefer_minimal else None,
                        prefer_minimal=prefer_minimal,
                        optimized_instances=optimized_instances,
                    )
                    return Response(data, status=status.HTTP_207_MULTI_STATUS)
                elif result.has_errors() and not result.has_successes():
                    data = BulkResponseFormatter.format_error(result.errors)
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data = BulkResponseFormatter.format_success(
                        result,
                        serializer=self.get_serializer if not prefer_minimal else None,
                        prefer_minimal=prefer_minimal,
                        optimized_instances=optimized_instances,
                    )
                    return Response(data, status=status.HTTP_200_OK)

            # Fallback to instance counts
            instances = instances if isinstance(instances, list) else [instances]
            if prefer_minimal:
                data = {"created": 0, "updated": len(instances), "failed": 0}
                return Response(data, status=status.HTTP_200_OK)
            optimized_instances = self.optimize_instances_for_serialization(instances)
            response_serializer = self.get_serializer(optimized_instances, many=True)
            data = {"created": 0, "updated": len(instances), "failed": 0, "data": response_serializer.data}
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            # Format any unexpected error consistently
            error_data = BulkResponseFormatter.format_error({"bulk_error": str(e)})
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_bulk_destroy(self, request):
        """
        Internal handler for bulk delete.

        Args:
            request: HTTP request

        Returns:
            Response
        """
        from .results import BulkResponseFormatter

        try:
            if not isinstance(request.data, list):
                from rest_framework.exceptions import ValidationError

                raise ValidationError("Bulk delete requires a list of objects with unique field identifiers")

            # Validate delete request
            validate_for_delete(request.data, self.get_unique_fields())

            # Execute delete operation
            model = self.get_queryset().model
            operation = BulkDeleteOperation(
                model=model,
                unique_fields=self.get_unique_fields(),
                batch_size=self.get_batch_size(),
                context={"request": request, "view": self},
            )

            # Validate data (simple structure validation)
            validated_data = request.data

            transaction_manager = BulkTransactionManager(
                atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
            )

            with transaction_manager.execute():
                result = operation.execute(validated_data)

            # Format response
            data = {"deleted": result.deleted}

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            # Format any unexpected error consistently
            error_data = BulkResponseFormatter.format_error({"bulk_error": str(e)})
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
