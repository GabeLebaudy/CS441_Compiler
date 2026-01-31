from ir_components import *
from optimizer_components import *

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
			
			while worklist:
				block_name = worklist.pop(0)
				if block_name in processed:
					continue
				
				block_id = block_to_id.get(block_name)
				if block_id is None:
					continue
					
				block = f.blocks()[block_id]				
				pred_list = prio_blocks[block_name]
				initial_versions = {}
				
				if len(pred_list) == 1:
					pred_name = pred_list[0]
					if pred_name in block_last_versions:
						initial_versions = block_last_versions[pred_name].copy()
				
				last_versions = self.replaceWithSSA(block, ssa_vars, initial_versions)
				block_last_versions[block.name()] = last_versions
				processed.add(block_name)
				
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
