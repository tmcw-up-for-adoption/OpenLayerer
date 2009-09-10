#!/usr/bin/env python

import sys
sys.path.append("../tools")
import mergejs

source_directory = "../lib"
config_filename = "full.cfg"
output_filename = "OpenLayers.js"

def minimize(text):
    try:
        import jsmin
        return jsmin.jsmin(text)
    except Exception, e:
        import minimize
        return minimize.minimize(text)

def build(config_filename, output_filename, compress = True, **kwargs):
    config = mergejs.Config()
    config.read(config_filename)
    merged = mergejs.merge(kwargs.get('source_directory', source_directory), config)
    if compress:
        try:
            output = minimize(merged)
        except Exception, e:
            print "Neither mergejs nor minimize was found for compression.\
                Install one of these modules or specify --nocompress"
    else:
        output = merged
    license = file(kwargs.get('license', 'license.txt')).read() 
    return license + output

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "usage: build.py config output [--nocompress don't compress output]"
    parser = OptionParser(usage=usage)
    parser.add_option('-N', '--nocompress', dest="compress", action="store_false",
        default=True, help="Do not compress output. Not recommended for production.")
    (options, args) = parser.parse_args()

    license = file("license.txt").read() 

    try:
        config_filename = sys.argv[1]
        output_filename = sys.argv[2]
    except:
        parser.print_help()
        sys.exit()

    output = build(config_filename, output_filename, options.compress)
    
    print "Writing to %s." % output_filename
    file(output_filename, "w").write(output)
