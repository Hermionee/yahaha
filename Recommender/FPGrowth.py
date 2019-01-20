import csv
import sys
from itertools import chain
import json
import os
import argparse


class TreeNode:
    def __init__(self, nodename, count, nodeparent):
        self.name = nodename
        self.count = count
        self.parent = nodeparent
        self.nextSimilarItem = None
        self.children = {}


def create_fptree(frozends, min_support):
    # scan database at the first time, filter out items whose frequencies are smaller than min support
    head = {}
    for items in frozends.keys():
        for item in items:
            head[item] = head.get(item, 0) + frozends[items]
    head = {k: v for k, v in head.items() if v >= min_support}
    frequent_items = set(head.keys())
    if len(frequent_items) == 0:
        return None, None

    for k in head.keys():
        head[k] = [head[k], None]

    fptree = TreeNode("null", 1, None)
    # scan database at the second time, filter out items for each record
    for items in frozends:
        frequent_items_record = {}
        for item in items:
            if item in frequent_items:
                frequent_items_record[item] = head[item][0]
        if len(frequent_items_record) > 0:
            frequent_items_ordered = [v[0] for v in sorted(frequent_items_record.items(), key=lambda v: v[1], reverse=True)]
            update_fptree(fptree, frequent_items_ordered, head, frozends[items])

    return fptree, head


def update_fptree(fptree, frequent_items_ordered, head, count):
    # handle the first item
    if frequent_items_ordered[0] in fptree.children:
        fptree.children[frequent_items_ordered[0]].count += count
    else:
        fptree.children[frequent_items_ordered[0]] = TreeNode(frequent_items_ordered[0], count, fptree)
        # update head
        if head[frequent_items_ordered[0]][1] is None:

            head[frequent_items_ordered[0]][1] = fptree.children[frequent_items_ordered[0]]
        else:
            update_head(head[frequent_items_ordered[0]][1], fptree.children[frequent_items_ordered[0]])
    # handle other items except the first item
    if len(frequent_items_ordered) > 1:
        update_fptree(fptree.children[frequent_items_ordered[0]], frequent_items_ordered[1::], head, count)


def update_head(node, child):
    while node.nextSimilarItem is not None:
        node = node.nextSimilarItem
    node.nextSimilarItem = child


def mine_fptree(head, prefix, pattern, min_support):
    # for each item in head, find conditional prefix path, create conditional fptree,
    # then iterate until there is only one element in conditional fptree
    head_items = [v[0] for v in sorted(head.items(), key=lambda v: v[1][0])]
    if len(head_items) == 0:
        return

    for item in head_items:
        new_prefix = prefix.copy()
        new_prefix.add(item)
        support = head[item][0]
        pattern[frozenset(new_prefix)] = support

        prefix_path = get_prefix_path(head, item)
        if prefix_path != {}:
            conditional_fptree, conditionalhead = create_fptree(prefix_path, min_support)
            if conditionalhead is not None:
                mine_fptree(conditionalhead, new_prefix, pattern, min_support)


def get_prefix_path(head, item):
    prefix_path = {}
    begin_node = head[item][1]
    prefixs = ascend_tree(begin_node)
    if prefixs:
        prefix_path[frozenset(prefixs)] = begin_node.count

    while begin_node is not None:
        begin_node = begin_node.nextSimilarItem
        prefixs = ascend_tree(begin_node)
        if prefixs:
            prefix_path[frozenset(prefixs)] = begin_node.count
    return prefix_path


def ascend_tree(node):
    prefix = []
    while node is not None and node.parent.name != 'null':
        node = node.parent
        prefix.append(node.name)
    return prefix


def rules_generator(pattern, min_confidence, rules):
    for frequentset in pattern:
        if len(frequentset) > 1:
            get_rules(frequentset, frequentset, rules, pattern, min_confidence)


def get_rules(frequentset, currentset, rules, pattern, min_confidence):
    for frequent_item in currentset:
        ss = subset(currentset, frequent_item)
        if ss in pattern.keys():
            if pattern[frequentset] > pattern[ss]:
                print(frequentset, ss, pattern[frequentset], pattern[ss])
            confidence = pattern[frequentset] / pattern[ss]
            if confidence >= min_confidence:
                flag = False
                for rule in rules:
                    if rule[0] == ss and rule[1] == frequentset - ss:
                        flag = True
                if not flag:
                    rules.append((ss, frequentset - ss, confidence))

                if len(ss) >= 2:
                    get_rules(frequentset, ss, rules, pattern, min_confidence)


def subset(frequentset, str):
    tempset = []
    for item in frequentset:
        if item != str:
            tempset.append(item)
    return frozenset(tempset)


def load_transactions(input_file, **kwargs):
    """
    Load transactions and returns a generator for transactions.

    Arguments:
        input_file -- An input file.

    Keyword arguments:
        delimiter -- The delimiter of the transaction.
    """
    delimiter = kwargs.get('delimiter', '\t')
    for transaction in csv.reader(input_file, delimiter=delimiter):
        yield transaction[0].split(',') if transaction else ['']


def parse_args(argv):
    """
    Parse commandline arguments.

    Arguments:
        argv -- An argument list without the program name.
    """
    output_funcs = {
        'rule': write_rule
    }
    default_output_func_key = 'rule'

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input', metavar='inpath', nargs='*',
        help='Input transaction file (default: stdin).',
        type=argparse.FileType('r'), default=[sys.stdin])
    parser.add_argument(
        '-o', '--output', metavar='outpath',
        help='Output file (default: stdout).',
        type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument(
        '-s', '--min-support', metavar='float',
        help='Minimum support ratio (must be > 0, default: 0.1).',
        type=float, default=0.1)
    parser.add_argument(
        '-c', '--min-confidence', metavar='float',
        help='Minimum confidence (default: 0.5).',
        type=float, default=0.5)
    parser.add_argument(
        '-d', '--delimiter', metavar='str',
        help='Delimiter for items of transactions (default: tab).',
        type=str, default='\t')
    parser.add_argument(
        '-f', '--out-format', metavar='str',
        help='Output format ({0}; default: {1}).'.format(
            ', '.join(output_funcs.keys()), default_output_func_key),
        type=str, choices=output_funcs.keys(), default=default_output_func_key)
    args = parser.parse_args(argv)

    args.output_func = output_funcs[args.out_format]
    return args


def write_rule(record, output_file):
    output_file.write(str(record) + os.linesep)


def FPgrowth(transactions, **kwargs):
    min_support = kwargs.get('min_support', 100)
    min_confidence = kwargs.get('min_confidence', 0.5)

    fptree, head = create_fptree(transactions, min_support)
    pattern = {}
    prefix = set([])
    mine_fptree(head, prefix, pattern, min_support)
    # print("frequent patterns:")
    # print(pattern)
    rules = []
    rules_generator(pattern, min_confidence, rules)
    # print("association rules:")
    # print(rules)
    for rule in rules:
        yield rule


def main(**kwargs):
    """
    Executes Apriori algorithm and print its result.
    """
    # For tests.
    _parse_args = kwargs.get('_parse_args', parse_args)
    _load_transactions = kwargs.get('_load_transactions', load_transactions)
    _fpgrowth = kwargs.get('_apriori', FPgrowth)

    args = _parse_args(sys.argv[1:])
    transactions = _load_transactions(
        chain(*args.input), delimiter=args.delimiter)

    frozends = {}
    for transaction in transactions:
        frozends[frozenset(transaction)] = 1

    result = _fpgrowth(
        frozends,
        min_support=args.min_support,
        min_confidence=args.min_confidence)

    for record in result:
        args.output_func(record, args.output)


if __name__ == '__main__':
    main()
