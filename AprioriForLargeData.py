# -*- coding: utf-8 -*-
import time
import itertools
from sys import exit, exc_info
from itertools import combinations
from collections import defaultdict
from optparse import OptionParser

class Apriori:
    """Algorithm computes frequent itemsets, given a data file
    and a support parameter.
    """

    def __init__(self):

        print "intialized."

    def get_input(self, parser):
        '''parse the arguments provided in the command line'''
        parser.add_option('-i', '--input', type='string', help='input file',
                          dest='input')
        parser.add_option('-s', '--support', type='int', help='minimum support',
                          dest='support')
        (options, args) = parser.parse_args()
        if not options.input:
            print('Input filename not given, will use default')

        if not options.support:
            print('Support not given, will use default, which is 4')

        return (options, args)

    def load_file(self, file_name):
        '''Returns the transactions from a given file. Items must be
        separated by spaces.

        :returns all_transactions: a list
        '''
        try:
            with open(file_name) as f:
                all_data = f.read().split('\n')
                f.close()
        except IOError as e:
            print 'I/O error({0}): {1}'.format(e.errno, e.strerror)
            exit()
        except:
            print 'Unexpected error: ', exc_info()[0]
            exit()
        return all_data

    def reduce_data(self, all_data, minsupport):
        """Reduces data by removing any item that does not meet
        min_support.  Also removes any rows of data that have
        fewer than 3 items
        Args:
            param1: all data items from load_file.
            param2: support
        Returns:
            Return reduced_data, a list
                  precalc_subsets, a map subsets of 2 and 3 and their counts
                  inverted_index, a map of items and transaction lists w/ these items
        """
        initial_reduced_data = []  # list of all transactions
        second_reduced_data = []  # list of reduced transactions
        # map containing item as key and all the transaction ids containing it as value
        inverted_index = {}
        # of of items and their frequencies. Used to eliminate rare from start.
        my_item_map = {}
        precalc_subsets = {}  # sets of size 3 and 2 and their counts
        for i in range(len(all_data)):
            row = all_data[i]
            items = row.split()
            ## make pre comp subsets
            if len(items) > 2:
                subsets2 = self._findsubsets(set(items), 2)
                ## there is some pretty way to do this iteratively but using built in func
                subsets3 = self._findsubsets(set(items), 3)
                # subsets4 = findsubsets(set(items), 4)
                precalc_subsets = self._memoize_small_sets(subsets2, precalc_subsets)
                precalc_subsets = self._memoize_small_sets(subsets3, precalc_subsets)
                # transactions_to_subsets[row] = subsets3
                # first level of reduction - remove any transaction length < 3
                initial_reduced_data.append(items)
                for item in items:
                    if item not in my_item_map:
                        my_item_map[item] = 1
                    else:
                        my_item_map[item] += 1
                    if item not in inverted_index:
                        inverted_index[item] = [i]
                    else:
                        inverted_index[item].append(i)
        ## second level of reduction - transactions w/ items whose
        ## frequency < minsupport
        for itemset in initial_reduced_data:
            smaller = []
            for item in itemset:
                if my_item_map[item] >= minsupport:
                    smaller.append(item)
            ## this reduce the length of each transaction by removing
            # items that do not occur often from the transaction itself.
            # helps contain the number of possible subsets we will generate
            second_reduced_data.append(smaller)  ## only take high occurance from start
        print " this many items in original ",   len(all_data)
        print " this many data in final reduced", len(second_reduced_data)
        return second_reduced_data, precalc_subsets, inverted_index

    def _memoize_small_sets(self, subsets, precalc_subsets):
        '''
        :param subsets: subsets of len 2 and three
        :param precalc_subsets: map of subset and its count
        :return: precalc_subset
        '''
        for s2 in subsets:
            str_s2 = " ".join(list(s2))
            if str_s2 not in precalc_subsets:
                precalc_subsets[str_s2] = 1
            else:
                precalc_subsets[str_s2] += 1
        return precalc_subsets

    def _findsubsets(self, S, m):
        '''
        :param S: set
        :param m: integer
        :return: all sets from set S of size(integer)
        '''
        ## could be more elegant or more efficient here, but using
        ## built in method.
        return set(itertools.combinations(S, m))

    def _find_common(self, all_candidates):
        '''finds overlapping elements in sets'''

        result = set(all_candidates[0])
        for s in all_candidates[1:]:
            result.intersection_update(s)
        return result

    def generate_initial_candidates(self, dataset):
        '''Generate intital candidate sets of size one.'''
        candidate_list = []
        initial_candidates = []
        for transaction in dataset:
            for item in transaction:
                candidate_list.append([item])
                initial_candidates.append(frozenset([item]))
        return initial_candidates

    def generate_more(self, freq_sets, k, memo, minsupport):
        '''Generate the self joins of transactions from candidate sets.
        Also eliminates candidates of size 2 or 3 here.
        There could be some nicer way to do this.
        I took lines ~ 163 - 170 from one of the implementations, [textbook Ch11
        mentioned in references in readme.txt ] but i don't
        think it is the best way to do self joins.
        Other ways do not seem better either. Leaving as is in interests of time.
        The crucial reduction of elements in lines 178 - 193 and inverted index look
        used in prune() method without which this runs in ~ 7hrs up are mine.'''

        start_time = time.time()
        initial_list = [];
        reduced_candidate_list = []
        if k >= 2: # dont iterate if lists are going to be empty
            for i in range(len(freq_sets)):
                for j in range(i + 1,len(freq_sets)):
                    L1 = list(freq_sets[i])[:k - 2]
                    L2 = list(freq_sets[j])[:k - 2]
                    L1.sort()
                    L2.sort()
                    if L1 == L2: ## if items from 0 to k-2 are the same in list
                        join = freq_sets[i].union(freq_sets[j])
                        initial_list.append(join) ## a way to join only common elements
        ## reduce list by eliminating infrequent sets of 3
        ## crucial step in reducing the number of iterations over candidate sets
        for i in range(len(initial_list)):
            item = list(initial_list[i])
            if len(item) >= 2 and len(item) < 4:
                item_string = " ".join(item)
                if item_string in memo:
                    freq = memo[item_string]
                    if freq >= minsupport:
                        reduced_candidate_list.append(initial_list[i])
            else:
                reduced_candidate_list.append(initial_list[i])
        print("spent this much time in generate_more ", "--- %s seconds ---" % (time.time() - start_time))
        print "reduced_candidate_list", len(reduced_candidate_list), " full list ", len(initial_list)
        return reduced_candidate_list

    def prune(self, candidates, min_support, inverted):  ## remove what does not meet support
        '''Eliminates per level any sets that do not meet support.
        Returns all candidates that meets a minimum support level'''

        minsupport_map = {}
        initial_map = {}
        start_time = time.time()  ## start timing
        print " this many candidates ", len(candidates)
        for can in candidates:  ## THIS IS VERY EXPENSIVE ; JUST LOOK UP CANDIDATES PERHAPS
            ## here we replace the loop over all transactions (n = ~ 25,000) with
            # loop over all members of candidate set
            candidate_transactions = []
            ## this is where usually the algorithm has a loop over all transactions
            ## while we still loop over each item in candidate, it is not close
            ## to looping over 25,000 transactions
            ## perhaps there is some better way to do this still.
            for c in can:
                transactions = inverted[c]  # list of transactions containing c
                candidate_transactions.append(transactions)
            ## get all the ids of transactions candidates share, e.g. they are subset of
            common = self._find_common(candidate_transactions)
            ## if candidate is a subset of some transaction,
            # # then add count of how many times we see it
            if len(common) > 0:
                initial_map[can] = len(common)

        for key in initial_map:
            support = initial_map[key]
            if support >= min_support:
                 minsupport_map[key] = support
        print(" this much time spent in prune ", "--- %s seconds ---" % (time.time() - start_time))
        return minsupport_map

    def run_apriori(self,dataset, minsupport, memo, inverted):
        '''The main algorithm. '''

        final_result = {}
        initial_candidates = self.generate_initial_candidates(dataset)
        #print "about to run prun for the very first time ", "dataset ",
        # "cand set ", len(initial_candidates)
        print "this is candidates before while loop ", len(initial_candidates)
        ## remove  candidates
        pruned_map = self.prune(initial_candidates, minsupport, inverted)
        pruned_list = [pruned_map.keys()]
        k = 2;
        print "just ran first round of elimination. about to enter while loop"
        while (len(pruned_list[k-2]) >  0): ## this way of writing while loop is also from
            ## https://www.manning.com/books/machine-learning-in-action (Ch 11)
            ## get next candidate lists
            augmented_candidates = self.generate_more(pruned_list[k - 2], k, memo, minsupport)
            ## prune candidates that were returned at previous iteration
            intermediate_candidates = self.prune(augmented_candidates, minsupport, inverted)
            print "we are at k ", k, " this many candidates", len(augmented_candidates)
            pruned_map.update(intermediate_candidates)
            print  "candidates at k", len(augmented_candidates)
            pruned_list.append(intermediate_candidates.keys())
            k += 1
        ## we don't care about candidate sets whose size is < 3
        ## we remove any set that has less items than 2
        for i in pruned_map:
            if  len(i) > 2:
                final_result[i] = pruned_map[i]
        return final_result

    def record_output(self, final_map, output_file):
        '''
        :param final_map:
        :return: nothing to return.
         Creates final output in the forma:
         <item set size (N)>, <co-occurrence frequency>, <item 1 id >, …. <item N id>

        '''

        with open(output_file, "w") as fw:
            fw.write("item_size,co-occurance,item_lists" +"\n")
            print " almost done writing output "
            for tup in reversed(sorted(final_map.items(), key=lambda x: x[1])):
                list_form = list(tup[0])
                fw.write((str(len(tup[0]))) + "," + str(tup[1]) + "," + \
                         str(list_form) + "\n")

        pass


if __name__ == '__main__':
    ap = Apriori()
    usage_text = 'Usage: %prog -i input_file -s minsup'

    parser = OptionParser(usage=usage_text)
    (options, args) = ap.get_input(parser)
    if options.input is not None:
        raw_transactions = ap.load_file(options.input)
    else:
        print "loading default input file "
        input = "retail_25k.dat" # test file = "testcase.txt"
        raw_transactions = ap.load_file(input)
    if options.support is not None:
        min_sup = options.support
    else:
        min_sup = 4
    # measure process time
    output_file = "frequent_sets_25K.txt"
    start_time = time.time()
    reduced_data, precalc_subsets, inverted_index = ap.reduce_data(raw_transactions, min_sup)
    final_result = ap.run_apriori(reduced_data, min_sup, precalc_subsets, inverted_index)
    ap.record_output(final_result, output_file)
    print("--- %s seconds ---" % (time.time() - start_time))
