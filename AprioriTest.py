import time
import itertools
from sys import exit, exc_info
from itertools import combinations
from collections import defaultdict
from optparse import OptionParser
import unittest

from AprioriForLargeData import (
    Apriori

)
class AprioriTest(unittest.TestCase):

    def test_return_items_with_min_support(self):
        ap = Apriori()
        input = "testcase.txt"  
        min_sup = 4
        raw_transactions = ap.load_file(input)
        print "loaded ", len(raw_transactions), " min support is", min_sup
        second_reduced_data, precalc_subsets, inverted_index = ap.reduce_data(raw_transactions, min_sup)
        final_result = ap.run_apriori(second_reduced_data, min_sup, precalc_subsets, inverted_index)

        print "testing"
        """
        input data looks like this
        1) 38 39 41 105 110 487
        2) 38 39 41 109 110
        3) 38 39 41 48 60 367 368
        4) 38 39 41 48 170 189
        5) 36 38 39 41 48 79 80 81
        6) 38 39 41 48 89 110
        7) 39 48 592 593 594 595
        8) 38 39 170 207 603
        """
        print final_result
        expected = {frozenset(['39', '38', '48', '41']): 4,
                    frozenset(['38', '48', '41']): 4,
                    frozenset(['39', '38', '48']): 4,
                    frozenset(['39', '38', '41']): 6,
                    frozenset(['39', '48', '41']): 4}
        self.assertEqual(final_result, expected)

if __name__ == '__main__':
    unittest.main()
