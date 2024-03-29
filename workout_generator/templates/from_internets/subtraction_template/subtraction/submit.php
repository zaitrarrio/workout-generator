<?php

$send_to = "#";
$send_subject = "Contact Form ";

$f_name = cleanupentries($_POST["name"]);
$f_email = cleanupentries($_POST["email"]);
$f_phone = cleanupentries($_POST["tel"]);
$f_message = cleanupentries($_POST["message"]);
$from_ip = $_SERVER['REMOTE_ADDR'];
$from_browser = $_SERVER['HTTP_USER_AGENT'];

function cleanupentries($entry) {
    $entry = trim($entry);
    $entry = stripslashes($entry);
    $entry = htmlspecialchars($entry);

    return $entry;
}

$message = "This email was submitted on " . date('m-d-Y') . 
"\n\nName: " . $f_name . 
"\n\nE-Mail: " . $f_email . 
"\n\nSubject: " . $f_phone .
"\n\nMessage: \n" . $f_message . 
"\n\n\nTechnical Details:\n" . $from_ip . "\n" . $from_browser;

$send_subject .= " - {$f_name}";

$headers = "From: " . $f_email . "\r\n" .
    "Reply-To: " . $f_email . "\r\n" .
    "X-Mailer: PHP/" . phpversion();

if (!$f_email) {
    echo "no email";
    exit;
}else if (!$f_name){
    echo "no name";
    exit;
}else{
    if (filter_var($f_email, FILTER_VALIDATE_EMAIL)) {
        mail($send_to, $send_subject, $message, $headers);
        echo "true";
    }else{
        echo "invalid email";
        exit;
    }
}

?>