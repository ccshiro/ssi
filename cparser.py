#NOTE: This code could definitely be made cleaner and easier to read!

class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Token:
    unrecognized = 0
    eof = 1
    identifier = 2
    integer = 3
    semicolon = 4
    comma = 5
    lbracer = 6
    rbracer = 7
    assign_op = 8
    enum_keyword = 9

    def get_str(t):
        if isinstance(t, tuple):
            t = t[0]
        if t == Token.unrecognized:
            return "unrecognized"
        elif t == Token.eof:
            return "eof"
        elif t == Token.identifier:
            return "identifier"
        elif t == Token.integer:
            return "integer"
        elif t == Token.semicolon:
            return "semicolon"
        elif t == Token.comma:
            return "comma"
        elif t == Token.lbracer:
            return "lbracer"
        elif t == Token.rbracer:
            return "rbracer"
        elif t == Token.assign_op:
            return "assign_op"
        elif t == Token.enum_keyword:
            return "enum_keyword"
        raise ParseError('Not a valid token id (' + str(t) + ')')

class Lexer:
    def __init__(self, filename, filestream):
        self.fs = filestream
        self.filename = filename
        self.enums = {}
        self.lineno = 1
        self.charno = 0
        self.peeked_token = None
        self.id = ''
        self.integer = 0

    def err(self, e):
        raise ParseError(self.filename + ':' + str(self.lineno) + ':' +
            str(self.charno) + ': ' + e)

    def getch(self):
        c = self.fs.read(1)
        if c == '\n':
            self.lineno += 1
            self.charno = 0
        else:
            self.charno += 1
        return c

    def peekch(self):
        pos = self.fs.tell()
        c = self.fs.read(1)
        self.fs.seek(pos)
        return c

    def peek_token(self):
        if self.peeked_token != None:
            self.err('Can only peek one token')
        self.peeked_token = self.get_token()
        return self.peeked_token

    def get_token(self):
        if self.peeked_token != None:
            t = self.peeked_token
            self.peeked_token = None
            return t
        while True:
            c = self.getch()
            if not c:
                return Token.eof
            # Whitepace
            if c == '\n' or (c == '\r' and self.peekch() == '\n'):
                if c == '\r':
                    self.getch() # eat \n
                continue
            if c.isspace():
                continue
            # Comments
            if c == '/':
                # C++ style
                if self.peekch() == '/':
                    self.getch()
                    # eat until newline
                    while True:
                        c = self.peekch()
                        if c == '\n':
                            break
                        else:
                            self.getch()
                    continue
                # C style
                elif self.peekch() == '*':
                    self.getch()
                    # eat until */
                    while True:
                        c = self.getch()
                        if c == '*' and self.peekch() == '/':
                            self.getch()
                            break
                    continue
            # Identifier
            if c.isalpha() or c == '_':
                id = c
                while True:
                    c = self.peekch()
                    if not c.isalnum() and c != '_':
                        # Keywords
                        keyword = self.as_keyword(id)
                        if keyword != Token.unrecognized:
                            return keyword
                        self.id = id
                        return Token.identifier
                    id += self.getch()
            # Integer
            if c.isdigit():
                intstr = c
                hexadecimal = False
                if self.peekch() == 'x':
                    hexadecimal = True
                    intstr += self.getch()
                while True:
                    c = self.peekch()
                    if (not c.isdigit() and
                        (not hexadecimal or not ('A' <= c.upper() <= 'F'))):
                        self.integer = int(intstr, base=10 if not hexadecimal
                            else 16)
                        return Token.integer
                    intstr += self.getch()
            # Semicolon, comma
            if c == ";":
                return Token.semicolon
            if c == ",":
                return Token.comma
            # Bracers
            if c == "{":
                return Token.lbracer
            if c == "}":
                return Token.rbracer
            # Some Operators
            if c == "=":
                # NOTE: This one is not necessarily an assing operator, other ops
                #       not implemented though!
                return Token.assign_op
            # Unrecognized token (most likely not yet implemented)
            return Token.unrecognized

    def as_keyword(self, id):
        if id == "enum":
            return Token.enum_keyword
        return Token.unrecognized

class Parser:
    def __init__(self, filename, filestream):
        self.filename = filename
        self.lexer = Lexer(filename, filestream)
        self.enums = {}

    def expected(self, tokenlist, token):
        strlist = '['
        for i, t in enumerate(tokenlist):
            strlist += Token.get_str(t)
            if i != len(tokenlist) - 1:
                strlist += ', '
        strlist += ']'
        self.lexer.err("expected one of tokens: '" + strlist +
            "', but instead got '" + Token.get_str(token) + "'")

    def parse(self):
        while True:
            t = self.lexer.get_token()
            if t == Token.eof:
                return
            elif t == Token.enum_keyword:
                self.parse_enum()

    def ignore_until(self, one_of):
        ignored = 0
        while True:
            t = self.lexer.peek_token()
            if t in one_of:
                return ignored
            ignored += 1
            t = self.lexer.get_token()

    def parse_enum(self):
        # enum <identifier>
        t = self.lexer.get_token()
        if t != Token.identifier:
            self.expected([Token.identifier], t)
        enum_id = self.lexer.id
        self.enums[enum_id] = {}

        # { or ;
        t = self.lexer.get_token()
        if t == Token.semicolon:
            return
        if t != Token.lbracer:
            self.expected([Token.lbracer], t)

        # Read enum values
        next_implicit_val = 0
        while True:
            t = self.lexer.get_token()

            # Identifier
            if t != Token.identifier:
                self.expected([Token.identifier], t)
            id = self.lexer.id
            if id in self.enums[enum_id].values():
                self.lexer.err("enum identifier '" + id + "' already used")
            t = self.lexer.get_token()

            # Comma or } => implicit value
            if t == Token.rbracer or t == Token.comma:
                self.enums[enum_id][next_implicit_val] = id
                next_implicit_val += 1
            # Assign op (specified value)
            else:
                # Assign op
                if t != Token.assign_op:
                    self.expected([Token.assign_op, Token.comma, Token.rbracer],
                        t)
                # TODO: Expression not handled, we only handle integer literals
                #       (and not even that fully!)
                # NOTE: If we encounter expression with comma, our parsing dies
                # Get numeric value if exists
                t = self.lexer.get_token()
                num = self.lexer.integer
                # Ignore anything else
                ignored = self.ignore_until([Token.comma, Token.rbracer])
                # If nothing ignored and we got numeric value, use it
                if t == Token.integer and ignored == 0:
                    if self.lexer.integer not in self.enums[enum_id]:
                        self.enums[enum_id][id] = self.lexer.integer
                t = self.lexer.get_token()

            # Tokens that might appear after a declared enum value:
            # } == end of enum
            if t == Token.rbracer:
                break
            # ,
            if t == Token.comma:
                # Comma can be followed by } == end of enum
                if self.lexer.peek_token() == Token.rbracer:
                    t = self.lexer.get_token()
                    break

        # Enum should end with };
        if t != Token.rbracer:
            self.expected([Token.rbracer], t)
        t = self.lexer.get_token()
        if t != Token.semicolon:
            self.expected([Token.semicolon], t)

    def get_enums(self):
        """Returns dictionary of enums, of format:
            {enum_id: {'integer0': 'identifier',
                      {'integer1': 'identifier'},
            {enum_id: ...}"""
        return self.enums
