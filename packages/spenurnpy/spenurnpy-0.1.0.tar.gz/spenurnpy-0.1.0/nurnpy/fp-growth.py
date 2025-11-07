import pandas as pd
from collections import defaultdict, Counter

# -------------------- FP-Tree Node Class --------------------
class FPNode:
    def __init__(self, name, count, parent):
        self.name = name
        self.count = count
        self.parent = parent
        self.children = {}
        self.link = None  # node-link for same item

    def increment(self, count):
        self.count += count

# -------------------- Tree Construction --------------------
def build_fp_tree(transactions, min_sup):
    # Step 1: Count frequency of each item
    item_counts = Counter()
    for trans in transactions:
        item_counts.update(trans)

    # Remove infrequent items
    item_counts = {item: count for item, count in item_counts.items() if count >= min_sup}
    if len(item_counts) == 0:
        return None, None

    # Sort items by descending frequency
    items = [item for item, count in sorted(item_counts.items(), key=lambda x: (-x[1], x[0]))]

    # Header table for node links
    header_table = {item: [count, None] for item, count in item_counts.items()}

    # Create root node
    root = FPNode('null', 1, None)

    # Insert transactions
    for trans in transactions:
        ordered_items = [item for item in items if item in trans]
        insert_tree(ordered_items, root, header_table)

    return root, header_table


def insert_tree(items, node, header_table):
    if len(items) == 0:
        return

    first_item = items[0]
    if first_item in node.children:
        node.children[first_item].increment(1)
    else:
        new_node = FPNode(first_item, 1, node)
        node.children[first_item] = new_node

        # Update header table links
        update_header(header_table, first_item, new_node)

    # Recurse for remaining items
    remaining_items = items[1:]
    insert_tree(remaining_items, node.children[first_item], header_table)


def update_header(header_table, item, new_node):
    # Maintain node-link connections
    head = header_table[item][1]
    if head is None:
        header_table[item][1] = new_node
    else:
        while head.link is not None:
            head = head.link
        head.link = new_node

# -------------------- FP-Growth Mining --------------------
def find_prefix_path(base_pat, node):
    cond_pats = {}
    while node is not None:
        prefix_path = []
        parent = node.parent
        while parent is not None and parent.name != 'null':
            prefix_path.append(parent.name)
            parent = parent.parent
        prefix_path.reverse()
        if len(prefix_path) > 0:
            cond_pats[frozenset(prefix_path)] = node.count
        node = node.link
    return cond_pats


def mine_tree(header_table, min_sup, prefix, freq_item_list):
    # Get items in ascending frequency order
    sorted_items = [item for item, v in sorted(header_table.items(), key=lambda x: x[1][0])]

    for base_pat in sorted_items:
        new_freq_set = prefix.copy()
        new_freq_set.add(base_pat)
        freq_item_list.append((new_freq_set, header_table[base_pat][0]))

        cond_patt_bases = find_prefix_path(base_pat, header_table[base_pat][1])
        cond_tree, cond_header = build_cond_tree(cond_patt_bases, min_sup)

        if cond_header is not None:
            mine_tree(cond_header, min_sup, new_freq_set, freq_item_list)


def build_cond_tree(cond_patt_bases, min_sup):
    # Build conditional FP-tree from pattern base
    transactions = []
    for pattern, count in cond_patt_bases.items():
        for i in range(count):
            transactions.append(list(pattern))
    return build_fp_tree(transactions, min_sup)

# -------------------- Utility: Tree Printing --------------------
def print_tree(node, indent=0):
    print('  ' * indent + f"{node.name} ({node.count})")
    for child in node.children.values():
        print_tree(child, indent + 1)

# Sample transactional dataset
transactions = [
    ['milk', 'bread', 'nuts', 'apple'],
    ['milk', 'bread', 'nuts'],
    ['milk', 'bread'],
    ['bread', 'nuts'],
    ['milk', 'apple'],
    ['bread', 'apple']
]

min_sup = 2

# Build FP-tree
root, header_table = build_fp_tree(transactions, min_sup)

print("FP-Tree Structure:")
print_tree(root)

# Mine frequent patterns
freq_items = []
mine_tree(header_table, min_sup, set(), freq_items)

print("\nFrequent Itemsets:")
for itemset, support in freq_items:
    print(f"{list(itemset)}: {support}")
