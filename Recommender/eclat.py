from sys import argv
import sys
import json
import os
import argparse
import csv
from itertools import chain


def eclat(prefix, items, dict_id, min_support, frequentset):
    while items:
        i, itids = items.pop()
        isupport = len(itids)
        if isupport >= min_support:
            frequentset[frozenset(prefix + [i])] = isupport
            suffix = []
            for j, jtids in items:
                tids = list(set(itids) & set(jtids))
                if len(tids) >= min_support:
                    suffix.append((j, tids))
            dict_id += 1
            eclat(prefix + [i], sorted(suffix, key=lambda item: len(item[1]), reverse=True), dict_id, min_support, frequentset)


def rules(itemset, min_confidence):
    rs = []
    cnt = 0
    for items, supp in itemset.items():
        if len(items) > 1:
            lst = list(items)
            antecedent = lst[:len(lst) - 1]
            consequent = lst[-1:]
            conf = float(itemset[frozenset(items)]) / itemset[frozenset(antecedent)]
            if conf >= min_confidence:
                cnt += 1
                rs.append((antecedent, consequent, supp, conf))

    print('Found %d Rules ' % cnt)
    return rs


def write_frequentsets(output_file, itemset):
    file = open(output_file, 'w+')
    for item, supp in itemset.items():
        file.write(" {} : {} \n".format(list(item), round(supp, 4)))


def write_rule(output_file, rule):
    file = open(output_file, 'w+')
    for a, b, supp, conf in sorted(rule):
        file.write("Rule: {} ==> {} : {} : {} \n".format((a), (b), round(supp, 4), round(conf, 4)))
    file.close()


def parse_args(argv):
    """
    Parse commandline arguments.

    Arguments:
        argv -- An argument list without the program name.
    """
    output_funcs = {
        'frequenct': write_frequentsets,
        'rule': write_rule,
    }
    default_output_func_key = 'json'

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


def write_frequentsets(record, output_file):

    output_file.write(str(record) + os.linesep)


def write_rule(record, output_file):
    output_file.write(str(record) +
            os.linesep)


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


def __eclat(data, **kwargs):
    min_support = kwargs.get('min_support', 100)
    min_confidence = kwargs.get('min_confidence', 0.5)
    frequentset = dict()
    eclat([], sorted(data.items(), key=lambda v: v[1], reverse=True), 0, min_support, frequentset)
    rs = rules(frequentset, min_confidence)
    print('found %d Frequent items' % len(frequentset))
    print('Writing Rules .....')
    for r in rs:
        yield r


def h2v(transactions):
    data = {}
    tid = 0
    for transaction in transactions:
        for item in transaction:
            if item not in data.keys():
                data[item] = [tid]
            else:
                data[item].append(tid)
        tid += 1
    return data


def main(**kwargs):
    _parse_args = kwargs.get('_parse_args', parse_args)
    _load_transactions = kwargs.get('_load_transactions', load_transactions)
    _eclat = kwargs.get('_apriori', __eclat)

    args = _parse_args(sys.argv[1:])
    transactions = _load_transactions(
        chain(*args.input), delimiter=args.delimiter)

    result = _eclat(h2v(transactions), min_support=args.min_support, min_confidence=args.min_confidence)

    for record in result:
        args.output_func(record, args.output)


if __name__ == "__main__":
    main()
