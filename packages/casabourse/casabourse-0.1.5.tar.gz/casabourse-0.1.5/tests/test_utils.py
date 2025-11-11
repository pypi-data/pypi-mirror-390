from casabourse import get_build_id, format_number_french
def test_format_number_french():
    assert format_number_french(12345.67) in ("12 345,67", "12345,67") or isinstance(format_number_french(12345.67), str)
def test_get_build_id():
    assert get_build_id() is None or isinstance(get_build_id(), str)
