"""Tests for AthenaSparkSessionManager."""

import sys
import unittest
from unittest.mock import Mock, patch

# Mock pyspark before importing  # noqa: E402
sys.modules["pyspark"] = Mock()
sys.modules["pyspark.sql"] = Mock()
sys.modules["pyspark.sql.connect"] = Mock()
sys.modules["pyspark.sql.connect.session"] = Mock()
sys.modules["pyspark.sql.connect.client"] = Mock()

# Mock Project class before any imports to prevent Domain ID error
with patch("sagemaker_studio.Project"):
    from sagemaker_studio.utils.spark.session.athena.athena_spark_session_manager import (
        AthenaSparkSessionManager,
    )


class TestAthenaSparkSessionManager(unittest.TestCase):
    """Test cases for AthenaSparkSessionManager."""

    @patch(
        "sagemaker_studio.utils.spark.session.athena.athena_spark_session_manager.AthenaSparkSessionManager._lazy_init"
    )
    def test_create(self, mock_lazy_init):
        """Test create method."""
        mock_lazy_init.side_effect = Exception("Test exception")

        manager = AthenaSparkSessionManager("test_connection")

        with self.assertRaises(Exception):
            manager.create()


if __name__ == "__main__":
    unittest.main()
