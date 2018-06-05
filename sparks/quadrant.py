import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

# Function to map the point to the right quadrant
def get_quadrant(line):
    # Convert the input string into a pair of numbers
    try:
        (x, y) = [float(x) for x in line.split()]
    except:
        print("Invalid input")
        return ('Invalid points', 1)

    # Map the pair of numbers to the right quadrant
    if x > 0 and y > 0:
        quadrant = 'First quadrant'
    elif x < 0 and y > 0:
        quadrant = 'Second quadrant'
    elif x < 0 and y < 0:
        quadrant = 'Third quadrant'
    elif x > 0 and y < 0:
        quadrant = 'Fourth quadrant'
    elif x == 0 and y != 0:
        quadrant = 'Lies on Y axis'
    elif x != 0 and y == 0:
        quadrant = 'Lies on X axis'
    else:
        quadrant = 'Origin'

    # The pair represents the quadrant and the counter increment
    return (quadrant, 1)
    #tuple of key value pairs

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise IOError("Invalid usage; the correct format is:\nquadrant_count.py <hostname> <port>")

    # Initialize a SparkContext with a name
    spc = SparkContext(appName="QuadrantCount")


    # Main entry point for Spark functionality.
    # A SparkContext represents the connection to a Spark cluster, and can be used to create RDD and broadcast variables on that cluster.



    # Create a StreamingContext with a batch interval of 2 seconds
    stc = StreamingContext(spc, 2)#spc is the sparkcontext

    # Main entry point for Spark Streaming functionality.
    # A StreamingContext represents the connection to a Spark cluster, and can be used to create DStream various input sources.
    #  It can be from an existing SparkContext. After creating and transforming DStreams, the streaming computation can be started and stopped using 
    #  context.start() and context.stop(), respectively. context.awaitTermination() allows the current thread to wait for the termination of the context 
    #  by stop() or by an exception.

    # # Set each DStreams in this context to remember RDDs it generated in the last given duration.
    # # DStreams remember RDDs only for a limited duration of time and releases them for garbage
    # # collection. This method allows the developer to specify how long to remember the RDDs (
    # # if the developer wishes to query old data outside the DStream computation).
    # ssc.remember(60)




    # Checkpointing feature
    stc.checkpoint("checkpoint")
    # Sets the context to periodically checkpoint the DStream operations for master fault-tolerance. The graph will be checkpointed every batch interval.

    # Creating a DStream to connect to (and read from a port ) hostname:port (like localhost:9999)
    lines = stc.socketTextStream(sys.argv[1], int(sys.argv[2]))
    # lines = ssc.textFileStream("YOUR_S3_PATH_HERE")
    # for textfilestreaming possibly

    # Function that's used to update the state
    updateFunction = lambda new_values, running_count=0: sum(new_values) + (running_count or 0)


    # # Update all the current counts of number of points in each quadrant
    # running_counts = lines.map(get_quadrant).updateStateByKey(updateFunction)
    # # running_counts = lines.map(get_quadrant).updateStateByKey(lambda x,y: x+y)
    # # mapping is a one to one transformation, and then it is updated by key using the updatefunction - newcount denotes the already counted
    # running_counts.pprint()



    words = lines.flatMap(lambda line: line.split(" "))
    pairs = words.map(lambda word: (word, 1))
    wordCounts = pairs.updateStateByKey(updateFunction)
    
    # wordCounts = pairs.reduceByKey(lambda x, y: x + y)
    # Print the first ten elements of each RDD generated in this DStream to the console
    wordCounts.pprint()







    print(type(lines))
    # print(type(running_counts))
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    # Print the current state
    # running_counts.pprint()

    # Start the computation
    stc.start()

    # Wait for the computation to terminate
    stc.awaitTermination()

# nc -lk 9999
# spark-submit /home/anuj/Desktop/sparks/sparki.py localhost 9999
