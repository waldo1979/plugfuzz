#!/usr/bin/python
import sys
sys.path.append("../sulley")
from sulley import *
from singleton import Singleton

@Singleton
class Fuzzer:
    def __init__(self):
        s_initialize("aspera plugin")
        s_static('<object id="')
        s_string('udp-web-transfers', fuzzable=False)
        s_static('" type="application/x-aspera-web" width="42" height="42">\n')
        self._init_paramblock("connect-launch-wait-timeout-ms", 5000)
        self._init_paramblock("image", "https://treehorn.clugston.org/images/crest.png")
        self._init_paramblock("drop-mode", "callback")
        self._init_paramblock("drop-upload-url", "https://treehorn.clugston.org/test/uploadtest.php")
        self._init_paramblock("drop-allow-directories", "true")
        self._init_paramblock("drop-allow-multiple", "true")
        s_string("</object>")

        self._req = s_get("aspera plugin")
        self._mutations = self._req.num_mutations()
        print "DONE"

    def _init_paramblock(self, param_name, param_value):
        if s_block_start("params-%s" %param_name):
            s_static('\t<param name="%s" ' % param_name)
            s_static('value="')
            if(isinstance(param_value, (int, long))):
                s_int(param_value)
            else:
                s_string(("%s" % param_value))
            s_static('">\n')
        s_block_end()
        s_repeat("params-%s" %param_name, min_reps=0, max_reps=1)
                    

    def num_mutations(self):
        return self._req.num_mutations()

    def get_next(self):
        self._req.mutate()
        return self._req.render()

if __name__ == "__main__":
    htmlgen = Fuzzer.Instance()
    num_muts = htmlgen.num_mutations()
    counter = 0
    while(counter < num_muts):
        print htmlgen.get_next()
        counter += 1
