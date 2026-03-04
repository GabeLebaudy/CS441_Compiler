from ast_components import *

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
	MAIN = 29,
	INT = 30,
	NULL = 31,
	RETURNING = 32,
	#Tokens with data
	OPERATOR = 33,
	NUMBER = 34,
	IDENTIFIER = 35

TOKEN_TYPE_TO_STDOUT = {
	1: "(", 2: ")", 3: "{", 4: "}", 5: "^", 6: "&", 7: "@", 8: "!",
	9: ".", 10: ":", 11: ",", 12: "_", 13: "=", 14: "[", 15: "]", 16: "this", 
 	17: "if", 18: "else", 19: "ifonly", 20: "while", 21: "return", 22: "print", 
	23: "EOF", 24: "with", 25: "fields", 26: "method", 27: "locals", 28: "class",
 	29: "main", 30: "int", 31: "null", 32: "returning", 33: "Operator", 34: "Number", 35: "Identifier"
}

def printToken(token):
	if type(token) == tuple:
		return f"Token: {TOKEN_TYPE_TO_STDOUT[token[0]]}"
	else:
		return str(token)

class Operator:
	def __init__(self, op: str):
		self._op = op
    
	def op(self) -> str:
		return self._op

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
     				'=': TokenType.EQUALS,
					'[': TokenType.LEFT_BRACKET,
					']': TokenType.RIGHT_BRACKET}
 
	KEYWORD_MAP = {'if': TokenType.IF,
					'else': TokenType.ELSE,
                	'ifonly': TokenType.IFONLY,
                 	'while': TokenType.WHILE,
                  	'return': TokenType.RETURN,
                   	'print': TokenType.PRINT,
                    'this': TokenType.THIS,
					'with': TokenType.WITH,
					'fields': TokenType.FIELDS,
					'method': TokenType.METHOD,
					'locals': TokenType.LOCALS,
					'class': TokenType.CLASS,
					'main': TokenType.MAIN,
     				'int': TokenType.INT,
         			'null': TokenType.NULL,
            		'returning': TokenType.RETURNING}
 
	OP_LIST = ['+', '-', '*', '/', '<', '>']

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
			new_op = Operator(self._text[self._current])
			self._current += 1
			return new_op

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
			while(self._current < len(self._text) and (self._text[self._current].isalpha() or self._text[self._current].isdigit())):
				self._current += 1
    
			fragment = self._text[start: self._current]
			tmp = Tokenizer.KEYWORD_MAP.get(fragment, None)
			if(tmp):
				return tmp
			return Identifier(fragment)

		else:
			raise Exception(f"Unsupported character: {self._text[self._current]}")

class Parser:
	def __init__(self, tokenizer: Tokenizer):
		self._tokenizer = tokenizer
	
	def getCommaSepVariables(self) -> list[Variable]:
		variables = []
		while (type(self._tokenizer.peek()) == Identifier):
			var_name = self._tokenizer.next()
			colon = self._tokenizer.next()
			if colon != TokenType.COLON:
				raise Exception("Expected ':', but got:", printToken(colon))

			var_type = self._tokenizer.next()
			cur_variable = Variable(var_name.name())
			if type(var_type) == Identifier:
				cur_variable.setType(var_type.name())
			elif var_type == TokenType.INT:
				cur_variable.setType('int')
			else:
				raise Exception("Invalid variable type:", printToken(var_type))

			variables.append(cur_variable)
			if self._tokenizer.peek() == TokenType.COMMA:
				self._tokenizer.next()
    
		return variables

	def parseExpr(self) -> Expression:
		tok = self._tokenizer.next()
		if tok == TokenType.EOF:
			raise Exception("No expression to parse: EOF")
		elif type(tok) == Number:
			return Constant(tok.value())
		elif type(tok) == Identifier:
			return Variable(tok.name())
		elif tok == TokenType.LEFT_PAREN: #Arithmetic operation
			lhs = self.parseExpr()
			optok = self._tokenizer.next()
			if optok == TokenType.EQUALS:
				nxt = self._tokenizer.next()
				if nxt != TokenType.EQUALS:
					raise Exception("Expected '=' but got:", printToken(nxt))
				else:
					optok = Operator("==")
     
			elif type(optok) != Operator:
				raise Exception("Expected operator token but found", printToken(optok))
			
			rhs = self.parseExpr()
			closetok = self._tokenizer.next() 
			if closetok != TokenType.RIGHT_PAREN:
				raise Exception("Expected ')' but got", printToken(closetok))
			return BinaryOp(lhs, optok, rhs)
		elif tok == TokenType.AMPERSAND: #Field Read
			base = self.parseExpr()
			dot = self._tokenizer.next()
			if dot != TokenType.DOT:
				raise Exception("Expected '.' but found", printToken(dot))
			fname = self._tokenizer.next()
			if type(fname) != Identifier:
				raise Exception("Expected valid field name but found", printToken(fname))
			return FieldRead(base, fname.name())
		elif tok == TokenType.CARET: #Method invocation
			mbase = self.parseExpr()
			mdot = self._tokenizer.next()
			if mdot != TokenType.DOT:
				raise Exception("Expected dot but found", printToken(mdot))
			mname = self._tokenizer.next()
			if type(mname) != Identifier:
				raise Exception("Expected valid method name but found", printToken(mname))
			open = self._tokenizer.next()
			if open != TokenType.LEFT_PAREN:
				raise Exception("Expected '(' but found", printToken(open))
			args = []
			while(self._tokenizer.peek() != TokenType.RIGHT_PAREN):
				e = self.parseExpr()
				args.append(e)
				punc = self._tokenizer.peek()
				if(punc == TokenType.COMMA):
					self._tokenizer.next()
			
			self._tokenizer.next() #Eat right paren
			return MethodCall(mbase, mname.name(), args)
		elif tok == TokenType.ATSIGN: #Class reference
			cname = self._tokenizer.next()
			if type(cname) != Identifier:
				raise Exception("Expected identifier, got", printToken(cname))
			return ClassRef(cname.name())
		elif tok == TokenType.THIS:
			return ThisExpr()
		elif tok == TokenType.NULL:
			colon = self._tokenizer.next()
			if colon != TokenType.COLON:
				raise Exception("Expected ':', but got:", printToken(colon))
			null_type = self._tokenizer.next()
			if type(null_type) != Identifier:
				raise Exception("Expected class type, got:", printToken(null_type))
			return NullExpr(null_type.name())
		else:
			raise Exception("Token", printToken(tok), "is not a valid start to an expression")

	def parseStatement(self) -> Statement:
		tok = self._tokenizer.next()
		if tok == TokenType.EOF:
			raise Exception("Unexpected EOF")
		elif type(tok) == Identifier:
			var_name = Variable(tok.name())
			eq = self._tokenizer.next()
			if eq != TokenType.EQUALS:
				raise Exception("Expected '=' but got:", printToken(eq))

			exp = self.parseExpr()
			return Assignment(var_name, exp)
		elif tok == TokenType.UNDERSCORE: # Statement to run for side effects
			eq = self._tokenizer.next()
			if eq != TokenType.EQUALS:
				raise Exception("Expected '=' but got:", printToken(eq))
			return UnderscoreAssignment(self.parseExpr())
		elif tok == TokenType.NOT: #Field update
			fbase = self.parseExpr()
			dot = self._tokenizer.next()
			if dot != TokenType.DOT:
				raise Exception("Expected '.', got:", printToken(dot))
			
			fname = self._tokenizer.next()
			if type(fname) != Identifier:
				raise Exception("Expected identifier, got:", printToken(fname))
			
			fread = FieldRead(fbase, fname.name())
			eq = self._tokenizer.next()
			if eq != TokenType.EQUALS:
				raise Exception("Expected '=' but got:", printToken(eq))
			exp = self.parseExpr()
			return FieldUpdate(fread, exp)
		elif tok == TokenType.IF:
			exp = self.parseExpr()
			colon = self._tokenizer.next()
			if(colon != TokenType.COLON):
				raise Exception("Expected ':' but got:", printToken(colon))

			left_brace = self._tokenizer.next()
			if(left_brace != TokenType.LEFT_BRACE):
				raise Exception("Expected '{' but got:", printToken(left_brace))

			if_statements = []
			while(self._tokenizer.peek() != TokenType.RIGHT_BRACE):
				if_statements.append(self.parseStatement())

			_ = self._tokenizer.next() #Move past right brace
			else_tok = self._tokenizer.next()
			if(else_tok != TokenType.ELSE):
				raise Exception("Expected else, but got:", printToken(else_tok))

			left_brace = self._tokenizer.next()
			if(left_brace != TokenType.LEFT_BRACE):
				raise Exception("Expected '{' but got:", printToken(left_brace))

			else_statements = []
			while(self._tokenizer.peek() != TokenType.RIGHT_BRACE):
				else_statements.append(self.parseStatement())
			
			_ = self._tokenizer.next()
			return IfStatement(exp, if_statements, else_statements)
			
		elif tok == TokenType.IFONLY:
			exp = self.parseExpr()
			colon = self._tokenizer.next()
			if(colon != TokenType.COLON):
				raise Exception("Expected ':' but got:", printToken(colon))

			left_brace = self._tokenizer.next()
			if(left_brace != TokenType.LEFT_BRACE):
				raise Exception("Expected '{' but got:", printToken(left_brace))

			if_statements = []
			while(self._tokenizer.peek() != TokenType.RIGHT_BRACE):
				if_statements.append(self.parseStatement())

			_ = self._tokenizer.next() #Advance past } char
			return IfOnlyStatement(exp, if_statements)
			
		elif tok == TokenType.WHILE:
			exp = self.parseExpr()
			colon = self._tokenizer.next()
			if colon != TokenType.COLON:
				raise Exception("Expected ':', but got:", printToken(colon))

			left_brace = self._tokenizer.next()
			if left_brace != TokenType.LEFT_BRACE:
				raise Exception("Expected '{', but got:", printToken(left_brace))

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
				raise Exception("Expected '(' but got:", printToken(left_paren))

			exp = self.parseExpr()
			right_paren = self._tokenizer.next()
			if right_paren != TokenType.RIGHT_PAREN:
				raise Exception("Expected ')' but got:", printToken(right_paren))

			return PrintStatement(exp)

		else:
			raise Exception("Unexpected token for start of statement:", printToken(tok))
    
	def parseClass(self) -> ClassDefinition:
		tok = self._tokenizer.next()
		if tok != TokenType.CLASS:
			raise Exception("Expected class definition, got:", printToken(tok)) # Should not trigger

		cname = self._tokenizer.next()
		if type(cname) != Identifier:
			raise Exception("Expected identifier, got:", printToken(cname))
		
		left_bracket = self._tokenizer.next()
		if left_bracket != TokenType.LEFT_BRACKET:
			raise Exception("Expected '[' but got:", printToken(left_bracket))

		tok = self._tokenizer.next()
		if tok != TokenType.FIELDS:
			raise Exception("Expected fields, got:", printToken(tok))

		field_vars = self.getCommaSepVariables()
		methods = []
		tok = self._tokenizer.next()
		while tok == TokenType.METHOD:
			mname = self._tokenizer.next()
			if type(mname) != Identifier:
				raise Exception("Expected identifier, got:", printToken(mname))

			left_paren = self._tokenizer.next()
			if left_paren != TokenType.LEFT_PAREN:
				raise Exception("Expected '(' got:", printToken(left_paren))

			statements = []
			method_params = self.getCommaSepVariables()
			tok = self._tokenizer.next()
			if tok != TokenType.RIGHT_PAREN:
				raise Exception("Expected ')' but got:", printToken(tok))
			
			returning_tok = self._tokenizer.next()
			if returning_tok != TokenType.RETURNING:
				raise Exception("Expected 'returning' keyword, but got:", printToken(returning_tok))

			return_type = self._tokenizer.next()
			if type(return_type) == Identifier:
				return_type = return_type.name()
			elif return_type == TokenType.INT:
				return_type = "int"
			else:
				raise Exception("Invalid return type:", printToken(return_type))

			tok = self._tokenizer.next()
			if tok != TokenType.WITH:
				raise Exception("Expected with, got:", printToken(tok))
			
			tok = self._tokenizer.next()
			if tok != TokenType.LOCALS:
				raise Exception("Expected locals, got:", printToken(tok))

			method_variables = self.getCommaSepVariables()
			colon = self._tokenizer.next()
			if colon != TokenType.COLON:
				raise Exception("Expected colon, got:", printToken(colon))

			while self._tokenizer.peek() != TokenType.METHOD and self._tokenizer.peek() != TokenType.RIGHT_BRACKET:
				statements.append(self.parseStatement())
	
			if not statements:
				raise Exception("Expected method body")

			methods.append(MethodDefinintion(mname.name(), method_params, return_type, method_variables, statements))
			tok = self._tokenizer.next()
   
		if tok != TokenType.RIGHT_BRACKET:
			raise Exception("Expected ']', but got:", printToken(tok))

		return ClassDefinition(cname.name(), field_vars, methods)			
	
	def parseMain(self) -> MainMethod:
		main_tok = self._tokenizer.next()
		if main_tok != TokenType.MAIN:
			raise Exception("Expected main method, got:", printToken(main_tok))
		
		with_tok = self._tokenizer.next()
		if with_tok != TokenType.WITH:
			raise Exception ("Expected with, got:", printToken(with_tok))
		
		main_variables = self.getCommaSepVariables()
		colon = self._tokenizer.next()
		if colon != TokenType.COLON:
			raise Exception("Expected ':', but got:", printToken(colon))
		
		statements = []
		while self._tokenizer.peek() != TokenType.EOF:
			statements.append(self.parseStatement())

		return MainMethod(main_variables, statements)
	
	def parseFile(self) -> list[ASTNode]:
		nodes = []
		while(self._tokenizer.peek() != TokenType.EOF):
			open_token = self._tokenizer.peek()
			if open_token == TokenType.CLASS:
				class_def = self.parseClass()
				nodes.append(ASTNode(class_def, None))
			elif open_token == TokenType.MAIN:
				main_def = self.parseMain()
				nodes.append(ASTNode(None, main_def))
			else:
				raise Exception("Unknown starting token:", printToken(open_token))
		return nodes
