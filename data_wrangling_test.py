import unittest
import numpy as np

import data_wrangling


class DataWranglingTest(unittest.TestCase):

    def testFormatDatetime(self):
        formatted_string_1 = data_wrangling.format_datetime("1998-07-02")
        self.assertEqual("19980702", formatted_string_1)

        formatted_string_2 = data_wrangling.format_datetime(np.datetime64("1998-07-02"))
        self.assertEqual("19980702", formatted_string_2)

        formatted_string_3 = data_wrangling.format_datetime(899337600, unit = "s") # same date but as integer unix timestamp
        self.assertEqual("19980702", formatted_string_3)

        formatted_string_1 = data_wrangling.format_datetime("1998-07-02", without_year = True)
        self.assertEqual("0702", formatted_string_1)

if __name__ == "__main__":
    unittest.main()
