#!/usr/bin/env python3

import argparse
import sys

class TokenType:
	#Fixed punctuation
	LEFT_PAREN = 1,
	RIGHT_PAREN = 2,
	LEFT_BRACE = 3,
	RIGHT_BRACE = 4,
	CARET = 5,
	AMPERSAND = 6,
	ATSIGN = 7,
	NOT = 8,
	DOT = 9,
	COLON = 10,
	COMMA = 11,
	UNDERSCORE = 12,
	EQUALS = 13,
	LEFT_BRACKET = 14,
	RIGHT_BRACKET = 15,
	#Keywords
	THIS = 16,
	IF = 17,
	ELSE = 18
	IFONLY = 19,
	WHILE = 20,
	RETURN = 21,
	PRINT = 22,
	EOF = 23,
	WITH = 24,
	FIELDS = 25,
	METHOD = 26,
	LOCALS = 27,
	CLASS = 28,
	#Tokens with data
	OPERATOR = 29,
	NUMBER = 30,
	IDENTIFIER = 31

TOKEN_TYPE_TO_STDOUT = {
	1: "(", 2: ")", 3: "{", 4: "}", 5: "^", 6: "&", 7: "@", 8: "!",
	9: ".", 10: ":", 11: ",", 12: "_", 13: "=", 14: "[", 15: "]", 16: "this", 
 	17: "if", 18: "else", 19: "ifonly", 20: "while", 21: "return", 22: "print", 
	23: "EOF", 24: "with", 25: "fields", 26: "method", 27: "locals", 28: "class",
 	29: "Operator", 30: "Number", 31: "Identifier"
}

class Operator:
    def __init__(self, op: str):
        self._op = op
    
    def __str__(self) -> str:
        return f"Operator: op={self._op}"
    
class Number:
	def __init__(self, num: int):
		self._num = num
  
	def value(self) -> int:
		return self._num

	def __str__(self) -> str:
		return f"Number: value={self._num}"
  
class Identifier:
	def __init__(self, item: str):
		self._item = item

	def name(self):
		return self._item

	def __str__(self):
		return f"Identifier: name={self._item}"
  
class Tokenizer:
	SPECIAL_MAP = {'(': TokenType.LEFT_PAREN,
					')': TokenType.RIGHT_PAREN,
					'{': TokenType.LEFT_BRACE,
					'}': TokenType.RIGHT_BRACE,
					':': TokenType.COLON,
					'!': TokenType.NOT,
					'@': TokenType.ATSIGN,
					'^': TokenType.CARET,
					'&': TokenType.AMPERSAND,
					'.': TokenType.DOT,
					',': TokenType.COMMA,
					'_': TokenType.UNDERSCORE,
     				'=': TokenType.EQUALS}
 
	KEYWORD_MAP = {'if': TokenType.IF,
					'else': TokenType.ELSE,
                	'ifonly': TokenType.IFONLY,
                 	'while': TokenType.WHILE,
                  	'return': TokenType.RETURN,
                   	'print': TokenType.PRINT,
                    'this': TokenType.THIS}
 
	OP_LIST = ['+', '-', '*', '/']

	def __init__(self, text: str):
		self._text = text
		self._current = 0
		self._cached = None
  
	def peek(self):
		if(self._cached is None):
			self._cached = self.advanceCurrent()
		return self._cached

	def next(self):
		if(self._cached is None):
			return self.advanceCurrent()
		else:
			tmp = self._cached
			self._cached = None
			return tmp

	def advanceCurrent(self):
		while(self._current < len(self._text) and self._text[self._current].isspace()):
			self._current += 1
   
		if(self._current >= len(self._text)):
			return TokenType.EOF

		tmp = Tokenizer.SPECIAL_MAP.get(self._text[self._current], None)
		if(tmp):
			self._current += 1
			return tmp

		if(self._text[self._current] in Tokenizer.OP_LIST):
			self._current += 1
			return Operator(self._text[self._current])

		if(self._text[self._current].isdigit()):
			#Number
			start = self._current
			self._current += 1 #Might be useless
			while(self._current < len(self._text) and self._text[self._current].isdigit()):
				self._current += 1
    
			return Number(int(self._text[start:self._current]))
		elif self._text[self._current].isalpha():
			start = self._current
			self._current += 1 #Might be useless
			while(self._current < len(self._text) and self._text[self._current].isalpha()):
				self._current += 1
    
			fragment = self._text[start: self._current]
			tmp = Tokenizer.KEYWORD_MAP.get(fragment, None)
			if(tmp):
				return tmp
			return Identifier(fragment)

		else:
			raise Exception(f"Unsupported character: {self._text[self._current]}")

class Expression:
    def __init__(self):
        pass
    
class Statement:
    def __init__(self):
        pass
    
class Constant(Expression):
    def __init__(self, value: int):
        super().__init__()
        self._value = value

class Variable(Expression):
	def __init__(self, name: str):
		super().__init__()
		self._name = name

	def __str__(self) -> str:
		super().__init__()
		return f"Variable: name={self._name}"

class BinaryOp(Expression):
    def __init__(self, lhs, op, rhs):
        super().__init__()
        self._lhs = lhs
        self._op = op
        self._rhs = rhs

class FieldName:
    def __init__(self, base, field_name):
        super().__init__()
        self._base = base
        self._field_name = field_name

class MethodCall(Expression):
    def __init__(self, base, methodname, args):
        super().__init__()
        self._base = base
        self._methodname = methodname
        self._args = args

class ClassRef(Expression):
	def __init__(self, name):
		super().__init__()
		self._name = name
  
	def __str__(self) -> str:
		return f"Class Reference: name={self._name}"

class ThisExpr:
    def __init__(self):
        pass
    
    def __str__(self) -> str:
        return "this"

class Assignment(Statement):
    def __init__(self, variable: Variable, expression: Expression):
        super().__init__()
        self._variable = variable
        self._expression = expression
        
    def __str__(self) -> str:
        return f"Assign {self._variable} = {self._expression}"

class FieldUpdate(Statement):
    def __init__(self, field_read: FieldName, expression: Expression):
        super().__init__()
        self._field_read = field_read
        self._expression = expression
        
    def __str__(self) -> str:
        return f"Field Assignment: {self._field_read} = {self._expression}"

class IfStatement(Statement):
	def __init__(self, condition: Expression, true_statements: list[Statement], else_statements: list[Statement]):
		super().__init__()
		self._condition = condition
		self._true_statements = true_statements
		self._else_statements = else_statements
	
	def __str__(self) -> str:
		return f"If statement: Condition = {self._condition}, \
      	if_block: {"\n".join(self._true_statements)}, \
           else_block: {"\n".join(self._else_statements)}"

class IfOnlyStatement(Statement):
    def __init__(self, condition: Expression, statements: list[Statement]):
        super().__init__()
        self._condition = condition
        self._statements = statements
        
    def __str__(self) -> str:
        return f"IfOnly Statement: Condition = {self._condition}, \
            statements: {"\n".join(self._statements)}"

class WhileStatement(Statement):
    def __init__(self, condition: Expression, statements: list[Statement]):
        super().__init__()
        self._condition = condition
        self._statements = statements
        
    def __str__(self) -> str:
        return f"While statement: Condition = {self._condition}, Statements: {"\n".join(self._statements)}"

class ReturnStatement(Statement):
    def __init__(self, exp: Expression):
        super().__init__()
        self._exp = exp
        
    def __str__(self) -> str:
        return f"Return statement: returns {self._exp}"

class PrintStatement(Statement):
    def __init__(self, exp):
        super().__init__()
        self._exp = exp
        
    def __str__(self) -> str:
        return f"Print statement: prints {self._exp}"

class Argument:
    def __init__(self, name: str):
        self._name = name
        
    def __str__(self) -> str:
        return f"Argument: name={self._name}"
    
class MethodDefinintion:
	def __init__(self, args: list[Argument], locals: list[Variable], statements: list[Statement]):
		self._args = args
		self._locals = locals
		self._statements = statements
        
	def __str__(self) -> str:
		return f"Arguments: {"\n".join(self._args)} \
      Local Variables: {"\n".join(self._locals)} \
      Statements: {"\n".join(self._statements)}"

class ClassDefinition:
	def __init__(self, fields: list[Variable], methods: list[MethodDefinintion]):
		self._fields = fields
		self._methods = methods
    
	def __str__(self) -> str:
		return f"Fields: {", ".join(self._fields)}, Methods:, {"\n".join(self._methods)}"
    
class Parser:
	def __init__(self, tokenizer: Tokenizer):
		self._tokenizer = tokenizer
	
	def parseExpr(self) -> Expression:
		tok = self._tokenizer.next()
		if tok == TokenType.EOF:
			raise Exception("No expression to parse: EOF")
		elif type(tok) == Number:
			return Constant(tok.value())
		elif type(tok) == Identifier:
			return Variable(tok.name())
		elif tok == TokenType.LEFT_PAREN:
			lhs = self.parseExpr()
			optok = self._tokenizer.next()
			if type(optok) != Operator:
				raise Exception("Expected operator token but found", optok)

			rhs = self.parseExpr()
			closetok = self._tokenizer.next() 
			if closetok != TokenType.RIGHT_PAREN:
				raise Exception("Expected ')' but got", closetok)
			return BinaryOp(lhs, optok, rhs)
		elif tok == TokenType.AMPERSAND:
			base = self.parseExpr()
			dot = self._tokenizer.next()
			if dot != TokenType.DOT:
				raise Exception("Expected '.' but found", dot)
			fname = self._tokenizer.next()
			if type(fname) != Identifier:
				raise Exception("Expected valid field name but found", fname)
			return FieldName(base, fname)
		elif tok == TokenType.CARET:
			mbase = self.parseExpr()
			mdot = self._tokenizer.next()
			if mdot != TokenType.DOT:
				raise Exception("Expected dot but found", mdot)
			mname = self._tokenizer.next()
			if type(mname) != Identifier:
				raise Exception("Expected valid method name but found", mname)
			open = self._tokenizer.next()
			if type(open) != TokenType.LEFT_PAREN:
				raise Exception("Expected '(' but found", open)
			args = []
			while(self._tokenizer.peek() != TokenType.RIGHT_PAREN):
				e = self.parseExpr()
				args.append(e)
				punc = self._tokenizer.peek()
				if(punc == TokenType.COMMA):
					self._tokenizer.next()
			return MethodCall(mbase, mname, args)
		elif tok == TokenType.ATSIGN:
			cname = self._tokenizer.next()
			if type(cname) != Identifier:
				raise Exception("Expected identifier, got", cname)
			return ClassRef(cname.name())
		elif tok == TokenType.THIS:
			return ThisExpr()
		else:
			raise Exception(f"Token {tok} is not a valid start to an expression")

	def parseStatement(self) -> Statement:
		tok = self._tokenizer.next()
		if tok == TokenType.EOF:
			raise Exception("Unexpected EOF")
		elif type(tok) == Identifier:
			var_name = Variable(tok.name())
			eq = self._tokenizer.next()
			if eq != TokenType.EQUALS:
				raise Exception("Expected '=' but got:", eq)

			exp = self.parseExpr()
			return Assignment(var_name, exp)
		elif tok == TokenType.UNDERSCORE:
			eq = self._tokenizer.next()
			if eq != TokenType.EQUALS:
				raise Exception("Expected '=' but got:", eq)
			return self.parseExpr()
		elif tok == TokenType.NOT:
			field_name = self.parseExpr()
			if type(field_name) != FieldName:
				raise Exception("Expected field read, got:", field_name)
			eq = self._tokenizer.next()
			if eq != TokenType.EQUALS:
				raise Exception("Expected '=' but got:", eq)
			exp = self.parseExpr()
			return FieldUpdate(field_name, exp)
		elif tok == TokenType.IF:
			exp = self.parseExpr()
			colon = self._tokenizer.next()
			if(colon != TokenType.COLON):
				raise Exception("Expected ':' but got:", colon)

			left_brace = self._tokenizer.next()
			if(left_brace != TokenType.LEFT_BRACE):
				raise Exception("Expected '{' but got:", left_brace)

			if_statements = []
			while(self._tokenizer.peek() != TokenType.RIGHT_BRACE):
				if_statements.append(self.parseStatement)

			_ = self._tokenizer.next() #Move past right brace
			else_tok = self._tokenizer.next()
			if(else_tok != TokenType.ELSE):
				raise Exception("Expected else, but got:", else_tok)

			left_brace = self._tokenizer.next()
			if(left_brace != TokenType.LEFT_BRACE):
				raise Exception("Expected '{' but got:", left_brace)

			else_statements = []
			while(self._tokenizer.peek() != TokenType.RIGHT_BRACE):
				else_statements.append(self.parseStatement())
			
			_ = self._tokenizer.next()
			return IfStatement(exp, if_statements, else_statements)
			
		elif tok == TokenType.IFONLY:
			exp = self.parseExpr()
			colon = self._tokenizer.next()
			if(colon != TokenType.COLON):
				raise Exception("Expected ':' but got:", colon)

			left_brace = self._tokenizer.next()
			if(left_brace != TokenType.LEFT_BRACE):
				raise Exception("Expected '{' but got:", left_brace)

			if_statements = []
			while(self._tokenizer.peek() != TokenType.RIGHT_BRACE):
				if_statements.append(self.parseStatement())

			_ = self._tokenizer.next() #Advance past } char
			return IfOnlyStatement(exp, if_statements)
			
		elif tok == TokenType.WHILE:
			exp = self.parseExpr()
			colon = self._tokenizer.next()
			if colon != TokenType.COLON:
				raise Exception("Expected ':', but got:", colon)

			left_brace = self._tokenizer.next()
			if left_brace != TokenType.LEFT_BRACE:
				raise Exception("Expected '{', but got:", left_brace)

			while_statements = []
			while(self._tokenizer.peek() != TokenType.RIGHT_BRACE):
				while_statements.append(self.parseStatement())

			_ = self._tokenizer.next()
			return WhileStatement(exp, while_statements)

		elif tok == TokenType.RETURN:
			exp = self.parseExpr()
			return ReturnStatement(exp)

		elif tok == TokenType.PRINT:
			left_paren = self._tokenizer.next()
			if left_paren != TokenType.LEFT_PAREN:
				raise Exception("Expected '(' but got:", left_paren)

			exp = self.parseExpr()
			right_paren = self._tokenizer.next()
			if right_paren != TokenType.RIGHT_PAREN:
				raise Exception("Expected ')' but got:", right_paren)

			return PrintStatement(exp)

		else:
			raise Exception("Unexpected token for start of statement:", tok)
    
	def parseClass(self):
		tok = self._tokenizer.next()
		if tok != TokenType.CLASS:
			raise Exception("Expected class definition, got:", tok) # Should not trigger

		left_bracket = self._tokenizer.next()
		if left_bracket != TokenType.LEFT_BRACKET:
			raise Exception("Expected '[' but got:", left_bracket)

		fields = []
		methods = []
		tok = self._tokenizer.next()
		if type(tok) != TokenType.FIELDS or type(tok) != TokenType.METHOD:
			raise Exception("Unknown Identifier", tok)

		if tok == TokenType.FIELDS:
			field_token = self._tokenizer.next()
			if field_token != Identifier:
				raise Exception("Expected identifier, got:", field_token)

			fields.append(Variable(field_token.name()))
			while(self._tokenizer.peek() == TokenType.COMMA):
				_ = self._tokenizer.next() #Advance past comma
				field_token = self._tokenizer.next()
				if field_token != Identifier:
					raise Exception("Expected identifier, got:", field_token)

				fields.append(Variable(field_token.name()))
			tok = self._tokenizer.next()
	
		while tok == TokenType.METHOD:
			mname = self._tokenizer.next()
			if type(mname) != Identifier:
				raise Exception("Expected identifier, got:", mname)

			left_paren = self._tokenizer.next()
			if left_paren != TokenType.LEFT_PAREN:
				raise Exception("Expected '(' got:", left_paren)

			margs = []
			mlocals = []
			statements = []
			arg_tok = self._tokenizer.next()
			if type(arg_tok) != Identifier:
				raise Exception("Expected identifier, got:", arg_tok)
    
			margs.append(arg_tok)
			while(self._tokenizer.peek() == TokenType.COMMA):
				_ = self._tokenizer.next()
				arg_tok = self._tokenizer.next()
				if type(arg_tok) != Identifier:
					raise Exception("Expected identifier, got:", arg_tok)
				margs.append(Argument(arg_tok.name()))

			if len(margs) > 6:
				raise Exception("Maximum 6 arguments for a method")
    
			
			if self._tokenizer.peek() == TokenType.WITH:
				_ = self._tokenizer.next()
				tok = self._tokenizer.next()
				if tok != TokenType.LOCALS:
					raise Exception("Expected locals, got:", tok)

				local_tok = self._tokenizer.next()
				if type(local_tok) != Identifier:
					raise Exception("Expected identifier, got:", local_tok)
				mlocals.append(Variable(local_tok.name()))
    
				while(self._tokenizer.peek() == TokenType.COMMA):
					_ = self._tokenizer.next()
					local_tok = self._tokenizer.next()
					if type(local_tok) != Identifier:
						raise Exception("Expected identifier, got:", local_tok)
					mlocals.append(Variable(local_tok.name()))

			colon = self._tokenizer.next()
			if colon != TokenType.COLON:
				raise Exception("Expected colon, got:", colon)

			while self._tokenizer.peek() != TokenType.METHOD or self._tokenizer.peek() != TokenType.RIGHT_BRACKET:
				statements.append(self.parseStatement())
    
			if not statements:
				raise Exception("Expected method body")

			methods.append(MethodDefinintion(margs, mlocals, statements))
			tok = self._tokenizer.next()
   
		if tok != TokenType.RIGHT_BRACKET:
			raise Exception("Expected ']', but got:", tok)

		return ClassDefinition(fields, methods)			
			
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: comp {tokenize|parseExpr} [args...]")
		sys.exit(1)
  
	str_text = " ".join(sys.argv[2:])
	print(str_text)
	if sys.argv[1] == "tokenize":
		tokenizer = Tokenizer(str_text)
		token = None
		while(tokenizer.peek() != TokenType.EOF):
			token = tokenizer.next()
			if(type(token) == Operator or type(token) == Number or type(token) == Identifier):
				print(token)
			else:
				print("Token is:", TOKEN_TYPE_TO_STDOUT[token[0]])
    
	elif sys.argv[1] == "parseExpr":
		parser = Parser(Tokenizer(str_text))
		print(parser.parseExpr())
	else:
		raise Exception("Invalid usage")
  
