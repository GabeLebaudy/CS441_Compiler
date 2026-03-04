from ast_components import *
from ir_components import *

class CFGGenerator:
	def __init__(self, ast_nodes: list[ASTNode], opts):
		self._ast_nodes = ast_nodes
		self._program = IRProgram()
		self._temp_counter = 1
		self._label_counter = 1
		self._current_block = None
		self._current_class = None
		self._current_function = None
		self._current_return_type = None
		self._class_mappings = {} 

		self._class_info = {}
		self._field_ids = {}
		self._method_ids = {}
		self._variable_types = {}
		self._field_types = {}

		self._opts = opts
  
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
				if f.type() != "int":
					if f.type() not in self._class_info:
						raise Exception(f"Field {f} has type of undefined class: {f.type()}")
					self._field_types[(cname, f.name())] = f.type()
     
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

	def computeExpressionType(self, exp) -> str:
		if type(exp) == Constant:
			return 'int'
		elif type(exp) == Variable or type(exp) == NullExpr:
			return exp.type()
		elif type(exp) == BinaryOp:
			lhs_type = self.computeExpressionType(exp.lhs())
			rhs_type = self.computeExpressionType(exp.rhs())
			if lhs_type != 'int' and rhs_type != 'int':
				raise Exception(f"Binary operation cannot compute types {lhs_type} and {rhs_type}")
			return 'int'
		elif type(exp) == FieldRead:
			base_class = self.computeExpressionType(exp.base())
			if base_class not in self._class_info:
				raise Exception("Unknown class name for field read:", base_class)
			
			field_id = self._field_ids.get((base_class, exp.field_name()), None)
			if field_id == None:
				raise Exception("Unknown field name for class:", exp.field_name())

			field_var = self._class_info[base_class]['fields'][field_id]
			return field_var.type()
		elif type(exp) == MethodCall:
			method_base_type = self.computeExpressionType(exp.base())
			if method_base_type not in self._class_info:
				raise Exception("Unknown class for method call:", method_base_type)

			method_name = exp.name()
			method_id = self._method_ids.get((method_base_type, method_name), None)
			if method_id == None:
				raise Exception(f"Unknown method for class {method_base_type}: {method_name}")

			method_def = self._class_info[method_base_type]['methods'][method_id]
			for i, arg in enumerate(exp.args()):
				params = method_def.params()
				if arg.type() != params[i].type():
					raise Exception(f"Method argument {arg} is of type, {arg.type()}, but expected {params[i].type()}")
			return method_def.returnType()
		elif type(exp) == ClassRef:
			return exp.name()
		elif type(exp) == ThisExpr:
			return self._current_class

	def generateBinaryOp(self, exp: BinaryOp, var_map: dict[str, IRVariable]) -> IRValue:
		lhs = self.generateExpression(exp.lhs(), var_map)
		rhs = self.generateExpression(exp.rhs(), var_map)
  
		op_str = exp.op().op()
		res = self.new_tmp()
		if op_str == "<" or op_str == ">":
			self._current_block.addStatement(IRBinaryOp(res, lhs, op_str, rhs))
		else:
			if self._opts.const_arith and type(lhs) == IRConstant and type(rhs) == IRConstant:
				if op_str == "+":
					res_val = lhs.value() + rhs.value()
				elif op_str == "-":
					res_val = lhs.value() + rhs.value()
				elif op_str == "*":
					res_val = lhs.value() * rhs.value()
				else:
					res_val = lhs.value() // rhs.value()
				
				self._current_block.addStatement(IRAssignment(res, IRConstant(res_val)))
			else:
				self._current_block.addStatement(IRBinaryOp(res, lhs, op_str, rhs))
				
		return res

	def generateFieldRead(self, exp: FieldRead, var_map: dict[str, IRVariable]):
		obj_base = self.generateExpression(exp.base(), var_map)

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
		
		field_ptr_addr = self.new_tmp()
		self._current_block.addStatement(IRBinaryOp(field_ptr_addr, obj_base, "+", IRConstant(8 * (field_id + 1))))
		
		field_val = self.new_tmp()
		self._current_block.addStatement(IRLoad(field_val, field_ptr_addr))
		return field_val
	
	def getReceiverClass(self, receiver_base: Expression):
		if type(receiver_base) == ThisExpr:
			return self._current_class
		elif type(receiver_base) == Variable:
			return self._class_mappings.get(receiver_base.name(), None)
		elif type(receiver_base) == FieldRead:
			base_class = self.getReceiverClass(receiver_base.base())
			if base_class is None:
				return None
			field_name = receiver_base.field_name()
			field_type = self._field_types.get((base_class, field_name), None)
			return field_type
		else:
			raise Exception("Cannot determine class for method call")

	def generateMethodCall(self, exp: MethodCall, var_map: dict[str, IRVariable]):
		receiver = self.generateExpression(exp.base(), var_map)
  
		vtable_ptr = self.new_tmp()
		self._current_block.addStatement(IRLoad(vtable_ptr, receiver))
		
		method_name = exp.name()
		receiver_base = exp.base()
		
		cur_class = self.getReceiverClass(receiver_base)
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
		self._current_block.addStatement(IRAlloc(obj_ptr, obj_size))

		vtable_global = IRGlobal(f"vtbl{cname}")
		self._current_block.addStatement(IRStore(obj_ptr, vtable_global))
		return obj_ptr

	def generateExpression(self, exp: Expression, var_map: dict[str, IRVariable]):
		if type(exp) == Constant:
			return IRConstant(exp.value())
		elif type(exp) == Variable:
			if not var_map.get(exp.name()):
				raise Exception("Variable not defined:", exp.name())
			
			return var_map[exp.name()]
		elif type(exp) == ThisExpr:
			if not var_map.get("this"):
				raise Exception("This expression used outside method context")
			
			return var_map.get("this")
		elif type(exp) == NullExpr:
			return IRConstant(0)
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
		self._current_block.addStatement(IRBinaryOp(addr_tmp, obj, "+", IRConstant(8 * (field_id + 1))))
		
		self._current_block.addStatement(IRStore(addr_tmp, value))

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
			
			expr_type = self.computeExpressionType(statement.expression())
			if statement.variable().type() != expr_type:
				raise Exception(f"Error: Assignment of type {expr_type} cannot assign to type {statement.variable().type()}")
			if type(statement.expression()) == ClassRef:
				self._class_mappings[name] = statement.expression().name()
			elif type(statement.expression()) == NullExpr:
				self._class_mappings[name] = statement.expression().type()
    
			res = self.generateExpression(statement.expression(), var_map)
			self._current_block.addStatement(IRAssignment(var_map[name], res))
		elif type(statement) == UnderscoreAssignment:
			self.generateExpression(statement.expression(), var_map)
		elif type(statement) == FieldUpdate:
			field_read_type = self.computeExpressionType(statement.field_read())
			expr_type = self.computeExpressionType(statement.expression())
			if field_read_type != expr_type:
				raise Exception(f"Cannot set field of type {field_read_type} to {expr_type}")

			self.generateFieldUpdate(statement, var_map)
		elif type(statement) == PrintStatement:
			print_expr_type = self.computeExpressionType(statement.expression())
			if print_expr_type != "int":
				raise Exception("Expected type int for print, but got:", print_expr_type)
			res = self.generateExpression(statement.expression(), var_map)
			self._current_block.addStatement(IRPrint(res))
		elif type(statement) == ReturnStatement:
			return_type = self.computeExpressionType(statement.expression())
			if return_type != self._current_return_type:
				raise Exception(f"Expected return type of {self._current_return_type}, but got: {return_type}")

			res = self.generateExpression(statement.expression(), var_map)
			self._current_block.setControlTransfer(IRReturn(res))
		elif type(statement) == IfStatement:
			condition_type = self.computeExpressionType(statement.condition())
			if condition_type != "int":
				raise Exception("Expected type int for If statement condition, but got:", condition_type)

			self.generateIfStatement(statement, var_map)
		elif type(statement) == IfOnlyStatement:
			condition_type = self.computeExpressionType(statement.condition())
			if condition_type != "int":
				raise Exception("Expected type int for If Only statement condition, but got:", condition_type)
			
			self.generateIfOnlyStatement(statement, var_map)
		elif type(statement) == WhileStatement:
			condition_type = self.computeExpressionType(statement.condition())
			if condition_type != "int":
				raise Exception("Expected type int for While statement condition, but got:", condition_type)
			
			self.generateWhileStatement(statement, var_map)

	def assignExpressionVariableTypes(self, exp):
		if type(exp) == Variable:
			if not exp.type():
				exp.setType(self._variable_types[exp.name()])
		elif type(exp) == BinaryOp:
			self.assignExpressionVariableTypes(exp.lhs())
			self.assignExpressionVariableTypes(exp.rhs())
		elif type(exp) == FieldRead:
			self.assignExpressionVariableTypes(exp.base())
		elif type(exp) == MethodCall:
			self.assignExpressionVariableTypes(exp.base())
			for arg in exp.args():
				self.assignExpressionVariableTypes(arg)
		elif type(exp) == Constant or type(exp) == ClassRef or type(exp) == ThisExpr or type(exp) == NullExpr:
			pass #Expressions already have a type, or type is inherent
		else:
			raise Exception("Unknown expression type", type(exp))

	def assignStatementVariableTypes(self, stmt):
		if type(stmt) == Assignment:
			if not stmt.variable().type():
				stmt.variable().setType(self._variable_types[stmt.variable().name()])
			self.assignExpressionVariableTypes(stmt.expression())
		elif type(stmt) == FieldUpdate:
			self.assignExpressionVariableTypes(stmt.field_read())
			self.assignExpressionVariableTypes(stmt.expression())
		elif type(stmt) == IfStatement:
			self.assignExpressionVariableTypes(stmt.condition())
			for if_stmt in stmt.if_statements():
				self.assignStatementVariableTypes(if_stmt)
			for else_stmt in stmt.else_statements():
				self.assignStatementVariableTypes(else_stmt)
		elif type(stmt) == IfOnlyStatement or type(stmt) == WhileStatement:
			self.assignExpressionVariableTypes(stmt.condition())
			for stmt in stmt.statements():
				self.assignStatementVariableTypes(stmt)
		elif type(stmt) == ReturnStatement or type(stmt) == PrintStatement or type(stmt) == UnderscoreAssignment:
			self.assignExpressionVariableTypes(stmt.expression())
		else:
			raise Exception("Unknown statement type.", type(stmt))
		
	def genMethod(self, class_name: str, method_def: MethodDefinintion):
		mlabel = f"{method_def.name()}{class_name}"
		this_param = IRVariable("this")
		self._temp_counter = 1

		var_map = {'this': this_param}
		self._variable_types = {'this': class_name}
		method_params = [this_param]
		for param in method_def.params():
			if var_map.get(param.name()):
				raise Exception("Method parameter already defined:", param.name())

			mparam = IRVariable(param.name())
			var_map[param.name()] = mparam
			self._variable_types[param.name()] = param.type()
			method_params.append(mparam)

		for var in method_def.locals():
			if var_map.get(var.name()):
				raise Exception("Local variable already defined", var.name())
			var_map[var.name()] = IRVariable(var.name())
			self._variable_types[var.name()] = var.type()

		cur_method = IRFunction(method_def.name(), var_map)
		self._current_function = cur_method
		entry_block = BasicBlock(mlabel, method_params)
		self._current_block = entry_block
		self._class_mappings = {}
		self._current_return_type = method_def.returnType()
		for stmt in method_def.statements():
			self.assignStatementVariableTypes(stmt)
			self.generateStatement(stmt, var_map)

		if not self._current_block.control():
			self._current_block.setControlTransfer(IRReturn(IRConstant(0)))
		
		self._current_function.addBlock(self._current_block)
		self._program.addFunction(self._current_function)
  
	def genMainMethod(self, main_method: MainMethod):
		main_block = BasicBlock("main")
		self._current_block = main_block

		var_map = {}
		self._variable_types = {}
		for l in main_method.vars():
			if var_map.get(l.name()):
				raise Exception("Variable already defined:", l.name())
			var_map[l.name()] = IRVariable(l.name())
			self._variable_types[l.name()] = l.type()

		main_function = IRFunction("main", var_map)
		self._current_function = main_function
		self._current_class = None
		self._current_return_type = "int" #Returns 0
		self._class_mappings = {}
		for stmt in main_method.statements():
			self.assignStatementVariableTypes(stmt)
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
