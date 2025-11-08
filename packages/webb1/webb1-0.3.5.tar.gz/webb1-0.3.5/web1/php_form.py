def php_form():
    return """
# PHP Form Handling

<form method="post" action="welcome.php">
Name: <input type="text" name="name">
<input type="submit">
</form>

<?php
echo "Welcome " . $_POST['name'];
?>
"""
