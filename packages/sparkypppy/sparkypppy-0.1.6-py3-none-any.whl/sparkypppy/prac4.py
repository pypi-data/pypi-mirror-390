def prac4():
    code = '''
#Open spark-shell
>spark-shell


scala> import org.apache.spark._
scala> import org.apache.spark.rdd.RDD
scala> import org.apache.spark.graphx._


#Define vertices
// 1L = vertex ID, "A" = airport name
scala> val vertices =Array((1L, ("A")), (2L, ("B")), (3L, ("C")))


#Create vertex RDD
scala> val vRDD=sc.parallelize(vertices)

#Check vertices
scala> vRDD.take(1) // Get the first vertex

scala> vRDD.take(3) // Get all vertices

scala> vRDD.take(2) // Get first two vertices


#Define value for edges
scala> val edges =Array(Edge(1L, 2L, 1800), Edge(2L, 3L, 800), Edge(3L, 1L, 1400))

#Command to put in spark context in parallelize manner (Create edge RDD)
scala> val eRDD=sc.parallelize(edges)

#Check edges
scala> eRDD.take(2)

#Creating a graph
//List of vertices, list of edges and nowhere( Default value if a vertex referenced in edges does not exist.)
scala> val graph= Graph(vRDD, eRDD, "nowhere")

#Get all vertices which is part of graph
scala> graph.vertices.collect.foreach(println)


#Get all edges
scala> graph.edges.collect.foreach(println)


#How many number of airports is present
//Press tab for options
scala> val numberAirport=graph.


scala> val numberAirport=graph.numVertices

#Number of edges
scala> val numRoutes=graph.numEdges


#For graph in degrees(Vertex degrees)
//In-degree  Number of edges coming into a vertex
scala> val i =graph.inDegrees
scala> i.collect()

#For out degrees
//Out-degree  Number of edges going out of a vertex
scala> val o = graph.outDegrees
scala> o.collect()


#Total degree
//Total degree  Sum of in-degree and out-degree
scala> val d=graph.degrees
scala> d.collect()


#Distances val greater than 1000 (Filter edges (e.g., distance > 1000))
(Route Distance>1000)
scala> (graph.edges.filter{case Edge(src, dst, prop) => prop>1000}.collect.foreach(println))

#longDistances method2
scala> val longDistanceEdges = graph.edges.filter(e=>e.attr>1000)
scala> longDistanceEdges.collect.foreach(println)
'''
    return code