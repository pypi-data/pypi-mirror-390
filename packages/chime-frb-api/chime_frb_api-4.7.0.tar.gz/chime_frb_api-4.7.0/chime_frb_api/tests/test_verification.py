#!/usr/bin/env python
"""Tests for Verification API pagination features."""

import pytest


def test_get_all_verifications_for_all_types(master):
    """Test that get_all_* methods work for all verification types and return data."""
    test_methods = [
        (
            "NEW CANDIDATE",
            master.verification.get_all_new_candidate_verifications,
        ),
        (
            "KNOWN CANDIDATE",
            master.verification.get_all_known_candidate_verifications,
        ),
        ("FAINT", master.verification.get_all_faint_verifications),
        (
            "KNOWN SOURCE",
            master.verification.get_all_known_source_verifications,
        ),
        ("RFI", master.verification.get_all_rfi_verifications),
        (
            "UNCLASSIFIED",
            master.verification.get_all_unclassified_verifications,
        ),
    ]

    for verification_type, method in test_methods:
        verifications = method()
        assert isinstance(verifications, list), (
            f"Failed for {verification_type}"
        )
        assert len(verifications) >= 1, (
            f"No data returned for {verification_type}"
        )


def test_get_verifications_paginated_basic(master):
    """Test basic pagination with default parameters."""
    verifications = master.verification.get_verifications_paginated(
        "NEW CANDIDATE"
    )
    assert isinstance(verifications, list)
    assert len(verifications) >= 1


def test_get_verifications_paginated_with_skip_and_limit(master):
    """Test pagination with skip and limit parameters."""
    verifications = master.verification.get_verifications_paginated(
        "KNOWN CANDIDATE", skip=0, limit=10
    )
    assert isinstance(verifications, list)

    verifications = master.verification.get_verifications_paginated(
        "NEW CANDIDATE", skip=1, limit=1
    )
    assert isinstance(verifications, list)


def test_get_verifications_paginated_all_types(master):
    """Test pagination works for all verification types."""
    verification_types = [
        "NEW CANDIDATE",
        "KNOWN CANDIDATE",
        "KNOWN SOURCE",
        "FAINT",
        "RFI",
        "UNCLASSIFIED",
        "TODELETE",
        "REPEATER",
    ]

    for verification_type in verification_types:
        verifications = master.verification.get_verifications_paginated(
            verification_type, skip=0, limit=5
        )
        assert isinstance(verifications, list), (
            f"Failed for type: {verification_type}"
        )


def test_get_verifications_paginated_different_limits(master):
    """Test pagination respects various limit values."""
    limits = [5, 100, 1000, 1500]

    for limit in limits:
        verifications = master.verification.get_verifications_paginated(
            "NEW CANDIDATE", skip=0, limit=limit
        )
        assert isinstance(verifications, list)


def test_get_verifications_paginated_invalid_type(master):
    """Test that invalid verification type raises ValueError."""
    with pytest.raises(ValueError, match="Invalid verification_type"):
        master.verification.get_verifications_paginated(
            "INVALID_TYPE", skip=0, limit=10
        )


def test_get_verifications_paginated_limit_capping(master):
    """Test that limit over MAX_LIMIT_PER_REQUEST raise an error."""
    with pytest.raises(ValueError, match="limit must be between 1 and 1500"):
        master.verification.get_verifications_paginated(
            "RFI", skip=0, limit=5000
        )


def test_verification_data_with_test_data(master, test_db):
    """Test that seeded test data is accessible through the API."""
    test_verification = test_db.verification.find_one({"id": 100001})
    assert test_verification is not None, "Test data should be accessible"

    verifications = master.verification.get_verifications_paginated(
        "NEW CANDIDATE", skip=0, limit=100
    )

    test_ids = [v.get("id") or v.get("event_id") for v in verifications]
    assert 100001 in test_ids, "Test data should be returned by API"
