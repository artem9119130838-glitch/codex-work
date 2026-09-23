<?php
// Connect to WordPress engine to use wp_mail()
$wp_load_path = dirname(__FILE__) . '/../../../wp-load.php';
if (file_exists($wp_load_path)) {
    require_once($wp_load_path);
}

header('Content-Type: application/json; charset=utf-8');

// Target email
$to_email = "sales@доставкакитай.рф";
$subject = "Новая заявка с сайта ДоставкаКитай.рф (Ци Линь)";

// Retrieve form values
$name = isset($_POST['Name']) ? trim(strip_tags($_POST['Name'])) : '';
$email = isset($_POST['Email']) ? trim(strip_tags($_POST['Email'])) : '';
$phone = isset($_POST['Phone']) ? trim(strip_tags($_POST['Phone'])) : '';
$message_text = isset($_POST['message']) ? trim(strip_tags($_POST['message'])) : '';

if (empty($name) || empty($phone)) {
    echo json_encode(array('success' => false, 'message' => 'Пожалуйста, заполните обязательные поля: Имя и Телефон.'));
    exit;
}

// Build email content
$message = "Поступила новая заявка с сайта:\n\n";
$message .= "Имя: " . $name . "\n";
$message .= "Телефон: " . $phone . "\n";
if (!empty($email)) {
    $message .= "Email: " . $email . "\n";
}
if (!empty($message_text)) {
    $message .= "Сообщение: " . $message_text . "\n";
}

// Headers
$headers = array(
    'Content-Type: text/plain; charset=UTF-8',
    'From: no-reply@доставкакитай.рф',
);
if (!empty($email)) {
    $headers[] = 'Reply-To: ' . $email;
}

// Send via WordPress wp_mail()
if (function_exists('wp_mail')) {
    $success = wp_mail($to_email, $subject, $message, $headers);
} else {
    // Fallback to standard PHP mail if WP not loaded
    $headers_str = "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nFrom: no-reply@доставкакитай.рф\r\n";
    $success = mail($to_email, $subject, $message, $headers_str);
}

if ($success) {
    echo json_encode(array('success' => true, 'message' => 'Спасибо! Ваша заявка успешно отправлена. Мы свяжемся с вами в ближайшее время.'));
} else {
    echo json_encode(array('success' => false, 'message' => 'Не удалось отправить сообщение. Пожалуйста, проверьте настройки почты на сервере.'));
}
?>