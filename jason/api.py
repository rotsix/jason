from jason.lexer import Lexer, is_lexer
from jason.parser import Parser, is_parser
from jason.query import Query
from jason.lib import log


def query(ast, request):
    log("api.query")
    if isinstance(ast, str):
        log("  api.query: arg is str")
        return query(lexer(ast), request)
    if is_lexer(ast):
        log("  api.query: arg is lexer")
        return query(parser(ast), request)
    if is_parser(ast):
        log("  api.query: arg is parser")
        q = Query(ast)
        return q.exec(request)
    raise Exception("wrong ast type")


def unmarshal(ast):
    log("api.unmarshal")
    if isinstance(ast, str):
        log("  api.unmarshal: arg is str")
        return unmarshal(lexer(ast))
    if is_lexer(ast):
        log("  api.unmarshal: arg is lexer")
        return unmarshal(parser(ast))
    if is_parser(ast):
        log("  api.unmarshal: arg is parser")
        return ast.unmarshal()
    raise Exception("wrong ast type")


def lexer(json):
    log("api.lexer")
    if isinstance(json, str):
        log("  api.lexer: arg is str")
        return list(Lexer(str(json)))
    if is_lexer(json):
        log("  api.lexer: arg is lexer")
        return json
    raise Exception("wrong lexer type")


def parser(lex):
    log("api.parser")
    if isinstance(lex, str):
        log("  api.parser: arg is str")
        return lexer(lex)
    if is_lexer(lex):
        log("  api.parser: arg is lexer")
        return Parser(lex)
    if is_parser(lex):
        log("  api.parser: arg is parser")
        return lex
    raise Exception("wrong lexer type")
