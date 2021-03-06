#!/usr/bin/env python
#
# Merge multiple JavaScript source code files into one.
#
# Usage:
# This script requires source files to have dependencies specified in them.
#
# Dependencies are specified with a comment of the form:
#
#     // @requires <file path>
#
#  e.g.
#
#    // @requires Geo/DataSource.js
#
# This script should be executed like so:
#
#     mergejs.py <output.js> <directory> [...]
#
# e.g.
#
#     mergejs.py openlayers.js Geo/ CrossBrowser/
#
#  This example will cause the script to walk the `Geo` and
#  `CrossBrowser` directories--and subdirectories thereof--and import
#  all `*.js` files encountered. The dependency declarations will be extracted
#  and then the source code from imported files will be output to 
#  a file named `openlayers.js` in an order which fulfils the dependencies
#  specified.
#
#
# Note: This is a very rough initial version of this code.
#
# -- Copyright 2005-2008 MetaCarta, Inc. / OpenLayers project --
#

# TODO: Allow files to be excluded. e.g. `Crossbrowser/DebugMode.js`?
# TODO: Report error when dependency can not be found rather than KeyError.

import re, os, sys

SUFFIX_JAVASCRIPT = ".js"
RE_REQUIRE = "@requires:? (.*)\n" # TODO: Ensure in comment?

class SourceFile:
    """
    Represents a Javascript source code file.
    """

    def __init__(self, filepath, source):
        """
        """
        self.filepath = filepath
        self.source = source

        self.requiredBy = []


    def _getRequirements(self):
        """
        Extracts the dependencies specified in the source code and returns
        a list of them.
        """
        # TODO: Cache?
        return re.findall(RE_REQUIRE, self.source)

    requires = property(fget=_getRequirements, doc="")

class Config:
    """
    Represents a parsed configuration file.

    A configuration file should be of the following form:

        [first]
        3rd/prototype.js
        core/application.js
        core/params.js
        # A comment

        [last]
        core/api.js # Another comment

        [exclude]
        3rd/logger.js

    All headings are required.

    The files listed in the `first` section will be forced to load
    *before* all other files (in the order listed). The files in `last`
    section will be forced to load *after* all the other files (in the
    order listed).

    The files list in the `exclude` section will not be imported.

    Any text appearing after a # symbol indicates a comment.
    
    """
    
    def __init__(self, **kwargs):
        self.forceFirst = kwargs.get('forceFirst', [])
        self.forceLast = kwargs.get('forceLast', [])
        self.include = kwargs.get('include', [])
        self.exclude = kwargs.get('exclude', [])

    def read(self, filename):
        """
        Parses the content of the named file and stores the values.
        :param filename: the path to a configuration file
        :return none
        """
        lines = [re.sub("#.*?$", "", line).strip() # Assumes end-of-line character is present
                 for line in open(filename)
                 if line.strip() and not line.strip().startswith("#")] # Skip blank lines and comments

        self.forceFirst = lines[lines.index("[first]") + 1:lines.index("[last]")]

        self.forceLast = lines[lines.index("[last]") + 1:lines.index("[include]")]
        self.include =  lines[lines.index("[include]") + 1:lines.index("[exclude]")]
        self.exclude =  lines[lines.index("[exclude]") + 1:]

def scanjs(sourceDirectory, config = None):
    """ scans scanDirectory recursively and returns a list of paths to javascript files
    :param sourceDirectory: the directory root
    :return list object of all file paths
    """
    allFiles = []
    ## Find all the Javascript source files
    for root, dirs, files in os.walk(sourceDirectory):
        for filename in files:
            if filename.endswith(SUFFIX_JAVASCRIPT) and not filename.startswith("."):
                filepath = os.path.join(root, filename)[len(sourceDirectory)+1:]
                filepath = filepath.replace("\\", "/")
                if config and config.include:
                    if filepath in config.include or filepath in config.forceFirst:
                        allFiles.append(filepath)
                elif (not config) or (filepath not in config.exclude):
                    allFiles.append(filepath)
    return allFiles

def merge (sourceDirectory, config = None):
    """ Merges source files within a given directory according to a configuration
    :param sourceDirectory: a string designating the path of the OpenLayers source
    :param config: a mergejs.Config object
    """
    from toposort import toposort

    allFiles = scanjs(sourceDirectory, config)

    ## Header inserted at the start of each file in the output
    HEADER = "/* " + "=" * 70 + "\n    %s\n" + "   " + "=" * 70 + " */\n\n"

    files = {}

    ## Import file source code
    ## TODO: Do import when we walk the directories above?
    for filepath in allFiles:
        fullpath = os.path.join(sourceDirectory, filepath).strip()
        content = open(fullpath, "U").read() # TODO: Ensure end of line @ EOF?
        files[filepath] = SourceFile(filepath, content) # TODO: Chop path?

    complete = False
    resolution_pass = 1

    while not complete:
        order = [] # List of filepaths to output, in a dependency satisfying order 
        nodes = []
        routes = []
        ## Resolve the dependencies
        resolution_pass += 1 

        for filepath, info in files.items():
            nodes.append(filepath)
            for neededFilePath in info.requires:
                routes.append((neededFilePath, filepath))

        for dependencyLevel in toposort(nodes, routes):
            for filepath in dependencyLevel:
                order.append(filepath)
                if not files.has_key(filepath):
                    fullpath = os.path.join(sourceDirectory, filepath).strip()
                    content = open(fullpath, "U").read() # TODO: Ensure end of line @ EOF?
                    files[filepath] = SourceFile(filepath, content) # TODO: Chop path?

        # Double check all dependencies have been met
        complete = True
        try:
            for fp in order:
                if max([order.index(rfp) for rfp in files[fp].requires] +
                       [order.index(fp)]) != order.index(fp):
                    complete = False
        except:
            complete = False

    ## Move forced first and last files to the required position
    if config:
        order = config.forceFirst + [item
                     for item in order
                     if ((item not in config.forceFirst) and
                         (item not in config.forceLast))] + config.forceLast
    
    ## Output the files in the determined order
    result = []

    for fp in order:
        f = files[fp]
        result.append(HEADER % f.filepath)
        source = f.source
        result.append(source)
        if not source.endswith("\n"):
            result.append("\n")

    return "".join(result)

if __name__ == "__main__":
    from optparse import OptionParser

    usage = "usage: mergejs.py <output.js> <source directory> [--config config filename]"
    parser = OptionParser(usage=usage)
    parser.add_option('-c', '--config', dest="config_filename", action="store",
        help="Config file name")
    (options, args) = parser.parse_args()
    
    try:
        outputFilename = sys.argv[0]
        sourceDirectory = sys.argv[1]
    except IndexError:
        parser.print_help()
        sys.exit()

    if options.config_filename:
        config = Config()
        config.read(options.config_filename)
    else:
        config = None

    output = merge(sourceDirectory, config)
    file(outputFilename, "w").write(output)
