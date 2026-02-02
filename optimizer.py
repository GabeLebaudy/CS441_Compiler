from ir_components import *
from optimizer_components import *

class Optimizer:
	def __init__(self, ir_program: IRProgram):
		self._ir_program = ir_program
		self._predecessor_table = {} #str(function name) => predecessor table
		self._blocknames_to_ids = {} #str(function name) => name to ID mapping
		self._dominance_tree_table = {} #str(function name) => dominance value tbale
		self._immediate_dominator_table = {} #str(function name) => Immediate dominator dict
		self._dominance_frontier_table = {} #str(function name) => dominance frontier table

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

	def generatePredecessorTree(self, function: IRFunction):
		predecessor_tree = {} #int (block_id) => set(int) (predecessor_ids)
		self._blocknames_to_ids[function.name()] = {} #str (block_name) => int(block_id)
		for i, block in enumerate(function.blocks()):
			predecessor_tree[i] = set()
			self._blocknames_to_ids[function.name()][block.name()] = i

		for i, block in enumerate(function.blocks()):
			ctrl = block.control()
			if type(ctrl) == IRJump:
				succ_id = self._blocknames_to_ids[function.name()].get(ctrl.name(), None)
				if not succ_id:
					raise Exception("IR Jump has label for unknown block", ctrl)
				predecessor_tree[succ_id].add(i)
			elif type(ctrl) == IRConditional:
				left_succ_id = self._blocknames_to_ids[function.name()].get(ctrl.if_name(), None)
				if not left_succ_id:
					raise Exception("IR Conditional has label for positive condition to unknown block", ctrl)
				predecessor_tree[left_succ_id].add(i)
				right_succ_id = self._blocknames_to_ids[function.name()].get(ctrl.else_name(), None)
				if not right_succ_id:
					raise Exception("IR Conditional has label for negative condition to unknown block", ctrl)
				predecessor_tree[right_succ_id].add(i)
    
		return predecessor_tree

	def getPredecessorTrees(self):
		for f in self._ir_program.functions():
			self._predecessor_table[f.name()] = self.generatePredecessorTree(f)

	def genDominatorTree(self, function: IRFunction) -> dict[int, set[int]]:
		dominator_tree = {} #int => set(int)
		num_blocks = len(function.blocks())
		dominator_tree[0] = {0}
		for i in range(1, num_blocks):
			dominator_tree[i] = set(range(num_blocks))
   
		changed = True
		while(changed):
			changed = False
			for i in range(1, num_blocks):
				tmp = set([i])
				pred_block_ids = list(self._predecessor_table[function.name()][i])
				if len(pred_block_ids) == 1:
					tmp = tmp.union(dominator_tree[pred_block_ids[0]])
				elif len(pred_block_ids) > 1:
					set_intersection = dominator_tree[pred_block_ids[0]]
					for j in range(1, len(pred_block_ids)):
						set_intersection = set_intersection.intersection(dominator_tree[pred_block_ids[j]])
					tmp = tmp.union(set_intersection)
     
				if tmp != dominator_tree[i]:
					dominator_tree[i] = tmp
					changed = True
     
		return dominator_tree

	def getDominanceTrees(self):
		for f in self._ir_program.functions():
			self._dominance_tree_table[f.name()] = self.genDominatorTree(f)

	def generateImmediateDominator(self, dominance_tree: dict[int, set[int]]) -> dict[int, int]:
		idom = {}
		for node, dominators in dominance_tree.items():
			if node == 0:
				continue
			
   
			candidates = dominators - {node}
			idom[node] = max(candidates, key=lambda d: len(dominance_tree[d]))
		return idom

	def getImmediateDominators(self):
		for f in self._ir_program.functions():
			self._immediate_dominator_table[f.name()] = self.generateImmediateDominator(self._dominance_tree_table[f.name()])

	def generateDominanceFrontier(self, function: IRFunction):
		dominance_fronter = {}
		for i in range(len(function.blocks())):
			dominance_fronter[i] = set()
   
		for i in range(len(function.blocks())):
			block_preds = list(self._predecessor_table[function.name()][i])
			if len(block_preds) > 1:
				imm_dominator = self._immediate_dominator_table[function.name()][i]
				for pred_id in block_preds:
					runner = pred_id
					while runner != imm_dominator:
						dominance_fronter[runner] = dominance_fronter[runner].union(set([i]))
						runner = self._immediate_dominator_table[function.name()][runner]
		
		return dominance_fronter 

	def getDominanceFrontiers(self):
		for f in self._ir_program.functions():
			self._dominance_frontier_table[f.name()] = self.generateDominanceFrontier(f)

	def convertFunctionToSSA(self, function: IRFunction):
		globals = set()
		blocks = {}
		
		for block in function.blocks():
			varkill = set()
			for statement in block.statements():
				if type(statement) == IRBinaryOp:
					if type(statement.lhs()) == IRVariable:
						lhs_name = statement.lhs().name()
						if lhs_name not in varkill:
							globals.add(lhs_name)
					
					if type(statement.rhs()) == IRVariable:
						rhs_name = statement.rhs().name()
						if rhs_name not in varkill:
							globals.add(rhs_name)
					
					def_name = statement.name().name()
					varkill.add(def_name)
					if def_name not in blocks:
						blocks[def_name] = set()
					blocks[def_name].add(block)
				
				elif type(statement) == IRAssignment:
					if type(statement.value()) == IRVariable:
						val_name = statement.value().name()
						if val_name not in varkill:
							globals.add(val_name)
					elif type(statement.value()) == IRBinaryOp:
						if type(statement.value().lhs()) == IRVariable:
							lhs_name = statement.value().lhs().name()
							if lhs_name not in varkill:
								globals.add(lhs_name)
						if type(statement.value().rhs()) == IRVariable:
							rhs_name = statement.value().rhs().name()
							if rhs_name not in varkill:
								globals.add(rhs_name)
					
					def_name = statement.name().name()
					varkill.add(def_name)
					if def_name not in blocks:
						blocks[def_name] = set()
					blocks[def_name].add(block)

			if block.control():
				if type(block.control()) == IRConditional:
					cond_name = block.control().condition().name()
					if cond_name not in varkill:
						globals.add(cond_name)
				elif type(block.control()) == IRReturn:
					if type(block.control().return_val()) == IRVariable:
						ret_name = block.control().return_val().name()
						if ret_name not in varkill:
							globals.add(ret_name)
		
		for var_name in globals:
			if var_name not in blocks:
				continue
				
			worklist = blocks[var_name].copy()
			processed = set()
			while worklist:
				block = worklist.pop()
				block_id = self._blocknames_to_ids[function.name()][block.name()]
				if block_id in processed:
					continue
 
				processed.add(block_id)
				dominance_frontier_block_ids = self._dominance_frontier_table[function.name()][block_id]
				for df_id in dominance_frontier_block_ids:
					df_block = function.blocks()[df_id]
					phi_var = IRVariable(var_name)
					if not df_block.hasPhi(phi_var):
						phi = IRPhi(phi_var, [])
						df_block.insertPhi(phi)
						worklist.add(df_block)

	def renameVariables(self, function: IRFunction):
		counters = {}  # var_name => next version number
		stacks = {}    # var_name => stack of current versions
		
		# Initialize for all variables that appear in the function
		for block in function.blocks():
			for statement in block.statements():
				if type(statement) == IRPhi:
					var_name = statement.name().name()
					if var_name not in counters:
						counters[var_name] = 0
						stacks[var_name] = []
				elif hasattr(statement, 'name') and callable(statement.name):
					if type(statement.name()) == IRVariable and not statement.name().isTemp():
						var_name = statement.name().name()
						if var_name not in counters:
							counters[var_name] = 0
							stacks[var_name] = []
		
		# Build dominator tree children mapping
		idom = self._immediate_dominator_table[function.name()]
		dom_children = {}  # block_id => list of child block_ids
		for block_id in range(len(function.blocks())):
			dom_children[block_id] = []
		
		for child_id, parent_id in idom.items():
			dom_children[parent_id].append(child_id)
		
		# Start renaming from entry block (block 0) using iterative approach with stack
		# Stack contains: (block_id, phase) where phase is 'process' or 'cleanup'
		work_stack = [(0, 'process', [])]
		
		while work_stack:
			block_id, phase, pushed = work_stack.pop()
			
			if phase == 'cleanup':
				# Pop all versions we pushed
				for var_name in pushed:
					stacks[var_name].pop()
				continue
			
			# phase == 'process'
			block = function.blocks()[block_id]
			pushed = []  # Track what we pushed for cleanup
			
			# Process phi functions first
			for statement in block.statements():
				if type(statement) != IRPhi:
					break  # Phis are at the beginning
				
				var_name = statement.name().name()
				i = counters[var_name]
				counters[var_name] += 1
				
				# Rename the phi result
				new_var = IRVariable(f"{var_name}{i}")
				statement._name = new_var
				
				stacks[var_name].append(i)
				pushed.append(var_name)
			
			# Process regular statements
			for statement in block.statements():
				if type(statement) == IRPhi:
					continue
				
				# Replace uses with current versions
				if type(statement) == IRBinaryOp:
					if type(statement.lhs()) == IRVariable:
						lhs_name = statement.lhs().name()
						if lhs_name in stacks and stacks[lhs_name]:
							version = stacks[lhs_name][-1]
							statement.replaceLhs(IRVariable(f"{lhs_name}{version}"))
					
					if type(statement.rhs()) == IRVariable:
						rhs_name = statement.rhs().name()
						if rhs_name in stacks and stacks[rhs_name]:
							version = stacks[rhs_name][-1]
							statement.replaceRhs(IRVariable(f"{rhs_name}{version}"))
					
					# Create new version for definition
					def_name = statement.name().name()
					if def_name in counters:
						i = counters[def_name]
						counters[def_name] += 1
						new_var = IRVariable(f"{def_name}{i}")
						statement._name = new_var
						stacks[def_name].append(i)
						pushed.append(def_name)
				
				elif type(statement) == IRAssignment:
					# Replace uses
					if type(statement.value()) == IRVariable:
						val_name = statement.value().name()
						if val_name in stacks and stacks[val_name]:
							version = stacks[val_name][-1]
							statement.replaceValue(IRVariable(f"{val_name}{version}"))
				
					# Create new version for definition
					def_name = statement.name().name()
					if def_name in counters:
						i = counters[def_name]
						counters[def_name] += 1
						new_var = IRVariable(f"{def_name}{i}")
						statement.replaceName(new_var)
						stacks[def_name].append(i)
						pushed.append(def_name)
      
				elif type(statement) == IRCall:
					if type(statement.name()) == IRVariable:
						var_name = statement.name().name()
						if var_name in stacks and stacks[var_name]:
							version = stacks[var_name][-1]
							statement.replaceName(IRVariable(f"{var_name}{version}"))

					if type(statement.code_addr()) == IRVariable:
						code_name = statement.code_addr().name()
						if code_name in stacks and stacks[code_name]:
							version = stacks[code_name][-1]
							statement.replaceCodeAddr(IRVariable(f"{code_name}{version}"))

					if type(statement.receiver()) == IRVariable:
						recv_name = statement.receiver().name()
						if recv_name in stacks and stacks[recv_name]:
							version = stacks[recv_name][-1]
							statement.replaceReceiver(IRVariable(f"{recv_name}{version}"))
       
					for i, arg in enumerate(statement.args()):
						if type(arg) == IRVariable:
							arg_name = arg.name()
							if arg_name in stacks and stacks[arg_name]:
								version = stacks[arg_name][-1]
								statement.replaceArg(IRVariable(f"{arg_name}{version}", i))
        
					def_name = statement.name().name()
					if def_name in counters:
						i = counters[def_name]
						counters[def_name] += 1
						new_var = IRVariable(f"{def_name}{i}")
						statement.replaceName(new_var)
						stacks[def_name].append(i)
						pushed.append(def_name)

				elif type(statement) == IRSetElt:
					if type(statement.arr_pointer()) == IRVariable:
						arr_pointer_name = statement.arr_pointer().name()
						if arr_pointer_name in stacks and stacks[arr_pointer_name]:
							version = stacks[arr_pointer_name][-1]
							statement.replaceArrPointer(IRVariable(f"{arr_pointer_name}{version}"))

					if type(statement.ind()) == IRVariable:
						ind_name = statement.ind().name()
						if ind_name in stacks and stacks[ind_name]:
							version = stacks[arr_pointer_name][-1]
							statement.replaceInd(IRVariable(f"{ind_name}{version}"))

					if type(statement.val()) == IRVariable:
						val_name = statement.val().name()
						if val_name in stacks and stacks[val_name]:
							version = stacks[val_name][-1]
							statement.replaceVal(IRVariable(f"{val_name}{version}"))
       
				elif type(statement) == IRLoad:
					if type(statement.base()) == IRVariable:
						base_name = statement.base().name()
						if base_name in stacks and stacks[base_name]:
							version = stacks[base_name][-1]
							statement.replaceBase(IRVariable(f"{base_name}{version}"))

					def_name = statement.name().name()
					if def_name in counters:
						i = counters[def_name]
						counters[def_name] += 1
						new_var = IRVariable(f"{def_name}{i}")
						statement.replaceName(new_var)
						stacks[def_name].append(i)
						pushed.append(def_name)
      
			# Handle control transfers
			if block.control():
				if type(block.control()) == IRConditional:
					cond = block.control().condition()
					if type(cond) == IRVariable:
						cond_name = cond.name()
						if cond_name in stacks and stacks[cond_name]:
							version = stacks[cond_name][-1]
							block.control().replaceCondition(IRVariable(f"{cond_name}{version}"))
				
				elif type(block.control()) == IRReturn:
					ret_val = block.control().return_val()
					if type(ret_val) == IRVariable:
						ret_name = ret_val.name()
						if ret_name in stacks and stacks[ret_name]:
							version = stacks[ret_name][-1]
							block.control().replaceReturnVal(IRVariable(f"{ret_name}{version}"))
			
			# Fill in phi function arguments in successors
			successors = block.getControlLabels()
			for succ_name in successors:
				succ_id = self._blocknames_to_ids[function.name()][succ_name]
				succ_block = function.blocks()[succ_id]
				
				for statement in succ_block.statements():
					if type(statement) != IRPhi:
						break
					
					var_name = statement.name().name()
					# Extract base name (remove version number)
					base_name = var_name.rstrip('0123456789')
					
					if base_name in stacks and stacks[base_name]:
						version = stacks[base_name][-1]
						phi_arg = IRVariable(f"{base_name}{version}")
					else:
						phi_arg = IRVariable(base_name)
					
					# Add to phi (block_name, variable)
					statement.prior_blocks().append((block.name(), phi_arg))
			
			# Push cleanup onto stack (will execute after children)
			work_stack.append((block_id, 'cleanup', pushed))
			
			# Push children in reverse order so they process in correct order
			if block_id in dom_children:
				for child_id in reversed(dom_children[block_id]):
					work_stack.append((child_id, 'process', []))
					
	def getOptimizedSSA(self):
		self.getPredecessorTrees()
		self.getDominanceTrees()
		self.getImmediateDominators()
		self.getDominanceFrontiers()
		for f in self._ir_program.functions():
			self.convertFunctionToSSA(f)
			self.renameVariables(f)
	
	def valHash(self, vli, vri, op) -> int:
		op_to_val = {
			"+": 0, "-": 1, "*": 2, "/": 3, ">>": 4, "<<": 5, ">": 6, "<": 7, "==": 8, "&": 9, "|": 10 
		}
		return (op_to_val[op] << 32) | (vli << 16) | vri

	def getValueNumber(self, operand, value_number_table, names, nextvn):
		if type(operand) == IRConstant:
			#Avoid collisions by processing variables and constants separately.
			const_key = f"const_{operand.value()}"
			if const_key not in value_number_table:
				value_number_table[const_key] = nextvn
				names[nextvn] = const_key
				nextvn += 1
			return value_number_table[const_key], nextvn
		elif type(operand) == IRVariable:
			var_name = operand.name()
			if var_name not in value_number_table:
				value_number_table[var_name] = nextvn
				names[nextvn] = var_name
				nextvn += 1
			return value_number_table[var_name], nextvn
		else:
			raise Exception("Binary op has invalid component:", operand)

	def applyBlockVN(self, block: BasicBlock):
		value_number_table = {} 
		names = {} 
		nextvn = 0
		
		for i, statement in enumerate(block.statements()):
			if type(statement) != IRBinaryOp:
				continue
			
			vli, nextvn = self.getValueNumber(statement.lhs(), value_number_table, names, nextvn)
			vri, nextvn = self.getValueNumber(statement.rhs(), value_number_table, names, nextvn)
			h = self.valHash(vli, vri, statement.op())
			
			if h in value_number_table:
				existing_vn = value_number_table[h]
				existing_name = names[existing_vn]
				new_stmt = IRAssignment(statement.name(), IRVariable(existing_name))
				block.replaceStatement(i, new_stmt)
				value_number_table[statement.name().name()] = existing_vn
			else:
				names[nextvn] = statement.name().name()
				value_number_table[statement.name().name()] = nextvn
				value_number_table[h] = nextvn
				nextvn += 1
		

	def applyValueNumbering(self):
		for f in self._ir_program.functions():
			for block in f.blocks():
				self.applyBlockVN(block)

	def getProgram(self) -> IRProgram:
		return self._ir_program

