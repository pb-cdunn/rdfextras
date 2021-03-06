================================================
Comparative performance of Stores and back-ends
================================================

Assessing comparative performance is problematic - it's a "how long is a 
piece of string?" problem, i.e. one that is subject to multiply-interacting,
often subtle, information-theoretic factors.

Also, RDFLib is a Python library for programming Pythonically with RDF and not
necessarily an industrial-grade solution to a set of specialised technical 
domain problems.

And bulk RDF storage **is** a specialised technical domain problem.

So, the aftergoing is basically "colour supplement" material - mildly diverting
but not what you'd call "a serious approach".

For info, the test platforms are i) a Dell Inspiron (32bit x86) laptop with 2G RAM 
running Ubuntu natty narwhal for running simple storage timings and ii) a 
commodity-build 64bit x68 desktop, again with 2Gb of RAM running natty that was
drafted in to do the relative heavy lifting of 50,000 triples. 

Neither machine is configured to be a suitable platform for this kind of work.
Existing background processes such as cron jobs and running services such 
anti-UCE measures will have introduced significant distortions compared to a result
set obtained from running the tests on a dedicated machine with a OS tuned
to just this task.

The test suite is part of the repository branch distribution and anyone with an
interest in seeing results specific to their local installation can easily 
replicate the tests, e.g.:

.. code-block:: bash

   $ python run_tests.py -s -q test/test_store/store_load_and_query_performance.py

So ... YMMV as they say, but on the other hand this isn't an untypical working 
set-up so the timings will be in the ball-park for similiar general-purpose
installations.

Storage of 500 - 10k triples
-----------------------------
500 - 25k triples in Notation 3 form, from a dataset generated by the
`sp2b test suite and generator <http://dbis.informatik.uni-freiburg.de/index.php?project=SP2B>`_.

The basic test is: read the data into a Graph, iterate over the triples 
in the graph, adding each to a store-backed Graph, thus testing just the 
time taken to write to permanent store.

.. code-block:: python

    store = Graph(store="MySQL/SQLite/Sleepycat/etc")
    input = Graph()
    input.parse(location="<inputlocn>", format="n3")
    start_timer()
    for triple in input:
        store.add(triple)
    end_timer()

It was immediately clear that a test set of 25k triples was too limited 
to enable the BDBOptimized Store to demonstrate the expected speed advantage 
accruing from the optimized indexing system that it employs.

Similarly, it was evident from the figures turned in by BerkeleyDB 
(a transaction-adding Store layered on top of the Sleepycat Store) 
that transactions impose a heavy toll in terms of time taken writing to 
store --- as one might well expect. Both Stores returned storage times 
an order of magnitude slower than any of the other Stores. 

At triple counts of 20k and higher, the BDBOptimized Store hints at a 
query speed advantage. This is a topic for further exploration (see below)
but for the current exercise, both BDB Stores must be considered to be 
oranges amongst the apples and so have been excluded from this reporting.

For some inexplicable reason, MySQL ran like a slug in these tests. 
This apparent poor performance is no doubt due to DBA ignorance on my 
part but nevertheless, the view is clearer when the distorting results 
are excluded and so MySQL was sent to join the BerkeleyDB Stores in the 
naughty corner for making a nonsense of the vertical scale.

.. image:: /_static/store/time_to_store_triples.png
   :alt: store 500 - 25k triples
   :align: center


Load and query 50k triples
---------------------------
50,000 triples of statements generated by the sp2b data generator and using
the (arbitrarily-selected) first SPARQL query listed in the sp2b set:

.. code-block:: sparql

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
    }

For this test, the BDB Stores and MySQL returned to the arena.

Extended storage times are the norm for RDF in bulk.
 
.. image:: /_static/store/store_50ktriples.png
   :alt: store 50k triples
   :align: center

Query times will play a significant role in UI.

.. image:: /_static/store/answer_query.png
   :alt: answer a SPARQL query
   :align: center

The increased number of triples enabled the BSDBOptimized 
Store to show the anticipated advantages of its optimized indexing.

