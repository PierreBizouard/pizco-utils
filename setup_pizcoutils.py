# -*- coding: utf-8 -*-

__author__ = 'Pierre'


#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2.7
# 02/2011

import sys, os
from helpers.BuildExeUtils import SetupParams, add_package_to_params
from cx_Freeze import setup, Executable

'''
#############################################################################
# préparation des options
# chemins de recherche des modules

path = sys.path + []

# options d'inclusion/exclusion des modules
includes = ["sip","matplotlib","matplotlib.backends.backend_qt4agg", "numpy", "scipy", "scipy.integrate" ,"scipy.sparse", "scipy.sparse.csgraph._validation",
            "scipy.special._ufuncs","pygments.lexer"]
excludes = ['tk', '_tkagg', '_gtkagg', '_gtk', 'tcl','PyQt4.uic.port_v3.proxy_base']
packages = ['scipy','zmq.backend.cython']

includes += ["pyqtgraph","OpenGL.platform.win32","OpenGL.arrays.ctypesarrays",
            "OpenGL.arrays.numpymodule","OpenGL.arrays.lists","OpenGL.arrays.numbers",
            "OpenGL.arrays.strings"]
includes += ['zmq', 'zmq.utils.garbage']
includes += ['pygments.styles.default','pygments.lexers.agile','pygments.lexers.asm','pygments.lexers.compiled','pygments.lexers.dalvik','pygments.lexers.dotnet','pygments.lexers.foxpro',
'pygments.lexers.functional','pygments.lexers.hdl','pygments.lexers.jvm',
'pygments.lexers.math','pygments.lexers.other','pygments.lexers.parsers','pygments.lexers.shell','pygments.lexers.special','pygments.lexers.sql',
'pygments.lexers.templates','pygments.lexers.text','pygments.lexers.web']
# copier les fichiers et/ou répertoires et leur contenu
includefiles = [('C:\\Python27\\Lib\\site-packages\\scipy\\special\\_ufuncs.pyd','_ufuncs.pyd')]


'''



stp = SetupParams()

stp.path = path = sys.path + []
add_package_to_params("pizco",stp)
add_package_to_params("ipython",stp)
add_package_to_params("opengl",stp)
add_package_to_params("guiqwt",stp)
add_package_to_params("numpy",stp)


if sys.platform == "linux2":
	stp.includefiles += []
elif sys.platform == "win32":
	stp.includefiles += []
else:
	pass
# inclusion éventuelle de bibliothèques supplémentaires
binpathincludes = []
if sys.platform == "linux2":
	# pour que les bibliothèques de /usr/lib soient copiées aussi
	stp.binpathincludes += ["/usr/lib"]


# construction du dictionnaire des options
options = {"path": stp.path,
	"includes": stp.includes,
	"excludes": stp.excludes,
	"packages": stp.packages,
    "include_msvcr" : True,
	"include_files": stp.includefiles,
	"bin_path_includes": stp.binpathincludes,
    #"init_script" : stp.initscript,
    'append_script_to_exe':False,
    'build_exe':"dist/bin",
    'compressed':True,
    'copy_dependent_files':True,
    'create_shared_zip':True,
    'include_in_shared_zip':True,
    'optimize':1, #Note : numba parsers are disrupted with the optimize flag set at 2
}

#############################################################################
# préparation des cibles
if sys.platform == "win32":
    base = "Win32GUI"


cible_1 = Executable(
	script = "WaveBuilder.py",
	#base = base,
	icon = "ico/wave_builder.ico",
    targetDir = "dist",
    targetName = "WaveBuilder.exe",
    initScript=stp.initscript,
    compress = True,
    copyDependentFiles = True,
    appendScriptToExe = True,
    appendScriptToLibrary = False
)

cible_2 = Executable(
	script = "WaveProcessor.py",
	#base = base,
	icon = "ico/wave_processor.ico",
    targetDir = "dist",
    targetName = "WaveProcessor.exe",
    initScript=stp.initscript,
    compress = True,
    copyDependentFiles = True,
    appendScriptToExe = True,
    appendScriptToLibrary = False
)

cible_3 = Executable(
	script = "SpectroWaveViewer.py",
	#base = base,
	icon = "ico/spectro_viewer.ico",
    targetDir = "dist",
    targetName = "SpectroViewer.exe",
    initScript=stp.initscript,
    compress = True,
    copyDependentFiles = True,
    appendScriptToExe = True,
    appendScriptToLibrary = False
)

#############################################################################
# création du setup
setup(
	name = "Toolbox",
	version = "1",
	description = "PulseShaperToolbox",
	author = "Pierre",
	options = {"build_exe": options},
	executables = [cible_1, cible_2, cible_3]
)