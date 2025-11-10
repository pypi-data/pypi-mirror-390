def prac3():
    code = '''
    #start the spark in scala
winget install virtuslab.scalacli
spark-shell

#Read and storing a JSON and CSV file into a DataFrame
#Go to C drive>spark3.5>example>src >main >resources

scala> val XJSON=spark.read.json("C:/spark-3.5.6-bin-hadoop3/examples/src/main/resources/people.json") 
scala> XJSON.show()

scala> val YCSV=spark.read.csv("C:/spark-3.5.6-bin-hadoop3/examples/src/main/resources/people.csv") 
scala> YCSV.show()

#Register the DataFrame as a temporary SQL view named "people"
scala> XJSON.createOrReplaceTempView("people")

-----------Running an SQL query on the temporary view "people"--------------------

#This will select all the rows and columns from the DataFrame view
scala> val sqlDF=spark.sql("Select * from people")
scala> sqlDF.show() 

#select only the "name" column from the "people" view
scala> val PName=spark.sql("Select name from people") 
scala> PName.show()

#select only the "name", “age” column from the "people" view
scala> val PName=spark.sql("Select name, age from people") 
scala> PName.show()

#select from people Where age is not null
scala> val PName=spark.sql("Select name, age from people where age IS NOT NULL") 
scala> PName.show()

#select from people Where age greater than 20
scala> val PName=spark.sql("Select name, age from people where age>20")
scala> PName.show()

#Defining variable 
scala> var X:Int=12; 
scala> var Y:Int=10; 
scala> var Z:Int=X+Y;

#Schema of the data
scala> XJSON.show()
scala> XJSON.printSchema()

#Select columns from the DataFrame
scala> XJSON.select()

#Select the 'age' column and add 1 to each value
scala> XJSON.select($"age"+1).show()

#Count How many records
scala> XJSON.count()

#Average of age
scala> val PName=spark.sql("Select avg (age) as average_age from people") 
scala> PName.show()

#Min and Max of age
scala> spark.sql("SELECT MAX(age) AS max_age, MIN(age) AS min_age FROM df").show()

#Sort by age
spark.sql("SELECT name, age FROM people ORDER BY age DESC").show()

#Download bank data csv from kaggle
scala> val mydata=spark.read.format("csv").option("header","true").load("C:/spark-3.5.6-bin-hadoop3/examples/src/main/resources/banking.csv") 
scala> mydata.show()

#Select age,job from kaggle data CSV
scala> val v1=mydata.select($"age",$"job") 
scala> v1.show()

#v1.w press tab for more options
scala> v1.w 

#Save the DataFrame 'v1' to disk at the folder named "Current"
scala> v1.write.save("C:/spark-3.5.6/examples/src/main/resources/ok")

v1.write.s

-------------------------------------------parquet file------------------------------------------------

#To show the saved data use the parquet file name from current folder
scala>spark.read.load("Current/part-00000-4c1c45f4-70d1-43e5-b513-85369b0da8b3-c000.snappy.parquet").show()


-------------------------------Creating own dataset.------------------------------------
#Define a case class 'Student' with two fields: name and age
scala> case class Student(name:String, age:Long)

#Dataset
#Create a Dataset with a single Student object
scala> val mynewdata=Seq(Student("AAA",23)).toDS()

#Create a Dataset with multiple Student objects
scala> val mynewdata=Seq((Student("BBB",24)), Student("CCC", 26)).toDS()

#To Save the Dataset 'mynewdata' to disk in the folder "MyStudent"
scala> mynewdata.write.save("MyStudent")

#2 datas are stored so two parquet file is created

#To load the data and show
scala>spark.read.load("MyStudent/part-00000-2c653f68-0885-496d-8b3d-bd24f9c85fd1-c000.snappy. parquet").show()
'''
    return code