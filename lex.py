import enum
import sys

class Lexer:
    def __init__(self, source):
        self.source = source + '\n' # Source code to lex as a string. Append a newline to simplify lexing/parsing the last token/statement.
        self.curChar = ''   # Current character in the string.
        self.curPos = -1   # Current position in the string.
        self.nextChar()

    # Invlaid token found, print error message and exit
    def abort(self, message):
        sys.exit("Lexing error. " + message)

    # Process the next character
    def nextChar(self):
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = '\0' #EOF
        else:
            self.curChar = self.source[self.curPos]

    # Return the lookahead character
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos + 1]
    
    # Skip whitespace except newlines, which we will use to indicate the end of a statement
    def skipWhitespace(self):
        while self.curChar == ' ' or \
        self.curChar == '\t' or \
        self.curChar == '\r':
            self.nextChar()

    
    # Skip comments in the code
    def skipComment(self):
        if self.curChar == '#':
            while self.curChar != '\n':
                self.nextChar()
    
    # Detect keywords
    @staticmethod
    def checkIfKeyword(tokenText):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None


    # Return the next token
    def getToken(self):
        self.skipWhitespace()
        self.skipComment()
        token = None

        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest.
        if self.curChar == '+':
            token = Token(self.curChar, TokenType.PLUS) 

        elif self.curChar == '-':
            token = Token(self.curChar, TokenType.MINUS)

        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ASTERISK) 

        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.SLASH) 

        elif self.curChar == '=':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEQ)
            else:
                token = Token(self.curChar ,TokenType.EQ)

        elif self.curChar == '>':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar, TokenType.GTEQ)
            else:
                token = Token(self.curChar, TokenType.GT)

        elif self.curChar == '<':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar, TokenType.LTEQ)
            else:
                token = Token(self.curChar, TokenType.LT)

        elif self.curChar == '!':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())

        elif self.curChar == '\"':
            # Get characters between quotations
            self.nextChar()
            startPos = self.curPos
            
            while self.curChar != '\"':
                # Don't allow special characters in the string.
                # No special characters, newlines, tab,s or %.
                # This is using printf from C.
                if self.curChar == '\r' or \
                   self.curChar == '\n' or \
                   self.curChar == '\t' or \
                   self.curChar == '\\' or \
                   self.curChar == '%':
                    self.abort("Illegal character in string. ")
                self.nextChar()
            tokText = self.source[startPos : self.curPos] # Get the substring.
            token = Token(tokText, TokenType.STRING)

        elif self.curChar.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.': # Decimal
                self.nextChar()
                if not self.peek().isdigit():
                    self.abort("Illegal character in number: " + self.peek())
                while self.peek().isdigit():
                    self.nextChar()
            tokText = self.source[startPos : self.curPos + 1] # Get the complete number
            token = Token(tokText, TokenType.NUMBER)
        
        elif self.curChar.isalpha():
            # Leading character is a letter, so this must be an identified or keyword.
            # Get all consecutive alphanumeric characters.
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()

            # Check if the resultant token is in the list of keywords.
            tokText = self.source[startPos : self.curPos + 1] # Get the substring.
            keyword = self.checkIfKeyword(tokText)
            if keyword: # Identifier
                token = Token(tokText, keyword)
            else:
                token = Token(tokText, TokenType.IDENT)

        elif self.curChar == '\n':
            token = Token(self.curChar, TokenType.NEWLINE)

        elif self.curChar == '\0':
            token = Token(self.curChar, TokenType.EOF) 

        else: 
            self.abort("Unknown token: " + self.curChar)

        self.nextChar()
        return token

class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText   # The token's actual text. Used for identifiers, strings, and numbers.
        self.kind = tokenKind   # The TokenType that this token is classfied as.

# TokenType is our enum for all the types of tokens.
class TokenType(enum.Enum):
	EOF = -1
	NEWLINE = 0
	NUMBER = 1
	IDENT = 2
	STRING = 3
	# Keywords.
	LABEL = 101
	GOTO = 102
	YAP = 103
	PREACH = 104
	NOCAP = 105
	IF = 106
	THEN = 107
	ENDIF = 108
	WHILE = 109
	RUNITBACK = 110
	ENDWHILE = 111
	# Operators.
	EQ = 201  
	PLUS = 202
	MINUS = 203
	ASTERISK = 204
	SLASH = 205
	EQEQ = 206
	NOTEQ = 207
	LT = 208
	LTEQ = 209
	GT = 210
	GTEQ = 211