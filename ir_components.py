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
