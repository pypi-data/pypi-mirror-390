import pytest
from unittest.mock import MagicMock
import sys
import os
import json

# Adjust the path to import from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from join_agent.agent import JoinAgent
from join_agent.models import JoinInput, JoinOutput, ValidationError
from join_agent.constants import PromptsClass # assuming prompts.py is the name of your prompts file

# Mock the SFNAIHandler to avoid actual LLM calls
@pytest.fixture
def mock_ai_handler():
    handler = MagicMock()
    return handler

@pytest.fixture
def join_agent(mock_ai_handler):
    agent = JoinAgent()
    agent.ai_handler = mock_ai_handler
    return agent

# Fixture for common input data
@pytest.fixture
def basic_manual_data_prep_input():
    return JoinInput(
        operation="manual_data_prep",
        tables=["customers", "orders"],
        col_metadata={
            "customers": {
                "customer_id": {"data_type": "int", "row_count": 1000, "null_count": 0, "unique_count": 1000, "sample_values": [1, 2, 3], "description": "Unique identifier for each customer"},
                "name": {"data_type": "str", "row_count": 1000, "null_count": 0, "unique_count": 950, "sample_values": ["Alice", "Bob"], "description": "Customer name"},
                "email": {"data_type": "str", "row_count": 1000, "null_count": 5, "unique_count": 995, "sample_values": ["a@example.com"], "description": "Customer email address"},
                "signup_date": {"data_type": "date", "row_count": 1000, "null_count": 0, "unique_count": 1000, "sample_values": ["2025-01-01"], "description": "Signup date"},
                "region": {"data_type": "str", "row_count": 1000, "null_count": 10, "unique_count": 5, "sample_values": ["US", "EU"], "description": "Customer region"}
            },
            "orders": {
                "order_id": {"data_type": "int", "row_count": 5000, "null_count": 0, "unique_count": 5000, "sample_values": [101,102], "description": "Unique order identifier"},
                "customer_id": {"data_type": "int", "row_count": 5000, "null_count": 0, "unique_count": 1000, "sample_values": [1,2], "description": "FK to customers table"},
                "product_id": {"data_type": "int", "row_count": 5000, "null_count": 0, "unique_count": 100, "sample_values": [11,12], "description": "Product identifier"},
                "quantity": {"data_type": "int", "row_count": 5000, "null_count": 0, "unique_count": 50, "sample_values": [1,2], "description": "Quantity ordered"},
                "order_date": {"data_type": "date", "row_count": 5000, "null_count": 0, "unique_count": 365, "sample_values": ["2025-01-01"], "description": "Date of order"}
            }
        },
        primary_table="customers",
        groupby_fields={"customers": ["customer_id"], "orders": ["customer_id"]},
        use_case="Analyze customer purchasing behavior",
        ml_approach="regression",
        domain_metadata={}
    )

@pytest.fixture
def basic_golden_dataset_input():
    return JoinInput(
        operation="golden_dataset",
        tables=["users", "profiles", "payments"],
        col_metadata={
            "users": {"user_id": {
                    "data_type": "int",
                    "row_count": 1000,
                    "null_count": 0,
                    "unique_count": 1000,
                    "sample_values": [1, 2],
                    "description": "Unique user identifier"
                },
                "username": {
                    "data_type": "string",
                    "row_count": 1000,
                    "null_count": 0,
                    "unique_count": 950,
                    "sample_values": ["alice", "bob"],
                    "description": "Username of the user"
                }
            },
            "profiles": {
                "profile_id": {
                    "data_type": "int",
                    "row_count": 1000,
                    "null_count": 0,
                    "unique_count": 990,
                    "sample_values": [101, 102],
                    "description": "Unique profile identifier"
                },
                "user_id": {
                    "data_type": "int",
                    "row_count": 1000,
                    "null_count": 20,  
                    "unique_count": 980,
                    "sample_values": [1, 2],
                    "description": "Foreign key referencing users"
                }
            },
            "payments": {
                "payment_id": {
                    "data_type": "int",
                    "row_count": 5000,
                    "null_count": 0,
                    "unique_count": 5000,
                    "sample_values": [101, 102],
                    "description": "Unique payment identifier"
                },
                "user_id": {
                    "data_type": "int",
                    "row_count": 5000,
                    "null_count": 50,  
                    "unique_count": 999,
                    "sample_values": [1, 2],
                    "description": "Foreign key referencing users"
                }
            }

        },
        primary_table=None,
        groupby_fields=None,
        use_case=None,
        ml_approach=None,
        domain_metadata=None
    )

@pytest.fixture
def unjoinable_tables_input():
    return JoinInput(
        operation="manual_data_prep",
        tables=["Products", "payments"],
        col_metadata={
            "products": {"product_id": {"data_type": "int", "row_count": 100, "null_count": 0, "unique_count": 100, "sample_values": [11,12], "description": "Unique product identifier"}},
            "payments": {"payment_id": {"data_type": "int", "row_count": 5000, "null_count": 0, "unique_count": 5000, "sample_values": [1001,1002], "description": "Unique payment identifier"}}
        },
        primary_table="products",
        groupby_fields=None,
        use_case=None,
        ml_approach=None,
        domain_metadata={}
    )


# =============================================================================
# TESTS
# =============================================================================

def test_manual_data_prep_success(join_agent, mock_ai_handler, basic_manual_data_prep_input):
    """
    Test case for a successful 'manual_data_prep' operation.
    """
    # Mock the LLM's successful JSON response
    mock_llm_output = {
        "joins": [
            {
                "left_table": "customers",
                "right_table": "orders",
                "join_type": "LEFT JOIN",
                "join_fields": [["customer_id", "customer_id"]]
            }
        ],
        "unjoinable_tables": []
    }
    mock_ai_handler.route_to.return_value = (json.dumps(mock_llm_output), 0.5)

    result, cost = join_agent.execute_task(basic_manual_data_prep_input)

    assert result.joins[0].left_table == "customers"
    assert result.joins[0].right_table == "orders"
    assert result.joins[0].join_type == "LEFT JOIN"
    assert result.joins[0].join_fields == [("customer_id", "customer_id")]
    assert len(result.unjoinable_tables) == 0
    assert cost == 0.5
    print("[TEST SUCCESS] test_manual_data_prep passed!")


def test_golden_dataset_success(join_agent, mock_ai_handler, basic_golden_dataset_input):
    """
    Test case for a successful 'golden_dataset' operation with multiple tables.
    """
    # Mock the LLM's successful JSON response
    mock_llm_output = {
        "joins": [
            {
                "left_table": "profiles",
                "right_table": "users",
                "join_type": "LEFT",
                "join_fields": [["user_id", "user_id"]]
            },
            {
                "left_table": "users",
                "right_table": "payments",
                "join_type": "LEFT",
                "join_fields": [["user_id", "user_id"]]
            }
        ],
        "unjoinable_tables": []
    }
    mock_ai_handler.route_to.return_value = (json.dumps(mock_llm_output), 1.2)

    result, cost = join_agent.execute_task(basic_golden_dataset_input)

    assert len(result.joins) == 2
    assert len(result.unjoinable_tables) == 0
    assert cost == 1.2
    print("[TEST SUCCESS] test_golden_dataset passed!")


def test_invalid_operation(join_agent, basic_manual_data_prep_input):
    """
    Test case for an invalid operation name.
    """
    with pytest.raises(ValueError, match="operation must be 'golden_dataset' or 'manual_data_prep'"):
        basic_manual_data_prep_input.operation = "invalid_op"
        join_agent.execute_task(basic_manual_data_prep_input)
    print("[TEST SUCCESS] test_invalid_operation passed!")


def test_manual_data_prep_too_many_tables(join_agent, basic_manual_data_prep_input):
    """
    Test case for 'manual_data_prep' with more than two tables.
    """
    with pytest.raises(ValueError, match="Only two tables can be analyzed"):
        basic_manual_data_prep_input.tables = ["customers", "orders", "payments"]
        join_agent.execute_task(basic_manual_data_prep_input)
    print("[TEST SUCCESS] test_manual_data_prep_too_many_tables passed!")


def test_unjoinable_tables(join_agent, mock_ai_handler, unjoinable_tables_input):
    """
    Test case where no join keys are found.
    """
    mock_llm_output = {
        "joins": [],
        "unjoinable_tables": ["products", "payments"]
    }
    mock_ai_handler.route_to.return_value = (json.dumps(mock_llm_output), 0.1)

    result, cost = join_agent.execute_task(unjoinable_tables_input)

    assert len(result.joins) == 0
    assert sorted(result.unjoinable_tables) == sorted(["products", "payments"])
    assert cost == 0.1
    print("[TEST SUCCESS] test_unjoinable_tables passed!")
    


def test_malformed_json_response(join_agent, mock_ai_handler, basic_manual_data_prep_input):
    """
    Test case for when the LLM returns a malformed or invalid JSON string.
    """
    # This JSON is missing a "joins" key, which should trigger a ValidationError
    mock_llm_output = """
        {
            "unjoinable_tables": ["customers", "orders"]
        }
    """
    mock_ai_handler.route_to.return_value = (mock_llm_output, 0.5)

    with pytest.raises(ValidationError):
        join_agent.execute_task(basic_manual_data_prep_input)

    print("[TEST SUCCESS] test_malformed_json_response passed!")