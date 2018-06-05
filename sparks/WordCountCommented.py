import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise IOError("Invalid usage; the correct format is:\nquadrant_count.py <hostname> <port>")

    # Initialize a SparkContext with a name
    spc = SparkContext(appName="QuadrantCount")


    # Main entry point for Spark functionality.
    # A SparkContext represents the connection to a Spark cluster, and can be used to create RDD and broadcast variables on that cluster.

    # Create a StreamingContext with a batch interval of 2 seconds
    stc = StreamingContext(spc, 2)#spc is the sparkcontext
       # Spark streaming needs batch size to be defined before any stream processing. It’s because spark streaming follows micro batches 
       #  for stream processing which is also known as near realtime .
       #  But flink follows one message at a time way where each message is processed as and when it arrives. So flink does not need any batch size 
       #  to be specified.


    # Main entry point for Spark Streaming functionality.
    # A StreamingContext represents the connection to a Spark cluster, and can be used to create DStream various input sources.
    #  It can be from an existing SparkContext. After creating and transforming DStreams, the streaming computation can be started and stopped using 
    #  context.start() and context.stop(), respectively. context.awaitTermination() allows the current thread to wait for the termination of the context 
    #  by stop() or by an exception.

    # Set each DStreams in this context to remember RDDs it generated in the last given duration.
    # DStreams remember RDDs only for a limited duration of time and releases them for garbage
    # collection. This method allows the developer to specify how long to remember the RDDs (
    # if the developer wishes to query old data outside the DStream computation).



    # Checkpointing feature
    stc.checkpoint("checkpoint")
    # Sets the context to periodically checkpoint the DStream operations for master fault-tolerance. The graph will be checkpointed every batch interval.

    # Creating a DStream to connect to (and read from a port ) hostname:port (like localhost:9999)
    lines = stc.socketTextStream(sys.argv[1], int(sys.argv[2]))
    # lines = ssc.textFileStream("YOUR_S3_PATH_HERE")
    # for textfilestreaming possibly

    # Function that's used to update the state
    updateFunction = lambda new_values, running_count: sum(new_values) + (running_count or 0)


    words = lines.flatMap(lambda line: line.split(" "))
    pairs = words.map(lambda word: (word, 1))
    
    wordCounts = pairs.reduceByKey(lambda x, y: x + y)
    # wordCounts = pairs.updateStateByKey(updateFunction)
        # In spark, after each batch, the state has to be updated explicitly if you want to keep track of wordcount across batches.
        # But in flink the state is up-to-dated as and when new records arrive implicitly.

    # Print the first ten elements of each RDD generated in this DStream to the console
    wordCounts.pprint()


    # Start the computation
    stc.start()

    # Wait for the computation to terminate
    stc.awaitTermination()

# nc -lk 9999
# spark-submit /home/anuj/Desktop/sparks/sparki.py localhost 9999
