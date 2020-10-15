from jason.lib import log
import jason.lexer as lexer


class ParserError(Exception):
    pass


class Value:
    class OBJECT:  # { prop, prop }
        def __init__(self, properties=None):
            if properties:
                self.properties = properties
            else:
                self.properties = []

    class ARRAY:  # [ value, value ]
        def __init__(self, values=None):
            if values:
                self.values = values
            else:
                self.values = []

    class PROPERTY:  # 'a': 'b'
        def __init__(self, key, value):
            self.key = key
            self.value = value

    class NULL:  # null
        pass

    class STRING:  # "word"
        def __init__(self, value):
            self.value = value

    class NUMBER:  # 42; -68,5; 1e8
        def __init__(self, value):
            self.value = value

    class BOOLEAN:  # true, false
        def __init__(self, value):
            self.value = value


def is_parser(obj):
    return isinstance(obj, Parser)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.position = 0
        self.current = ""
        self.ast = self.read_value()

    def _read_next(self):
        if self.position >= len(self.lexer):
            self.current = "EOF"
            return
        self.current = self.lexer[self.position]
        self.position += 1

    def _unread(self):
        if self.position <= 0:
            raise ParserError("cannot unread, already at start")
        self.position -= 1
        self.current = self.lexer[self.position]

    def read_value(self, indent=""):
        log(f"{indent}read_value")
        self._read_next()

        if self.current == "EOF":
            log(f"{indent}  EOF")
            return None

        if isinstance(self.current, lexer.Value.BRACE_LEFT):
            res = self.read_object(indent + "  ")
            log(f"{indent}  found object")
            return res

        if isinstance(self.current, lexer.Value.BRACKET_LEFT):
            res = self.read_array(indent + "  ")
            log(f"{indent}  found array")
            return res

        for lit in [
            lexer.Value.STRING,
            lexer.Value.NUMBER,
            lexer.Value.BOOLEAN,
            lexer.Value.NULL,
        ]:
            if isinstance(self.current, lit):
                self._unread()
                res = self.read_litteral(indent + "  ")
                log(f"{indent}  found litteral")
                return res

        # brace and bracket right, colon, comma
        self.fail()

    def _read_until(self, read, end, separator=lexer.Value.COMMA, indent=""):
        sep = True
        empty = True

        def reach_end():
            log(f"{indent}  read_end..", end="")
            self._read_next()
            if isinstance(self.current, end):
                log("found")
                return True
            self._unread()
            log("not found")
            return False

        while not reach_end():
            empty = False
            if not sep:
                self.fail()
            sep = False
            yield read(indent + "  ")
            log(f"{indent}  read_comma..", end="")
            self._read_next()
            if isinstance(self.current, separator):
                log("found")
                sep = True
            else:
                log("not found")
                self._unread()
        if sep and not empty:  # trailing comma
            self.fail()

    def read_object(self, indent=""):
        log(f"{indent}read_object")
        res = Value.OBJECT()
        end = lexer.Value.BRACE_RIGHT
        res.properties = list(self._read_until(self.read_property, end))
        return res

    def read_property(self, indent=""):
        log(f"{indent}read_property")
        log(f"{indent}  read_string..", end="")
        self._read_next()
        if not isinstance(self.current, lexer.Value.STRING):
            log("not found")
            self.fail()
        log("found")
        key = Value.STRING(self.current.value)

        log(f"{indent}  read_colon..", end="")
        self._read_next()
        if not isinstance(self.current, lexer.Value.COLON):
            log("not found")
            self.fail()
        log("found")
        value = self.read_value(indent + "  ")

        if not value:
            self.fail()
        return Value.PROPERTY(key, value)

    def read_array(self, indent=""):
        log(f"{indent}read_array")
        res = Value.ARRAY()
        end = lexer.Value.BRACKET_RIGHT
        res.values = list(self._read_until(self.read_value, end))
        return res

    def read_litteral(self, indent=""):
        self._read_next()
        log(f"{indent}read_litteral")
        if isinstance(self.current, lexer.Value.STRING):
            return Value.STRING(self.current.value)
        if isinstance(self.current, lexer.Value.BOOLEAN):
            return Value.BOOLEAN(self.current.value)
        if isinstance(self.current, lexer.Value.NUMBER):
            return Value.NUMBER(self.current.value)
        if isinstance(self.current, lexer.Value.NULL):
            return Value.NULL()
        self.fail()

    def fail(self):
        raise ParserError(f"unexpected token: {self.current}")

    def unmarshal(self, ast=None, indent=""):
        if not ast:
            ast = self.ast

        if isinstance(ast, Value.OBJECT):
            log(f"{indent}object")
            unmarshal = lambda x: self.unmarshal(ast=x, indent=indent + "  ")
            return {k: v for k, v in map(unmarshal, ast.properties)}

        if isinstance(ast, Value.ARRAY):
            log(f"{indent}array")
            unmarshal = lambda x: self.unmarshal(ast=x, indent=indent + "  ")
            return list(map(unmarshal, ast.values))

        if isinstance(ast, Value.PROPERTY):
            log(f"{indent}property")
            key = self.unmarshal(ast=ast.key, indent=indent + "  ")
            value = self.unmarshal(ast=ast.value, indent=indent + "  ")
            return key, value

        if isinstance(ast, Value.NULL):
            log(f"{indent}null")
            return None

        if isinstance(ast, Value.STRING):
            log(f"{indent}string")
            return str(ast.value)

        if isinstance(ast, Value.NUMBER):
            log(f"{indent}number")
            return float(ast.value)

        if isinstance(ast, Value.BOOLEAN):
            log(f"{indent}boolean")
            return bool(ast.value)

        raise ParserError(f"unexpected ast: {ast}")
