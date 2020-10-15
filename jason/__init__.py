from argparse import ArgumentParser
from sys import argv, exit

import jason.lib as lib
from jason.lib import log

from jason.api import query, lexer, parser, unmarshal


def parse_args():
    argparser = ArgumentParser()
    argparser.add_argument("-i", "--input", help="input file", default="/dev/stdin")
    argparser.add_argument("query", help="query to perform")
    argparser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")
    if len(argv) == 1:
        argparser.print_usage()
        exit(0)
    return argparser.parse_args()


def main():
    args = parse_args()
    lib.VERBOSE = args.verbose

    with open(args.input) as intput_file:
        json = "\n".join(intput_file.readlines())

    log("::: LEXER :::")
    l = lexer(json)
    log(f"l: {l}")
    log()
    log("::: PARSER :::")
    p = parser(l)
    log(f"p: {p}")
    log(f"p.ast: {p.ast}")
    log()
    log("::: UNMARSHAL :::")
    res = unmarshal(json)
    log(f"py: {res}")
    log()
    log("::: QUERY :::")
    res = query(json, args.query)
    log(f"q: {res}")
    log()

    if not lib.VERBOSE:
        print(res)


if __name__ == "__main__":
    main()
