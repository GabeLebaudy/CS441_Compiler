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

	def name(self) -> str:
		return "this"

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
		params = " ".join(str(p) for p in self._params)
		local_vars = " ".join(str(local) for local in self._locals)
		statements = "\n".join(str(statement) for statement in self._statements)
		return (
				f"Method Definition: Name={self._name} [Arguments={params}, "
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
  
	def name(self) -> str:
		return self._name
  
	def isTemp(self) -> bool:
		return self._name.isdigit() or self._name == "this"

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
	def __init__(self, name: IRVariable, value: IRValue):
		self._name = name
		self._value = value
		self._isSSA = False
        
	def name(self) -> IRVariable:
		return self._name

	def value(self):
		return self._value

	def replaceName(self, name: IRVariable):
		self._name = name
		self._isSSA = True

	def replaceValue(self, value: IRValue):
		self._value = value
  
	def isSSA(self) -> bool:
		return self._isSSA

	def __str__(self) -> str:
		return f"  {self._name} = {self._value}" 

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

	def replaceLhs(self, value: IRValue):
		self._lhs = value
		
	def replaceRhs(self, value: IRValue):
		self._rhs = value

	def __str__(self) -> str:
		return f"  {self._name} = {self._lhs} {self._op} {self._rhs}"

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
    
    def replaceCodeAddr(self, value: IRValue):
        self._code_addr = value
        
    def replaceReceiver(self, value: IRValue):
        self._receiver = value
        
    def replaceArg(self, value: IRValue, ind: int):
        self._args[ind] = value
         
    def receiver(self) -> IRVariable:
        return self._receiver
    
    def args(self) -> list[IRValue]:
        return self._args
    
    def __str__(self) -> str:
        args_str = ", " + ", ".join(str(a) for a in self._args)
        return f"  {self._name} = call({self._code_addr}, {self._receiver}{args_str})"

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
        return f"  {self._name} = phi({prior_block_str})"

class IRAlloc(IRStatement):
    def __init__(self, name: IRVariable, size: int):
        self._name = name
        self._size = size
        
    def name(self) -> IRVariable:
        return self._name
    
    def val(self) -> int:
        return self._size
    
    def __str__(self) -> str:
        return f"  {self._name} = alloc({self._size})"
    
class IRPrint(IRStatement):
    def __init__(self, print_var: IRValue):
        self._print_var = print_var
        
    def print_var(self) -> IRValue:
        return self._print_var
    
    def replacePrintVal(self, value: IRValue):
        self._print_var = value
    
    def __str__(self) -> str:
        return f"  print({self._print_var})"
    
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
    
    def replaceArrPointer(self, value: IRValue):
        self._arr_pointer = value
        
    def replaceInd(self, value: IRValue):
        self._ind = value
        
    def __str__(self) -> str:
        return f"  {self._name} = getelt({self._arr_pointer}, {self._ind})"

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
    
    def replaceArrPointer(self, value: IRValue):
        self._arr_pointer = value
        
    def replaceInd(self, value: IRValue):
        self._ind = value
        
    def replaceVal(self, value: IRValue):
        self._val = value
        
    def __str__(self) -> str:
        return f"  setelt({self._arr_pointer}, {self._ind}, {self._val})"
    
class IRLoad(IRStatement):
    def __init__(self, name: IRVariable, base: IRVariable):
        self._name = name
        self._base = base
        
    def name(self) -> IRVariable:
        return self._name
    
    def base(self) -> IRVariable:
        return self._base
    
    def replaceBase(self, value: IRValue):
        self._base = value
        
    def __str__(self) -> str:
        return f"  {self._name} = load({self._base})"

class IRStore(IRStatement):
    def __init__(self, base: IRVariable, val: IRValue):
        self._base = base
        self._val = val
        
    def base(self) -> IRVariable:
        return self._base
    
    def val(self) -> IRValue:
        return self._val
    
    def replaceBase(self, value: IRValue):
        self._base = value
        
    def replaceVal(self, value: IRValue):
        self._val = value
        
    def __str__(self) -> str:
        return f"  store({self._base}, {self._val})"

class IRControlTransfer:
    pass

class IRJump(IRControlTransfer):
    def __init__(self, name: str):
        self._name = name
        
    def name(self) -> str:
        return self._name
    
    def __str__(self) -> str:
        return f"  jump {self._name}"
    
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

	def replaceCondition(self, value: IRValue):
		self._condition = value

	def __str__(self) -> str:
		return f"  if {self._condition} then {self._if_name} else {self._else_name}"

class IRReturn(IRControlTransfer):
	def __init__(self, return_val: IRValue):
		self._return_val = return_val
        
	def return_val(self) -> str:
		return self._return_val
    
	def replaceReturnVal(self, value: IRValue):
		self._return_val = value

	def __str__(self) -> str:
		return f"  ret {self._return_val}"

class IRFail(IRControlTransfer):
    def __init__(self, fail_reason: str):
        self._fail = fail_reason
        
    def fail(self) -> str:
        return self._fail
    
    def __str__(self) -> str:
        return f"  fail {self._fail}"

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
  
	def getControlLabels(self) -> list[str]:
		if self._control is None:
			return []

		if type(self._control) == IRJump:
			return [self._control.name()]
		elif type(self._control) == IRConditional:
			return [self._control.if_name(), self._control.else_name()]
		else:
			return []
	
	def insertPhi(self, phi_statement: IRPhi):
		self._statements.insert(0, phi_statement)
  
	def __str__(self) -> str:
		if self._params:
			params_str = ", ".join(str(p)[1:] for p in self._params)
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

class IRFunction:
	def __init__(self, name: str, var_map: dict[str, IRVariable]):
		self._name = name
		self._blocks = []
		self._var_map = var_map
		
	def name(self) -> str:
		return self._name

	def addBlock(self, block: BasicBlock):
		self._blocks.append(block)
		
	def blocks(self) -> list[BasicBlock]:
		return self._blocks

	def getNonTempVariables(self) -> list[IRVariable]:
		vars = []
		for var in self._var_map.values():
			if not var.isTemp():
				vars.append(var)
		return vars

	def __str__(self) -> str:
		result = ""
		for b in self._blocks:
			result += "\n" + str(b)
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
        return f"global array {self._name}: {{ {values_str} }}"

class IRProgram:
	def __init__(self):
		self._globals = []
		self._functions = []
        
	def globals(self) -> list[GlobalArray]:
		return self._globals
    
	def functions(self) -> list[IRFunction]:
		return self._functions
    
	def addGlobal(self, global_arr: GlobalArray):
		self._globals.append(global_arr)
        
	def addFunction(self, f: IRFunction):
		self._functions.append(f)

	def __str__(self) -> str:
		result = "data:\n"
		for g in self._globals:
			result += str(g) + "\n"

		result += "code:\n"
		for f in self._functions:
			result += str(f)
   
		return result

class CFGGenerator:
	def __init__(self, ast_nodes: list[ASTNode]):
		self._ast_nodes = ast_nodes
		self._program = IRProgram()
		self._temp_counter = 1
		self._label_counter = 1
		self._current_block = None
		self._current_class = None
		self._current_function = None
		self._class_mappings = {} 

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
			method_labels = [f"{m.name()}{cname}" for m in cls.methods()]
			self._program.addGlobal(GlobalArray(vtable_name, method_labels))

			num_fields = len(cls.fields())
			field_offsets = [IRConstant(2 + i) for i in range(num_fields)]
			field_map_name = f"fields{cname}"
			self._program.addGlobal(GlobalArray(field_map_name, field_offsets))

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
		self._current_function.addBlock(self._current_block)
		self._current_function.addBlock(fail_block)
  
		ok_left_block = BasicBlock(ok_left_label)
		self._current_block = ok_left_block

		right_check = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(right_check, rhs, "&", IRConstant(1)))
		fail_right_label = self.new_label("not_a_number")
		fail_right_block = BasicBlock(fail_right_label)
		fail_right_block.addStatement(IRFail("NotANumber"))
  
		ok_right_label = self.new_label("ok_right")
		self._current_block.setControlTransfer(IRConditional(right_check, ok_right_label, fail_right_label))
		self._current_function.addBlock(self._current_block)
		self._current_function.addBlock(fail_right_block)
  
		ok_right_block = BasicBlock(ok_right_label)
		self._current_block = ok_right_block

		op_str = exp.op().op()
		res = self.new_tmp()
		if op_str == "<" or op_str == ">":
			self._current_block.addStatement(IRBinaryOp(res, lhs, op_str, rhs))
		else:
			lhs_untagged = self.new_tmp()
			self._current_block.addStatement(IRBinaryOp(lhs_untagged, lhs, ">>", IRConstant(1)))
   
			rhs_untagged = self.new_tmp()
			self._current_block.addStatement(IRBinaryOp(rhs_untagged, rhs, ">>", IRConstant(1)))
			
			result_untagged = self.new_tmp()
			self._current_block.addStatement(IRBinaryOp(result_untagged, lhs_untagged, op_str, rhs_untagged))
			
			result_shifted = self.new_tmp()
			self._current_block.addStatement(IRBinaryOp(result_shifted, result_untagged, "<<", IRConstant(1)))
			self._current_block.addStatement(IRBinaryOp(res, result_shifted, "|", IRConstant(1)))

		return res

	def generateFieldRead(self, exp: FieldRead, var_map: dict[str, IRVariable]):
		obj_base = self.generateExpression(exp.base(), var_map)
  
		ptr_check = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(ptr_check, obj_base, "&", IRConstant(1)))
  
		ok_ptr_label = self.new_label("ok_ptr")
		fail_label = self.new_label("not_a_pointer")

		fail_block = BasicBlock(fail_label)
		fail_block.setControlTransfer(IRFail("NotAPointer"))

		self._current_block.setControlTransfer(IRConditional(ptr_check, fail_label, ok_ptr_label))
		self._current_function.addBlock(self._current_block)
		self._current_function.addBlock(fail_block)
  
		ok_block = BasicBlock(ok_ptr_label)
		self._current_block = ok_block

		field_map_ptr_addr = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(field_map_ptr_addr, obj_base, "+", IRConstant(8)))
		
		field_map_ptr = self.new_tmp()
		self._current_block.addStatement(IRLoad(field_map_ptr, field_map_ptr_addr))
		
		field_name = exp.field_name()
		field_base = exp.base()
		
		if type(field_base) == ThisExpr:
			cur_class = self._current_class
		elif type(field_base) == Variable:
			cur_class = self._class_mappings.get(field_base.name(), None)
		else:
			raise Exception("Cannot determine class for field read")
		
		if not cur_class:
			raise Exception("Object base is not initialized to a class:", field_name)

		field_id = self._field_ids.get((cur_class, field_name), None)
		if field_id is None:
			raise Exception("Invalid field name:", field_name)
		
		field_offset = self.new_tmp()
		self._current_block.addStatement(IRGelElt(field_offset, field_map_ptr, IRConstant(field_id)))
		
		field_exists_label = self.new_label("field_exists")
		no_field_label = self.new_label("bad_field")
		
		no_field_block = BasicBlock(no_field_label)
		no_field_block.setControlTransfer(IRFail("NoSuchField"))
		
		self._current_block.setControlTransfer(IRConditional(field_offset, field_exists_label, no_field_label))
		self._current_function.addBlock(self._current_block)
		self._current_function.addBlock(no_field_block)
		
		field_exists_block = BasicBlock(field_exists_label)
		self._current_block = field_exists_block
		
		field_value = self.new_tmp()
		self._current_block.addStatement(IRGelElt(field_value, obj_base, field_offset))
		self._current_function.addBlock(self._current_block)
		return field_value
  
	def generateMethodCall(self, exp: MethodCall, var_map: dict[str, IRVariable]):
		receiver = self.generateExpression(exp.base(), var_map)

		ptr_check = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(ptr_check, receiver, "&", IRConstant(1)))
		ok_ptr_label = self.new_label("ok_pointer_call")
		fail_label = self.new_label("not_a_pointer")

		fail_block = BasicBlock(fail_label)
		fail_block.setControlTransfer(IRFail("NotAPointer"))
		self._current_block.setControlTransfer(IRConditional(ptr_check, fail_label, ok_ptr_label))
		self._current_function.addBlock(self._current_block)
		self._current_function.addBlock(fail_block)

		ok_block = BasicBlock(ok_ptr_label)
		self._current_block = ok_block
  
		vtable_ptr = self.new_tmp()
		self._current_block.addStatement(IRLoad(vtable_ptr, receiver))
		
		method_name = exp.name()
		receiver_base = exp.base()
		
		if type(receiver_base) == ThisExpr:
			cur_class = self._current_class
		elif type(receiver_base) == Variable:
			cur_class = self._class_mappings.get(receiver_base.name(), None)
		else:
			raise Exception("Cannot determine class for method call")
		
		if not cur_class:
			raise Exception("Object base is not initialized to a class:", method_name)
		
		method_id = self._method_ids.get((cur_class, method_name), None)
		if method_id is None:
			raise Exception("Invalid method name:", method_name)
		
		method_addr = self.new_tmp()
		self._current_block.addStatement(IRGelElt(method_addr, vtable_ptr, IRConstant(method_id)))

		arg_vals = []
		for arg_exp in exp.args():
			arg_vals.append(self.generateExpression(arg_exp, var_map))
		res = self.new_tmp()
		self._current_block.addStatement(IRCall(res, method_addr, receiver, arg_vals))
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
		self._current_block.addStatement(IRBinaryOp(ptr_check, obj, "&", IRConstant(1)))
  
		ok_ptr_label = self.new_label("ok_pointer")
		fail_label = self.new_label("not_a_pointer")
		fail_block = BasicBlock(fail_label)
		fail_block.setControlTransfer(IRFail("NotAPointer"))
		self._current_block.setControlTransfer(IRConditional(ptr_check, fail_label, ok_ptr_label))

		self._current_function.addBlock(self._current_block)
		self._current_function.addBlock(fail_block)
  
		ok_ptr_block = BasicBlock(ok_ptr_label)
		self._current_block = ok_ptr_block

		field_name = field_read.field_name()
		field_base = field_read.base()
		if type(field_base) == ThisExpr:
			cur_class = self._current_class
		elif type(field_base) == Variable:
			cur_class = self._class_mappings.get(field_base.name(), None)
		else:
			raise Exception("Cannot determine class for field update")

		if not cur_class:
			raise Exception("Object base is not initialized to a class:", field_name)

		field_id = self._field_ids.get((cur_class, field_name), None)
		if field_id is None:
			raise Exception("Invalid field name:", field_name)
		
		addr_tmp = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(addr_tmp, obj, "+", IRConstant(8)))
		load_tmp = self.new_tmp()
		self._current_block.addStatement(IRLoad(load_tmp, addr_tmp))
		field_lookup = self.new_tmp()
		self._current_block.addStatement(IRGelElt(field_lookup, load_tmp, IRConstant(field_id)))
		
		store_works_label = self.new_label("store_works")
		bad_field_label = self.new_label("bad_field")
		bad_field_block = BasicBlock(bad_field_label)
		bad_field_block.addStatement(IRFail("NoSuchField"))
		self._current_block.setControlTransfer(IRConditional(field_lookup, store_works_label, bad_field_label))
		self._current_function.addBlock(self._current_block)
		self._current_function.addBlock(bad_field_block)

		store_works_block = BasicBlock(store_works_label)
		self._current_block = store_works_block
		self._current_block.addStatement(IRSetElt(obj, field_lookup, value))

	def generateIfStatement(self, statement: IfStatement, var_map: dict[str, IRVariable]):
		condition = self.generateExpression(statement.condition(), var_map)

		then_label = self.new_label("then")
		else_label = self.new_label("else")
		merge_label = self.new_label("merge")
  
		self._current_block.setControlTransfer(IRConditional(condition, then_label, else_label))
		self._current_function.addBlock(self._current_block)

		then_block = BasicBlock(then_label)
		self._current_block = then_block
		for s in statement.if_statements():
			self.generateStatement(s, var_map)
		if not self._current_block.control():
			self._current_block.setControlTransfer(IRJump(merge_label))
		self._current_function.addBlock(self._current_block)
  
		else_block = BasicBlock(else_label)
		self._current_block = else_block
		for s in statement.else_statements():
			self.generateStatement(s, var_map)
		if not self._current_block.control():
			self._current_block.setControlTransfer(IRJump(merge_label))
		self._current_function.addBlock(self._current_block)
  
		merge_block = BasicBlock(merge_label)
		self._current_block = merge_block
  
	def generateIfOnlyStatement(self, statement: IfOnlyStatement, var_map: dict[str, IRVariable]):
		condition = self.generateExpression(statement.condition(), var_map)

		then_label = self.new_label("then")
		merge_label = self.new_label("merge")
  
		self._current_block.setControlTransfer(IRConditional(condition, then_label, merge_label))
		self._current_function.addBlock(self._current_block)
  
		then_block = BasicBlock(then_label)
		self._current_block = then_block
		for s in statement.statements():
			self.generateStatement(s, var_map)
		if not self._current_block.control():
			self._current_block.setControlTransfer(IRJump(merge_label))
		self._current_function.addBlock(self._current_block)

		merge_block = BasicBlock(merge_label)
		self._current_block = merge_block
  
	def generateWhileStatement(self, statement: WhileStatement, var_map: dict[str, IRVariable]):
		top_label = self.new_label("loop_top")
		body_label = self.new_label("loop_body")
		end_label = self.new_label("loop_end")
  
		self._current_block.setControlTransfer(IRJump(top_label))
		self._current_function.addBlock(self._current_block)
  
		top_block = BasicBlock(top_label)
		self._current_block = top_block
		condition = self.generateExpression(statement.condition(), var_map) 
		self._current_block.setControlTransfer(IRConditional(condition, body_label, end_label))
		self._current_function.addBlock(self._current_block)
  
		body_block = BasicBlock(body_label)
		self._current_block = body_block
		for s in statement.statements():
			self.generateStatement(s, var_map)
		if not self._current_block.control():
			self._current_block.setControlTransfer(IRJump(top_label))
		self._current_function.addBlock(self._current_block)
    
		end_block = BasicBlock(end_label)
		self._current_block = end_block
	
	def generateStatement(self, statement: Statement, var_map: dict[str, IRVariable]) -> IRStatement:
		if type(statement) == Assignment:
			name = statement.variable().name()
			if not var_map.get(name):
				raise Exception(f"Assignment to undefined variable: {name}")
			
			if type(statement.expression()) == ClassRef:
				self._class_mappings[name] = statement.expression().name()
    
			res = self.generateExpression(statement.expression(), var_map)
			self._current_block.addStatement(IRAssignment(var_map[name], res))
		elif type(statement) == UnderscoreAssignment:
			self.generateExpression(statement.expression(), var_map)
		elif type(statement) == FieldUpdate:
			self.generateFieldUpdate(statement, var_map)
		elif type(statement) == PrintStatement:
			res = self.generateExpression(statement.expression(), var_map)
			untagged = self.new_tmp()
			self._current_block.addStatement(IRBinaryOp(untagged, res, ">>", IRConstant(1)))
			self._current_block.addStatement(IRPrint(untagged))
			retagged_res = self.new_tmp()
			self._current_block.addStatement(IRBinaryOp(retagged_res, untagged, "<<", IRConstant(1)))
			retagged = self.new_tmp()
			self._current_block.addStatement(IRBinaryOp(retagged, retagged_res, "|", IRConstant(1)))
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

		cur_method = IRFunction(method_def.name(), var_map)
		self._current_function = cur_method
		entry_block = BasicBlock(mlabel, method_params)
		self._current_block = entry_block
		self._class_mappings = {}
		for stmt in method_def.statements():
			self.generateStatement(stmt, var_map)

		if not self._current_block.control():
			self._current_block.setControlTransfer(IRReturn(IRConstant(0)))
		
		self._current_function.addBlock(self._current_block)
		self._program.addFunction(self._current_function)
  
	def genMainMethod(self, main_method: MainMethod):
		main_block = BasicBlock("main")
		self._current_block = main_block

		var_map = {}
		for l in main_method.vars():
			if var_map.get(l.name()):
				raise Exception("Variable already defined:", l.name())
			var_map[l.name()] = IRVariable(l.name())

		main_function = IRFunction("main", var_map)
		self._current_function = main_function
		self._current_class = None
		self._class_mappings = {}
		for stmt in main_method.statements():
			self.generateStatement(stmt, var_map)

		if not self._current_block.control():
			self._current_block.setControlTransfer(IRReturn(IRConstant(0)))
		
		self._current_function.addBlock(self._current_block)
		self._program.addFunction(self._current_function)

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
			self._current_class = cls.name()
			for m in cls.methods():
				self.genMethod(cls.name(), m)
	
		self.genMainMethod(main_method)
		return self._program

class SSAVariable:
    def __init__(self, base_name: str):
        self._base_name = base_name
        self._version = 0
    
    def name(self) -> str:
        return self._base_name
    
    def getVersion(self) -> int:
        return self._version
    
    def nextName(self):
        return f"{self._base_name}{self._version}"
    
    def incVersion(self) -> int:
        self._version += 1
        
class Optimizer:
	def __init__(self, ir_program: IRProgram):
		self._ir_program = ir_program

	def replaceVariableUses(self, value: IRValue, current_versions: dict[str, IRVariable]):
		if type(value) == IRVariable:
			var_name = value.name()
			if var_name in current_versions:
				return current_versions[var_name]
			return value
		elif type(value) == IRBinaryOp:
			if type(value.lhs()) == IRVariable:
				lhs_name = value.lhs().name()
				if lhs_name in current_versions:
					value.replaceLhs(current_versions[lhs_name])
			if type(value.rhs()) == IRVariable:
				rhs_name = value.rhs().name()
				if rhs_name in current_versions:
					value.replaceRhs(current_versions[rhs_name])
		return value

	def replaceWithSSA(self, block: BasicBlock, ssa_vars: dict[str, SSAVariable], initial_versions: dict[str, IRVariable] = None):
		block_last_versions = {}
		current_versions = initial_versions.copy() if initial_versions else {}

		for s in block.statements():
			if type(s) == IRPhi:
				phi_var = s.name()
				var_base_name = phi_var.name()
				i = len(var_base_name) - 1
				while i >= 0 and var_base_name[i].isdigit():
					i -= 1
				base_name = var_base_name[:i+1]
				current_versions[base_name] = phi_var
				block_last_versions[base_name] = phi_var
    
		for s in block.statements():
			if type(s) == IRPhi:
				continue

			if type(s) == IRAssignment:
				if type(s.value()) == IRVariable:
					var_name = s.value().name()
					if var_name in current_versions:
						s.replaceValue(current_versions[var_name])
				elif type(s.value()) == IRBinaryOp:
					self.replaceVariableUses(s.value(), current_versions)
      
				if not s.isSSA():
					var = s.name()
					var_name = var.name()
					ssa_name = ssa_vars[var.name()].nextName()
					ssa_vars[var.name()].incVersion()
					next_var = IRVariable(ssa_name)
					s.replaceName(next_var)
					current_versions[var_name] = next_var
					block_last_versions[var_name] = next_var
			elif type(s) == IRBinaryOp:
				self.replaceVariableUses(s, current_versions)
			elif type(s) == IRPrint:
				if type(s.print_var()) == IRVariable:
					var_name = s.print_var().name()
					if var_name in current_versions:
						s.replacePrintVal(current_versions[var_name])
			elif type(s) == IRCall:
				if type(s.code_addr()) == IRVariable:
					var_name = s.code_addr().name()
					if var_name in current_versions:
						s.replaceCodeAddr(current_versions[var_name])
				if type(s.receiver()) == IRVariable:
					var_name = s.receiver().name()
					if var_name in current_versions:
						s.replaceReceiver(current_versions[var_name])
				for i, arg in enumerate(s.args()):
					if type(arg) == IRVariable:
						var_name = arg.name()
						if var_name in current_versions:
							s.replaceArg(current_versions[var_name], i)
			elif type(s) == IRLoad:
				if type(s.base()) == IRVariable:
					var_name = s.base().name()
					if var_name in current_versions:
						s.replaceBase(current_versions[var_name])

			elif type(s) == IRStore:
				if type(s.base()) == IRVariable:
					var_name = s.base().name()
					if var_name in current_versions:
						s.replaceBase(current_versions[var_name])
				if type(s.val()) == IRVariable:
					var_name = s.val().name()
					if var_name in current_versions:
						s.replaceVal(current_versions[var_name])
			
			elif type(s) == IRGelElt:
				if type(s.arr_pointer()) == IRVariable:
					var_name = s.arr_pointer().name()
					if var_name in current_versions:
						s.replaceArrPointer(current_versions[var_name])
				if type(s.ind()) == IRVariable:
					var_name = s.ind().name()
					if var_name in current_versions:
						s.replaceInd(current_versions[var_name])
			
			elif type(s) == IRSetElt:
				if type(s.arr_pointer()) == IRVariable:
					var_name = s.arr_pointer().name()
					if var_name in current_versions:
						s.replaceArrPointer(current_versions[var_name])
				if type(s.ind()) == IRVariable:
					var_name = s.ind().name()
					if var_name in current_versions:
						s.replaceInd(current_versions[var_name])
				if type(s.val()) == IRVariable:
					var_name = s.val().name()
					if var_name in current_versions:
						s.replaceVal(current_versions[var_name])
		
		if block.control():
			if type(block.control()) == IRReturn:
				if type(block.control().return_val()) == IRVariable:
					var_name = block.control().return_val().name()
					if var_name in current_versions:
						block.control().replaceReturnVal(current_versions[var_name])
			
			elif type(block.control()) == IRConditional:
				if type(block.control().condition()) == IRVariable:
					var_name = block.control().condition().name()
					if var_name in current_versions:
						block.control().replaceCondition(current_versions[var_name])
		return current_versions

	def convertToSSA(self):
		for f in self._ir_program.functions():
			block_to_id = {}
			prio_blocks = {}
			for i, block in enumerate(f.blocks()):
				block_to_id[block.name()] = i
				prio_blocks[block.name()] = []
			
			for block in f.blocks():
				successors = block.getControlLabels()
				for s in successors:
					prio_blocks[s].append(block.name())

			function_vars = f.getNonTempVariables()
			ssa_vars = {}
			for var in function_vars:
				ssa_vars[var.name()] = SSAVariable(var.name())
    
			blocks_with_phis = {}
			for block_name, pred_list in prio_blocks.items():
				if len(pred_list) > 1:
					blocks_with_phis[block_name] = {}
					block_id = block_to_id[block_name]
					b = f.blocks()[block_id]
     
					for v in function_vars:
						ssa_name = ssa_vars[v.name()].nextName()
						ssa_vars[v.name()].incVersion()
						phi_var = IRVariable(ssa_name)
						phi = IRPhi(phi_var, [])
						b.insertPhi(phi)
						blocks_with_phis[block_name][v.name()] = phi

			block_last_versions = {}
			processed = set()
			worklist = []
			if f.blocks():
				worklist.append(f.blocks()[0].name())
			
			# Process blocks in worklist order
			while worklist:
				block_name = worklist.pop(0)
				if block_name in processed:
					continue
				
				block_id = block_to_id.get(block_name)
				if block_id is None:
					continue
					
				block = f.blocks()[block_id]
				
				# Initialize current_versions based on predecessors
				pred_list = prio_blocks[block_name]
				initial_versions = {}
				
				if len(pred_list) == 1:
					# Single predecessor - inherit its versions
					pred_name = pred_list[0]
					if pred_name in block_last_versions:
						initial_versions = block_last_versions[pred_name].copy()
				# For multiple predecessors, phi nodes handle it, start empty
				
				last_versions = self.replaceWithSSA(block, ssa_vars, initial_versions)
				block_last_versions[block.name()] = last_versions
				processed.add(block_name)
				
				# Add successors to worklist
				successors = block.getControlLabels()
				if successors:
					for succ in successors:
						if succ not in processed:
							worklist.append(succ)
    
			for block_name, phi_dict in blocks_with_phis.items():
				pred_list = prio_blocks[block_name]
				for var_name, phi in phi_dict.items():
					for pred_name in pred_list:
						if var_name in block_last_versions.get(pred_name, {}):
							pred_var = block_last_versions[pred_name][var_name]
						else:
							pred_var = IRVariable(var_name)
						phi.prior_blocks().append((pred_name, pred_var))
      
	def checkBinaryOp(self, op: IRBinaryOp):
		valid_ops = ["+", "-", "*", "/"]
		if type(op.lhs()) == IRConstant and type(op.rhs()) == IRConstant and op.op() in valid_ops:
			return True
		else:
			return False

	def checkForConstantArithmetic(self, statement: IRStatement):
		if type(statement) == IRAssignment:
			if type(statement.value()) == IRBinaryOp:
				if self.checkBinaryOp(statement.value()):
					lhs_val = statement.value().lhs() >> 1
					rhs_val = statement.value().rhs() >> 1
					if statement.value().op() == "+":
						res = lhs_val + rhs_val
					elif statement.value().op() == "-":
						res = lhs_val - rhs_val
					elif statement.value().op() == "*":
						res = lhs_val * rhs_val
					elif statement.value().op() == "/":
						res = lhs_val // rhs_val 
					else:
						return
					statement.replaceValue(IRConstant((res << 1) | 1))
					
	def removeConstantArithmetic(self):
		functions = self._ir_program.functions()
		for f in functions:
			for block in f.blocks():
				for statement in block.statements():
					self.checkForConstantArithmetic(statement)
        
	def getProgram(self) -> IRProgram:
		return self._ir_program
    
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
		program = cfg_generator.convertAstToIr()
		optimizer = Optimizer(program)
		optimizer.convertToSSA()
		optimizer.removeConstantArithmetic()
		print(optimizer.getProgram())
	else:
		raise Exception("Invalid usage")
  
