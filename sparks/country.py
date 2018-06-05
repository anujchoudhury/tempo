import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

def get_countryname(line):
    country_name = line.strip()

    # if country_name == 'usa':
    #     output = 'USA'
    # elif country_name == 'ind':
    #     output = 'India'
    # elif country_name == 'aus':
    #     output = 'Australia'
    # else:
    #     output = 'Unknown'
    output=country_name
    return (output, 1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise IOError("Invalid usage; the correct format is:\nwindow_count.py <hostname> <port>")

    # batch_interval = 1 # base time unit (in seconds)
    window_length = 6 #* batch_interval
    frequency = 3 #* batch_interval

    spc = SparkContext(appName="WindowCount")
    stc = StreamingContext(spc, 3)
    stc.checkpoint("checkpoint")

    lines = stc.socketTextStream(sys.argv[1], int(sys.argv[2]))
    addFunc = lambda x, y: x + y
    invAddFunc = lambda x, y: x - y
    window_counts = lines.map(get_countryname).reduceByKeyAndWindow(addFunc, invAddFunc, window_length, frequency)
    window_counts.pprint()

    stc.start()
    stc.awaitTermination()

# nc -lk 9999
# spark-submit /home/anuj/Desktop/sparks/sparki.py localhost 9999
