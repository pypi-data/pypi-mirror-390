def php_db():
    return """
# PHP + MySQL Database Connection

<?php
$conn = mysqli_connect("localhost", "root", "", "test");
if ($conn) {
    echo "Connected Successfully";
} else {
    echo "Connection Failed";
}
?>
"""
