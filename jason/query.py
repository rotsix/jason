from jason.lib import log
from jason.parser import is_parser


class QueryError(Exception):
    pass


def parse_filter(f):
    raise Exception("todo")


class Query:
    def __init__(self, ast):
        if is_parser(ast):
            ast = ast.unmarshal()
        self.ast = ast

    def exec(self, req, ast=42, index=0):
        index += 1
        if index == 1:
            log("init")
            ast = self.ast
            if not req:
                log("  empty request")
                return self.ast
            if req[0] != "$":
                self.unexpected(0, req[0])
            log("  dollar")

            #       $*a, $/a or $a
            if len(req) == 2:
                self.unexpected(2, "EOF")
            if len(req) <= 2 and req[3:] not in ["", "$", "$."]:
                self.unexpected(1, req[1])
            return self.exec(req[1:], ast, index)

        # end of query - empty result
        if not ast or not req or req == "":
            return ast

        # select root
        if req[0] == "$":
            log("dollar")
            return self.exec(req[1:], self.ast, index)

        # child
        if req[0] == ".":
            if not isinstance(ast, list) and not isinstance(ast, dict):
                ast = [ast]
            log("dot")
            return self.exec(req[1:], ast, index)

        # wildcard
        if req[0] == "*":
            # TODO
            log("wildcard")
            return self.exec(req[1:], ast, index)

        # filter
        if req[0] == "[":
            f = ""
            i = 1
            try:
                while req[i] != "]":
                    f += req[i]
                    i += 1
            except IndexError:
                self.unexpected("EOF")
            finally:
                index += i + 1
            log(f"filter: {f}")

            # all
            if f == "":
                return self.exec(req[i + 1 :], ast, index)

            # direct access
            try:
                f = int(f)
                return self.exec(req[i + 1 :], ast[f], index)
            except IndexError:
                # a = [0, 1]; a[42]
                return None
            except ValueError:
                # f is not a number
                pass

            # custom filter
            f = parse_filter(f)
            if isinstance(ast, list):
                ast = {k: v for k, v in enumerate(ast)}

            return self.exec(req[i + 1 :], list(filter(f, ast)), index)

        # identifier
        i = 0
        while req[i] not in ["[", "."]:
            if i == len(req) - 1:
                try:
                    print(ast)
                    print(req[: i + 1])
                    return ast[req[: i + 1]]
                except KeyError:
                    return None
            i += 1
        iden = req[:i]
        index += i

        log(f"identifier: {iden}")
        try:
            ast = ast[iden]
        except TypeError:
            return None
        return self.exec(req[i:], ast, index)

    def unexpected(self, i, c):
        raise QueryError(f"unexpected character at index {i}: '{c}'")
