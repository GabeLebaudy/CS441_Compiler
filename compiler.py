#!/usr/bin/env python3

import argparse
import sys
import os
from collections import defaultdict

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
	#Tokens with data
	OPERATOR = 30,
	NUMBER = 31,
	IDENTIFIER = 32

TOKEN_TYPE_TO_STDOUT = {
	1: "(", 2: ")", 3: "{", 4: "}", 5: "^", 6: "&", 7: "@", 8: "!",
	9: ".", 10: ":", 11: ",", 12: "_", 13: "=", 14: "[", 15: "]", 16: "this", 
 	17: "if", 18: "else", 19: "ifonly", 20: "while", 21: "return", 22: "print", 
	23: "EOF", 24: "with", 25: "fields", 26: "method", 27: "locals", 28: "class",
 	29: "main", 30: "Operator", 31: "Number", 32: "Identifier"
}

def printToken(token):
	if type(token) == tuple:
		print("Token: ", TOKEN_TYPE_TO_STDOUT[token[0]])
	else:
		print(token)

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
					'main': TokenType.MAIN}
 
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

	def value(self) -> int:
		return self._value
	
	def __str__(self) -> str:
		return f"[Constant: value={self._value}]"

class Variable(Expression):
	def __init__(self, name: str):
		super().__init__()
		self._name = name

	def name(self) -> str:
		return self._name
	
	def __str__(self) -> str:
		super().__init__()
		return f"[Variable: name={self._name}]"

class BinaryOp(Expression):
	def __init__(self, lhs, op, rhs):
		super().__init__()
		self._lhs = lhs
		self._op = op
		self._rhs = rhs

	def lhs(self) -> Expression:
		return self._lhs
	
	def op(self) -> str:
		return self._op
	
	def rhs(self) -> Expression:
		return self._rhs
	
	def __str__(self) -> str:
		return f"Binary Op: [LHS ={self._lhs}, op={self._op}, RHS={self._rhs}]"

class FieldRead(Expression):
	def __init__(self, base: Expression, field_name: str):
		super().__init__()
		self._base = base
		self._field_name = field_name

	def base(self) -> Expression:
		return self._base
	
	def field_name(self) -> str:
		return self._field_name
	
	def __str__(self) -> str:
		return f"Field Read: [base={self._base}, field name={self._field_name}]"

class MethodCall(Expression):
	def __init__(self, base, methodname, args):
		super().__init__()
		self._base = base
		self._methodname = methodname
		self._args = args

	def base(self) -> str:
		return self._base
	
	def name(self) -> str:
		return self._methodname
	
	def args(self) -> list[Expression]:
		return self._args
	
	def __str__(self) -> str:
		args_str = ", ".join(str(arg) for arg in self._args)
		return (
			f"MethodCall("
			f"base={self._base}, "
			f"method={self._methodname}, "
			f"args=[{args_str}]"
			f")"
		)

class ClassRef(Expression):
	def __init__(self, name: str):
		super().__init__()
		self._name = name
	
	def name(self) -> str:
		return self._name
	
	def __str__(self) -> str:
		return f"Class Reference: name={self._name}"

class ThisExpr(Expression):
    def __init__(self):
        pass
    
    def __str__(self) -> str:
        return "This Expression"

class Assignment(Statement):
	def __init__(self, variable: Variable, expression: Expression):
		super().__init__()
		self._variable = variable
		self._expression = expression

	def variable(self) -> Variable:
		return self._variable
		
	def expression(self) -> Expression:
		return self._expression
		
	def __str__(self) -> str:
		return f"Assignment: [variable={self._variable} expression={self._expression}]"

class UnderscoreAssignment(Statement):
	def __init__(self, expression: Expression):
		self._exp = expression

	def expression(self) -> Expression:
		return self._exp
		
	def __str__(self) -> str:
		return f"Underscore statement: [expression={self._exp}]"

class FieldUpdate(Statement):
	def __init__(self, field_read: FieldRead, expression: Expression):
		super().__init__()
		self._field_read = field_read
		self._expression = expression

	def field_read(self) -> FieldRead:
		return self._field_read

	def expression(self) -> Expression:
		return self._expression
		
	def __str__(self) -> str:
		return f"Field Update: [field read={self._field_read} expression={self._expression}]"

class IfStatement(Statement):
	def __init__(self, condition: Expression, true_statements: list[Statement], else_statements: list[Statement]):
		super().__init__()
		self._condition = condition
		self._true_statements = true_statements
		self._else_statements = else_statements
	
	def condition(self) -> Expression:
		return self._condition
	
	def if_statements(self) -> list[Statement]:
		return self._true_statements
	
	def else_statements(self) -> list[Statement]:
		return self._else_statements
	
	def __str__(self) -> str:
		if_block_statements = "\n".join(str(statement) for statement in self._true_statements)
		else_block_statements = "\n".join(str(statement) for statement in self._else_statements)
		return (
			f"If statement: [Condition = {self._condition},"
			f"if_block: {if_block_statements},"
           	f"else_block: {else_block_statements}]"
		)

class IfOnlyStatement(Statement):
	def __init__(self, condition: Expression, statements: list[Statement]):
		super().__init__()
		self._condition = condition
		self._statements = statements
    
	def condition(self) -> Expression:
		return self._condition
	
	def statements(self) -> list[Statement]:
		return self._statements
	
	def __str__(self) -> str:
		if_block_statements = "\n".join(str(statement) for statement in self._statements)
		return (
			f"IfOnly Statement: [Condition = {self._condition}"
			f"Statements: {if_block_statements}]"
		)

class WhileStatement(Statement):
	def __init__(self, condition: Expression, statements: list[Statement]):
		super().__init__()
		self._condition = condition
		self._statements = statements

	def condition(self) -> Expression:
		return self._condition
	
	def statements(self) -> list[Statement]:
		return self._statements
	
	def __str__(self) -> str:
		while_block_statements = "\n".join(str(statement) for statement in self._statements)
		return (
			f"While Statement: [Condition = {self._condition}"
			f"Statements: {while_block_statements}]"
		)

class ReturnStatement(Statement):
	def __init__(self, exp: Expression):
		super().__init__()
		self._exp = exp

	def expression(self) -> Expression:
		return self._exp

	def __str__(self) -> str:
		return f"Return statement: [returns {self._exp}]"

class PrintStatement(Statement):
	def __init__(self, exp):
		super().__init__()
		self._exp = exp
    
	def expression(self) -> Expression:
		return self._exp
		
	def __str__(self) -> str:
		return f"Print statement: [prints {self._exp}]"
    
class MethodDefinintion:
	def __init__(self, name: str, params: list[Variable], locals: list[Variable], statements: list[Statement]):
		self._name = name
		self._params = params
		self._locals = locals
		self._statements = statements
    
	def name(self) -> str:
		return self._name
	
	def params(self) -> list[Variable]:
		return self._params
	
	def locals(self) -> list[Variable]:
		return self._locals
	
	def statements(self) -> list[Statement]:
		return self._statements

	def __str__(self) -> str:
		arguments = " ".join(str(arg) for arg in self._args)
		local_vars = " ".join(str(local) for local in self._locals)
		statements = "\n".join(str(statement) for statement in self._statements)
		return (
				f"Method Definition: Name={self._name} [Arguments={arguments}, "
      			f"Local Variables={local_vars}, "
      			f"Statements={statements}]"
		)

class ClassDefinition:
	def __init__(self, name: str, fields: list[Variable], methods: list[MethodDefinintion]):
		self._name = name
		self._fields = fields
		self._methods = methods
    
	def name(self) -> str:
		return self._name
	
	def fields(self) -> list[Variable]:
		return self._fields
	
	def methods(self) -> list[MethodDefinintion]:
		return self._methods

	def __str__(self) -> str:
		fields = " ".join(str(field) for field in self._fields)
		methods = "\n".join(str(method) for method in self._methods)
		return f"Class Definition: [name={self._name}, Fields={fields}, Methods={methods}"

class MainMethod:
	def __init__(self, vars: list[Variable], statements: list[Statement]):
		self._vars = vars
		self._statements = statements

	def vars(self) -> list[Variable]:
		return self._vars
	
	def statements(self) -> list[Statement]:
		return self._statements
	
	def __str__(self) -> str:
		var_str = " ".join(str(var) for var in self._vars)
		statements = " ".join(str(statement) for statement in self._statements)
		return f"Main Method: [variables={var_str}, statements={statements}]"

class ASTNode:
	def __init__(self, class_def: ClassDefinition, main_method: MainMethod):
		self._class_def = class_def
		self._main_def = main_method
  
	def getValue(self):
		return self._class_def if self._class_def else self._main_def

	def __str__(self) -> str:
		class_str = f"{str(self._class_def)}" if self._class_def else ""
		main_str = f"{str(self._main_def)}" if self._main_def else ""
		return f"AST Node: {class_str}{main_str}"

class Parser:
	def __init__(self, tokenizer: Tokenizer):
		self._tokenizer = tokenizer
	
	def getCommaSepIdentifiers(self) -> list[Identifier]:
		identifiers = []
		if type(self._tokenizer.peek()) != Identifier:
			return identifiers
		
		tok = self._tokenizer.next()
		identifiers.append(tok)
		while self._tokenizer.peek() == TokenType.COMMA:
			_ = self._tokenizer.next()
			tok = self._tokenizer.next()
			if type(tok) != Identifier:
				raise Exception("Expected identifier, got:", tok)
			identifiers.append(tok)
		return identifiers

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
			if type(optok) != Operator:
				raise Exception("Expected operator token but found", optok)

			rhs = self.parseExpr()
			closetok = self._tokenizer.next() 
			if closetok != TokenType.RIGHT_PAREN:
				raise Exception("Expected ')' but got", closetok)
			return BinaryOp(lhs, optok, rhs)
		elif tok == TokenType.AMPERSAND: #Field Read
			base = self.parseExpr()
			dot = self._tokenizer.next()
			if dot != TokenType.DOT:
				raise Exception("Expected '.' but found", dot)
			fname = self._tokenizer.next()
			if type(fname) != Identifier:
				raise Exception("Expected valid field name but found", fname)
			return FieldRead(base, fname.name())
		elif tok == TokenType.CARET: #Method invocation
			mbase = self.parseExpr()
			mdot = self._tokenizer.next()
			if mdot != TokenType.DOT:
				raise Exception("Expected dot but found", mdot)
			mname = self._tokenizer.next()
			if type(mname) != Identifier:
				raise Exception("Expected valid method name but found", mname)
			open = self._tokenizer.next()
			if open != TokenType.LEFT_PAREN:
				raise Exception("Expected '(' but found", open)
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
		elif tok == TokenType.UNDERSCORE: # Statement to run for side effects
			eq = self._tokenizer.next()
			if eq != TokenType.EQUALS:
				raise Exception("Expected '=' but got:", eq)
			return UnderscoreAssignment(self.parseExpr())
		elif tok == TokenType.NOT: #Field update
			fbase = self.parseExpr()
			dot = self._tokenizer.next()
			if dot != TokenType.DOT:
				raise Exception("Expected '.', got:", dot)
			
			fname = self._tokenizer.next()
			if type(fname) != Identifier:
				raise Exception("Expected identifier, got:", fname)
			
			fread = FieldRead(fbase, fname.name())
			eq = self._tokenizer.next()
			if eq != TokenType.EQUALS:
				raise Exception("Expected '=' but got:", eq)
			exp = self.parseExpr()
			return FieldUpdate(fread, exp)
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
				if_statements.append(self.parseStatement())

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
    
	def parseClass(self) -> ClassDefinition:
		tok = self._tokenizer.next()
		if tok != TokenType.CLASS:
			raise Exception("Expected class definition, got:", tok) # Should not trigger

		cname = self._tokenizer.next()
		if type(cname) != Identifier:
			raise Exception("Expected identifier, got:", cname)
		
		left_bracket = self._tokenizer.next()
		if left_bracket != TokenType.LEFT_BRACKET:
			raise Exception("Expected '[' but got:", left_bracket)

		tok = self._tokenizer.next()
		if tok != TokenType.FIELDS:
			raise Exception("Expected fields, got:", tok)

		field_ids = self.getCommaSepIdentifiers()
		fields = []
		for i in field_ids:
			fields.append(Variable(i.name()))

		methods = []
		tok = self._tokenizer.next()
		while tok == TokenType.METHOD:
			mname = self._tokenizer.next()
			if type(mname) != Identifier:
				raise Exception("Expected identifier, got:", mname)

			left_paren = self._tokenizer.next()
			if left_paren != TokenType.LEFT_PAREN:
				raise Exception("Expected '(' got:", left_paren)

			statements = []
			method_identifiers = self.getCommaSepIdentifiers()
			margs = []
			for i in method_identifiers:
				margs.append(Variable(i.name()))
			
			tok = self._tokenizer.next()
			if tok != TokenType.RIGHT_PAREN:
				raise Exception("Expected ')' but got:", tok)
			
			tok = self._tokenizer.next()
			if tok != TokenType.WITH:
				raise Exception("Expected with, got:", tok)
			
			tok = self._tokenizer.next()
			if tok != TokenType.LOCALS:
				raise Exception("Expected locals, got:", tok)

			local_identifiers = self.getCommaSepIdentifiers()
			mlocals = []
			for i in local_identifiers:
				mlocals.append(Variable(i.name()))
    
			while(self._tokenizer.peek() == TokenType.COMMA):
				_ = self._tokenizer.next()
				local_tok = self._tokenizer.next()
				if type(local_tok) != Identifier:
					raise Exception("Expected identifier, got:", local_tok)
				mlocals.append(Variable(local_tok.name()))

			colon = self._tokenizer.next()
			if colon != TokenType.COLON:
				raise Exception("Expected colon, got:", colon)

			while self._tokenizer.peek() != TokenType.METHOD and self._tokenizer.peek() != TokenType.RIGHT_BRACKET:
				statements.append(self.parseStatement())
	
			if not statements:
				raise Exception("Expected method body")

			methods.append(MethodDefinintion(mname.name(), margs, mlocals, statements))
			tok = self._tokenizer.next()
   
		if tok != TokenType.RIGHT_BRACKET:
			raise Exception("Expected ']', but got:", tok)

		return ClassDefinition(cname.name(), fields, methods)			
	
	def parseMain(self) -> MainMethod:
		main_tok = self._tokenizer.next()
		if main_tok != TokenType.MAIN:
			raise Exception("Expected main method, got:", main_tok)
		
		with_tok = self._tokenizer.next()
		if with_tok != TokenType.WITH:
			raise Exception ("Expected with, got:", with_tok)
		
		local_identifiers = self.getCommaSepIdentifiers()
		locals = []
		for i in local_identifiers:
			locals.append(Variable(i.name()))
		
		colon = self._tokenizer.next()
		if colon != TokenType.COLON:
			raise Exception("Expected ':', but got:", colon)
		
		statements = []
		while self._tokenizer.peek() != TokenType.EOF:
			statements.append(self.parseStatement())

		return MainMethod(locals, statements)
	
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
				raise Exception("Unknown starting token:", open_token)
		return nodes

#Base class (Might come in handy later)
class IRValue:
    pass

class IRVariable(IRValue):
	def __init__(self, name: str):
		self._name = name
		self._latest_version = 0
  
	def name(self) -> str:
		return self._name

	def latest_version(self) -> int:
		return self._latest_version

	def incVersion(self):
		self._latest_version += 1
  
	def __str__(self) -> str:
		return f"%{self._name}"

class IRConstant(IRValue):
    def __init__(self, value: int):
        self._value = value
    
    def value(self) -> int:
        return self._value
    
    def __str__(self) -> str:
        return f"{self._value}"

class IRGlobal(IRValue):
    def __init__(self, name: str):
        self._name = name
        
    def name(self) -> str:
        return self._name
    
    def __str__(self) -> str:
        return f"@{self._name}"

class IRStatement:
    pass

class IRAssignment(IRStatement):
    def __init__(self, name: str, value):
        self._name = name
        self._value = value
        
    def name(self) -> str:
        return self._name
    
    def __str__(self) -> str:
        return f"	{self._name} = {self._value}" 

class IRBinaryOp(IRStatement):
    def __init__(self, name: IRVariable, lhs: IRValue, op: str, rhs: IRValue):
        self._name = name
        self._lhs = lhs
        self._op = op
        self._rhs = rhs
        
    def name(self) -> IRVariable:
        return self._name
    
    def lhs(self) -> IRValue:
        return self._lhs
    
    def op(self) -> str:
        return self._op
    
    def rhs(self) -> IRValue:
        return self._rhs
    
    def __str__(self) -> str:
        return f"	{self._name} = {self._lhs} {self._op} {self._rhs}"

class IRCall(IRStatement):
    def __init__(self, name: IRVariable, code_addr: IRVariable, receiver: IRVariable, args: list[IRValue]):
        self._name = name
        self._code_addr = code_addr
        self._receiver = receiver
        self._args = args
        
    def name(self) -> IRVariable:
        return self._name
    
    def code_addr(self) -> IRVariable:
        return self._code_addr
    
    def receiver(self) -> IRVariable:
        return self._receiver
    
    def args(self) -> list[IRValue]:
        return self._args
    
    def __str__(self) -> str:
        args_str = ", " + ", ".join(str(a) for a in self._args)
        return f"	{self._name} = call({self._code_addr}, {self._receiver}{args_str})"

class IRPhi(IRStatement):
    def __init__(self, name: IRVariable, prior_blocks: list[tuple[str, IRVariable]]):
        self._name = name
        self._prior_blocks = prior_blocks
        
    def name(self) -> IRVariable:
        return self._name
    
    def prior_blocks(self) -> list[tuple[str, IRVariable]]:
        return self._prior_blocks
    
    def __str__(self) -> str:
        prior_block_str = ", ".join(f"{label}, {var}" for label, var in self._prior_blocks)
        return f"	{self._name} = phi({prior_block_str})"

class IRAlloc(IRStatement):
    def __init__(self, name: IRVariable, size: int):
        self._name = name
        self._size = size
        
    def name(self) -> IRVariable:
        return self._name
    
    def val(self) -> int:
        return self._size
    
    def __str__(self) -> str:
        return f"	{self._name} = alloc({self._size})"
    
class IRPrint(IRStatement):
    def __init__(self, print_var: IRValue):
        self._print_var = print_var
        
    def print_var(self) -> IRValue:
        return self._print_var
    
    def __str__(self) -> str:
        return f"	print({self._print_var})"
    
class IRGelElt(IRStatement):
    def __init__(self, name: IRVariable, arr_pointer: IRVariable, ind: IRValue):
        self._name = name
        self._arr_pointer = arr_pointer
        self._ind = ind
        
    def name(self) -> IRVariable:
        return self._name
    
    def arr_pointer(self) -> IRVariable:
        return self._arr_pointer
    
    def ind(self) -> IRValue:
        return self._ind
    
    def __str__(self) -> str:
        return f"	{self._name} = getelt({self._arr_pointer}, {self._ind})"

class IRSetElt(IRStatement):
    def __init__(self, arr_pointer: IRVariable, ind: IRValue, val: IRValue):
        self._arr_pointer = arr_pointer
        self._ind = ind
        self._val = val
        
    def arr_pointer(self) -> IRVariable:
        return self._arr_pointer
    
    def ind(self) -> IRValue:
        return self._ind
    
    def val(self) -> IRValue:
        return self._val
    
    def __str__(self) -> str:
        return f"	setelt({self._arr_pointer}, {self._ind}, {self._val})"
    
class IRLoad(IRStatement):
    def __init__(self, name: IRVariable, base: IRVariable):
        self._name = name
        self._base = base
        
    def name(self) -> IRVariable:
        return self._name
    
    def base(self) -> IRVariable:
        return self._base
    
    def __str__(self) -> str:
        return f"	{self._name} = load({self._base})"

class IRStore(IRStatement):
    def __init__(self, base: IRVariable, val: IRValue):
        self._base = base
        self._val = val
        
    def base(self) -> IRVariable:
        return self._base
    
    def val(self) -> IRValue:
        return self._val
    
    def __str__(self) -> str:
        return f"	store({self._base}, {self._val})"

class IRControlTransfer:
    pass

class IRJump(IRControlTransfer):
    def __init__(self, name: str):
        self._name = name
        
    def name(self) -> str:
        return self._name
    
    def __str__(self) -> str:
        return f"	jump {self._name}"
    
class IRConditional(IRControlTransfer):
	def __init__(self, condition: IRVariable, if_name: str, else_name: str):
		self._condition = condition
		self._if_name = if_name
		self._else_name = else_name
  
	def condition(self) -> IRVariable:
		return self._condition
    
	def if_name(self) -> str:
		return self._if_name
    
	def else_name(self) -> str:
		return self._else_name
    
	def __str__(self) -> str:
		return f"	if {self._condition}, then {self._if_name} else {self._else_name}"

class IRReturn(IRControlTransfer):
    def __init__(self, return_val: IRValue):
        self._return_val = return_val
        
    def return_val(self) -> str:
        return self._return_val
    
    def __str__(self) -> str:
        return f"	ret {self._return_val}"
    
class IRFail(IRControlTransfer):
    def __init__(self, fail_reason: str):
        self._fail = fail_reason
        
    def fail(self) -> str:
        return self._fail
    
    def __str__(self) -> str:
        return f"	fail {self._fail}"

class BasicBlock:
	def __init__(self, name: str, params: list = None):
		self._name = name
		self._params = params if params else []
		self._statements = []
		self._control = None 
    
	def name(self) -> str:
		return self._name

	def params(self) -> list[IRVariable]:
		return self._params

	def statements(self) -> list[IRStatement]:
		return self._statements

	def control(self) -> IRControlTransfer:
		return self._control

	def addStatement(self, statement: IRStatement):
		self._statements.append(statement)
  
	def setControlTransfer(self, control_transfer: IRControlTransfer):
		self._control = control_transfer
  
	def __str__(self) -> str:
		if self._params:
			params_str = ", ".join(str(p) for p in self._params)
			result = f"{self._name}({params_str}):\n"
		else:
			result = f"{self._name}:\n"

		statement_str = "\n".join(str(stmt) for stmt in self._statements)
		if statement_str:
			statement_str += "\n"
		result += statement_str
		if self._control:
			result += str(self._control) + "\n"

		return result

class GlobalArray:
    def __init__(self, name: str, values: list[IRValue]):
        self._name = name
        self._values = values
        
    def name(self) -> str:
        return self._name
        
    def values(self) -> list[IRValue]:
        return self._values
    
    def __str__(self) -> str:
        values_str = ", ".join(str(v) for v in self._values)
        return f"global array @{self._name}: {{ {values_str} }}"

class IRProgram:
	def __init__(self):
		self._globals = []
		self._blocks = []
        
	def globals(self) -> list[GlobalArray]:
		return self._globals
    
	def blocks(self) -> list[BasicBlock]:
		return self._blocks
    
	def addGlobal(self, global_arr: GlobalArray):
		self._globals.append(global_arr)
        
	def addBlock(self, block: BasicBlock):
		self._blocks.append(block)

	def __str__(self) -> str:
		result = "data:\n"
		for g in self._globals:
			result += str(g) + "\n"

		result += "\ncode:\n"
		for b in self._blocks:
			result += "\n" + str(b)

		return result

class CFGGenerator:
	def __init__(self, ast_nodes: list[ASTNode]):
		self._ast_nodes = ast_nodes
		self._program = IRProgram()
		self._temp_counter = 1
		self._label_counter = 1
		self._current_block = None

		self._class_info = {}
		self._field_ids = {}
		self._method_ids = {}
  
	def new_tmp(self) -> IRVariable:
		temp = IRVariable(str(self._temp_counter))
		self._temp_counter += 1
		return temp
	
	def new_label(self, prefix: str = "l") -> str:
		label = f"{prefix}{self._label_counter}"
		self._label_counter += 1
		return label
	
	def collectClassInfo(self, class_defs: list[ClassDefinition]):
		for cls in class_defs:
			cname = cls.name()
			cfields = cls.fields()
			cmethods = cls.methods()

			if cname in self._class_info:
				raise Exception("Class is already defined:", cname)

			self._class_info[cname] = {
				'fields': cfields,
				'methods': cmethods
			}

			for i, f in enumerate(cfields):
				if (cname, f.name()) in self._field_ids:
					raise Exception("Class field already defined:", f.name())
 
				self._field_ids[(cname, f.name())] = i

			for i, m in enumerate(cmethods):
				if (cname, m.name()) in self._method_ids:
					raise Exception("Method is already defined:", m.name())
 
				self._method_ids[(cname, m.name())] = i

	def genVtables(self, class_defs: list[ClassDefinition]):
		for cls in class_defs:
			cname = cls.name()

			vtable_name = f"vtbl{cname}"
			method_labels = [f"{cname}{m.name()}" for m in cls.methods()]
			self._program.addGlobal(GlobalArray(vtable_name, method_labels))

			num_fields = len(cls.fields())
			field_offsets = [IRConstant(2 + i) for i in range(num_fields)]
			field_map_values = [IRConstant(num_fields)] + field_offsets

			field_map_name = f"fields{cname}"
			self._program.addGlobal(GlobalArray(field_map_name, field_map_values))

	def generateBinaryOp(self, exp: BinaryOp, var_map: dict[str, IRVariable]) -> IRValue:
		lhs = self.generateExpression(exp.lhs(), var_map)
		rhs = self.generateExpression(exp.rhs(), var_map)
  
		left_check = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(left_check, lhs, "&", IRConstant(1)))

		ok_left_label = self.new_label("ok_left")
		fail_label = self.new_label("not_a_number")
		fail_block = BasicBlock(fail_label)
		fail_block.setControlTransfer(IRFail("NotANumber"))
  
		self._current_block.setControlTransfer(IRConditional(left_check, ok_left_label, fail_label))
		self._program.addBlock(self._current_block)
		self._program.addBlock(fail_block)
  
		ok_left_block = BasicBlock(ok_left_label)
		self._current_block = ok_left_block

		right_check = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(right_check, rhs, "&", IRConstant(1)))

		ok_right_label = self.new_label("ok_right")
		self._current_block.setControlTransfer(IRConditional(right_check, ok_right_label, fail_label))
		self._program.addBlock(self._current_block)
  
		res = self.new_tmp()
		op_str = exp.op().op()

		self._current_block.addStatement(IRBinaryOp(res, lhs, op_str, rhs))
		self._program.addBlock(self._current_block)
		return res

	def generateFieldRead(self, exp: FieldRead, ssa_ctx: SSAContext):
		obj_base = self.generateExpression(exp.base(), ssa_ctx)
  
		ptr_check = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(ptr_check, obj_base, "&", 1))
  
		ok_ptr_label = self.new_label("ok_ptr")
		fail_label = self.new_label("not_a_pointer")

		fail_block = BasicBlock(fail_label)
		fail_block.setControlTransfer(IRFail("Not a Pointer"))

		self._current_block.setControlTransfer(IRConditional(ptr_check, fail_label, ok_ptr_label))
		self._program.addBlock(self._current_block)
		self._program.addBlock(fail_block)
  
		ok_block = BasicBlock(ok_ptr_label)
		self._current_block = ok_block

		field_value = self.new_tmp()
		self._current_block.addStatement(IRGelElt(field_value, obj_base, IRConstant(2)))
		self._program.addBlock(self._current_block)
		return field_value
  
	def generateMethodCall(self, exp: MethodCall, ssa_ctx):
		receiver = self.generateExpression(exp.base(), ssa_ctx)

		ptr_check = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(ptr_check, receiver, "&", 1))
		ok_ptr_label = self.new_label("ok_pointer_call")
		fail_label = self.new_label("not_a_pointer")

		fail_block = BasicBlock(fail_label)
		fail_block.setControlTransfer(IRFail("Not a Pointer"))
		self._current_block.setControlTransfer(IRConditional(ptr_check, fail_label, ok_ptr_label))
		self._program.addBlock(self._current_block)
		self._program.addBlock(fail_block)

		ok_block = BasicBlock(ok_ptr_label)
		self._current_block = ok_block
  
		vtable_ptr = self.new_tmp()
		self._current_block.addStatement(IRLoad(vtable_ptr, receiver))
		method_addr = self.new_tmp()
		self._current_block.addStatement(IRGelElt(method_addr, vtable_ptr, IRConstant(0)))

		arg_vals = []
		for arg_exp in exp.args():
			arg_vals.append(self.generateExpression(arg_exp, ssa_ctx))
		res = self.new_tmp()
		self._current_block.addStatement(IRCall(res, method_addr, receiver, arg_vals))
		self._program.addBlock(self._current_block)
		return res

	def allocateClass(self, exp: ClassRef):
		cname = exp.name()

		if cname not in self._class_info:
			raise Exception("Undefined class:", cname)

		num_fields = len(self._class_info[cname]["fields"])
		obj_size = 2 + num_fields
  
		obj_ptr = self.new_tmp()
		self._current_block.addStatement(IRAlloc(obj_ptr, obj_size)) #Change to IR Constant?

		vtable_global = IRGlobal(f"vtbl{cname}")
		self._current_block.addStatement(IRStore(obj_ptr, vtable_global))
		field_map_addr = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(field_map_addr, obj_ptr, "+", IRConstant(8)))

		field_map_global = IRGlobal(f"fields{cname}")
		self._current_block.addStatement(IRStore(field_map_addr, field_map_global))
		return obj_ptr

	def generateExpression(self, exp: Expression, var_map: dict[str, IRVariable]):
		if type(exp) == Constant:
			return IRConstant((exp.value() << 1) | 1)
		elif type(exp) == Variable:
			if not var_map.get(exp.name()):
				raise Exception("Variable not defined:", exp.name())
			
			return var_map[exp.name()]
		elif type(exp) == ThisExpr:
			if not var_map.get("this"):
				raise Exception("This expression used outside method context")
			
			return var_map.get("this")
		elif type(exp) == BinaryOp:
			return self.generateBinaryOp(exp, var_map)
		elif type(exp) == FieldRead:
			return self.generateFieldRead(exp, var_map)
		elif type(exp) == MethodCall:
			return self.generateMethodCall(exp, var_map)
		elif type(exp) == ClassRef:
			return self.allocateClass(exp)
		else:
			raise Exception("Unexpected expression:", exp)

	def generateFieldUpdate(self, field_update: FieldUpdate, var_map: dict[str, IRVariable]):
		field_read = field_update.field_read()
		obj = self.generateExpression(field_read.base(), var_map)
		value = self.generateExpression(field_update.expression(), var_map)

		ptr_check = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(ptr_check, field_read, "&", IRConstant(1)))
  
		ok_ptr_label = self.new_label("ok_poiter")
		fail_label = self.new_label("not_a_pointer")
		fail_block = BasicBlock(fail_label)
		fail_block.setControlTransfer(IRFail("Not a Pointer"))
		self._current_block.setControlTransfer(IRConditional(ptr_check, fail_label, ok_ptr_label))

		self._program.addBlock(self._current_block)
		self._program.addBlock(fail_block)
  
		ok_ptr_block = BasicBlock(ok_ptr_label)
		self._current_block = ok_ptr_block
		self._current_block.addStatement(IRSetElt(obj, IRConstant(2), value))
		self._program.addBlock(self._current_block)

	def generateIfStatement(self, statement: IfStatement, var_map: dict[str, IRVariable]):
		condition = self.generateExpression(statement.condition(), var_map)

		then_label = self.new_label("then")
		else_label = self.new_label("else")
		merge_label = self.new_label("merge")
  
		self._current_block.setControlTransfer(IRConditional(condition, then_label, else_label))
		self._program.addBlock(self._current_block)

		then_block = BasicBlock(then_label)
		self._current_block = then_block
		for s in statement.if_statements():
			self.generateStatement(s, var_map)
		if not self._current_block.control():
			self._current_block.setControlTransfer(IRJump(merge_label))
		self._program.addBlock(self._current_block)
  
		else_block = BasicBlock(else_label)
		self._current_block = else_block
		for s in statement.else_statements():
			self.generateStatement(s, var_map)
		if not self._current_block.control():
			self._current_block.setControlTransfer(IRJump(merge_label))
		self._program.addBlock(self._current_block)
  
		merge_block = BasicBlock(merge_label)
		self._current_block = merge_block
  
	def generateIfOnlyStatement(self, statement: IfOnlyStatement, var_map: dict[str, IRVariable]):
		condition = self.generateExpression(statement.condition(), var_map)

		then_label = self.new_label("then")
		merge_label = self.new_label("merge")
  
		current_label = self._current_block.name()
		self._current_block.setControlTransfer(IRConditional(condition, then_label, merge_label))
		then_block = BasicBlock(then_label)
		self._current_block = then_block
		for s in statement.statements():
			self.generateStatement(s, var_map)
		if not self._current_block.control():
			self._current_block.setControlTransfer(IRJump(merge_label))
		self._program.addBlock(self._current_block)

		merge_block = BasicBlock(merge_label)
		self._current_block = merge_block
  
	def generateWhileStatement(self, statement: WhileStatement, var_map: dict[str, IRVariable]):
		top_label = self.new_label("loop_top")
		body_label = self.new_label("loop_body")
		end_label = self.new_label("loop_end")
  
		self._current_block.setControlTransfer(IRJump(top_label))
		self._program.addBlock(self._current_block)
  
		top_block = BasicBlock(top_label)
		self._current_block = top_block
		condition = self.generateExpression(statement.condition(), var_map) 
		self._current_block.addStatement(IRConditional(condition, body_label, end_label))
		self._program.addBlock(self._current_block)
  
		body_block = BasicBlock(body_label)
		self._current_block = body_block
		for s in statement.statements():
			self.generateStatement(s, var_map)
		if not self._current_block.control():
			self._current_block.setControlTransfer(IRJump(end_label))
		self._program.addBlock(body_block)
    
		end_block = BasicBlock(end_label)
		self._current_block = end_block
	
	def generateStatement(self, statement: Statement, var_map: dict[str, IRVariable]) -> IRStatement:
		if type(statement) == Assignment:
			name = statement.variable().name()
			if not var_map.get(name):
				raise Exception(f"Assignment to undefined variable: {name}")
			
			res = self.generateExpression(statement.expression(), var_map)
			self._current_block.addStatement(IRAssignment(var_map[name], res))
		elif type(statement) == UnderscoreAssignment:
			self.generateExpression(statement.expression(), var_map)
		elif type(statement) == FieldUpdate:
			self.generateFieldUpdate(statement, var_map)
		elif type(statement) == PrintStatement:
			res = self.generateExpression(statement.expression(), var_map)
			self._current_block.addStatement(IRPrint(res))
		elif type(statement) == ReturnStatement:
			res = self.generateExpression(statement.expression(), var_map)
			self._current_block.setControlTransfer(IRReturn(res))
		elif type(statement) == IfStatement:
			self.generateIfStatement(statement, var_map)
		elif type(statement) == IfOnlyStatement:
			self.generateIfOnlyStatement(statement, var_map)
		elif type(statement) == WhileStatement:
			self.generateWhileStatement(statement, var_map)

	def genMethod(self, class_name: str, method_def: MethodDefinintion):
		mlabel = f"{method_def.name()}{class_name}"
		this_param = IRVariable("this")
		self._temp_counter = 1

		var_map = {'this': this_param}
		method_params = [this_param]
		for param in method_def.params():
			mparam = IRVariable(param.name())
			var_map[param.name()] = mparam
			method_params.append(mparam)

		for var in method_def.locals():
			if var_map.get(var.name()):
				raise Exception("Local variable already defined as method parameter", var.name())
			var_map[var.name()] = IRVariable(var.name())

		entry_block = BasicBlock(mlabel, method_params)
		self._current_block = entry_block
		for stmt in method_def.statements():
			self.generateStatement(stmt, var_map)

		if not self._current_block.control():
			self._current_block.setControlTransfer(IRReturn(IRConstant(0)))
		
		self._program.addBlock(self._current_block) #Come back to this
		
	def genMainMethod(self, main_method: MainMethod):
		main_block = BasicBlock("main")
		self._current_block = main_block

		ssa_ctx = SSAContext()
		
		for l in main_method.vars():
			local_name = l.name() if hasattr(l, 'name') else str(l)
			local_ssa = ssa_ctx.new_version(local_name)
			self._current_block.addStatement(IRAssignment(local_ssa, IRConstant(0)))

		for stmt in main_method.statements():
			self.generateStatement(stmt, ssa_ctx)

		if not self._current_block.control():
			self._current_block.setControlTransfer(IRReturn(IRConstant(0)))
		
		self._program.addBlock(self._current_block)

	def convertAstToIr(self) -> IRProgram:
		classes = []
		main_method = None
		for node in self._ast_nodes:
			val = node.getValue()
			if type(val) == ClassDefinition:
				classes.append(val)
			else:
				main_method = val
				
		self.collectClassInfo(classes)
		self.genVtables(classes)
  
		for cls in classes:
			for m in cls.methods():
				self.genMethod(cls.name(), m)
	
		self.genMainMethod(main_method)
		return self._program

class SSAVariable:
	def __init__(self, base_name: str, version: int):
		self._base_name = base_name
		self._version = version
		self._is_param = False
		
	def mark_as_param(self): #Mark as function parameter
		self._is_param = True
		
	def name(self) -> str:
		return self.__str__()
    
	def version(self) -> int:
		return self._version

	def __str__(self) -> str:
		if self._is_param:
			return f"%{self._base_name}"
		# Regular SSA variables show version
		if self._base_name:
			return f"%{self._base_name}_{self._version}"
		else:
			return f"%{self._version}"

	def __eq__(self, other):
		return isinstance(other, SSAVariable) and self._base_name == other._base_name and self._version == other._version

	def __hash__(self):
		return hash((self._base_name, self._version))

class SSAContext:
	def __init__(self):
		self._version_counters = defaultdict(int)
		self._current_versions = {}
        
	def new_version(self, var_name: str) -> SSAVariable:
		version = self._version_counters[var_name]
		self._version_counters[var_name] += 1
		ssa_var = SSAVariable(var_name, version)
		self._current_versions[var_name] = ssa_var
		return ssa_var
    
	def get_current(self, var_name: str) -> SSAVariable:
		if var_name not in self._current_versions:
			return self.new_version(var_name)
		return self._current_versions[var_name]
    
	def set_current(self, var_name: str, ssa_var: SSAVariable):
		self._current_versions[var_name] = ssa_var
    
	def version_counters(self) -> defaultdict[int]:
		return self._version_counters

	def current_versions(self) -> dict:
		return self._current_versions

	def copy(self):
		new_ctx = SSAContext()
		for k, v in self._version_counters.items():
			new_ctx._version_counters[k] = v
		new_ctx._current_versions = dict(self._current_versions)
		return new_ctx

	def get_all_variables(self) -> set[str]:
		return set(self._version_counters.keys())
	
class Optimizer:
	def __init__(self, ir_program: IRProgram):
		self._ir_program = ir_program

	def convertToSSA(self):
		pass
		
	def removeConstantArithmetic(self):
		pass
        
    
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: comp {tokenize|parseExpr|parseStatement|parseClass|parseFile} file")
		sys.exit(1)
  
	str_text = ""
	if not os.path.exists(sys.argv[2]):
		raise Exception(f"Error, file: {sys.argv[2]} does not exist")
	
	with open(sys.argv[2], 'r') as f:
		str_text = "".join(f.readlines())
	
	if sys.argv[1] == "tokenize":
		tokenizer = Tokenizer(str_text)
		token = None
		while(tokenizer.peek() != TokenType.EOF):
			token = tokenizer.next()
			printToken(token)
    
	elif sys.argv[1] == "parseExpr":
		parser = Parser(Tokenizer(str_text))
		print(parser.parseExpr())
	elif sys.argv[1] == "parseStatement":
		parser = Parser(Tokenizer(str_text))
		print(parser.parseStatement())
	elif sys.argv[1] == "parseClass":
		parser = Parser(Tokenizer(str_text))
		print(parser.parseClass())
	elif sys.argv[1] == "parseMain":
		parser = Parser(Tokenizer(str_text))
		print(parser.parseMain())
	elif sys.argv[1] == "parseFile":
		parser = Parser(Tokenizer(str_text))
		ast_nodes = parser.parseFile()
		# for node in ast_nodes:
		# 	print(node)
   
		cfg_generator = CFGGenerator(ast_nodes)
		print(cfg_generator.convertAstToIr())
	else:
		raise Exception("Invalid usage")
  
