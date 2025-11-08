def php_db():
    return """
Step 1: form.html
<!DOCTYPE html>
<html>
<body>

<h3>Insert Data</h3>

<form action="save.php" method="POST">
Name: <input type="text" name="name"><br><br>
Email: <input type="text" name="email"><br><br>
<input type="submit" value="Save">
</form>

</body>
</html>
________________________________________
✅ Step 2: save.php
<?php
$name = $_POST['name'];
$email = $_POST['email'];

$conn = mysqli_connect("localhost", "root", "", "practiceDB");

if(!$conn){
   die("Connection Failed");
}

$sql = "INSERT INTO users(name,email) VALUES('$name','$email')";

if(mysqli_query($conn, $sql)){
   echo "Record Inserted Successfully!";
} else {
   echo "Error!";
}

mysqli_close($conn);
?>
________________________________________


"""
