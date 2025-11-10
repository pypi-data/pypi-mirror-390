def prac5():
    code = '''
    #Write a program in Scala to store and print details of a student.
object Studentinfo{
     def main(args:Array[String]): Unit={
     val name="Raj"
     val age=20
     val branch="Computer science"
     println(s"Hello My name is $name and my age is $age")
     println(s"My branch name is $branch")
     }
     }

#Add 2 number 
scala> object AddNumbers{
     def main(args: Array[String]): Unit={
     var x=10
     var y=20
     var c=x+y
     println(c)
     }
     }
scala> AddNumbers.main(Array())

#Infinite while loop
scala> object Infiniteloop{
     def main(args: Array[String]): Unit={
     var x=0
     while(x<1){
     println(s"$x Infinite Loop")
     }
     }
     }
Infiniteloop.main(Array())


#Basic Syntax
object HelloWorld {
  def main(args: Array[String]): Unit = {
    println("Hello, Scala!")
  }
}
HelloWorld.main(Array())


#if else if else
scala> object finalexam{
     def main(args: Array[String]): Unit={
     val age=25
     
     if (age < 13) {
     println("You are a child.")
     } else if (age < 20){
     println("You are a Teenager")
     } else if (age < 60){
     println("You are an Adult.")
     } else {
     println("you are a Senior citizen")
     }
     }
     }
scala> finalexam.main(Array())

#print All number
scala> object Allnumber{
     def main(arags: Array[String]): Unit={
     for(i <- 1 to 5){
     println(i)
     }
     }
     }
scala> Allnumber.main(Array())


#print one less number
scala> object Lessnumber{
     def main(arags: Array[String]): Unit={
     for(i <- 1 until 5){
     println(i)
     }
     }
     }
scala> Lessnumber.main(Array())

#while loop
scala> object whileloop{
     def main(args: Array[String]): Unit={
     var i = 0
     while(i<5){
     println(i)
     i=i+1
     }
     }
     }
scala> whileloop.main(Array())


#Switch in scala
scala> object MatchExample {
     def main(args: Array[String]): Unit = {
     val day = 3
     day match {
     case 1 => println("Mon")
     case 2 => println("Tue")
     case 3 => println("Wed")
     case 4 => println("Thu")
     case 5 => println("Fri")
     case 6 => println("Sat")
     case 7 => println("Sun")
     case _ => println("Other")
     } }}
scala>  MatchExample.main(Array())


var mutableVar = 10   // mutable
val immutableVal = 20 // immutable

// Integer types
val age: Int = 25                 // 32-bit integer
val smallNumber: Short = 32000    // 16-bit integer
val bigNumber: Long = 1234567890L // 64-bit integer (note the L at the end)
val tinyNumber: Byte = 100        // 8-bit integer

// Floating-point types
val price: Double = 99.99         // 64-bit floating-point
val pi: Float = 3.14f              // 32-bit floating-point (note the f at the end)

// Boolean type
val flag: Boolean = true

// Character type
val grade: Char = 'A'

// String type
val name: String = "Scala Programming"


-------------------------#Taking Input from user----------------------------
import scala.io.StdIn

// Reading a string
print("Enter your username: ")
val username = StdIn.readLine()
println(s"Hello, $username!")

// Reading an integer
print("Enter your roll number: ")
val rollno = StdIn.readInt()
println(s"Your roll number is $rollno")

// Reading a double
print("Enter the price: ")
val inputPrice = StdIn.readDouble()
println(s"You entered price: $inputPrice")
'''
    return code