import os
import pytest
import json
from pathlib import Path

from mock_get import get_mock_driver

test_dir = f"{os.getcwd()}/test/mock_data"
test_paths = []
for platform in os.listdir(test_dir):
    for getter in os.listdir(f"{test_dir}/{platform}"):
        for test in os.listdir(f"{test_dir}/{platform}/{getter}"):
            test_paths.append(Path(f"{test_dir}/{platform}/{getter}/{test}"))


@pytest.mark.parametrize("test_path", test_paths)
def test_getter(test_path: Path):
    driver = get_mock_driver(test_path.parts[-3])
    with driver(test_path) as device:
        result = getattr(device, test_path.parts[-2])()

    with open(f"{test_path}/expected_result.json", encoding="utf-8") as fh:
        expected_result = json.load(fh)

    assert result == expected_result
