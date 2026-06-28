from optimizer.data_loader import load_all_data
from optimizer.validator import validate_all_data


def test_data_validation_passes():
    data = load_all_data()
    result = validate_all_data(data)

    assert result["is_valid"] is True
    assert result["errors"] == []