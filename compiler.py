import os
import argparse
from parser import Parser, Tokenizer
from cfg_generator import CFGGenerator
from optimizer import Optimizer

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-printCFG", dest="printCfg", action="store_true", help="print the AST Nodes after parsing")
	parser.add_argument("-noSSA", dest="noSSA", action="store_true", help="Don't run SSA")
	parser.add_argument("-noopt", dest="noOpt", action="store_true", help="Don't optimize output")
	parser.add_argument("filename", help="input file to compile")
	args = parser.parse_args()

	str_text = ""
	if not args.filename:
		raise Exception("File to compile required")

	if not os.path.exists(args.filename):
		raise Exception(f"Error, file: {args.filename} does not exist")

	with open(args.filename, 'r') as f:
		str_text = "".join(f.readlines())

	file_parser = Parser(Tokenizer(str_text))
	ast_nodes = file_parser.parseFile()
	if args.printCfg:
		for node in ast_nodes:
			print(node)

	cfg_generator = CFGGenerator(ast_nodes)
	program = cfg_generator.convertAstToIr()
	optimizer = Optimizer(program)
	if not args.noSSA:
		optimizer.convertToSSA()

	if not args.noOpt:
		optimizer.removeConstantArithmetic()
	print(optimizer.getProgram())
