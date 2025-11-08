def php_validation():
    return """
✅ index.html
<form action="validate.php" method="post">
   Name: <input type="text" name="name"><br><br>
   Email: <input type="text" name="email"><br><br>
   Age: <input type="text" name="age"><br><br>
   <input type="submit" value="Submit">
</form>
________________________________________
✅ validate.php
<?php

$name = $_POST['name'];
$email = $_POST['email'];
$age = $_POST['age'];

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
   echo "Form submitted successfully!";
}

?>
"""
