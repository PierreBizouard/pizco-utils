__author__ = 'Pierre'

from subprocess import Popen
import os, fnmatch

'''
Typical usage in importing ui_file
import os
from helpers.AutobuildUi import autobuild_ui_files
fpath=os.path.split(os.path.abspath(__file__))[0]
autobuild_ui_files(fpath)
'''



def autobuild_ui_files(basedir, uidir="", rcdir="res", destdir="gen"):
    ''' usage call basedir with os.getcwd si le fichier se trouve dans la racine '''
    ''' sinon appeler avec os.path.abspath(inspect.getfile(inspect.currentframe())) '''
    import sys
    if getattr(sys,"frozen",False):
        return

    cwd_bckup = os.getcwd()
    search_ui_dir = basedir + "/" + uidir + "/"
    src_ui=get_files_mtime(search_ui_dir,"*.ui")
    search_rc_dir = basedir + "/" + rcdir + "/"
    src_rc=get_files_mtime(search_rc_dir,"*.qrc")
    search_dest_dir = basedir + "/"+ destdir + "/"

    ui_build_dict = {}
    for ui in src_ui:
        dest_file = search_dest_dir+ui_src_name_to_dest_name(ui)
        build_ui = True
        if os.path.isfile(dest_file):
            dest_file_date = os.path.getmtime(dest_file)
            if src_ui[ui] < dest_file_date:
                build_ui = False
        if build_ui:
            print("file {} required update of ui".format(os.path.split(ui)[-1]))
        ui_build_dict[ui] = (dest_file, build_ui)

    rc_build_dict = {}
    for rc in src_rc:
        dest_file = search_dest_dir + rc_src_name_to_dest_name(rc)
        build_rc = True
        if os.path.isfile(dest_file):
            dest_file_date = os.path.getmtime(dest_file)
            if src_rc[rc] < dest_file_date:
                build_rc = False
        if build_rc:
            print("file {} required update of rc".format(os.path.split(rc)[-1]))
        rc_build_dict[rc] = (dest_file, build_rc)

    script_ext = ".bat"
    for f in ui_build_dict:
        if ui_build_dict[f][1]:
            cmd_name = "pyuic4{} -d -x {} -o {}".format(script_ext, f,ui_build_dict[f][0])
            proc_cmd = cmd_name.split(" ")
            p = Popen(proc_cmd, cwd=search_ui_dir)
            stdout, stderr = p.communicate()

    script_ext = ".exe"
    for f in rc_build_dict:
        if rc_build_dict[f][1]:
            cmd_name = "pyrcc4{} {} -o {}".format(script_ext, f, rc_build_dict[f][0])
            proc_cmd = cmd_name.split(" ")
            p = Popen(proc_cmd, cwd=search_rc_dir)
            stdout, stderr = p.communicate()
    os.chdir(cwd_bckup)

def ui_src_name_to_dest_name(src_name):
    dest_name = ""
    path, fname = os.path.split(src_name)
    ext = fname.split(".")[-1]
    assert(ext.lower()=="ui")
    bname = ".".join(fname.split(".")[:-1])
    for char in bname:
        if char.isalpha() and char.isupper() and dest_name[-1] != "_":
            dest_name += "_"
        dest_name += char.lower()
    if not dest_name.startswith("ui_"):
        dest_name = "ui_" + dest_name
    return dest_name+".py"

def rc_src_name_to_dest_name(src_name):
    dest_name = ""
    path, fname = os.path.split(src_name)
    ext = fname.split(".")[-1]
    assert(ext.lower()=="qrc")
    bname = ".".join(fname.split(".")[:-1])
    for char in bname:
        if char.isalpha() and char.isupper() and dest_name[-1] != "_":
            dest_name += "_"
        dest_name += char.lower()
    if not dest_name.endswith("_rc"):
        dest_name = dest_name + "_rc"
    return dest_name+".py"

def get_files_mtime(search_dir, file_filter="*.*"):
    search_dir = search_dir
    os.chdir(search_dir)
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files] # add path to each file
    files_dict=dict()
    for f in fnmatch.filter(files,file_filter):
        files_dict[f] = os.path.getmtime(f)
    return files_dict

import unittest
class TestAutoBuild(unittest.TestCase):
    def test_normal_case(self):
        autobuild_ui_files(os.getcwd())

if __name__ == "__main__":
    unittest.main()