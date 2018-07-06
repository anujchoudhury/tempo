# __Write up on Spark JVM Profiler __

To mine the resource usage patterns without changing user code, JVM Profiler was built and open sourced by Uber It is a distributed profiler to collect performance and resource usage metrics and serve them for further analysis.

Though built for Spark, its generic implementation makes it applicable to any Java virtual machine (JVM)-based service or application.


-------------------------------------------------------------------------------------------------------------------------------------------------------
Why is this required, when a standard Spark UI already exists?
------------------------------------------------------
i)In a distributed environment, multiple Spark applications run on the same server and each Spark application has a large number of processes (e.g. thousands of executors) running across many servers.

  - We do not know when these processes will launch and how long they will take. To be able to collect metrics in this environment, the profiler needs to be launched automatically with each process.

  - Existing tools could only monitor server-level metrics and did not gauge metrics for individual applications.
		
  - a solution that could collect metrics for each process and correlate them across processes for each application.
		
ii)In their current implementations, Spark and Apache Hadoop libraries do not export performance metrics; however, there are often situations where we need to collect these metrics without changing user or framework code, for perusal at a later time
	
iii)There are some existing open source tools, like [Etsy’s statsd-jvm-profiler](https://github.com/etsy/statsd-jvm-profiler), which could collect metrics at the individual application level, but they do not provide the capability to dynamically inject code into existing Java binary to collect metrics. 

-------------------------------------------------------------------------------------------------------------------------------------------------------

Features:-
----------
- A java agent: By incorporating a Java agent into this profiler, users can collect various metrics (e.g. CPU/memory usage) and stack traces for JVM processes in a distributed way. 
- Advanced profiling capabilities: The JVM Profiler allows to trace arbitrary Java methods and arguments in the user code without making any actual code changes. This feature can be used ,for example, to trace HDFS NameNode RPC call latency for Spark applications and identify slow method calls. 
- Data analytics reporting: This profiler can be used to report metrics to Kafka topics and Apache Hive tables, making data analytics faster and easier, as is done in Uber.

-------------------------------------------------------------------------------------------------------------------------------------------------------

<p align="center">
  <img src="https://eng.uber.com/wp-content/uploads/2018/06/image5-1.png" alt="How this profiler is used to monitor resource usage"/></p>

A brief overview of how this works
------------------------------------------------------

 - Bytecode instrumentation is a process where new functionality is added to a program by modifying the bytecode of a set of classes before they are loaded by the virtual machine.

 - JMX (Java Management Extensions) - The JMX technology provides a simple, standard way of managing resources such as applications, devices, and services. Because the JMX technology is dynamic, you can use it to monitor and manage resources as they are created, installed and implemented. You can also use the JMX technology to monitor and manage the Java Virtual Machine (Java VM).

<p align="center">
  <img src="https://eng.uber.com/wp-content/uploads/2018/06/image7-2.png" alt="How this profiler is used to monitor resource usage"/></p>
     

<div id="attachment_3487" style="width: 610px" class="wp-caption aligncenter"><p class="wp-caption-text"> The  JVM Profiler is composed of several different profilers that measure specific metrics related to JVM usage and performance.</p></div>
<p><span style="font-weight: 400;">The JVM Profiler code is loaded into a Java process via a </span><a href="https://docs.oracle.com/javase/7/docs/api/java/lang/instrument/package-summary.html" target="_blank" rel="noopener"><span style="font-weight: 400;">Java agent</span></a><span style="font-weight: 400;"> argument once the process starts. It consists of three main parts:</span></p>
<ul>
<li><b>Class File Transformer: </b><span style="font-weight: 400;">instruments Java method bytecode inside the process to profile arbitrary user code and save metrics in an internal metric buffer.</span></li>
<li><b>Metric Profilers</b>
<ul>
<li style="font-weight: 400;"><b>CPU/Memory Profiler:</b><span style="font-weight: 400;"> collects CPU/Memory usage metrics via </span><a href="https://docs.oracle.com/javase/tutorial/jmx/index.html" target="_blank" rel="noopener"><span style="font-weight: 400;">JMX</span></a><span style="font-weight: 400;"> and sends them to the reporters.</span></li>
<li style="font-weight: 400;"><b>Method Duration Profiler:</b><span style="font-weight: 400;"> reads method duration (latency) metrics from the metrics buffer and sends to the reporters.</span></li>
<li style="font-weight: 400;"><b>Method Argument Profiler:</b><span style="font-weight: 400;"> reads method argument values from the metrics buffer and sends to the reporters.</span></li>
</ul>
</li>
<li><b>Reporters </b>
<ul>
<li style="font-weight: 400;"><b>Console Reporter</b><span style="font-weight: 400;">: writes metrics in the console output.</span></li>
<li style="font-weight: 400;"><b>Kafka Reporter</b><span style="font-weight: 400;">: sends metrics to Kafka topics.</span></li>
</ul>
</li>
</ul>

<p><span style="font-weight: 400;">Now, let’s walkthrough how to run the profiler with the Spark application.</span></p>
<p><span style="font-weight: 400;">Assuming we already have an HDFS cluster, we upload the JVM Profiler JAR file to our HDFS:</span></p>

	hdfs dfs -put target/jvm-profiler-0.0.5.jar hdfs://hdfs_url/lib/jvm-profiler-0.0.5.jar
<p> Or,try putting this jar such that it could be accessible from wherever you are trying to run it from. </p>

<p><span style="font-weight: 400;">Then we use the spark-submit command line to launch the Spark application with the profiler:</span></p>

	spark-submit --deploy-mode cluster --master yarn --conf spark.jars=hdfs://hdfs_url/lib/jvm-profiler-0.0.5.jar --conf spark.driver.extraJavaOptions=-javaagent:jvm-profiler-0.0.5.jar --conf spark.executor.extraJavaOptions=-javaagent:jvm-profiler-0.0.5.jar --class com.company.SparkJob spark_job.jar
<p> An running example for running a Pyspark file - newcount.py with all jars</p>	

	spark-submit --jars=jvm-profiler-0.0.7.jar,spark-streaming-kafka-0-8-assembly_2.11-2.3.0.jar,kafka_2.11-0.8.2.1.jar,kafka-clients-0.8.2.1.jar,metrics-core-2.2.0.jar,zkclient-0.10.jar,zookeeper-3.4.5.jar  --conf spark.driver.extraJavaOptions=-javaagent:jvm-profiler-0.0.7.jar=reporter=com.uber.profiling.reporters.ConsoleOutputReporter,metricInterval=5000 --conf spark.executor.extraJavaOptions=-javaagent:jvm-profiler-0.0.7.jar=reporter=com.uber.profiling.reporters.ConsoleOutputReporter,metricInterval=5000        --conf spark.eventlog.enabled=false newcount.py arg1 arg2 </p>
 
 In Addition to this page, please look into [this page](https://eng.uber.com/jvm-profiler/)
