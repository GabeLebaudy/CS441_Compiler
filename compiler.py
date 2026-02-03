import os
import argparse
from parser import Parser, Tokenizer
from cfg_generator import CFGGenerator
from optimizer import Optimizer

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-printCFG", dest="printCfg", action="store_true", help="print the AST Nodes after parsing")
	parser.add_argument("-ssa_type", dest="ssa_type", help="Options: max(maximally suboptimal SSA), opt(optimized ssa), or none")
	parser.add_argument("-const_arithmetic", dest="const_arith", action="store_true", help="Flag for optimizing out constant arithmetic")
	parser.add_argument("-vn", dest="vn", action="store_true", help="Flag for running value numbering for local blocks")
	parser.add_argument("filename", help="input file to compile")
	args = parser.parse_args()

	str_text = ""
	if not args.filename:
		raise Exception("File to compile required")

	if not os.path.exists(args.filename):
		raise Exception(f"Error, file: {args.filename} does not exist")

	if args.ssa_type != "max" and args.ssa_type != "opt" and args.ssa_type != "none":
		raise Exception("Error: Must choose a valid ssa type (max, opt, none)")

	if args.ssa_type == "none" and args.vn:
		raise Exception("Cannot run value numbering without SSA type")

	with open(args.filename, 'r') as f:
		str_text = "".join(f.readlines())

	file_parser = Parser(Tokenizer(str_text))
	ast_nodes = file_parser.parseFile()
	if args.printCfg:
		for node in ast_nodes:
			print(node)

	cfg_generator = CFGGenerator(ast_nodes, args)
	program = cfg_generator.convertAstToIr() #Pass in constant arithmetic optimizer flag (needs to be done in here)
	optimizer = Optimizer(program)
	if args.ssa_type == "max":
		optimizer.convertToSSA()
	elif args.ssa_type == "opt":
		optimizer.getOptimizedSSA()
	
	if args.vn:
		optimizer.applyValueNumbering()
  
	print(optimizer.getProgram())
