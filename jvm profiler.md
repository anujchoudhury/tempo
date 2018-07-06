# __Write up on Spark JVM Profiler(By Uber)__

⋅⋅* To mine the resource usage patterns without changing user code, JVM Profiler was built and open sourced by Uber It is a distributed profiler to collect performance and resource usage metrics and serve them for further analysis.
⋅⋅* Though built for Spark, its generic implementation makes it applicable to any Java virtual machine (JVM)-based service or application.


-------------------------------------------------------------------------------------------------------------------------------------------------------
Challenges(the need for this)
	i)In a distributed environment, multiple Spark applications run on the same server and each Spark application has a large number of processes (e.g. thousands of executors) running across many servers,
		1)Existing tools could only monitor server-level metrics and did not gauge metrics for individual applications.
		2)do not know when these processes will launch and how long they will take. To be able to collect metrics in this environment, the profiler needs to be launched automatically with each process.
		3)a solution that could collect metrics for each process and correlate them across processes for each application.
	ii)In their current implementations, Spark and Apache Hadoop libraries do not export performance metrics; however, there are often situations where we need to collect these metrics without changing user or framework code.
	iii)There are some existing open source tools, like Etsy’s statsd-jvm-profiler, which could collect metrics at the individual application level, but they do not provide the capability to dynamically inject code into existing Java binary to collect metrics. 

-------------------------------------------------------------------------------------------------------------------------------------------------------

Features:-
	A java agent: By incorporating a Java agent into our profiler, users can collect various metrics (e.g. CPU/memory usage) and stack traces for JVM processes 	in a distributed way. 
	Advanced profiling capabilities: Our JVM Profiler allows us to trace arbitrary Java methods and arguments in the user code without making any actual code 		changes. This feature can be used to trace HDFS NameNode RPC call latency for Spark applications and identify slow method calls. 
	Data analytics reporting: At Uber, we use the profiler to report metrics to Kafka topics and Apache Hive tables, making data analytics faster and easier.

-------------------------------------------------------------------------------------------------------------------------------------------------------
https://eng.uber.com/wp-content/uploads/2018/06/image5-1.png

Bytecode instrumentation is a process where new functionality is added to a program by modifying the bytecode of a set of classes before they are loaded by the virtual machine.

JMX (Java Management Extensions) - The JMX technology provides a simple, standard way of managing resources such as applications, devices, and services. Because the JMX technology is dynamic, you can use it to monitor and manage resources as they are created, installed and implemented. You can also use the JMX technology to monitor and manage the Java Virtual Machine (Java VM).
     
Three main features of this ugly little shit

Class File Transformer: instruments Java method bytecode inside the process to profile arbitrary user code and save metrics in an internal metric buffer.

Metric Profilers

    CPU/Memory Profiler: collects CPU/Memory usage metrics via JMX and sends them to the reporters.
    Method Duration Profiler: reads method duration (latency) metrics from the metrics buffer and sends to the reporters.
    Method Argument Profiler: reads method argument values from the metrics buffer and sends to the reporters.


Reporters

    Console Reporter: writes metrics in the console output.
    Kafka Reporter: sends metrics to Kafka topics.


spark-submit --deploy-mode cluster --master yarn --conf spark.jars=hdfs://hdfs_url/lib/jvm-profiler-0.0.5.jar --conf spark.driver.extraJavaOptions=-javaagent:jvm-profiler-0.0.5.jar --conf spark.executor.extraJavaOptions=-javaagent:jvm-profiler-0.0.5.jar --class com.company.SparkJob spark_job.jar



spark-submit --jars=jvm-profiler-0.0.7.jar,spark-streaming-kafka-0-8-assembly_2.11-2.3.0.jar,kafka_2.11-0.8.2.1.jar,kafka-clients-0.8.2.1.jar,metrics-core-2.2.0.jar,zkclient-0.10.jar,zookeeper-3.4.5.jar  --conf spark.driver.extraJavaOptions=-javaagent:jvm-profiler-0.0.7.jar=reporter=com.uber.profiling.reporters.ConsoleOutputReporter,metricInterval=5000 --conf spark.executor.extraJavaOptions=-javaagent:jvm-profiler-0.0.7.jar=reporter=com.uber.profiling.reporters.ConsoleOutputReporter,metricInterval=5000        --conf spark.eventlog.enabled=false newcount.py jn iu 


