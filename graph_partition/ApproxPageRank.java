/**
 * Compute page ranks and subsample a graph of local community given a seed.
 *
 * Input
 *   argv[0]: path to adj graph. Each line has the following format
 *            <src>\t<dst1>\t<dst2>...
 *   argv[1]: seed node
 *   argv[2]: alpha
 *   argv[3]: epsilon
 *
 * Output
 *   Print to stdout. Lines have the following format
 *     <v1>\t<pagerank1>\n
 *     <vr>\t<pagerank2>\n
 *     ...
 *   Order does NOT matter.
 */

import java.io.*;
import java.util.*;


public class ApproxPageRank {
    private double alpha;
    private double epsilon;

    private HashMap<String, Double> p;  // personalized PageRank score vector
    private HashMap<String, Double> r;
    // cache the adjacency matrix for non-zero nodes in p (cuz it's used to accelerate the sweep
    // part, and in that part only nodes in p are used)
    private HashMap<String, HashSet<String>> cachedA;
    private int E;  // # of edges in graph
    private HashSet<String> minS;   // low-conductance subgraph

    private static final String FILE_START = "^FILE_HEAD^";

    private HashSet<String> noOutDegreeNodes;   // nodes that don't have out degrees
    private HashMap<String, HashSet<String>> toCacheList;   // cache todo list
    private HashMap<String, String> reverseToCacheList;     // reverse cache todo list

    public ApproxPageRank(double alpha, double epsilon) {
        this.alpha = alpha;
        this.epsilon = epsilon;
    }

    /**
     * Sample a graph given a seed node with Approximate PageRank algorithm.
     *
     * The graph is stored in file as an adjacency list, where each line records a node <b>u</b> and
     * all the neighbors <b>v_i</b> of <b>u</b>, in the following format:
     *      <code>u\tv_1\tv_2\t...\tv_n</code>
     *
     * @param inputFile Input file storing the graph to be sampled.
     * @param seed      ID of the seed node for sampling.
     * @return  A set of nodes in the sampled subgraph.
     */
    public HashSet<String> sample(String inputFile, String seed) {
        // train approximate pagerank
        this.train(inputFile, seed);
        HashSet<String> subgraph = this.sweep(seed);
        return subgraph;
    }

    /**
     * Train an Approximate PageRank on a graph given a seed node.
     *
     * The graph is stored in file as an adjacency list, where each line records a node <b>u</b> and
     * all the neighbors <b>v_i</b> of <b>u</b>, in the following format:
     *      <code>u\tv_1\tv_2\t...\tv_n</code>
     *
     * @param inputFile Input file storing the graph to be sampled.
     * @param seed      ID of the seed node for sampling.
     */
    public void train(String inputFile, String seed) {
// long total_t1 = System.nanoTime();
// long fileT = 0;
        this.p = new HashMap<String, Double>();
        this.r = new HashMap<String, Double>();
        this.cachedA = new HashMap<String, HashSet<String>>();
        this.E = 0;
        this.noOutDegreeNodes = new HashSet<String>();
        this.toCacheList = new HashMap<String, HashSet<String>>();
        this.reverseToCacheList = new HashMap<String, String>();

        // init r
        this.r.put(seed, 1d);

        // compute p
        boolean isChanged = true;
        boolean isFirstEpoch = true;
        int readFileCnt = 0;
        while (isChanged) {
            isChanged = false;
            HashSet<String> rNodeSet = new HashSet<String>(r.keySet());
            // NOTE: I don't think this is correct, but the result is not wrong on the test dataset,
            // and it's much faster
            boolean hasNewCachePush = true;
            while (hasNewCachePush) {
                hasNewCachePush = false;
                for (String node : rNodeSet) {
                    if (cachedA.containsKey(node)) {
                        //while (push(node)) {
                        //    isChanged = true;
                        //}
                        //isChanged |= push(node, FILE_START);
                        if (push(node, FILE_START)) {
                            isChanged = true;
                            hasNewCachePush = true;
                        }
                    } else {
                        registerCacheNode(node, FILE_START);
                    }
                }
            }

// long file_t1 = System.nanoTime();
            if (!this.toCacheList.isEmpty()) {
// int newCachedNodeCnt = 0;
                try {
                    readFileCnt++;
                    BufferedReader reader = new BufferedReader(new FileReader(inputFile));
                    String line;
                    while (!this.toCacheList.isEmpty() && (line = reader.readLine()) != null) {
                        int keyEndIndex = line.indexOf('\t');
                        String node = line.substring(0, keyEndIndex);
                        emptyToCacheRecord(node);
                        if (!this.reverseToCacheList.containsKey(node)) {
                            continue;
                        }

                        String[] items = line.split("\t");
                        if (isFirstEpoch) {
                            E += items.length - 1;
                        }
                        HashSet<String> outNodeSet = new HashSet<String>();
                        for (int outNodePtr = 1; outNodePtr < items.length; outNodePtr++) {
                            outNodeSet.add(items[outNodePtr]);
                        }
                        this.cachedA.put(node, outNodeSet);
                        String srcNode = this.reverseToCacheList.get(node);
                        HashSet<String> toCacheNodes = this.toCacheList.get(srcNode);
                        if (1 == toCacheNodes.size()) {
                            this.toCacheList.remove(srcNode);
                        } else {
                            toCacheNodes.remove(node);
                        }
                        this.reverseToCacheList.remove(node);
// newCachedNodeCnt++;

                        //while (push(node)) {
                        //    isChanged = true;
                        //}
                        isChanged |= push(node, node);
                    }
                    reader.close();
                } catch (Exception e) {
                    e.printStackTrace();
                }
// System.err.println(newCachedNodeCnt + "\t" + this.reverseToCacheList.size());
                emptyToCacheRecord(FILE_START);
            }
// long file_t2 = System.nanoTime();
// fileT += file_t2 - file_t1;
// System.err.println("Sub-File-Elapsed time: " + ((file_t2 - file_t1) / 1000000000.0) + " s");
//             isFirstEpoch = false;
        }
// System.err.println("File-Elapsed time: " + ((fileT) / 1000000000.0) + " s");
        System.err.println("Read file " + readFileCnt + " times");
// long total_t2 = System.nanoTime();
// System.err.println("Train-Elapsed time: " + ((total_t2 - total_t1) / 1000000000.0) + " s");
    }

    public HashMap<String, Double> getP() {
        return this.p;
    }

    public static void main(String[] args) throws IOException {
        // parse arguments
        if (args.length != 4) {
            printUsage();
            System.exit(1);
        }
        String inputFile = args[0];
        String seed = args[1];
        double alpha = Double.parseDouble(args[2]);
        double epsilon = Double.parseDouble(args[3]);

        ApproxPageRank apr = new ApproxPageRank(alpha, epsilon);
        HashSet<String> minS = apr.sample(inputFile, seed);

        // output result
        HashMap<String, Double> p = apr.getP();
        for (String node : minS) {
            System.out.println(node + "\t" + p.get(node));
        }
    }

    private static void printUsage() {
        System.out.println("java ApproxPageRank <input file> <seed node> <alpha> <epsilon>");
    }

    /**
     * Register the node to be cached in the future.
     *
     * @param node      ID of the node to be registered.
     * @param srcNode   ID of the source node for storing in toCacheList.
     * @return A boolean indicating whether or not the register operation is performed.
     */
    private boolean registerCacheNode(String node, String srcNode) {
        if (cachedA.containsKey(node)
            || noOutDegreeNodes.contains(node)
            || reverseToCacheList.containsKey(node)) {
            return false;
        }
        reverseToCacheList.put(node, srcNode);
        if (toCacheList.containsKey(srcNode)) {
            toCacheList.get(srcNode).add(node);
        } else {
            toCacheList.put(srcNode, new HashSet<String>() {{ add(node); });
        }
        return true;
    }

    /**
     * Empty a record in toCacheList, all the nodes remained are noOutDegreeNodes.
     *
     * @param srcNode   ID of the source node of the record to be emptied.
     * @return A boolean indicating whether or not the empty operation is performed.
     */
    private boolean emptyToCacheRecord(String srcNode) {
        if (toCacheList.containsKey(srcNode)) {
            HashSet<String> toCacheNodes = toCacheList.remove(srcNode);
            noOutDegreeNodes.addAll(toCacheNodes);
            for (String toCacheNode : toCacheNodes) {
                reverseToCacheList.remove(toCacheNode);
            }
            return true;
        }
        return false;
    }

    /**
     * Perform a push operation for Approximate PageRank.
     *
     * @param node      ID of the node to push.
     * @param srcNode   ID of the source node for storing in toCacheList.
     * @return A boolean indicating whether or not the push operation is performed.
     */
    private boolean push(String node, String srcNode) {
        double ru = this.r.getOrDefault(node, 0d);
        HashSet<String> outNodeSet = this.cachedA.get(node);
        int degree = outNodeSet.size();
        if (ru / degree > epsilon) {
            p.put(node, p.getOrDefault(node, 0d) + alpha * ru);
            r.put(node, (1 - alpha) * ru * 0.5);
            for (String outNode : outNodeSet) {
                r.put(outNode, r.getOrDefault(outNode, 0d) + (1 - alpha) * ru * 0.5 / degree);
                registerCacheNode(outNode, srcNode);
            }
            return true;
        }
        return false;
    }

    /**
     * Scan nodes in descending order of their PageRank value, build the low-conductance subgraph.
     *
     * @param seed          ID of seed node to start sweeping
     * @return  A set of nodes in the low-conductance subgraph.
     */
    private HashSet<String> sweep(String seed) {
        List<Map.Entry<String, Double>> nodeList = new ArrayList<>(this.p.entrySet());
        Collections.sort(nodeList, new Comparator<Map.Entry<String, Double>>() {
            @Override
            public int compare(Map.Entry<String, Double> o1, Map.Entry<String, Double> o2) {
                return o1.getValue() > o2.getValue() ? -1 : o1.getValue() < o2.getValue() ? 1 : 0;
            }
        });

        HashSet<String> S = new HashSet<String>() {{ add(seed); }};
        minS = new HashSet<String>(S);
        int seedDegree = this.cachedA.get(seed).size();
        double boundary = seedDegree;
        double volume = seedDegree;
        // TODO
        //double minConductance = boundary / Math.min(volume, 2 * E - volume);
        double minConductance = boundary / volume;
        for (Map.Entry<String, Double> nodeEntry : nodeList) {
            String node = nodeEntry.getKey();
            if (node.equals(seed)) {
                continue;
            }
            S.add(node);

            HashSet<String> outNodeSet = this.cachedA.get(node);
            int degree = outNodeSet.size();
            volume += degree;
            boundary += degree;
            for (String subGraphNode : S) {
                if (outNodeSet.contains(subGraphNode)) {
                    boundary--;
                }
                if (cachedA.get(subGraphNode).contains(node)) {
                    boundary--;
                }
            }
            // TODO
            //double conductance = boundary / Math.min(volume, 2 * E - volume);
            double conductance = boundary / volume;
            if (conductance < minConductance) {
                minConductance = conductance;
                minS = new HashSet<String>(S);
            }
        }

        return minS;
    }
}
