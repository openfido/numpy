"""numpy - OpenFIDO numpy pipeline

This pipeline provides access to the full numpy library in OpenFIDO.

INPUTS

	The structure of inputs depends on the numpy function called.  See numpy for details.

OUTPUTS

	The structure of outputs depends on the numpy function called.  See numpy for details.

"""
import sys, os, importlib

def openfido(options,stream):

	sys.path.append(f"/usr/local/bin")
	if not os.path.exists(f"/usr/local/bin/numpy_cli.py"):
		raise Exception(f"numpy_cli not installed (/usr/local/bin/numpy not found)")
	spec = importlib.util.spec_from_file_location("numpy_cli","/usr/local/bin/numpy_cli.py")
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	if not hasattr(module,"main") or not callable(module.main):
		raise Exception(f"/usr/local/bin/numpy_cli missing callable main")

	return module.main(options)
