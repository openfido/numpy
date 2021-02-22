"""Command line numpy interface

This module is a CLI for the python numpy matrix class and supporting
linear algebra library. The general syntax is

  shell% numpy FUNCTION [arguments]

where function is a numpy function that takes zero or more positional
and/or keyword arguments.  Position arguments may be provided explicitly
as a string, or implicitly from stdin.  Keyword argument are provided in
the form KEYWORD=VALUE.  

Examples:

1) Generate a matrix of random numbers

  shell% numpy random.normal size=2,1
  [[-0.35433847]; [ 0.66326107]]

2) Transpose a matrix

  shell% numpy transpose '[[ 0.60125537] [-0.45920654]]'
  [[ 0.60125537]; [-0.45920654]]

3) Pipe data from one operation to another

  shell% numpy random.normal size=2 | matrix transpose
  [[ 1.57581807]; [-0.25069095]]

Getting help:

The "help" command provide additional information on available functions
using the syntax:

  shell% numpy help [command]

Note: any matrix can be provided as a URL, e.g.,

  shell% echo "1,2;3,4" > /tmp/A
  shell% numpy transpose file:///tmp/A
  1,3
  2,4

"""

# exit codes
E_OK = 0
E_NOARGS = 1
E_FAILED = 2
E_NOTFOUND = 3
E_INVALID = 4

import sys, os, subprocess, csv, urllib.request, re
cmdname = os.path.basename(sys.argv[0])
try:
	import numpy
except:
	try:
		subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-q","numpy"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		import numpy
	except Exception as err:
		print(f"ERROR [{cmdname}]: unable to install numpy automatically ({err}), manual installation required",file=sys.stderr)
		exit(E_FAILED)
import numpy.matlib as matlib
import numpy.linalg as linalg

#
# Argument types
#
def matrix(a):
	"""Matrix or input file"""
	try: # normally it's a string that can be read as a matrix
		return numpy.matrix(a.rstrip(";"))
	except: # maybe it's a file
		with urllib.request.urlopen(a) as req:
			return numpy.matrix(req.read().decode("utf-8"))

def intlist(s):
	"""Parse intlist as N[,M[,[...]]]"""
	return list(map(lambda n:int(n),s.split(',')))

def boollist(s):
	"""Parse intlist as N[,M[,[...]]]"""
	return list(map(lambda n:bool(n),s.split(',')))

def tuplelist(s):
	"""Parse intlist as N[,M[,[...]]]"""
	return list(map(lambda n:intlist(n),s.split(',')))

def intlist_args(*s):
	"""Parse arguments as integer list"""
	return list(map(lambda n:int(n),*s))

def arrayorint(a):
	try:
		return int(a)
	except:
		pass
	return numpy.array(numpy.matrix(a).flatten())[0]

def array(a):
	return numpy.array(numpy.matrix(a).flatten())[0]

def order(a):
	if a in ["inf","-inf"]:
		return float(a)
	try:
		return int(a)
	except:
		return a

#
# Arguments and options
#
POSITIONAL="" # keyword for required arguments
VARARGS = [intlist_args] # variable argument list handlers
UARGS = "**" # keywork for kwargs for ufunc
UFUNC = {
	"where" : boollist,
	"axes" : tuplelist,
	"axis" : intlist,
	"keepdims" : bool,
	"casting" : str,
	"order" : str,
	"dtype" : str,
	"subok" : bool,
}
UKEYS = list(UFUNC.keys())
functions = {

	# arithmetic
	"add" :
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"reciprocal" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"positive" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"negative" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"multiply" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"divide" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"power" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"subtract" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"true_divide" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"floor_divide" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"float_power" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"fmod" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"mod" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"modf" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"remainder" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"divmod" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	
	# complex numbers
	"angle" : 
	{
		POSITIONAL : [matrix],
		"deg" : bool,
	},
	"real" : 
	{
		POSITIONAL : [matrix],
	},
	"imag" : 
	{
		POSITIONAL : [matrix],
	},
	"conj" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"conjugate" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},

	# miscellaneous
	"convolve" : 
	{
		POSITIONAL : [array,array],
		"mode" : str,
	},
	"clip" : 
	{
		POSITIONAL : [matrix],
		"a_min" : matrix,
		"a_max" : matrix,
		UARGS : UKEYS,
	},
	"sqrt" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"cbrt" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"square" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"absolute" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"fabs" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"sign" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"heaviside" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"maximum" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"minimum" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"fmax" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"fmin" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	# "nan_to_num" : 
	# {
	# 	POSITIONAL : [matrix],
	# 	UARGS : UKEYS,
	# },
	"real_if_close" : 
	{
		POSITIONAL : [matrix],
		"tol" : float
	},
	"interp" : 
	{
		POSITIONAL : [array,array,array],
		"left" : complex,
		"right" : complex,
		"period" : complex,
	},

	# trigonometric
	"sin" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"cos" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"tan" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"arcsin" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"arccos" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"arctan" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"hypot" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"arctan2" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"degrees" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"radians" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"unwrap" : 
	{
		POSITIONAL : [matrix],
		"discont" : float,
		"axis" : int,
	},
	"deg2rad" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"rad2deg" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},

	# hyperbolic functions
	"sinh" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"cosh" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"tanh" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"arcsinh" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"arccosh" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"arctanh" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},

	# rounding
	"around" : 
	{
		POSITIONAL : [matrix],
		"decimals" : int,
	},
	"round_" : 
	{
		POSITIONAL : [matrix],
		"decimals" : int,
	},
	"rint" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"fix" : 
	{
		POSITIONAL : [matrix],
	},
	"floor" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"ceil" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"trunc" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	
	# sums, profducts, differences
	"prod" : 
	{
		POSITIONAL : [matrix],
		"initial" : float,
		UARGS : ["axis","dtype","keepdims","where"],
	},
	"sum" : 
	{
		POSITIONAL : [matrix],
		"initial" : float,
		UARGS : ["axis","dtype","keepdims","where"],
	},
	"nanprod" : 
	{
		POSITIONAL : [matrix],
		"initial" : float,
		UARGS : ["axis","dtype","keepdims","where"],
	},
	"nansum" : 
	{
		POSITIONAL : [matrix],
		"initial" : float,
		UARGS : ["axis","dtype","keepdims","where"],
	},
	"cumprod" : 
	{
		POSITIONAL : [matrix],
		UARGS : ["axis","dtype"],
	},
	"cumsum" : 
	{
		POSITIONAL : [matrix],
		UARGS : ["axis","dtype"],
	},
	"nancumprod" : 
	{
		POSITIONAL : [matrix],
		UARGS : ["axis","dtype"],
	},
	"nancumsum" : 
	{
		POSITIONAL : [matrix],
		UARGS : ["axis","dtype"],
	},
	"diff" : 
	{
		POSITIONAL : [matrix],
		"n" : int,
		"prepend" : matrix,
		"append" : matrix,
		UARGS : ["axis"],
	},
	# "ediff1d" : 
	# {
	# 	POSITIONAL : [matrix],
	# 	"to_end" : matrix,
	# 	"to_begin" : matrix,
	# },
	"gradient" : 
	{
		POSITIONAL : [matrix],
		"spacing" : matrix,
		"axis" : int,
		"edge_order" : int,
	},
	"cross" : 
	{
		POSITIONAL : [matrix,matrix],
		"axisa" : int,
		"axisb" : int,
		"axisc" : int,
		"axis" : int,
	},
	"trapz" : 
	{
		POSITIONAL : [matrix],
		"x" : matrix,
		"dx" : float,
		"axis" : int,
	},
	
	# exponents and logarithms
	"exp" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"expm1" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"exp2" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"log" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"log10" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"log2" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"log1p" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"logaddexp" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"logaddexp2" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},

	# other special functions
	"i0" : 
	{
		POSITIONAL : [array],
	},
	"sinc" : 
	{
		POSITIONAL : [matrix],
	},

	# floating point routines
	"signbit" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"copysign" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"frexp" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},
	"ldexp" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"nextafter" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"spacing" : 
	{
		POSITIONAL : [matrix],
		UARGS : UKEYS,
	},

	# rational routines
	"lcm" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},
	"gcd" : 
	{
		POSITIONAL : [matrix,matrix],
		UARGS : UKEYS,
	},

	# numpy 
	"eye" :
	{
		POSITIONAL : [int],
		"M" : int,
		"k" : int,
		"dtype" : str,
		"order" : str,
	},
	"identity" :
	{
		POSITIONAL : [int],
		"dtype" : str,
	},
	"ones" : 
	{
		POSITIONAL : [intlist],
		"dtype" : str,
		"order" : str,
	},
	"dot" :
	{
		POSITIONAL : [matrix,matrix],
	},
	"savetxt" : 
	{
		POSITIONAL : [str, matrix],
		"fmt" : str,
		"delimiter" : str,
		"newline" : str,
		"header" : str,
		"footer" : str,
		"comments" : str,
		"encoding" : str,
	},
	"trace" :
	{
		POSITIONAL : [matrix],
		"offset" : int,
		"axis" : int,
		"dtype" : str,
	},
	"transpose" : 
	{
		POSITIONAL : [matrix],
	},
	"zeros" :
	{
		POSITIONAL : [intlist],
		"dtype" : str,
		"order" : str,
	},

	# linag
	"linalg.cholesky" :
	{
		POSITIONAL : [matrix],
	},
	"linalg.cond" :
	{
		POSITIONAL : [matrix],
		"p" : order,
	},
	"linalg.det" :
	{
		POSITIONAL : [matrix],
	},
	"linalg.eig" :
	{
		POSITIONAL : [matrix],
	},
	"linalg.eigh" :
	{
		POSITIONAL : [matrix],
		"UPLO" : str,
	},
	"linalg.eigvals" :
	{
		POSITIONAL : [matrix],
	},
	"linalg.eigvalsh" :
	{
		POSITIONAL : [matrix],
		"UPLO" : str,
	},
	"linalg.inv" :
	{
		POSITIONAL : [matrix],
	},
	"linalg.lstsq" : 
	{
		POSITIONAL : [matrix,matrix],
		"rcond" : float,
	},
	"linalg.matrix_rank" :
	{
		POSITIONAL : [matrix],
	},
	"linalg.norm" :
	{
		POSITIONAL : [matrix],
		"ord" : order,
		"axis" : int,
		"keepdims" : bool,
	},
	"linalg.pinv" :
	{
		POSITIONAL : [matrix],
	},
	"linalg.qr" :
	{
		POSITIONAL : [matrix],
		"mode" : str,
	},
	"linalg.slogdet" :
	{
		POSITIONAL : [matrix],
	},
	"linalg.solve" : 
	{
		POSITIONAL : [matrix,matrix],
	},
	"linalg.svd" : 
	{
		POSITIONAL : [matrix],
		"full_matrices" : bool,
		"compute_uv" : bool,
		"hermitian" : bool,
	},

	# matlib
	"matlib.rand" :
	{
		POSITIONAL : intlist_args,
	},
	"matlib.randn" :
	{
		POSITIONAL : intlist_args,
	},
	"matlib.repmat" : 
	{
		POSITIONAL : [matrix, int, int],
	},

	# matrix
	"matrix.all" : 
	{
		POSITIONAL : [matrix],
		"axis" : int,
	},
	"matrix.any" : 
	{
		POSITIONAL : [matrix],
		"axis" : int,
	},
	"matrix.argmax" : 
	{
		POSITIONAL : [matrix],
		"axis" : int,
	},
	"matrix.argmin" : 
	{
		POSITIONAL : [matrix],
		"axis" : int,
	},
	"matrix.argpartition" : 
	{
		POSITIONAL : [matrix],
		"axis" : int,
		"kind" : str,
		"order" : intlist,
	},
	"matrix.argsort" : 
	{
		POSITIONAL : [matrix],
		"axis" : int,
		"kind" : str,
		"order" : intlist,
	},
	"matrix.astype" :
	{
		POSITIONAL : [matrix],
		"order" : str,
		"casting" : str,
		"subok" : bool,
	},
	"matrix.byteswap" :
	{
		POSITIONAL : [matrix],
	},
	"matrix.choose" :
	{
		POSITIONAL : [matrix,intlist],
		"mode" : str,
	},
	"matrix.clip" :
	{
		POSITIONAL : [matrix],
		"min" : float,
		"max" : float,
		UARGS : UKEYS,
	},
	"matrix.compress" : {
		POSITIONAL : [matrix],
	},
	"matrix.conj" : {
		POSITIONAL : [matrix],
	},
	"matrix.conjugate" : {
		POSITIONAL : [matrix],
	},
	"matrix.cumprod" : {
		POSITIONAL : [matrix],
	},
	"matrix.cumsum" : {
		POSITIONAL : [matrix],
	},
	"matrix.diagonal" : {
		POSITIONAL : [matrix],
	},
	"matrix.dot" : {
		POSITIONAL : [matrix],
	},
	"matrix.fill" : {
		POSITIONAL : [matrix],
	},
	"matrix.flatten" : {
		POSITIONAL : [matrix],
	},
	"matrix.getH" : {
		POSITIONAL : [matrix],
	},
	"matrix.getI" : {
		POSITIONAL : [matrix],
	},
	"matrix.getT" : {
		POSITIONAL : [matrix],
	},
	"matrix.getfield" : {
		POSITIONAL : [matrix],
	},
	"matrix.item" : {
		POSITIONAL : [matrix],
	},
	"matrix.itemset" : {
		POSITIONAL : [matrix],
	},
	"matrix.max" : {
		POSITIONAL : [matrix],
	},
	"matrix.mean" : {
		POSITIONAL : [matrix],
	},
	"matrix.min" : {
		POSITIONAL : [matrix],
	},
	"matrix.nonzero" : {
		POSITIONAL : [matrix],
	},
	"matrix.partition" : {
		POSITIONAL : [matrix],
	},
	"matrix.prod" : {
		POSITIONAL : [matrix],
	},
	"matrix.ptp" : {
		POSITIONAL : [matrix],
	},
	"matrix.put" : {
		POSITIONAL : [matrix],
	},
	"matrix.ravel" : {
		POSITIONAL : [matrix],
	},
	"matrix.repeat" : {
		POSITIONAL : [matrix],
	},
	"matrix.reshape" : {
		POSITIONAL : [matrix],
	},
	"matrix.resize" : {
		POSITIONAL : [matrix],
	},
	"matrix.round" : {
		POSITIONAL : [matrix],
	},
	"matrix.searchsorted" : {
		POSITIONAL : [matrix],
	},
	"matrix.setfield" : {
		POSITIONAL : [matrix],
	},
	"matrix.sort" : {
		POSITIONAL : [matrix],
	},
	"matrix.squeeze" : {
		POSITIONAL : [matrix],
	},
	"matrix.std" : {
		POSITIONAL : [matrix],
	},
	"matrix.sum" : {
		POSITIONAL : [matrix],
	},
	"matrix.swapaxes" : {
		POSITIONAL : [matrix],
	},
	"matrix.take" : {
		POSITIONAL : [matrix],
	},
	"matrix.trace" : {
		POSITIONAL : [matrix],
	},
	"matrix.transpose" : {
		POSITIONAL : [matrix],
	},
	"matrix.var" : {
		POSITIONAL : [matrix],
	},

	# random
	"random.normal" : 
	{
		POSITIONAL : [],
		"loc" : matrix, 
		"scale" : matrix,
		"size" : intlist,
	},
	"random.rand" : 
	{
		POSITIONAL : intlist_args
	},
	"random.randn" : 
	{
		POSITIONAL : intlist_args
	},
	"random.randint" : 
	{
		POSITIONAL : [int],
		"high" : int,
		"size" : intlist,
		"dtype" : str,
	},
	"random.random_sample" : 
	{
		POSITIONAL : [],
		"size" : intlist,
	},
	"random.random" : 
	{
		POSITIONAL : [],
		"size" : intlist,
	},
	"random.ranf" :
	{
		POSITIONAL : [],
		"size" : intlist,
	},
	"random.sample" :
	{
		POSITIONAL : [],
		"size" : intlist,
	},
	"random.choice" :
	{
		POSITIONAL : [arrayorint],
		"size" : intlist,
		"replace" : bool,
		"p" : array,	
	},

}

#
# Configuration values
#
class config:
	warning = True
	quiet = False
	debug = False
	exception = False
	newline = '\n'
	format = "%.8g"

numpy.set_printoptions(threshold=sys.maxsize)

#
# Output routines
#
def output(result):
	if type(result) == type(None):
		return
	if type(result) == tuple:
		for item in result:
			output(item)
	elif type(result) == list:
		numpy.savetxt(sys.stdout,result,fmt=config.format,delimiter=",",newline=config.newline)
	elif type(result) == str:
		print(result,file=sys.stdout)
	else:
		try:
			output(numpy.matrix(result).tolist())
		except:
			print(f"output({type(result)}={result}) failed",file=sys.stderr)

def warning(msg):
	if config.warning:
		print(f"WARNING [{cmdname}]: {msg}",file=sys.stderr)

def error(msg,code=None):
	if not config.quiet:
		print(f"ERROR [{cmdname}]: {msg}",file=sys.stderr)
	if config.exception:
		raise Exception(msg)
	elif code != None:
		exit(code)
	
def debug(msg):
	if config.debug:
		print(f"DEBUG [{cmdname}]: {msg}",file=sys.stderr)

def makedocs():
	for function in functions.keys():
		specs = function.split(".")
		path = "/".join(list(map(lambda n:n.title(),specs[0:-1])))
		if len(specs) > 1:
			path = "/" + path
			os.makedirs("docs"+path.title(),exist_ok=True)
		name = specs[-1].title()
		with open(f"docs{path}/{name}.md","w") as fh:
			lib = numpy
			for pkg in specs[0:-1]:
				lib = getattr(lib,pkg)
			call = getattr(lib,specs[-1])
			NL="\n"
			docs = call.__doc__.split(NL)
			fspecs = functions[function]
			args = []
			for tag, value in fspecs.items():
				if tag == POSITIONAL:
					if type(value) is list:
						for item in value:
							args.append(f"<{item.__name__}>")
					else:
						args.append(f"<{value.__name__}>")
				elif tag == UARGS:
					for utag in value:
						uval = UFUNC[utag]
						args.append(f"[{utag}=<{uval.__name__}>]")
				elif hasattr(value,"__name__"):
					args.append(f"{tag}=<{value.__name__}>")
				else:
					args.append(f"[{tag}=<{str(value)}>]")
			try:
				parameters = docs.index("Parameters")
			except:
				parameters = 0
			try:
				examples = docs.index("Examples")
			except:
				examples = -1
			if parameters > 0:
				fh.write(f"[[{path}/{name}]] -- {docs[2]}")
			else:
				fh.write(f"[[{path}/{name}]]")				
			fh.write("\n\n~~~\n")
			fh.write(f"Syntax\n------\n\n")
			fh.write(f"numpy {specs[-1]} {' '.join(args)}\n\n")
			fh.write("\n".join(docs[parameters:examples]))
			fh.write("\n~~~\n")

def help(name='.*'):
	if name in list(functions.keys()):
		if not name in functions.keys():
			error(f"'{name}' not found",code=E_NOTFOUND)
		sys.stderr = sys.stdout
		package = name.split('.')
		lib = numpy
		for pkg in package[0:-1]:
			lib = getattr(lib,pkg)
		call = getattr(lib,package[-1])
		specs = functions[name]
		args = []
		for tag, value in specs.items():
			if tag == POSITIONAL:
				if type(value) is list:
					for item in value:
						args.append(f"<{item.__name__}>")
				else:
					args.append(f"<{value.__name__}>")
			else:
				args.append(f"{tag}=<{value.__name__}>")
		print("numpy",name," ".join(args),file=sys.stdout)
		output(call.__doc__)
	else:
		print(f"Syntax: {cmdname} [options] [command] [arguments]",file=sys.stdout)
		if not name == None:
			print("Options:",file=sys.stdout)
			print("  -d|--debug       enable debugging output",file=sys.stdout)
			print("  -e|--exception   raise exceptions on errors",file=sys.stdout)
			print("  -f|--flatten     use semicolon as newline",file=sys.stdout)
			print("  -h|--help        print this help info",file=sys.stdout)
			print("  -q|--quiet       suppress all output to stderr",file=sys.stdout)
			print("  -w|--warning     suppress warning output",file=sys.stdout)
			print("Commands:",file=sys.stdout)
			print("  help [pattern]",file=sys.stdout)
			for function in sorted(list(functions.keys())):
				if not re.search(name,function): 
					continue
				specs = functions[function]
				args = []
				for tag, value in specs.items():
					if tag == POSITIONAL:
						if type(value) is list:
							for item in value:
								args.append(f"<{item.__name__}>")
						else:
							args.append(f"<{value.__name__}>")
					elif tag == UARGS:
						for utag in value:
							ufunc = UFUNC[utag]
							args.append(f"[{utag}=<{UFUNC[utag].__name__}>]")
					else:
						args.append(f"{tag}=<{value.__name__}>")
				print(" ",function," ".join(args),file=sys.stdout)

#
# Main function
#
def main(argv):
	done = False
	while not done and len(argv) > 1:
		if argv[1] in ["-w","--warning"]:
			config.warning = not config.warning
			del argv[1]
		elif argv[1] in ["-q","--quiet"]:
			config.quiet = not config.quiet
			del argv[1]
		elif argv[1] in ["-d","--debug"]:
			config.debug = not config.debug
			del argv[1]
		elif argv[1] in ["-e","--exception"]:
			config.exception = not config.exception
			del argv[1]
		elif argv[1] in ["-f","--flatten"]:
			config.newline = ';'
			del argv[1]
		elif argv[1] in ["-h","--help"]:
			argv[1] = "help"
		elif argv[1] in ["-v","--version"]:
			argv[1] = "version"
		elif argv[1] == "--makedocs":
			makedocs()
			exit(E_OK)
		elif argv[1][0] == '-':
			error(f"option '{argv[1]}' is not valid",code=E_INVALID)
		else:
			done = True

	if len(sys.argv) < 2:
		help(None)
		exit(E_NOARGS)
	elif sys.argv[1] == "help":
		if len(sys.argv) == 2:
			help()
			exit(E_OK)
		elif len(argv) == 3 and argv[1] == "help":
			help(argv[2])
			exit(E_OK)
		else:
			error("too many help functions requested",code=E_INVALID)
	elif argv[1] == "version":
		print(numpy.__version__,file=sys.stdout)
		exit(E_OK)

	try:
		package = argv[1].split('.')
		lib = numpy
		for name in package[0:-1]:
			lib = getattr(lib,name)
		call = getattr(lib,package[-1])
	except:
		if config.exception:
			raise
		error(f"'{argv[1]}' not found",code=E_NOTFOUND)

	try:
		args = []
		kwargs = {}
		pos = 0
		name = argv[1]
		function = functions[name]
		if function[POSITIONAL] in VARARGS:
			atype = function[POSITIONAL]
			if len(argv) > 2:
				args = atype(argv[2:])
		else:
			for arg in argv[2:]:
				spec = arg.split("=")
				if len(spec) < 2:
					if pos >= len(function[POSITIONAL]):
						error("too many positional argument",E_INVALID)
					atype = function[POSITIONAL][pos]
					args.append(atype(arg))
					pos += 1
				else:
					atype = function[spec[0]]
					kwargs[spec[0]] = atype(spec[1])
			while len(args) < len(function[POSITIONAL]):
				if sys.stdin.isatty():
					error("missing positional argument",E_INVALID)
				atype = function[POSITIONAL][pos]
				data = sys.stdin.readlines()
				args.append(atype(";".join(data)))
				pos += 1
		if args and kwargs:
			result = call(*args,**kwargs)
		elif args:
			result = call(*args)
		elif kwargs:
			result = call(**kwargs)
		else:
			result = call()
		output(result)
	except Exception as info:
		if config.exception:
			raise
		error(f"'{' '.join(argv[1:])}' failed - {info}",E_FAILED)

	exit(E_OK)

if __name__ == '__main__':
	main(sys.argv)
