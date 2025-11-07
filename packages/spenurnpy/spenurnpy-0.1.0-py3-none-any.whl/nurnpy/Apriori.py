import pandas as pd
from itertools import combinations

def apriori(D, min_sup):
    # Step 1: Find frequent 1-itemsets
    item_counts = {}
    for transaction in D:
        for item in transaction:
            item_counts[frozenset([item])] = item_counts.get(frozenset([item]), 0) + 1

    # Convert support count threshold to actual count if given as fraction
    if 0 < min_sup < 1:
        min_sup = min_sup * len(D)

    L1 = {item for item, count in item_counts.items() if count >= min_sup}
    L = [L1]
    k = 2

    # Step 2: Iteratively find Lk
    while True:
        prev_L = L[-1]
        Ck = apriori_gen(prev_L, k)

        # Count support for candidates
        count_dict = {c: 0 for c in Ck}
        for t in D:
            t_set = set(t)
            for c in Ck:
                if c.issubset(t_set):
                    count_dict[c] += 1

        # Filter by min_sup
        Lk = {c for c, count in count_dict.items() if count >= min_sup}
        if not Lk:
            break
        L.append(Lk)
        k += 1

    # Combine all frequent itemsets
    all_freq = set().union(*L)
    return all_freq


def apriori_gen(L_prev, k):
    """Generate candidate k-itemsets from frequent (k-1)-itemsets."""
    candidates = set()
    L_prev_list = list(L_prev)
    for i in range(len(L_prev_list)):
        for j in range(i + 1, len(L_prev_list)):
            l1 = sorted(list(L_prev_list[i]))
            l2 = sorted(list(L_prev_list[j]))
            if l1[:k - 2] == l2[:k - 2]:
                c = frozenset(set(l1) | set(l2))
                if not has_infrequent_subset(c, L_prev):
                    candidates.add(c)
    return candidates


def has_infrequent_subset(c, L_prev):
    """Check if any (k-1)-subset of candidate c is not in L_prev."""
    for subset in combinations(c, len(c) - 1):
        if frozenset(subset) not in L_prev:
            return True
    return False

# Sample dataset (list of transactions)
transactions = [
    ['milk', 'bread', 'nuts', 'apple'],
    ['milk', 'bread', 'nuts'],
    ['milk', 'bread'],
    ['bread', 'nuts'],
    ['milk', 'apple'],
    ['bread', 'apple']
]

# Minimum support = 0.5 (i.e., itemsets must appear in ≥ 50% of transactions)
min_support = 0.3

# Run Apriori
frequent_itemsets = apriori(transactions, min_support)

print("Frequent Itemsets:")
for itemset in sorted(frequent_itemsets, key=lambda x: (len(x), sorted(x))):
    print(list(itemset))
