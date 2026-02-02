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
		self._class_mappings = {} 

		self._class_info = {}
		self._field_ids = {}
		self._method_ids = {}

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
			if not self._opts.noOpt and type(lhs) == IRConstant and type(rhs) == IRConstant:
				lhs_val = lhs.value() >> 1
				rhs_val = rhs.value() >> 1
				if op_str == "+":
					res_val = lhs_val + rhs_val
				elif op_str == "-":
					res_val = lhs_val + rhs_val
				elif op_str == "*":
					res_val = lhs_val * rhs_val
				else:
					res_val = lhs_val // rhs_val
				
				res_val = (res_val << 1) | 1
				self._current_block.addStatement(IRAssignment(res, IRConstant(res_val)))
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
		self._current_block.addStatement(IRAlloc(obj_ptr, obj_size))

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
