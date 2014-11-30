#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" helpers.py : common utilities functions used in project """
__author__ = "SVNUSER"
__status__ = "Prototype" #Prototype #Developpement
__all__ = ['PersistentConfig','YAMLObject']

#__package__ =  "PersistentConfig"
##########################################
##YAML FACILITIES
##########################################

try:
    from yaml import load, dump, YAMLObject
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper
except ImportError:
    from .ImportUtils import import_failure
    import_failure("pyyaml","YAML file support serializing/deserializing")


import shutil
import os
import yaml
from collections import OrderedDict
from .LogUtils import debug, debug_var, info, error, warning

import sys

import six
if six.PY2:
    class quoted(unicode): pass

    def quoted_presenter(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
    yaml.add_representer(quoted, quoted_presenter)

    class literal(unicode): pass

    def literal_presenter(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    yaml.add_representer(literal, literal_presenter)

    #def ordered_dict_presenter(dumper, data):
        #return dumper.represent_dict(data.items())

    #yaml.add_representer(OrderedDict, ordered_dict_presenter)
    yaml.add_representer(unicode, quoted_presenter)


##http://pyyaml.org/wiki/PyYAMLDocumentation#Flowcollections
def update_yaml_tag(self):
    pass

#FIXME : create a container for all config to be saved on app exit

class PersistentConfig(object):
    _fname = ""
    _initialized = ""
    _defaults = []
    def __init__(self,defaults,fname):
        super(PersistentConfig, self).__setattr__("_initialized", False)
        if (not hasattr(defaults,"revision")):
            debug("object must have a revision attribute")
            raise AttributeError
        super(PersistentConfig, self).__setattr__("_defaults", defaults) #defaults param
        super(PersistentConfig, self).__setattr__("_fname", fname)
        super(PersistentConfig, self).__setattr__("_child",self.load())
    def load(self):
        info("loading parameters in " +self._fname)
        child = self._defaults
        try:
            loaded_child = load(open(self._fname),Loader=Loader)
            if (loaded_child.revision == child.revision) and (loaded_child.yaml_tag == child.yaml_tag):
                child = loaded_child
                if (set(dir(loaded_child))-set(dir(child))) == set([]):
                    child = loaded_child
                else:
                    error('Different object contents at first level - Defaulting parameters')
            else:
                error('Different object revision - Defaulting parameters')
        except IOError:
            error('Unable to open config - Defaulting parameters')
        except AttributeError:
            error("Unable to check object revision - Defaulting parameters")
        except:
            error("unknown error to check object revision - Defaulting parameters")
            pass
        self._initialized = True
        return child
    def __getattr__(self, name):
        if name == "_fname" or name == "_child" or name == "_defaults" or name == "_initialized":
            error("initialization error")
            return getattr(self, name)
        else:
            return getattr(self._child, name)
    def __setattr__(self, name, value):
        if name == "_fname" or name == "_child" or name == "_defaults" or name == "_initialized":
            return object.__setattr__(self, name,value)
        else:
            return setattr(self._child, name, value)
    def sync(self):
        #atomic write
        info("syncing parameters in " +self._fname)
        tempname = self._fname+".tmp"
        fileobj = open(tempname, 'wb')
        try:
            dump(self._child,fileobj,Dumper=Dumper, default_flow_style=False)
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()
        shutil.move(tempname, self._fname)    # atomic commit
        #os.chmod(self._fname, 0x6777)
    def close(self):
        self.sync()
    def __enter__(self):
        return self
    def __exit__(self, *exc_info):
        self.close()

##################################
# TRACING / PROFILING FACILITIES
##################################

class subconfig_test(YAMLObject):
    yaml_tag = "!subconfig_test"
    def __init__(self):
        self.revision=1
        self.value=5
        self.textdata=u"35 petits oiseaux delta Δ"
        self.listdata=[25.121,23232.232,11]

class config_test(YAMLObject):
    yaml_tag = "!config_test"
    def __init__(self):
        self.revision=1
        self.value=3
        self.textdata=u"35 petits cochons delta δ"
        self.listdata=[25.24232311,23232.111111323434341,12121111]
        self.sub=subconfig_test()

class config_test2(YAMLObject):
    yaml_tag = "!config_test2"
    def __init__(self):
        debug("no revision set in class")
        self.value=3
        self.textdata=u"35 petits cochons delta δ"
        self.listdata=[25.24232311,23232.111111323434341,12121111]

def test_config_holder():
    fname=u"test_config.yml"
    with PersistentConfig(config_test(),fname) as cfg:
        debug(cfg.value)
        debug(cfg.textdata)
        debug(cfg.listdata)
        debug(cfg.sub.listdata)

    with PersistentConfig(config_test(),fname) as cfg:
        debug(cfg.value)
        debug(cfg.textdata)
        debug(cfg.listdata)
        debug(cfg.sub.listdata)

    fname2=u"test_config2.yml"
    with PersistentConfig(config_test(),fname2) as cfg:
        debug(cfg.value)
        debug(cfg.textdata)
        debug(cfg.listdata)
        debug(cfg.sub.value)
    os.remove(fname2)

def test_exception():
    with PersistentConfig(config_test2(),"testfile") as cfg:
        debug(cfg.value)
        debug(cfg.textdata)
        debug(cfg.listdata)

import unittest



class testPersistentConfig(unittest.TestCase):
    def testNormalCase(self):
        test_config_holder()
    def testNoRevision(self):
        self.assertRaises(AttributeError, test_exception)
if __name__ == "__main__":
    unittest.main()

