CC := javac
SRC := ApproxPageRank.java
CLS := ApproxPageRank
DATA := data 
OUTPUT := pr.txt

TESTGRAPH := adj_list.txt

SEED_TEST := 5c6ee08028001fff5e6ee08028729ffffffff0e0e8f21ebd 
ALPHA := 3e-1
EPS := 1e-5

all: apr

apr: $(SRC)
	$(CC) $(SRC)

time: all
	time java $(CLS) $(DATA)/$(TEST_GRAPH) $(SEED_TEST) $(ALPHA) $(EPS) > $(OUTPUT)

#time java ApproximatePageRank.class $EDGE_ADJLIST 5c6ee08028001fff5e6ee08028729ffffffff0e0e8f21ebd 3e-1 1e-5 > test.txt

clean:
	rm -rf *.class *.tar

.PHONY:
	data pagerank clean
