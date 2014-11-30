#------------------------------------------------------------------------------
# BuildExeStartup.py
#   Initialization script for cx_Freeze which manipulates the path so that the
# directory in which the executable is found is searched for extensions but
# no other directory is searched. It also sets the attribute sys.frozen so that
# the Win32 extensions behave as expected.
#------------------------------------------------------------------------------

import os
import sys

subpath = "bin"
# if trap for frozen script wrapping
base_path = os.path.join(os.path.dirname(sys.executable),subpath)
sys.path.insert(0,base_path+'\\library.zip')
sys.path.insert(0,base_path)

os.environ['MATPLOTLIBDATA'] = os.path.join(os.path.dirname(sys.executable),subpath+'\\mpl-data')

import zipimport

sys.frozen = True
sys.path = sys.path[:2]

#print "IPython can require the zip_imp utils // patching qt_loaders allows this"
#from zip_imp import patch
#patch()
#However it does work so we end monkey patching qt loading
from helpers.LogUtils import *

if (os.path.isdir(DIR_NAME+"\\IPython") or os.path.isdir(base_path+"\\IPython")):
    debug("monkey patching ipython")
    os.environ["IPYTHONDIR"] = base_path
    from IPython.external import qt_loaders
    from IPython.external.qt_loaders import *

    def new_load_qt(api_option):
        loaders = {QT_API_PYSIDE: import_pyside,
                   QT_API_PYQT: import_pyqt4,
                   QT_API_PYQTv1: partial(import_pyqt4, version=1),
                   QT_API_PYQT_DEFAULT: partial(import_pyqt4, version=None)
                   }
        api = loaded_api()
        result = loaders[api]()
        api = result[-1]  # changed if api = QT_API_PYQT_DEFAULT
        commit_api(loaded_api())
        return result
    qt_loaders.load_qt = new_load_qt

os.environ["TCL_LIBRARY"] = os.path.join(DIR_NAME, "tcl")
os.environ["TK_LIBRARY"] = os.path.join(DIR_NAME, "tk")


#Enforce sip vars version on loading
if (os.path.isfile(DIR_NAME+"\\QtGui4.dll") or os.path.isfile(base_path+"\\QtGui4.dll")):
    debug("setting sip to v2")
    #perform qt4 rthook like pyinstaller
    import sip
    sip.setapi(u'QDate', 2)
    sip.setapi(u'QDateTime', 2)
    sip.setapi(u'QString', 2)
    sip.setapi(u'QTextStream', 2)
    sip.setapi(u'QTime', 2)
    sip.setapi(u'QUrl', 2)
    sip.setapi(u'QVariant', 2)

m = __import__("__main__")
importer = zipimport.zipimporter(INITSCRIPT_ZIP_FILE_NAME)
if INITSCRIPT_ZIP_FILE_NAME != SHARED_ZIP_FILE_NAME:
    moduleName = m.__name__
else:
    name, ext = os.path.splitext(os.path.basename(os.path.normcase(FILE_NAME)))
    moduleName = "%s__main__" % name
code = importer.get_code(moduleName)


exec(code, m.__dict__)

versionInfo = sys.version_info[:3]
if versionInfo >= (2, 5, 0) and versionInfo <= (2, 6, 4):
    module = sys.modules.get("threading")
    if module is not None:
        module._shutdown()

