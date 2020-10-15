import re
import string
from jason.lib import log


class LexerError(Exception):
    pass


class Value:
    class NULL:  # null
        pass

    class BRACE_LEFT:  # {
        pass

    class BRACE_RIGHT:  # }
        pass

    class BRACKET_LEFT:  # [
        pass

    class BRACKET_RIGHT:  # ]
        pass

    class COLON:  # :
        pass

    class COMMA:  # ,
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


def is_lexer(obj, indent=""):
    log(f"{indent}is_lexer")

    # [Value.NULL, Value.BRACE_LEFT, ...]
    types = list(filter(lambda x: not "__" in x, dir(Value)))
    types = list(map(lambda x: Value.__getattribute__(Value, x), types))

    is_valid = lambda o: any(map(lambda x: isinstance(o, x), types))

    # empty list or all in `types`
    return isinstance(obj, list) and (
        len(obj) == 0 or all(map(lambda x: is_valid(x), obj))
    )


class Lexer:
    def __init__(self, json):
        self.json = json
        self.position = 0
        self.current = ""
        self.line, self.col = 1, 0

    def _read_next(self):
        if self.position >= len(self.json):
            self.current = "EOF"
            return
        self.current = self.json[self.position]
        self.position += 1

    def _unread(self):
        if self.position <= 0:
            raise LexerError("cannot unread, already at start")
        self.position -= 1
        self.current = self.json[self.position]

    def __iter__(self):
        self.position = 0
        try:
            self.current = self.json[self.position]
        except KeyError:
            raise StopIteration
        return self

    def __next__(self, indent=""):
        log(f"{indent}next")
        self._read_next()

        if self.current == "\n":
            log(f"{indent}  next: new line")
            self.col = 0
            self.line += 1
        else:
            self.col += 1

        if self.current in " \t\r\n":
            log(f"{indent}  next: blank")
            return next(self)
        if self.current == "{":
            log(f"{indent}  next: brace_left")
            return Value.BRACE_LEFT()
        if self.current == "}":
            log(f"{indent}  next: brace_right")
            return Value.BRACE_RIGHT()
        if self.current == "[":
            log(f"{indent}  next: bracket_left")
            return Value.BRACKET_LEFT()
        if self.current == "]":
            log(f"{indent}  next: bracket_right")
            return Value.BRACKET_RIGHT()
        if self.current == ":":
            log(f"{indent}  next: colon")
            return Value.COLON()
        if self.current == ",":
            log(f"{indent}  next: comma")
            return Value.COMMA()

        if self.current == '"':
            log(f"{indent}  next: quote")
            return self.read_string(indent=indent + "  ")
        if self.current in [*string.digits, "-"]:
            log(f"{indent}  next: number")
            return self.read_number(indent=indent + "  ")
        if self.current in "tf":
            log(f"{indent}  next: boolean")
            return self.read_boolean(indent=indent + "  ")
        if self.current in "n":
            log(f"{indent}  next: null")
            return self.read_null(indent=indent + "  ")

        if self.current == "EOF":
            log(f"{indent}  next: EOF")
            raise StopIteration

        log(f"{indent}  next: fail")
        self.fail()

    def read_string(self, indent=""):
        res = ""
        log(f"{indent}  read_string")
        self._read_next()

        while self.current != '"':
            if self.current == "EOF":
                log(f"{indent}  read_string: EOF")
                self.fail()
            res += self.current
            self._read_next()

        if not re.fullmatch(r'([^"\\]|(\"|\\|\/|\b|\f|\n|\r|\t|\\u[0-9]{4}))*', res):
            raise LexerError(f"this is not a valid string: {res}")
        return Value.STRING(res)

    def read_number(self, indent=""):
        log(f"{indent}read_number")
        res = ""
        while self.current in [*string.digits, ".", "e", "-"]:
            if self.current == "EOF":
                self.fail()
            res += self.current
            self._read_next()
        log(f"{indent}  read_number: valid digits")
        if not re.fullmatch(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?((e|E)(\+|-)?[0-9]+)?", res):
            raise LexerError(f"this is not a valid number: {res}")
        self._unread()
        log(f"{indent}  read_number: valid regex")
        return Value.NUMBER(res)

    def read_boolean(self, indent=""):
        log(f"{indent}read_boolean")
        if self.current == "t":
            log(f"{indent}  read_boolean: guessed true")
            word = "true"
        elif self.current == "f":
            log(f"{indent}  read_boolean: guessed false")
            word = "false"
        else:
            self.fail()

        for i in word:
            if self.current != i:
                log(f"{indent}  read_boolean: wrong guessed")
                self.fail()
            self._read_next()
        log(f"{indent}  read_boolean: well guessed")
        self._unread()
        return Value.BOOLEAN(word)

    def read_null(self, indent=""):
        log(f"{indent}read_null")
        for i in "null":
            if i != self.current:
                log(f"{indent}  read_null: fail")
                self.fail()
            self._read_next()
        self._unread()
        return Value.NULL()

    def fail(self):
        raise LexerError(
            f"unexpected character at {self.line}:{self.col}: {self.current}"
        )
