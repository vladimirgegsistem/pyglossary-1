# -*- coding: utf-8 -*-
## ui_cmd.py
##
## Copyright © 2008-2010 Saeed Rasooli <saeed.gnu@gmail.com> (ilius)
## This file is part of PyGlossary project, http://sourceforge.net/projects/pyglossary/
##
## This program is a free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3, or (at your option)
## any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with this program. Or on Debian systems, from /usr/share/common-licenses/GPL
## If not, see <http://www.gnu.org/licenses/gpl.txt>.

from os.path import join

from pyglossary.glossary import *
from base import *
import progressbar as pb


if os.sep=='\\': ## Operating system is Windows
    startRed = ''
    endFormat = ''
    startBold = ''
    startUnderline = ''
    endFormat = ''
else:
    startRed = '\x1b[31m'
    endFormat = '\x1b[0;0;0m'

    startBold = '\x1b[1m' ## Start Bold ## len=4
    startUnderline = '\x1b[4m' ## Start Underline ## len=4
    endFormat = '\x1b[0;0;0m' ## End Format ## len=8
    #redOnGray = '\x1b[0;1;31;47m'

def printAsError(text='An error occured!', exit=False):
    sys.stderr.write('%s%s%s\n'%(startRed, text, endFormat))
    if exit:
        sys.exit(1)

def cmdRaise():
    i = sys.exc_info()
    printAsError(
        startRed +
        'File %s line %s: %s: %s'%(
            __file__,
            i[2].tb_lineno,
            i[0].__name__,
            i[1]
        ) +
        endFormat
    )

COMMAND = 'pyglossary'
#COMMAND = sys.argv[0]



def help():
    text = open(join(rootDir, 'help')).read()\
        .replace('%CMD',COMMAND)\
        .replace('%SB',startBold)\
        .replace('%SU',startUnderline)\
        .replace('%EF',endFormat)
    text += '\n%sSupported input formats:%s'%(startBold, endFormat)
    for f in Glossary.readFormats:
        text += '\n  %s'%Glossary.formatsDesc[f]
    text += '\n%sSupported output formats:%s'%(startBold, endFormat)
    for f in Glossary.writeFormats:
        text += '\n  %s'%Glossary.formatsDesc[f]
    print(text)


def parseFormatOptionsStr(st):
    opt = {}
    parts = st.split(';')
    for part in parts:
        try:
            (key, value) = part.split('=')
        except ValueError:
            printAsError('bad option syntax: %s'%part)
            continue
        key = key.strip()
        value = value.strip()
        try:
            value = eval(value) ## if it is string form of a number or boolean or tuple ...
        except:
            pass
        opt[key] = value
    return opt

class NullObj:
    def __getattr__(self, attr):
        return self
    def __setattr__(self, attr, value):
        pass
    def __call__(self, *args, **kwargs):
        pass

class UI(UIBase):
    def __init__(self, text='Loading: ', noProgressBar=None, **options):
        self.ptext = text
        self.reverseStop = False
        self.pref = {}
        self.pref_load()
        #print self.pref
        if noProgressBar is None:
            self.progressBuild()
        else:
            self.pbar = NullObj()
    def setText(self, text):
        self.pbar.widgets[0]=text
    def progressStart(self):
        self.pbar.start()
    def progress(self, rat, text=''):
        self.pbar.update(rat)
    def progressEnd(self):
        self.pbar.finish()
        print
    def progressBuild(self):
        rot = pb.RotatingMarker()
        ## SyntaxError(invalid syntax) with python3 with unicode(u'█') argument ## FIXME
        self.pbar = pb.ProgressBar(
            widgets=[
                self.ptext,
                pb.Bar(marker=u'█', right=rot),
                pb.Percentage(),
                '% ',
                pb.ETA(),
            ],
            maxval=1.0,
            update_step=0.5,
        )
        rot.pbar = self.pbar
    def r_start(self, *args):
        self.rWords = self.glosR.takeOutputWords()
        print('Number of input words:', len(self.rWords))
        print('Reversing glossary... (Press Ctrl+C to stop)')
        try:
            self.glosR.reverseDic(self.rWords, self.pref)
        except KeyboardInterrupt:
            self.r_stop()
            ## if the file closeed ????
    def r_stop(self, *args):
        self.glosR.continueFrom = self.glosR.i
        self.glosR.stoped = True
        self.reverseStop = True
        print('Stoped! Press Enter to resume, and press Ctrl+C to quit.')
        try:
            raw_input()
        except KeyboardInterrupt:
            return 0
        else:
            self.r_resume()
    def r_resume(self, *args):
        if self.glosR.stoped==True:
            ## update reverse configuration?
            self.reverseStop = False
            print('Continue reversing from index %d ...'%self.glosR.continueFrom)
            try:
                self.glosR.reverseDic(self.rWords, self.pref)
            except KeyboardInterrupt:
                self.r_stop()
        else:
            print('self.glosR.stoped=%s'%self.glosR.stoped)
            print('Not stoped yet. Wait many seconds and press "Resume" again...')
    def r_finished(self, *args):
        self.glosR.continueFrom=0
        print('Reversing completed.')
    def pref_load(self, *args):
        fp = open(join(srcDir, 'rc.py'))
        exec(fp.read())
        if save==0 and os.path.exists(self.prefSavePath[0]): # save is defined in rc.py
            try:
                fp=open(self.prefSavePath[0])
            except:
                cmdRaise()
            else:
                exec(fp.read())
        for key in self.prefKeys:
            self.pref[key] = eval(key)
        return True
    def yesNoQuestion(self, msg, yesDefault=True):## FIXME
        return True
    def run(self, ipath, opath='', read_format='', write_format='',
                  read_options={}, write_options={}, reverse=False):
        if read_format:
            #read_format = read_format.capitalize()
            if not read_format in Glossary.readFormats:
                printAsError('invalid read format %s'%read_format)
        if write_format:
            #write_format = write_format.capitalize()
            if not write_format in Glossary.writeFormats:
                printAsError('invalid write format %s'%write_format)
                print 'try: %s --help'%COMMAND
                return 1
        if not opath:
            if reverse:
                opath = os.path.splitext(ipath)[0] + '-reversed.txt'
            elif write_format:
                try:
                    ext = Glossary.formatsExt[write_format]
                except KeyError:
                    printAsError('invalid write format %s'%write_format)
                    print 'try: %s --help'%COMMAND
                    return 1
                else:
                    opath = os.path.splitext(ipath)[0] + ext
            else:
                printAsError('neither output file nor output format is given')
                print 'try: %s --help'%COMMAND
                return 1
        g = Glossary()
        print('Reading file "%s"'%ipath)
        g.ui = self
        if g.read(ipath, format=read_format, **read_options)!=False:
            ## When glossary reader uses progressbar, progressbar must be rebuilded:
            self.progressBuild()
            g.uiEdit()
            if reverse:
                print('Reversing to file "%s"'%opath)
                self.setText('')
                self.pbar.update_step = 0.1
                self.pref['savePath'] = opath
                self.glosR = g
                self.r_start()
            else:
                print('Writing to file "%s"'%opath)
                self.setText('Writing: ')
                if g.write(opath, format=write_format, **write_options)!=False:
                    print('done')
                    return 0
                else:
                    printAsError('writing output file was failed!')
                    return 1
        else:
            printAsError('reading input file was failed!')
            return 1
        return 0


