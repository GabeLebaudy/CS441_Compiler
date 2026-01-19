#!/usr/bin/env python3

import argparse
import sys
import os

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

	def __str__(self) -> str:
		return f"[Constant: value={self._value}]"

class Variable(Expression):
	def __init__(self, name: str):
		super().__init__()
		self._name = name

	def __str__(self) -> str:
		super().__init__()
		return f"[Variable: name={self._name}]"

class BinaryOp(Expression):
	def __init__(self, lhs, op, rhs):
		super().__init__()
		self._lhs = lhs
		self._op = op
		self._rhs = rhs

	def __str__(self) -> str:
		return f"Binary Op: [LHS ={self._lhs}, op={self._op}, RHS={self._rhs}]"

class FieldRead(Expression):
	def __init__(self, base: Expression, field_name: str):
		super().__init__()
		self._base = base
		self._field_name = field_name

	def __str__(self) -> str:
		return f"Field Read: [base={self._base}, field name={self._field_name}]"

class MethodCall(Expression):
	def __init__(self, base, methodname, args):
		super().__init__()
		self._base = base
		self._methodname = methodname
		self._args = args

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
	def __init__(self, name):
		super().__init__()
		self._name = name
  
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
        
    def __str__(self) -> str:
        return f"Assignment: [variable={self._variable} expression={self._expression}]"

class UnderscoreAssignment(Statement):
    def __init__(self, expression: Expression):
        self._exp = expression
    
    def __str__(self) -> str:
        return f"Underscore statement: [expression={self._exp}]"

class FieldUpdate(Statement):
    def __init__(self, field_read: FieldRead, expression: Expression):
        super().__init__()
        self._field_read = field_read
        self._expression = expression
        
    def __str__(self) -> str:
        return f"Field Update: [field read={self._field_read} expression={self._expression}]"

class IfStatement(Statement):
	def __init__(self, condition: Expression, true_statements: list[Statement], else_statements: list[Statement]):
		super().__init__()
		self._condition = condition
		self._true_statements = true_statements
		self._else_statements = else_statements
	
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
        
    def __str__(self) -> str:
        return f"Return statement: [returns {self._exp}]"

class PrintStatement(Statement):
    def __init__(self, exp):
        super().__init__()
        self._exp = exp
        
    def __str__(self) -> str:
        return f"Print statement: [prints {self._exp}]"

class Argument:
    def __init__(self, name: str):
        self._name = name
        
    def __str__(self) -> str:
        return f"Argument: [name={self._name}]"
    
class MethodDefinintion:
	def __init__(self, args: list[Argument], locals: list[Variable], statements: list[Statement]):
		self._args = args
		self._locals = locals
		self._statements = statements
        
	def __str__(self) -> str:
		arguments = " ".join(str(arg) for arg in self._args)
		local_vars = " ".join(str(local) for local in self._locals)
		statements = "\n".join(str(statement) for statement in self._statements)
		return (
				f"Method Definition: [Arguments={arguments}, "
      			f"Local Variables={local_vars}, "
      			f"Statements={statements}]"
		)

class ClassDefinition:
	def __init__(self, name: str, fields: list[Variable], methods: list[MethodDefinintion]):
		self._name = name
		self._fields = fields
		self._methods = methods
    
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

	def __str__(self) -> str:
		var_str = " ".join(str(var) for var in self._vars)
		statements = " ".join(str(statement) for statement in self._statements)
		return f"Main Method: [variables={var_str}, statements={statements}"

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
			return MethodCall(mbase, mname, args)
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
		fields = (Variable(i.name()) for i in field_ids)

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
			margs = (Argument(i.name()) for i in method_identifiers)
			
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
			mlocals = (Variable(i.name()) for i in local_identifiers)
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

			methods.append(MethodDefinintion(margs, mlocals, statements))
			tok = self._tokenizer.next()
   
		if tok != TokenType.RIGHT_BRACKET:
			raise Exception("Expected ']', but got:", tok)

		return ClassDefinition(cname, fields, methods)			
	
	def parseMain(self) -> MainMethod:
		main_tok = self._tokenizer.next()
		if main_tok != TokenType.MAIN:
			raise Exception("Expected main method, got:", main_tok)
		
		with_tok = self._tokenizer.next()
		if with_tok != TokenType.WITH:
			raise Exception ("Expected with, got:", with_tok)
		
		local_identifiers = self.getCommaSepIdentifiers()
		locals = (Variable(i.name()) for i in local_identifiers)
		
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
				print("Parsing Class!")
				class_def = self.parseClass()
				nodes.append(ASTNode(class_def, None))
			elif open_token == TokenType.MAIN:
				print("Parsing main")
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
        return f"%{self._name} = {self._value}" 

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
        return f"{self._name} = {self._lhs} {self._op} {self._rhs}"

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
        return f"{self._name} = call({self._code_addr}, {self._receiver}{args_str})"

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
        return f"{self._name} = phi({prior_block_str})"
    
class IRAlloc(IRStatement):
    def __init__(self, name: IRVariable, value: IRConstant):
        self._name = name
        self._val = value
        
    def name(self) -> IRVariable:
        return self._name
    
    def val(self) -> IRConstant:
        return self._constant
    
    def __str__(self) -> str:
        return f"{self._name} = alloc({self._value})"
    
class IRPrint(IRStatement):
    def __init__(self, print_var: IRValue):
        self._print_var = print_var
        
    def print_var(self) -> IRValue:
        return self._print_var
    
    def __str__(self) -> str:
        return f"print({self._print_var})"
    
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
        return f"{self._name} = getelt({self._arr_pointer}, {self._ind})"

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
        return f"setelt({self._arr_pointer}, {self._ind}, {self._val})"
    
class IRLoad(IRStatement):
    def __init__(self, name: IRVariable, base: IRVariable):
        self._name = name
        self._base = base
        
    def name(self) -> IRVariable:
        return self._name
    
    def base(self) -> IRVariable:
        return self._base
    
    def __str__(self) -> str:
        return f"{self._name} = load({self._base})"

class IRStore(IRStatement):
    def __init__(self, base: IRVariable, val: IRValue):
        self._base = base
        self._val = val
        
    def base(self) -> IRVariable:
        return self._base
    
    def val(self) -> IRValue:
        return self._val
    
    def __str__(self) -> str:
        return f"store({self._base}, {self._val})"

class IRControlTransfer:
    pass

class IRJump(IRControlTransfer):
    def __init__(self, name: str):
        self._name = name
        
    def name(self) -> str:
        return self._name
    
    def __str__(self) -> str:
        return f"jump {self._name}"
    
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
		return f"if {self._condition}, then {self._if_name} else {self._else_name}"

class IRReturn(IRControlTransfer):
    def __init__(self, return_val: IRValue):
        self._return_val = return_val
        
    def return_val(self) -> str:
        return self._return_val
    
    def __str__(self) -> str:
        return f"ret {self._return_val}"
    
class IRFail(IRControlTransfer):
    def __init__(self, fail_reason: str):
        self._fail = fail_reason
        
    def fail(self) -> str:
        return self._fail
    
    def __str__(self) -> str:
        return f"fail {self._fail}"

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
	def __init__(self, globals: list[GlobalArray], blocks: list[BasicBlock]):
		self._globals = globals
		self._blocks = blocks
        
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

	def collectClassInfo(self, class_defs: list[ClassDefinition]):
		pass

	def genVtables(self, class_defs: list[ClassDefinition]):
		pass

	def genMethod(self, method_def: MethodDefinintion):
		pass

	def genMainMethod(self, main_method: MainMethod):
		pass

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
		self.genVtables()
  
		for cls in classes:
			for m in cls.methods():
				self.genMethod(m)
	
		self.genMainMethod(main_method)
		return self._program

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
		for node in ast_nodes:
			print(node)
	else:
		raise Exception("Invalid usage")
  
