from os.path import realpath, dirname, join, isdir

srcDir = ''
if __file__:
    srcDir = dirname(realpath(__file__))
if not srcDir:
    srcDir = '/usr/share/pyglossary'
if not isdir(srcDir):
    srcDir = dirname(srcDir)
rootDir = dirname(srcDir)



