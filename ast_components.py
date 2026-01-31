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