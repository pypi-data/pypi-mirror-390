"""
Unit tests for LazySparkSession.

This module tests the lazy loading functionality for Spark sessions.
"""

import logging
import sys
from unittest.mock import Mock, patch

import pytest

# Mock PySpark and gRPC modules before importing our code
pyspark_modules = [
    "pyspark",
    "pyspark.sql",
    "pyspark.sql.session",
    "pyspark.sql.connect",
    "pyspark.sql.connect.session",
    "pyspark.sql.connect.client",
    "grpc",
]

for module_name in pyspark_modules:
    if module_name not in sys.modules:
        mock_module = Mock()
        if module_name == "grpc":
            # Mock gRPC specific classes and functions
            mock_module.insecure_channel = Mock()
            mock_module.secure_channel = Mock()
            mock_module.UnaryUnaryClientInterceptor = Mock()
        sys.modules[module_name] = mock_module

from sagemaker_studio.utils.spark.session.lazy_spark_session import LazySparkSession  # noqa: E402
from sagemaker_studio.utils.spark.session.spark_session_manager import (  # noqa: E402
    SparkSessionManager,
)


@pytest.fixture
def mock_spark_session():
    """Create a mock SparkSession for testing."""
    return Mock()


class TestLazySparkSession:
    """Test cases for LazySparkSession class."""

    def test_init_with_session_manager(self, mock_spark_session):
        """Test LazySparkSession initialization with session manager."""
        mock_manager = Mock(spec=SparkSessionManager)
        lazy_session = LazySparkSession(mock_manager)

        assert lazy_session._spark is None
        assert lazy_session._session_manager is mock_manager

    def test_init_without_session_manager(self):
        """Test LazySparkSession initialization without session manager."""
        lazy_session = LazySparkSession(None)

        assert lazy_session._spark is None
        assert lazy_session._session_manager is None

    def test_get_spark_creates_session_on_first_call(self, mock_spark_session):
        """Test that _get_spark creates session on first call."""
        mock_manager = Mock(spec=SparkSessionManager)
        mock_manager.create.return_value = mock_spark_session
        mock_project = Mock()
        mock_manager.project = mock_project
        mock_connection = Mock()
        mock_project.connection.return_value = mock_connection
        mock_connection.catalogs = []
        lazy_session = LazySparkSession(mock_manager)

        # First call should create the session
        result = lazy_session._get_spark()

        assert result is mock_spark_session
        assert lazy_session._spark is mock_spark_session
        mock_manager.create.assert_called_once()

    def test_get_spark_returns_existing_session_on_subsequent_calls(self, mock_spark_session):
        """Test that _get_spark returns existing session on subsequent calls."""
        mock_manager = Mock(spec=SparkSessionManager)
        mock_manager.create.return_value = mock_spark_session
        mock_project = Mock()
        mock_manager.project = mock_project
        mock_connection = Mock()
        mock_project.connection.return_value = mock_connection
        mock_connection.catalogs = []
        lazy_session = LazySparkSession(mock_manager)

        # First call creates the session
        first_result = lazy_session._get_spark()
        # Second call should return the same session
        second_result = lazy_session._get_spark()

        assert first_result is second_result
        assert first_result is mock_spark_session
        # create should only be called once
        mock_manager.create.assert_called_once()

    def test_get_spark_handles_creation_exception(self):
        """Test that _get_spark properly handles session creation exceptions."""
        mock_manager = Mock(spec=SparkSessionManager)
        mock_manager.create.side_effect = Exception("Creation failed")

        lazy_session = LazySparkSession(mock_manager)

        with pytest.raises(Exception, match="Creation failed"):
            lazy_session._get_spark()

    def test_getattr_delegates_to_spark_session(self, mock_spark_session):
        """Test that __getattr__ delegates to the underlying SparkSession."""
        mock_manager = Mock(spec=SparkSessionManager)
        mock_manager.create.return_value = mock_spark_session
        mock_project = Mock()
        mock_manager.project = mock_project
        mock_connection = Mock()
        mock_project.connection.return_value = mock_connection
        mock_connection.catalogs = []
        mock_spark_session.sql = Mock(return_value="sql_result")

        lazy_session = LazySparkSession(mock_manager)

        # Access an attribute - should delegate to SparkSession
        result = lazy_session.sql

        assert result is mock_spark_session.sql
        mock_manager.create.assert_called_once()

    def test_getattr_handles_spark_access_exception(self):
        """Test that __getattr__ handles exceptions when accessing Spark attributes."""
        mock_manager = Mock(spec=SparkSessionManager)
        mock_manager.create.side_effect = Exception("Spark access failed")

        lazy_session = LazySparkSession(mock_manager)

        with pytest.raises(Exception, match="Spark access failed"):
            _ = lazy_session.some_attribute

    def test_repr_returns_spark_session_repr(self, mock_spark_session):
        """Test that __repr__ returns the SparkSession representation."""
        mock_manager = Mock(spec=SparkSessionManager)
        mock_manager.create.return_value = mock_spark_session
        mock_project = Mock()
        mock_manager.project = mock_project
        mock_connection = Mock()
        mock_project.connection.return_value = mock_connection
        mock_connection.catalogs = []
        mock_spark_session.__repr__ = Mock(return_value="<MockSparkSession>")

        lazy_session = LazySparkSession(mock_manager)

        result = repr(lazy_session)

        assert result == "<MockSparkSession>"
        mock_manager.create.assert_called_once()

    def test_repr_handles_exception(self):
        """Test that __repr__ handles exceptions gracefully."""
        mock_manager = Mock(spec=SparkSessionManager)
        mock_project = Mock()
        mock_manager.project = mock_project
        mock_connection = Mock()
        mock_project.connection.return_value = mock_connection
        mock_connection.catalogs = []
        mock_manager.create.side_effect = Exception("Repr failed")

        lazy_session = LazySparkSession(mock_manager)

        result = repr(lazy_session)

        assert "LazySparkSession (error: Repr failed)" in result

    @patch("sagemaker_studio.utils.spark.session.lazy_spark_session._SparkSession")
    def test_class_property_returns_spark_session_class(self, mock_spark_session_class):
        """Test that __class__ property returns SparkSession class."""
        mock_manager = Mock(spec=SparkSessionManager)
        mock_project = Mock()
        mock_manager.project = mock_project
        mock_connection = Mock()
        mock_project.connection.return_value = mock_connection
        mock_connection.catalogs = []
        lazy_session = LazySparkSession(mock_manager)

        result = lazy_session.__class__

        assert result is mock_spark_session_class

    def test_stop_calls_session_manager_stop(self, mock_spark_session):
        """Test that stop() calls session manager stop and resets session."""
        mock_manager = Mock(spec=SparkSessionManager)
        mock_manager.create.return_value = mock_spark_session
        mock_project = Mock()
        mock_manager.project = mock_project
        mock_connection = Mock()
        mock_project.connection.return_value = mock_connection
        mock_connection.catalogs = []

        lazy_session = LazySparkSession(mock_manager)

        # Create the session first
        lazy_session._get_spark()
        assert lazy_session._spark is not None

        # Stop the session
        lazy_session.stop()

        mock_manager.stop.assert_called_once()
        assert lazy_session._spark is None

    def test_stop_handles_session_manager_exception(self, mock_spark_session, caplog):
        """Test that stop() handles session manager exceptions gracefully."""
        mock_manager = Mock(spec=SparkSessionManager)
        mock_manager.create.return_value = mock_spark_session
        mock_manager.stop.side_effect = Exception("Stop failed")
        mock_project = Mock()
        mock_manager.project = mock_project
        mock_connection = Mock()
        mock_project.connection.return_value = mock_connection
        mock_connection.catalogs = []

        lazy_session = LazySparkSession(mock_manager)

        # Create the session first
        lazy_session._get_spark()

        with caplog.at_level(logging.ERROR):
            lazy_session.stop()

        # Should still reset the session even if stop failed
        assert lazy_session._spark is None
        assert "Error while stopping session manager" in caplog.text

    def test_stop_with_no_session_manager(self):
        """Test that stop() works when no session manager is present."""
        lazy_session = LazySparkSession(None)

        # Should not raise an exception
        lazy_session.stop()

        assert lazy_session._spark is None
