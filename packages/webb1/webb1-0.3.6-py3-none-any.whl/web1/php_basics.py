def php_basics():
    return """
✅ Practical 9: C# Program Based on OOP Concepts
using System;

namespace OOP
{
    // Base class: Student
    class Student
    {
        protected int rollno;
        protected string name;
        protected int[] marks = new int[3];
        protected double average;

        // Default constructor
        public Student()
        {
            rollno = 0;
            name = "Unknown";
            marks[0] = marks[1] = marks[2] = 0;
        }

        // Parameterized constructor
        public Student(int r, string n, int m1, int m2, int m3)
        {
            rollno = r;
            name = n;
            marks[0] = m1;
            marks[1] = m2;
            marks[2] = m3;
        }

        // Method to calculate average (normal)
        public void CalculateAverage()
        {
            int total = marks[0] + marks[1] + marks[2];
            average = total / 3.0;
        }

        // Overloaded method (with internal marks)
        public void CalculateAverage(int internalMarks)
        {
            int total = marks[0] + marks[1] + marks[2];
            average = (total / 3.0) + internalMarks;
        }

        // Virtual Display method
        public virtual void Display()
        {
            Console.WriteLine($"\nRoll No: {rollno}, Name: {name}");
            Console.WriteLine($"Marks: {marks[0]}, {marks[1]}, {marks[2]}");
            Console.WriteLine($"Average: {average:F2}");
        }
    }

    // Derived class: SYBSC (inherits Student)
    class SYBSC : Student
    {
        string stream;

        public SYBSC(int r, string n, int m1, int m2, int m3, string str)
            : base(r, n, m1, m2, m3)
        {
            stream = str;
        }

        public override void Display()
        {
            base.Display();
            Console.WriteLine($"Stream: {stream}");
        }
    }

    // Main program
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("1. Default Constructor");
            Student s1 = new Student();
            s1.CalculateAverage();
            s1.Display();

            Console.WriteLine("\n2. Parameterized Constructor");
            Student s2 = new Student(101, "Nikhil", 78, 85, 92);
            s2.CalculateAverage();
            s2.Display();

            Console.WriteLine("\n3. Constructor Overloading (User Input)");
            Console.Write("Enter Roll No: ");
            int r = Convert.ToInt32(Console.ReadLine());
            Console.Write("Enter Name: ");
            string n = Console.ReadLine();
            Console.Write("Enter Marks 1: ");
            int m1 = Convert.ToInt32(Console.ReadLine());
            Console.Write("Enter Marks 2: ");
            int m2 = Convert.ToInt32(Console.ReadLine());
            Console.Write("Enter Marks 3: ");
            int m3 = Convert.ToInt32(Console.ReadLine());

            Student s3 = new Student(r, n, m1, m2, m3);
            s3.CalculateAverage();
            s3.Display();

            Console.WriteLine("\n4. Method Overloading");
            Console.Write("Enter Internal Marks (0 if none): ");
            int internalMarks = Convert.ToInt32(Console.ReadLine());

            if (internalMarks == 0)
                s3.CalculateAverage();
            else
                s3.CalculateAverage(internalMarks);

            s3.Display();

            Console.WriteLine("\n5. Inheritance Example");
            Console.Write("Enter Roll No: ");
            int r2 = Convert.ToInt32(Console.ReadLine());
            Console.Write("Enter Name: ");
            string n2 = Console.ReadLine();
            Console.Write("Enter Marks 1: ");
            int mm1 = Convert.ToInt32(Console.ReadLine());
            Console.Write("Enter Marks 2: ");
            int mm2 = Convert.ToInt32(Console.ReadLine());
            Console.Write("Enter Marks 3: ");
            int mm3 = Convert.ToInt32(Console.ReadLine());
            Console.Write("Enter Stream: ");
            string st = Console.ReadLine();

            SYBSC sy = new SYBSC(r2, n2, mm1, mm2, mm3, st);
            sy.CalculateAverage();
            sy.Display();

            Console.WriteLine("\nProgram Completed Successfully!");
            Console.ReadKey();
        }
    }
}

________________________________________
AJAX validation

✅ Step 1: index.html (with AJAX — Simple & Clean)
<!DOCTYPE html>
<html>
<head>
<title>AJAX Form Validation</title>

<script>
function validateForm(){
  var name  = document.getElementById("name").value;
  var email = document.getElementById("email").value;
  var age   = document.getElementById("age").value;

  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function(){
    if(this.readyState == 4 && this.status == 200){
      if(this.responseText.trim() == "OK"){
        window.location = "welcome.php?name=" + name;
      } else {
        document.getElementById("msg").innerHTML = this.responseText;
      }
    }
  };

  xhttp.open("POST", "validate.php", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("name="+name+"&email="+email+"&age="+age);
}
</script>

</head>
<body>

<h3>Registration Form</h3>

Name: <input type="text" id="name"><br><br>
Email: <input type="text" id="email"><br><br>
Age: <input type="text" id="age"><br><br>

<button onclick="validateForm()">Submit</button>

<div id="msg" style="color:red; margin-top:10px;"></div>

</body>
</html>

✅ Step 2: validate.php
<?php
$name  = $_POST['name'];
$email = $_POST['email'];
$age   = $_POST['age'];

if(empty($name) || empty($email) || empty($age)){
   echo "All fields are required!";
}
elseif(!filter_var($email, FILTER_VALIDATE_EMAIL)){
   echo "Invalid email format!";
}
elseif(!is_numeric($age)){
   echo "Age must be a number!";
}
else{
   echo "OK"; // important for AJAX success
}
?>

✅ Step 3: welcome.php
<?php
echo "<h2>Registration Successful!</h2>";
echo "Welcome, " . $_GET['name'];
?>
"""
