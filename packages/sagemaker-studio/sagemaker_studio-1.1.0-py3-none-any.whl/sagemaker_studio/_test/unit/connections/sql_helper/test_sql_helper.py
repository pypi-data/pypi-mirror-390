from dataclasses import make_dataclass

from sagemaker_studio.connections.sql_helper.big_query_sql_helper import BigQuerySqlHelper
from sagemaker_studio.connections.sql_helper.ddb_sql_helper import DDBSQLHelper
from sagemaker_studio.connections.sql_helper.mssql_sql_helper import MSSQLHelper
from sagemaker_studio.connections.sql_helper.mysql_sql_helper import MySQLHelper
from sagemaker_studio.connections.sql_helper.postgresql_helper import PostgreSQLHelper
from sagemaker_studio.connections.sql_helper.snowflake_sql_helper import SnowflakeSqlHelper

connection = make_dataclass("Connection", ["secret", "connection_creds", "data"])(
    {"username": "admin", "password": "secret"},
    make_dataclass("ConnectionCredentials", [])(),
    make_dataclass("ConnectionData", ["physical_endpoints"])(
        [
            make_dataclass("PhysicalEndpoint", ["awsLocation", "glueConnection"])(
                awsLocation={"awsRegion": "us-east-1"},
                glueConnection=make_dataclass("GlueConnection", ["connectionProperties"])(
                    connectionProperties={
                        "DATABASE": "sales",
                        "HOST": "db.example.com",
                        "PORT": "1433",
                        "WAREHOUSE": "wh1",
                    },
                ),
            )
        ]
    ),
)

snowflake_connection = make_dataclass("Connection", ["secret", "connection_creds", "data"])(
    {"username": "admin", "password": "secret"},
    make_dataclass("ConnectionCredentials", [])(),
    make_dataclass("ConnectionData", ["physical_endpoints"])(
        [
            make_dataclass("PhysicalEndpoint", ["awsLocation", "glueConnection"])(
                awsLocation={"awsRegion": "us-east-1"},
                glueConnection=make_dataclass("GlueConnection", ["connectionProperties"])(
                    connectionProperties={
                        "DATABASE": "sales",
                        "HOST": "db.example.com.snowflakecomputing.com",
                        "PORT": "1433",
                        "WAREHOUSE": "wh1",
                    },
                ),
            )
        ]
    ),
)


def test_to_big_query_helper_sql_config_returns_secret_identity():
    result = BigQuerySqlHelper.to_sql_config(connection)
    assert result == {"password": "secret", "username": "admin"}


def test_to_ddb_helper_sql_config_returns_secret_identity():
    result = DDBSQLHelper.to_sql_config(connection)
    assert result == {"region": "us-east-1"}


def test_to_mssql_helper_sql_config_returns_secret_identity():
    result = MSSQLHelper.to_sql_config(connection)
    assert result == {
        "host": "db.example.com",
        "port": 1433,
        "user": "admin",
        "database": "sales",
        "password": "secret",
    }


def test_to_mysql_helper_sql_config_returns_secret_identity():
    result = MySQLHelper.to_sql_config(connection)
    assert result == {
        "host": "db.example.com",
        "port": 1433,
        "user": "admin",
        "database": "sales",
        "password": "secret",
    }


def test_to_postgres_helper_sql_config_returns_secret_identity():
    result = PostgreSQLHelper.to_sql_config(connection)
    assert result == {
        "host": "db.example.com",
        "port": 1433,
        "user": "admin",
        "database": "sales",
        "password": "secret",
    }


def test_to_snowflake_helper_sql_config_returns_secret_identity():
    result = SnowflakeSqlHelper.to_sql_config(snowflake_connection)
    assert result == {
        "host": "db.example.com.snowflakecomputing.com",
        "port": 1433,
        "user": "admin",
        "database": "sales",
        "password": "secret",
        "account": "db.example.com.us-east-1",
        "region": "us-east-1",
        "warehouse": "wh1",
    }
