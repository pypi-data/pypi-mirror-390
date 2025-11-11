#!/usr/bin/env python

import logging
from urllib.parse import quote

from chime_frb_api.core import API

log = logging.getLogger(__name__)


class Verification:
    """
    CHIME/FRB Verification API
    """

    # Maximum number of records the FRB-Master Verifications API returns per request
    MAX_LIMIT_PER_REQUEST = 1500

    VERIFICATION_TYPES = {
        "FAINT",
        "KNOWN CANDIDATE",
        "KNOWN SOURCE",
        "NEW CANDIDATE",
        "RFI",
        "UNCLASSIFIED",
        "TODELETE",
        "REPEATER",
    }

    def __init__(self, API: API):
        self.API = API

    def get_verifications_paginated(
        self,
        verification_type: str,
        skip: int = 0,
        limit: int = 1500,
    ) -> list:
        """Retrieves CHIME/FRB Verification records with manual batch control.

        Use this method when you need fine-grained control over how many events
        to fetch and from which offset.

        For example, loading data in specific chunks.

        Args:
            verification_type (str): The type of verification to retrieve.
                Valid types: FAINT, KNOWN CANDIDATE, KNOWN SOURCE, NEW CANDIDATE,
                RFI, UNCLASSIFIED, TODELETE, REPEATER
            skip (int): Number of records to skip (pagination offset). Default: 0
            limit (int): Maximum number of records to return per request.
                Must be between 1 and 1500. Default: 1500

        Returns:
            A list of dictionaries containing verification records for the
            requested page.

        Example:
            ### Get first 100 records
            batch_1 = verification.get_verifications_paginated("NEW CANDIDATE", skip=0, limit=100)

            ### Get next 100 records
            batch_2 = verification.get_verifications_paginated("NEW CANDIDATE", skip=100, limit=100)

            ### Get the next 100 records
            batch_3 = verification.get_verifications_paginated("NEW CANDIDATE", skip=200, limit=100)
        """

        if limit < 1 or limit > self.MAX_LIMIT_PER_REQUEST:
            raise ValueError(
                f"limit must be between 1 and {self.MAX_LIMIT_PER_REQUEST}"
            )

        if verification_type not in self.VERIFICATION_TYPES:
            raise ValueError(
                f"Invalid verification_type: {verification_type}. "
                f"Must be one of: {', '.join(self.VERIFICATION_TYPES)}"
            )

        params = {"skip": skip, "limit": limit}
        verification_type_encoded = quote(verification_type)

        return self.API.get(
            f"/v1/verification/get-verifications/{verification_type_encoded}",
            params=params,
        )

    def _get_all_verifications_auto_paginate(
        self, verification_type: str
    ) -> list:
        """Internal method to fetch ALL verification records by auto-paginating.

        This method automatically handles pagination by making multiple API calls
        in batches of 1500 records until all records are retrieved.

        Args:
            verification_type (str): The type of verification to retrieve.

        Returns:
            A complete list of all verification records of the specified type.
        """
        all_results = []
        skip = 0
        batch_size = self.MAX_LIMIT_PER_REQUEST

        while True:
            batch = self.get_verifications_paginated(
                verification_type, skip=skip, limit=batch_size
            )

            if not batch:
                break

            all_results.extend(batch)

            if len(batch) < batch_size:
                break

            skip += batch_size
            log.info(
                f"Fetched {len(all_results)} {verification_type} verifications so far, "
                f"continuing..."
            )

        log.info(
            f"Fetched total of {len(all_results)} {verification_type} verification records"
        )
        return all_results

    def get_all_new_candidate_verifications(self) -> list:
        """Retrieves ALL CHIME/FRB Verification records of type NEW CANDIDATE.

        Note: For large datasets, this may take some time and use significant
        memory. If you need more control, use get_verifications_paginated()
        instead.

        Returns:
            A complete list of all events with NEW CANDIDATE classification.

        Example:
            ### Get ALL NEW CANDIDATE verifications (could be 5000+ records)
            all_verifications = verification.get_all_new_candidate_verifications()
        """
        return self._get_all_verifications_auto_paginate("NEW CANDIDATE")

    def get_all_known_candidate_verifications(self) -> list:
        """Retrieves ALL CHIME/FRB Verification records of type KNOWN CANDIDATE.

        Note: For large datasets, this may take some time and use significant
        memory. If you need more control, use get_verifications_paginated()
        instead.

        Returns:
            A complete list of all events with KNOWN CANDIDATE classification.

        Example:
            ### Get ALL KNOWN CANDIDATE verifications
            all_verifications = verification.get_all_known_candidate_verifications()
        """
        return self._get_all_verifications_auto_paginate("KNOWN CANDIDATE")

    def get_all_faint_verifications(self) -> list:
        """Retrieves ALL CHIME/FRB Verification records of type FAINT.

        Note: For large datasets, this may take some time and use significant
        memory. If you need more control, use get_verifications_paginated()
        instead.

        Returns:
            A complete list of all events with FAINT classification.

        Example:
            ### Get ALL FAINT verifications
            all_verifications = verification.get_all_faint_verifications()
        """
        return self._get_all_verifications_auto_paginate("FAINT")

    def get_all_known_source_verifications(self) -> list:
        """Retrieves ALL CHIME/FRB Verification records of type KNOWN SOURCE.

        Note: For large datasets, this may take some time and use significant
        memory. If you need more control, use get_verifications_paginated()
        instead.

        Returns:
            A complete list of all events with KNOWN SOURCE classification.

        Example:
            ### Get ALL KNOWN SOURCE verifications
            all_verifications = verification.get_all_known_source_verifications()
        """
        return self._get_all_verifications_auto_paginate("KNOWN SOURCE")

    def get_all_rfi_verifications(self) -> list:
        """Retrieves ALL CHIME/FRB Verification records of type RFI.

        Note: For large datasets, this may take some time and use significant
        memory. If you need more control, use get_verifications_paginated()
        instead.

        Returns:
            A complete list of all events with RFI classification.

        Example:
            ### Get ALL RFI verifications
            all_verifications = verification.get_all_rfi_verifications()
        """
        return self._get_all_verifications_auto_paginate("RFI")

    def get_all_unclassified_verifications(self) -> list:
        """Retrieves ALL CHIME/FRB Verification records of type UNCLASSIFIED.

        Note: For large datasets, this may take some time and use significant
        memory. If you need more control, use get_verifications_paginated()
        instead.

        Returns:
            A complete list of all events with UNCLASSIFIED classification.

        Example:
            ### Get ALL UNCLASSIFIED verifications
            all_verifications = verification.get_all_unclassified_verifications()
        """
        return self._get_all_verifications_auto_paginate("UNCLASSIFIED")

    def get_all_todelete_verifications(self) -> list:
        """Retrieves ALL CHIME/FRB Verification records of type TODELETE.

        Note: For large datasets, this may take some time and use significant
        memory. If you need more control, use get_verifications_paginated()
        instead.

        Returns:
            A complete list of all TODELETE verification records.

        Example:
            ### Get ALL TODELETE verifications
            all_verifications = verification.get_all_todelete_verifications()
        """
        return self._get_all_verifications_auto_paginate("TODELETE")

    def add_verification(self, event_id, verification: dict) -> dict:
        """Adds a new CHIME/FRB Verification record to Verification Database.

        Args:
            event_id: The event ID to add verification for.
            verification (dict): A dictionary of CHIME/FRB Verification record.

        Returns:
            A dictionary containing the added verification record.
        """
        return self.API.post(
            f"/v1/verification/add-user-classification/{event_id}",
            json=verification,
        )

    def get_verification_for_event(self, event_id) -> dict:
        """Retrieves a CHIME/FRB Verification record for a given event_id.

        Args:
            event_id (str): The event_id of the CHIME/FRB Verification record.

        Returns:
            A dictionary containing verification record for that event.
        """
        return self.API.get(f"/v1/verification/get-verification/{event_id}")

    def get_conflicting_verifications_faint(self) -> list:
        """Retrieves verification records for events that have conflicting tsar verifications and at least one classification of FAINT.

        Returns:
            A list of dictionaries each contains an eligible event verification record.
        """
        return self.API.get(
            "/v1/verification/get-conflicting-verifications-faint"
        )
