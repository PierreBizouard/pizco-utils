__author__ = 'Pierre'

__all__ = ["get_build_suffix_list", "build_exes", "add_package_to_params", "SetupParams", "pyqt4_hook","subpath_hook"]

'''
Parsing and launching setup_* parts
'''

from subprocess import Popen
import os, fnmatch
import sys
import glob

def get_build_suffix_list(directory=None):
    if directory is None:
        directory = os.getcwd()
    list = fnmatch.filter(os.listdir(directory),"setup_*.py")
    print

def build_exes(script_suffix_list,command="build"):
    cd = os.getcwd()
    os.chdir(cd)
    for suffix in script_suffix_list:
        cmd = "python setup_{}.py {}".format(suffix,command)
        p = Popen(cmd.split(" "), cwd=cd)
        stdout, stderr = p.communicate()

'''
Includes and exclude parts
'''
class SetupParams(object):
    path = []
    includes = []
    includefiles = []
    packages = []
    excludes = []
    binpathincludes = []
    datafiles_copy = []
    initscript = os.path.join(os.path.split(os.path.abspath(__file__))[0],"BuildExeStartup.py")

'''
opengl utils
'''

def build_opengl_plugin_list():
    #inspired from hookutils in pyinstaller

    import OpenGL
    opengl_mod_path = OpenGL.__path__[0]
    arrays_mod_path = os.path.join(opengl_mod_path, 'arrays')
    files = glob.glob(arrays_mod_path + '/*.py')
    modules = []

    for f in files:
        mod = os.path.splitext(os.path.basename(f))[0]
        # Skip __init__ module.
        if mod == '__init__':
            continue
        modules.append('OpenGL.arrays.' + mod)
    return modules

def build_ipython_dir_list():
    #inspired from hookutils in pyinstaller
    import IPython
    modules = []
    ipython_mod_path = IPython.__path__[0]
    html_dir = os.path.join(ipython_mod_path, 'html')
    for dirpath, dirnames, files in os.walk(html_dir):
        for f in files:
            extension = os.path.splitext(f)[1]
            if extension not in [".py",".pyc",".pyd",".pyo",".h"]:
                # Produce the tuple
                # (/abs/path/to/source/mod/submod/file.dat,
                #  mod/submod/file.dat)
                source = os.path.join(dirpath, f)
                base_path = os.path.dirname(html_dir) + os.sep
                dest = source.replace(base_path,"")
                modules.append((source, os.path.join("IPython",dest)))
    return modules


opengl_accelerate_includes = ['OpenGL_accelerate', 'OpenGL_accelerate.wrapper', 'OpenGL_accelerate.formathandler']
opengl_platform_includes = ['OpenGL',"OpenGL.platform.win32"]

matplotlib_includes = "matplotlib","matplotlib.backends.backend_qt4agg"
matplotlib_excludes = ['tk', '_tkagg', '_gtkagg', '_gtk', 'tcl']

qt_includes = ["sip"]
qt_excludes = ['PyQt4.uic.port_v3.proxy_base']
qt_packages = ["PyQt4.QtCore","PyQt4.QtGui","PyQt4.QtSvg"]

pygments_includes = ['pygments.styles.default','pygments.lexers.agile']

zmq_includes = ['zmq', 'zmq.utils.garbage']
zmq_packages = ['zmq.backend.cython'] #backend can be package

numpy_scipy_packages = ["numpy","scipy"]

numpy_scipy_includes =["numpy", "scipy", "scipy.integrate" ,"scipy.sparse", "scipy.sparse.csgraph._validation",
            "scipy.special._ufuncs", "scipy.special._ufuncs_cxx"] #maybe treat scipy as packages

numpy_scipy_includefiles = [('C:\\Python27\\Lib\\site-packages\\scipy\\special\\_ufuncs.pyd','_ufuncs.pyd')]


numba_includes = ["numba","llvmpy","llvm","pycparser","pycparser.ply"]
numba_packages = ["numba","cffi","pycparser","llvm","llvmpy"]


'''
    Add package utility
'''

def add_package_to_params(package_name, params):
    assert(isinstance(params,SetupParams))
    package_name = package_name.lower()
    if package_name == "opengl":
        opengl_includes = build_opengl_plugin_list() + opengl_accelerate_includes + opengl_platform_includes
        params.includes.extend(opengl_includes)
        return
    if package_name == "ipython":
        '''
        ipython requires a patch in load_qt / monkey patch is done in startup script
        '''
        warning = """
            Using Ipython frozen console requires, and setting right backend with matplotlib
            Sourcecode : IPython/external/qt_loaders.py

                commit_api(api)
                return result
            else:
                #Append data here
                #if getattr(sys,"frozen",False):
                #    api = loaded_api()
                #    result = loaders[api]()
                #    api = result[-1]  # changed if api = QT_API_PYQT_DEFAULT
                #    commit_api(loaded_api())
                #    return result
            raise ImportError("""
        params.includes.extend(pygments_includes)
        params.includes.extend(zmq_includes)
        params.packages.extend(zmq_packages)
        params.includes.extend(matplotlib_includes)
        params.excludes.extend(matplotlib_excludes)
        params.excludes.extend(qt_excludes)

        ipython_include_files = build_ipython_dir_list()
        params.includefiles.extend(ipython_include_files)
        return
    if package_name in ["zmq", "pizco"]:
        params.includes.extend(zmq_includes)
        params.packages.extend(zmq_packages)
        return
    if package_name in ["numpy","scipy"]:
        params.includes.extend(numpy_scipy_includes)
        params.includefiles.extend(numpy_scipy_includefiles)
        params.packages.extend(numpy_scipy_packages)
        params.includes.extend(numba_includes)
        params.packages.extend(numba_packages)

        return
    if package_name in ["guiqwt","guidata"]:
        params.includes.extend(qt_includes)
        params.excludes.extend(qt_excludes)
        params.packages.extend(qt_packages)
        from guidata import configtools
        guidata_add_source=configtools.get_module_data_path("guidata","images")
        import guiqwt
        guiqwt_mod_path = guiqwt.__path__[0]
        guiqwt_add_source = guiqwt_mod_path + "\\images"
        params.includefiles.extend([(guidata_add_source,"guidata/images/")])
        params.includefiles.extend([(guiqwt_add_source,"guiqwt/images")])
        return
    if package_name in ["pyqt"]:
        params.includes.extend(qt_includes)
        params.excludes.extend(qt_excludes)
        params.packages.extend(qt_packages)
        return
    if package_name in ["local_svg"]:
        list_files_in_cur = os.listdir(os.getcwd())
        svg_list = []
        for file in list_files_in_cur:
            if fnmatch(file,"*.svg"):
                svg_list.append(file)
        params.includefiles.append(svg_list)

'''

Hooks / Support of subdirs

'''

def pyqt4_hook():
    if getattr(sys,'frozen',False):
        import sip
        sip.setapi(u'QDate', 2)
        sip.setapi(u'QDateTime', 2)
        sip.setapi(u'QString', 2)
        sip.setapi(u'QTextStream', 2)
        sip.setapi(u'QTime', 2)
        sip.setapi(u'QUrl', 2)
        sip.setapi(u'QVariant', 2)

def subpath_hook(subpath):
    if getattr(sys,'frozen',False):
        # if trap for frozen script wrapping
        sys.path.append(os.path.join(os.path.dirname(sys.executable),subpath))
        sys.path.append(os.path.join(os.path.dirname(sys.executable),subpath+'\\library.zip'))

        os.environ['TCL_LIBRARY'] = os.path.join(os.path.dirname(sys.executable),subpath+'\\tcl')
        os.environ['TK_LIBRARY'] = os.path.join(os.path.dirname(sys.executable),subpath+'\\tk')
        os.environ['MATPLOTLIBDATA'] = os.path.join(os.path.dirname(sys.executable),subpath+'\\mpl-data')

'''

'''