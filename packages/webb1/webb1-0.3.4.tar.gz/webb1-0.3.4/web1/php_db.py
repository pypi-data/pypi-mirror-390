
def php_db():
    return """
# Form Validation (JS + PHP)

<script>
function validate() {
  let name = document.forms["myForm"]["name"].value;
  if (name == "") {
    alert("Name must be filled out");
    return false;
  }
}
</script>

<form name="myForm" method="post" onsubmit="return validate()">
Name: <input type="text" name="name">
<input type="submit">
</form>

<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
  if (empty($_POST["name"])) {
    echo "Name is required";
  } else {
    echo "Submitted Successfully";
  }
}
?>
"""
