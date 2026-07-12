import os
import ftplib
import re

BASE_DIR = "C:/Codex_Personal/projects/tilda_migration"
THEME_DIR = os.path.join(BASE_DIR, "qilin-theme")
INDEX_PHP = os.path.join(THEME_DIR, "index.php")
SENDMAIL_PHP = os.path.join(THEME_DIR, "sendmail.php")
IMG_DIR = os.path.join(THEME_DIR, "assets", "img")

# FTP Config
host = "185.26.122.79"
user = "host1847090_qilinftp"
password = "qilin_ftp"

def rename_and_upload():
    # 1. Rename files locally
    old_fav = os.path.join(IMG_DIR, "tildafavicon.ico")
    new_fav = os.path.join(IMG_DIR, "favicon.ico")
    
    old_svg = os.path.join(IMG_DIR, "tildafavicon.svg")
    new_svg = os.path.join(IMG_DIR, "favicon.svg")
    
    old_apple = os.path.join(IMG_DIR, "tildafavicon-180x180.png")
    new_apple = os.path.join(IMG_DIR, "apple-touch-icon.png")
    
    # Do renaming if files exist
    if os.path.exists(old_fav):
        if os.path.exists(new_fav): os.remove(new_fav)
        os.rename(old_fav, new_fav)
        print("Renamed favicon.ico")
    if os.path.exists(old_svg):
        if os.path.exists(new_svg): os.remove(new_svg)
        os.rename(old_svg, new_svg)
        print("Renamed favicon.svg")
    if os.path.exists(old_apple):
        if os.path.exists(new_apple): os.remove(new_apple)
        os.rename(old_apple, new_apple)
        print("Renamed apple-touch-icon.png")

    # 2. Update index.php (Title and Favicon paths)
    print("Modifying index.php...")
    with open(INDEX_PHP, "r", encoding="utf-8") as f:
        html = f.read()
        
    # Remove "Tilda: " from title
    html = html.replace("<title>Tilda: Ци Линь - импорт товаров из Китая</title>", "<title>Ци Линь - импорт товаров из Китая</title>")
    # Support potential dynamic spacing in title
    html = re.sub(r'<title>\s*Tilda:\s*([^<]+)</title>', r'<title>\1</title>', html)
    
    # Replace favicon links with new paths and version for cache busting (?v=2)
    html = html.replace("assets/img/tildafavicon.ico", "assets/img/favicon.ico?v=2")
    html = html.replace("assets/img/tildafavicon.svg", "assets/img/favicon.svg?v=2")
    html = html.replace("assets/img/tildafavicon-180x180.png", "assets/img/apple-touch-icon.png?v=2")
    
    with open(INDEX_PHP, "w", encoding="utf-8") as f:
        f.write(html)
    print("index.php modified.")

    # 3. Update sendmail.php
    print("Updating sendmail.php to use WordPress wp_mail()...")
    wp_sendmail_code = """<?php
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
$message = "Поступила новая заявка с сайта:\\n\\n";
$message .= "Имя: " . $name . "\\n";
$message .= "Телефон: " . $phone . "\\n";
if (!empty($email)) {
    $message .= "Email: " . $email . "\\n";
}
if (!empty($message_text)) {
    $message .= "Сообщение: " . $message_text . "\\n";
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
    $headers_str = "MIME-Version: 1.0\\r\\nContent-Type: text/plain; charset=UTF-8\\r\\nFrom: no-reply@доставкакитай.рф\\r\\n";
    $success = mail($to_email, $subject, $message, $headers_str);
}

if ($success) {
    echo json_encode(array('success' => true, 'message' => 'Спасибо! Ваша заявка успешно отправлена. Мы свяжемся с вами в ближайшее время.'));
} else {
    echo json_encode(array('success' => false, 'message' => 'Не удалось отправить сообщение. Пожалуйста, проверьте настройки почты на сервере.'));
}
?>"""
    with open(SENDMAIL_PHP, "w", encoding="utf-8") as f:
        f.write(wp_sendmail_code)
    print("sendmail.php updated.")

    # 4. Upload to FTP
    print("Connecting to FTP...")
    ftp = ftplib.FTP()
    ftp.connect(host)
    ftp.login(user, password)
    
    # Upload new icon files
    print("Uploading new icons...")
    for icon_file in ["favicon.ico", "favicon.svg", "apple-touch-icon.png"]:
        local_path = os.path.join(IMG_DIR, icon_file)
        if os.path.exists(local_path):
            remote_path = f"htdocs/www/wp-content/themes/qilin-theme/assets/img/{icon_file}"
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {remote_path}", f)
            print(f"Uploaded {icon_file}")
            
    # Delete old icon files from server
    print("Deleting old icon files from server...")
    for old_file in ["tildafavicon.ico", "tildafavicon.svg", "tildafavicon-180x180.png"]:
        try:
            ftp.delete(f"htdocs/www/wp-content/themes/qilin-theme/assets/img/{old_file}")
            print(f"Deleted old remote file: {old_file}")
        except Exception as e:
            # File might not exist
            pass
            
    # Upload index.php
    print("Uploading updated index.php...")
    with open(INDEX_PHP, "rb") as f:
        ftp.storbinary("STOR htdocs/www/wp-content/themes/qilin-theme/index.php", f)
        
    # Upload sendmail.php
    print("Uploading updated sendmail.php...")
    with open(SENDMAIL_PHP, "rb") as f:
        ftp.storbinary("STOR htdocs/www/wp-content/themes/qilin-theme/sendmail.php", f)
        
    ftp.quit()
    print("FTP sync complete. Changes deployed successfully!")

if __name__ == "__main__":
    rename_and_upload()
