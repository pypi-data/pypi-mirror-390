def prac1():
    code = '''
#Edit core-site 
<configuration>
<property>
<name>fs.defaultFS</name>
<value>hdfs://localhost:9000</value>
</property>
</configuration>

#Edit hadoop-env 
setJAVA_HOME=”C:\Java\jdk1.8.0_121” ---------------------(add this)

#Edit hdfs-site
<configuration>
<property>
<name>dfs.replication</name>
<value>1</value>
</property>
<property>
<name>dfs.namenode.name.dir</name>
<value>C:\hadoop-3.4.1\data\namenode</value>
</property>
<property>
<name>dfs.datanode.data.dir</name>
<value>C:\hadoop-3.4.1\data\datanode</value>
</property>
</configuration>

#Edit mapred-site
<configuration>
<property>
<name>mapreduce.framework.name</name>
<value>yarn</value>
</property>
</configuration>

#Edit this folder yarn-site
<configuration>
<property>
<name>yarn.nodemanager.aux-services</name>
<value>mapreduce_shuffle</value>
</property>
<property>
<name>yarn.nodemanager.auxservices.mapreduce.shuffle.class</name>
<value>org.apache.hadoop.mapred.ShuffleHandler</value>
</property>
</configuration>

cd C:\hadoop-3.4.1
hdfs namenode -format
cd C:\hadoop-3.4.1\sbin
start-dfs.cmd
start-yarn.cmd
jps 

#Go to these website
http://localhost:9870/dfshealth.html#tab-overview
http://localhost:8088/cluster

#prac2 
#Create a new folder in C:\hadoop-2.7.7 with the name input and create a file name sample and save it there with some text inside

hdfs dfs -mkdir -p /input
hdfs dfs -put C:\hadoop-2.7.7\input\sample.txt /input
hdfs dfs -ls /input
hadoop jar C:\hadoop-2.7.7\share\hadoop\mapreduce\hadoop-mapreduce-examples-2.7.7.jar wordcount /input /output
hdfs dfs -cat /output/part-r-00000

#to download the file from hdfs
Click on this http://localhost:50070/
http://localhost:8088/cluster
'''
    return code
