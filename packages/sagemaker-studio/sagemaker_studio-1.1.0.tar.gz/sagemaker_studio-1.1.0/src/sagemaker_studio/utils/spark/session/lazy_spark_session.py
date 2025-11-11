"""
Lazy Spark Session Initialization.

This module provides lazy loading functionality for Spark sessions, delaying
initialization until the first attribute access.
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from pyspark.sql.connect.session import SparkSession as _SparkSession

from sagemaker_studio.utils.spark.session.spark_session_manager import SparkSessionManager

logger = logging.getLogger("SparkConnect")


class LazySparkSession:
    """
    Lazy initializer for SparkSession.

    This class handles the lazy loading of Spark sessions, delaying the actual
    session creation until the first attribute access.
    """

    def __init__(self, session_manager: SparkSessionManager):
        """
        Initialize the lazy Spark session.

        Args:
            session_manager: Optional session manager.
        """
        self._spark = None
        self._session_manager = session_manager

    # TO-DO: Handle race condition with user executed code.
    def _async_auto_mount_catalogs(self):
        logger.debug("Mounting catalogs..")
        catalogs = self._session_manager.project.connection().catalogs
        queries = [f"USE `{catalog.name}`" for catalog in catalogs]
        executor = ThreadPoolExecutor(max_workers=5)

        futures = []
        for query in queries:
            futures.append(executor.submit(self._spark.sql, query))

        def run_final_query():
            # Wait for all previous queries to complete
            for future in futures:
                future.result()
            # Run the final USE query
            return self._spark.sql("USE spark_catalog")

        executor.submit(run_final_query)
        logger.debug("Initiated catalogs automount.")

    def _get_spark(self):
        """Get or create the SparkSession."""

        if self._spark is None:
            try:
                logger.debug("Initializing SparkSession...")

                # Use the session manager to create the session
                self._spark = self._session_manager.create()
                self._async_auto_mount_catalogs()
                logger.debug("SparkSession initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize SparkSession: {e}")
                raise
        return self._spark

    def __getattr__(self, name):
        """Delegate attribute access to the underlying SparkSession."""
        return getattr(self._get_spark(), name)

    def __repr__(self):
        """Return string representation of the SparkSession."""
        try:
            return repr(self._get_spark())
        except Exception as e:
            logger.error(f"Error getting Spark representation: {e}")
            return f"<LazySparkSession (error: {e})>"

    @property
    def __class__(self):
        """Faking the class identity. Without this, instance type would be LazySparkSession"""
        return _SparkSession

    def stop(self):
        """Stop the SparkSession and clean up resources."""
        logger.debug("Stopping lazy Spark session...")

        # Stop the session manager if it exists
        if self._session_manager:
            try:
                self._session_manager.stop()
            except Exception as e:
                logger.error(f"Error while stopping session manager: {e}")

        # Reset the Spark session reference
        self._spark = None

        logger.debug("Stopped lazy Spark session")

    def get_athena_session_id(self):
        # Stop the session manager if it exists
        if (
            self._session_manager
            and self._session_manager.__class__.__name__ == "AthenaSparkSessionManager"
        ):
            return self._session_manager.get_session_id()
