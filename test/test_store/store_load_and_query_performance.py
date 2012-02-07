import unittest
import os
import gc
import itertools
import textwrap
from time import time
from random import random
from tempfile import mkdtemp
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef
import rdflib
from rdflib import plugin

plugin.register(
    'sparql', rdflib.query.Processor,
    'rdfextras.sparql.processor', 'Processor')

plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')

def random_uri():
    return URIRef("%s" % random())

class StoreTestCase(unittest.TestCase):
    """
    Test case for testing store performance... probably should be
    something other than a unit test... but for now we'll add it as a
    unit test.
    """
    store = 'default'
    path = None
    storetest = True
    performancetest = True
    
    def setUp(self):
        self.gcold = gc.isenabled()
        gc.collect()
        gc.disable()
        
        self.graph = Graph(store=self.store)
        if not self.path:
            path = mkdtemp()
        else:
            path = self.path
        self.path = path
        self.graph.open(self.path, create=True)
        self.input = input = Graph()
        input.parse(data=open(os.getcwd()+"/test/sp2b/500triples.n3",'r').read(), format="n3")
    
    def tearDown(self):
        self.graph.close()
        if self.gcold:
            gc.enable()
        # TODO: delete a_tmp_dir
        self.graph.close()
        del self.graph
        if hasattr(self,'path') and self.path is not None:
            if os.path.exists(self.path):
                if os.path.isdir(self.path):
                    for f in os.listdir(self.path): os.unlink(self.path+'/'+f)
                    os.rmdir(self.path)
                elif len(self.path.split(':')) == 1:
                    os.unlink(self.path)
                else:
                    os.remove(self.path)
    
    def testTime(self):
        number = 1
        print("")
        print(self.store)
        res = ""
        for i in itertools.repeat(None, number):
            res += self._testInput()
        print("std file input: %s" % res)
        res = ""
        for i in itertools.repeat(None, number):
            res += self._testQuery()
        print("std query: %s" % res)
    
    def _testRandom(self):
        number = len(self.input)
        store = self.graph
        
        def add_random():
            s = random_uri()
            p = random_uri()
            o = random_uri()
            store.add((s, p, o))
        
        it = itertools.repeat(None, number)
        t0 = time()
        for _i in it:
            add_random()
        t1 = time()
        return "%.3g " % (t1 - t0)
    
    def _testInput(self):
        number = 1
        store = self.graph
        
        def add_from_input():
            for t in self.input:
                store.add(t)
        
        it = itertools.repeat(None, number)
        t0 = time()
        for _i in it:
            add_from_input()
        t1 = time()
        return "%.3g " % (t1 - t0)

    def _testQuery(self):
        number = 1
        store = self.graph
        
        def query_input():
            qres = store.query(textwrap.dedent("""\
                PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX dc:      <http://purl.org/dc/elements/1.1/>
                PREFIX dcterms: <http://purl.org/dc/terms/>
                PREFIX bench:   <http://localhost/vocabulary/bench/>
                PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#> 

                SELECT ?yr
                WHERE {
                  ?journal rdf:type bench:Journal .
                  ?journal dc:title "Journal 1 (1940)"^^xsd:string .
                  ?journal dcterms:issued ?yr 
                }"""),
                initNs=dict(
                    foaf=Namespace("http://xmlns.com/foaf/0.1/")))
            assert len(qres) > 0, qres.bindings
        it = itertools.repeat(None, number)
        t0 = time()
        for _i in it:
            query_input()
        t1 = time()
        return "%.3g " % (t1 - t0)

try:
    class SleepycatStoreTestCase(StoreTestCase):
        def setUp(self):
            self.store = "Sleepycat"
            self.path = '/var/tmp/scattest'
            StoreTestCase.setUp(self)
except ImportError, e:
    print("Can not test Sleepycat store:", e)

if __name__ == '__main__':
    unittest.main()
