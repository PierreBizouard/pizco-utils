__author__ = 'Pierre'

from pizco-utils.helpers.BuildExeUtils import get_build_suffix_list, build_exes

suffix_list = get_build_suffix_list()
build_exes(["pizcoutils"],"clean")
build_exes(["pizcoutils"])


