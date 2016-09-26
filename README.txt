Super Market Optimization Problem. 

1. Supermarket Optimization = Problem Statement
You’ve been hired as a market  consultant to try and help a local supermarket come up with better placement of items based on buyers preferences, and towards that goal you’d like to identify certain association rules based on existing records of buyers transactions.
You are given as input:
•   A transaction database - a file consisting of a single row per transaction, with individual product's SKUs given as space–separated integers. A single transaction consisting of products with SKUs 1001, 1002 and 1003 would have a line that looks like: ‘1001 1002 1003' 
•   A minimal ’support level’ parameter , sigma – a positive integer 
TO DO: Implement, in Python or Java, an efficient algorithm for generating all frequent item sets of size 3 or more: NAMELY: groups of 3 or more items that appear together in the transactions log at least as often as the support level parameter value. 
EXAMPLE: For example, given a value of sigma = 2, all sets of 3 items that appear 2 or more times together in the transaction log should be returned.
The results should be returned as a file with the following format: 
<item set size (N)>, <co-occurrence frequency>, <item 1 id >, <item 2 id>, …. <item N id>
Run the algorithm on the attached transaction log file and provide the results obtained for a value of sigma = 4

2. Algorithm. 
This problem is an instance of the “Association rules mining A Priori algorithm”  (Agrawal and Srikant 1994).   The goal is to find frequently purchased item sets where frequency is defined either as a fraction or as a integer, as in this case. This is called “support”. Here it is 4. In brute force fashion, to compute support for a given set, we go through every transaction and check for every set if the set at hand is   subset of the transaction.  If yes, we increment the total. Crucially, for any set of N items we can generate 2N-1 possible item sets (even if we remove sets of 2 or 1 from the power set, the number gets very large).  This combined with the need to check every transaction can cause a huge performance bottleneck.  Efficiency is a known problem for this algorithm.  However, the first optimization is the “A priori” principle itself:

A priori principle:  if  frequency of itemset < min_support,  then all the  supersets of the itemset have frequency <  min_support.

Note1: the apriori algorithm also involves computing confidence which is the proportion of transactions with item X, in which item Y also appears. We are not concerned with it here, nor are we concerned with mining actual association rules.
Note 2:  because the algorithm is so famous and given the ‘take-home’ nature of the exercise, I did use available resources such as indicated in references below. I believe since this is a known algorithm it is expected in a take-home exam to look at existing resources.  

Algorithm in plain words:
While  len(set_of_items) is greater than 0:
             Create a list of candidate itemsets of length k 
             Remove any sets with frequency < min_support
             With remaining itemsets that meet min_support  create itemsets of length k+1

The iterative elimination of candidates from candidate sets that do not meet support threshold is crucial to speed up the algorithm. However, even with this, the classic implementation that involves scanning all candidate sets for each transaction e.g. code snippet below involves two nested for-loops. When transaction size is small OR candidate set is small, it is slow but feasible. However, as the database of transactions grows and candidate item sets grows , the O(n*k) where n = number of transactions and k= number of candidate sets to explore becomes unmanageable.
while(len(candidate_item_sets) != 0):
   …
    for candidate in candidate_sets
        for transaction in transactions:
            if item_set.issubset(transaction):
	item_subsets+=1
…
3. Optimizations to reduce running time  
This bottleneck is a known problem for Apriori and various optimizations such as parallelizing or map-reduce have been proposed.  It is unmodified form e.g. with the nested loop running over candidates and inside over transactions, a python implementation of algorithm runs a whopping 7hrs (on Mac laptop). In my implementation I propose the following optimizations:
1)	Early elimination of transactions that cannot contain candidate sets of at least 3 items w/ support =4 such as transactions involving fewer than 3 items.  This reduces the number of transactions to ~22,000. Additionally, I remove from consideration any item that occurs by itself < 4 times, as any set containing this item will not meet min_support.
2)	Because the space of possible candidate sets is particularly great when candidate set size is small, eliminating candidate sets of size 3 that does not meet  minsupport early on, helps reduce the search space.  This brings the running time down to about 59 min on same machine.
3)	More crucially, I remove the need to loop over all transactions (~ 22,000 total transactions after transactions of < 3 items have been removed)  by creating an “inverted index” of transactions. Inverted index is a map where each item is key and the possible transactions that  contain this item is the value.  Example:  “39: [ 0, 1, 2, 3,..]” means item 39 is contained in transactions with id 0, 1, 2, 3    With this created, we can just look up for each item in a candidate set all the transactions that involved this item.  Doing this for all the items in a candidate set and finding the transactions they have in common is another way of checking if candidate set is a subset of transaction.  If every item in the candidate contains in its index some transection t, then the candidate is a subset of items purchased in t.  This optimization, while still requires a loop of the form:
          “for candidate_Set in candidate_sets:
		for item in candidate_set: “
	involves much fewer iterations, as the number of individual items in a candidate set is never as great as the number of transactions we had to loop over originally. This brings the running time down to 30 minutes.    
I can imagine many more additional optimizations such as computing subsets in a more efficient manner – there may be some way to do this a la dynamic programming where we leverage created smaller sets to grow subsets.   There could be others such as using a trie map. Finally, the data set is in a sorted order, something I am not currently leveraging, but it may be relevant.

4. Example.
Let’s consider a very small case of the problem at hand.  Let’s assume we have a db containing ONLY these rows: 1 – 6.  Let’s further assume that our support level parameter sigma is 4 as in the original problem statement..  Given our small example, and the statement of the problem above we will recover the following items I show in green.
Input data base reduced:
1) 38 39 41 105 110 487 
2) 38 39 41 109 110 
3) 38 39 41 48 60 367 368 
4) 38 39 41 48 170 189 
5) 36 38 39 41 48 79 80 81
6) 38 39 41 48 89 110 
7) 39 48 592 593 594 595 
8) 38 39 170 207 603 

Output:
1. <4>, < co-occurance-frequency=4, <38> <39> <41> <48> -> the rows we see this are 3, 4, 5, 6.
2. <3>, <co-occurance-frequency=6>, <38> <39> <41> ⇒ the rows we see this are 1-6 in data base.
3. <3>, <co-occurance-frequency=4>, <38> <39> <48> ⇒ the rows we see this are 3, 4, 5, 6 in data base.
Same for other subsets of cardinality 3 of the set of items: {<38> <39> <41> <48> } e.g.
4. <3>, <co-occurance-frequency=4>, <38> <41> <48> ⇒ the rows we see this are 3, 4, 5, 6 in data base.
5. <3>, <co-occurance-frequency=4>, <39> <41> <48> ⇒ the rows we see this are 3, 4, 5, 6 in data base.

itemset frozenset(['39', '38', '48', '41']) Count 4 
itemset frozenset(['39', '48', '41']) Count 4
itemset frozenset(['39', '38', '48']) Count 4
itemset frozenset(['38', '48', '41']) Count 4
itemset frozenset(['39', '38', '41']) Count 6


4. To run code:
https://github.com/tenselogician/SupermarketOptimization.git

python AprioriForLargeData.py  -i myfile.txt -s 4

it outputs a file "frequent_sets_25k.txt" that is uploaded as well onto github in zipped form.

5. Conclusion.

There are other optimizations I can think of that I had not done for the code.  The 
This is a great problem and I really enjoyed working on it!  It is a great example of how even a famous algorithm cannot scale easily to a real life scenario and requires further optimization. Thank you!

References:
Rakesh Agrawal and Ramakrishnan Srikant Fast algorithms for mining association rules in large databases. Proceedings of the 20th International Conference on Very Large Data Bases, VLDB, pages 487-499, Santiago, Chile, September 1994

http://aimotion.blogspot.com/2013/01/machine-learning-and-data-mining.html

http://www.kdnuggets.com/2016/04/association-rules-apriori-algorithm-tutorial.html

https://www.manning.com/books/machine-learning-in-action (Ch 11)

