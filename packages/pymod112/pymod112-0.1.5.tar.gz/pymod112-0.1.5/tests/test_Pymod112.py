import unittest
from src import pymod112


class TestPymod112(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.id1 = "11010519491231002X"
        self.detail = {  # type: ignore
            "id": "11010519491231002X",
            "province": ["11", "北京市"],
            "city": ["01", ""],
            "county": ["05", "朝阳区"],
            "birth_date": ["1949", "12", "31"],
            "gender": "女",
            "result": True,
            "problem": "000",
        }
        self.location = ["北京市", "朝阳区"]
        self.code = "110105"

    def test_mod112(self):
        self.assertTrue(pymod112.mod112(self.id1))
        self.assertEqual(pymod112.mod112(self.detail["id"], details=True, location_check=True), self.detail)  # type: ignore

    def test_location2code(self):
        self.assertEqual(pymod112.location2code(self.location), self.code)

    def test_code2location(self):
        self.location.insert(1, "")
        self.assertEqual(pymod112.code2location(self.code), self.location)
