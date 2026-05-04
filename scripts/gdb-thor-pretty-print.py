#!/usr/bin/env python
import glob, os, sys
matches = glob.glob("system-root/usr/share/gcc*/python/")
if matches:
	sys.path.insert(0, matches[0])
	try:
		import libstdcxx.v6.printers as libstdcxx_printers
		libstdcxx_printers.register_libstdcxx_printers(None)
	except:
		pass
