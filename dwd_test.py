import unittest

import dwd


class DWDTest(unittest.TestCase):
    def testFormatStationFilename(self):
        formatted_string = dwd.format_station_filename("00001")
        self.assertEqual("tageswerte_KL_00001_", formatted_string)


if __name__ == "__main__":
    unittest.main()
