"""
Pytest configuration and shared fixtures for CHIME/FRB API tests.
"""

import pymongo
import pytest

from chime_frb_api.backends import frb_master

# Test database configuration
DB_HOST = "localhost"
DB_PORT = 27017
TEST_EVENT_IDS = [100001, 100002, 100003, 100004, 100005, 100006]


@pytest.fixture(scope="session")
def test_db():
    """Provide access to test MongoDB database."""
    client = pymongo.MongoClient(host=DB_HOST, port=DB_PORT)
    db = client.frb_master
    yield db
    client.close()


@pytest.fixture(scope="session")
def master():
    """Provide FRBMaster instance for all tests."""
    return frb_master.FRBMaster(debug=True, base_url="http://localhost:8001")


@pytest.fixture(scope="session", autouse=True)
def initialize_test_verification_data(test_db):
    """
    Initialize the test database with dummy verification data.

    This runs once per test session and creates sample verification
    and event records that tests can use.
    """

    # Sample event data
    sample_events = [
        {
            "id": 100001,
            "event_type": "FRB",
            "measured_parameters": [
                {
                    "dm": 350.5,
                    "snr": 15.2,
                    "ra": 120.5,
                    "dec": 45.3,
                }
            ],
        },
        {
            "id": 100002,
            "event_type": "FRB",
            "measured_parameters": [
                {
                    "dm": 450.2,
                    "snr": 20.1,
                    "ra": 150.2,
                    "dec": 30.5,
                }
            ],
        },
        {
            "id": 100003,
            "event_type": "RFI",
            "measured_parameters": [
                {
                    "dm": 50.0,
                    "snr": 8.5,
                    "ra": 90.1,
                    "dec": 60.2,
                }
            ],
        },
        {
            "id": 100004,
            "event_type": "FRB",
            "measured_parameters": [
                {
                    "dm": 500.0,
                    "snr": 25.0,
                    "ra": 180.0,
                    "dec": 40.0,
                }
            ],
        },
        {
            "id": 100005,
            "event_type": "FRB",
            "measured_parameters": [
                {
                    "dm": 300.0,
                    "snr": 12.0,
                    "ra": 100.0,
                    "dec": 50.0,
                }
            ],
        },
        {
            "id": 100006,
            "event_type": "FRB",
            "measured_parameters": [
                {
                    "dm": 600.0,
                    "snr": 30.0,
                    "ra": 200.0,
                    "dec": 20.0,
                }
            ],
        },
    ]

    # Sample verification data
    sample_verifications = [
        {
            "id": 100001,
            "user_verification": [
                {"classification": "NEW CANDIDATE", "user": "test_user_1"},
                {"classification": "NEW CANDIDATE", "user": "test_user_2"},
            ],
        },
        {
            "id": 100002,
            "user_verification": [
                {"classification": "KNOWN CANDIDATE", "user": "test_user_1"},
            ],
        },
        {
            "id": 100003,
            "user_verification": [
                {"classification": "RFI", "user": "test_user_1"},
            ],
        },
        {
            "id": 100004,
            "user_verification": [
                {"classification": "FAINT", "user": "test_user_2"},
            ],
        },
        {
            "id": 100005,
            "user_verification": [
                {"classification": "KNOWN SOURCE", "user": "test_user_1"},
            ],
        },
        {
            "id": 100006,
            "user_verification": [
                {"classification": "UNCLASSIFIED", "user": "test_user_2"},
            ],
        },
    ]

    try:
        # Clear any previous test data
        test_db.events.delete_many({"id": {"$in": TEST_EVENT_IDS}})
        test_db.verification.delete_many({"id": {"$in": TEST_EVENT_IDS}})

        # Insert fresh test data
        test_db.events.insert_many(sample_events)
        test_db.verification.insert_many(sample_verifications)

        print(
            f"\n✓ Added {len(sample_events)} test events and {len(sample_verifications)} verifications to test DB."
        )
    except Exception as e:
        print(f"\n✗ Warning: Could not add test data: {e}")
        print("Tests will run but may not have expected data")

    yield

    try:
        test_db.events.delete_many({"id": {"$in": TEST_EVENT_IDS}})
        test_db.verification.delete_many({"id": {"$in": TEST_EVENT_IDS}})
        print("\n✓ Cleaned up test data")
    except Exception as e:
        print(f"\n✗ Warning: Could not clean up test data: {e}")
