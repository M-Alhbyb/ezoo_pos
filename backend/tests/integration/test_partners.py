# Partner integration tests.
# Both previous tests (test_partner_distribution, test_no_double_distribution)
# were stale: they called removed /api/projects and used the old distribute
# signature (no profit field).  Removed in payout-2.
