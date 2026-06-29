from retail_analytics.cleaning.br_holidays_cleaner import normalize_holiday_record


def test_normalize_holiday_record_maps_api_fields_to_clean_columns() -> None:
    raw_record = {
        "date": "2026-01-01",
        "localName": "Confraternização Universal",
        "name": "New Year's Day",
        "countryCode": "BR",
        "fixed": False,
        "global": True,
        "counties": None,
        "launchYear": None,
        "types": ["Public"],
    }

    normalized = normalize_holiday_record(
        record=raw_record,
        source_file_name="br_public_holidays_2026.json",
        extracted_at="2026-06-16T10:00:00+00:00",
        run_date="2026-06-16",
    )

    assert normalized["holiday_date"] == "2026-01-01"
    assert normalized["holiday_name"] == "New Year's Day"
    assert normalized["holiday_local_name"] == "Confraternização Universal"
    assert normalized["country_code"] == "BR"
    assert normalized["is_fixed"] is False
    assert normalized["is_global"] is True
    assert normalized["counties"] is None
    assert normalized["launch_year"] is None
    assert normalized["holiday_types"] == '["Public"]'
    assert normalized["source_system"] == "nager_date"
    assert normalized["source_file_name"] == "br_public_holidays_2026.json"
    assert normalized["extracted_at"] == "2026-06-16T10:00:00+00:00"
    assert normalized["run_date"] == "2026-06-16"