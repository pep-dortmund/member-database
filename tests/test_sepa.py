from member_database.models.sepa import is_valid_iban


def test_iban_validator():
    # Random example from the internet
    assert is_valid_iban("DE89370400440532013000")
    # Changed numbers, so validation digits are wrong
    assert not is_valid_iban("DE893704004240532013000")

