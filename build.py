#!/usr/bin/env python

import sys
#sys.path.append("../tools")
import mergejs

have_compressor = None
try:
    import jsmin
    have_compressor = "jsmin"
except ImportError:
    try:
        import minimize
        have_compressor = "minimize"
    except Exception, E:
        print E
        pass

def process(config):
    sourceDirectory = "./lib"
    merged = mergejs.run(sourceDirectory, None, config)
    if have_compressor == "jsmin":
        minimized = jsmin.jsmin(merged)
    elif have_compressor == "minimize":
        minimized = minimize.minimize(merged)
    else: # fallback
        minimized = merged 
    minimized = file("license.txt").read() + minimized
    return minimized

#file(outputFilename, "w").write(minimized)
