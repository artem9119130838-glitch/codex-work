import os
import json
import re

BASE_DIR = "C:/Codex_Personal/projects/tilda_migration"
HTML_FILE = os.path.join(BASE_DIR, "preview_response.html")
THEME_DIR = os.path.join(BASE_DIR, "qilin-theme")
MAPPING_FILE = os.path.join(BASE_DIR, "resource_mapping.json")

def main():
    # Load resource mapping
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)
        
    # Read original HTML
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()
        
    # 1. Replace resources in HTML
    # Replace CSS
    for orig, local in mapping['css'].items():
        html = html.replace(orig, f"<?php echo get_template_directory_uri(); ?>/{local}")
        
    # Replace JS
    for orig, local in mapping['js'].items():
        html = html.replace(orig, f"<?php echo get_template_directory_uri(); ?>/{local}")
        
    # Replace Images
    for orig, local in mapping['img'].items():
        html = html.replace(orig, f"<?php echo get_template_directory_uri(); ?>/{local}")

    # Add custom handler JS before </body> tag
    custom_js = """
    <!-- Custom WordPress Form Handler -->
    <script type="text/javascript">
    $(document).ready(function() {
        // Tilda might submit dynamically, we intercept submit event on any .t-form
        $(document).on('submit', '.t-form', function(e) {
            e.preventDefault();
            var $form = $(this);
            var $btn = $form.find('.t-submit');
            
            // Wait a tiny bit for Tilda's validator to run
            setTimeout(function() {
                // If form has error control active, stop
                if ($form.find('.js-error-control, .t-input-error_active').length > 0) {
                    return false;
                }
                
                $btn.addClass('t-btn_sending').prop('disabled', true);
                
                // Collect form data
                var formData = $form.serialize();
                
                $.ajax({
                    type: 'POST',
                    url: '<?php echo get_template_directory_uri(); ?>/sendmail.php',
                    data: formData,
                    dataType: 'json',
                    success: function(response) {
                        $btn.removeClass('t-btn_sending').prop('disabled', false);
                        if (response.success) {
                            // Show success message and hide inputs like Tilda does
                            $form.find('.t-form__inputsbox').hide();
                            $form.find('.js-successbox').text(response.message || 'Спасибо! Ваша заявка успешно отправлена.').show();
                        } else {
                            alert(response.message || 'Произошла ошибка при отправке.');
                        }
                    },
                    error: function() {
                        $btn.removeClass('t-btn_sending').prop('disabled', false);
                        alert('Произошла ошибка при отправке запроса.');
                    }
                });
            }, 100);
            
            return false;
        });
    });
    </script>
    """
    
    html = html.replace("</body>", f"{custom_js}\n</body>")

    # 2. Write index.php
    with open(os.path.join(THEME_DIR, "index.php"), "w", encoding="utf-8") as f:
        f.write(html)
    print("Created index.php")
    
    # 3. Write style.css
    style_css = """/*
Theme Name: Qilin Theme
Theme URI: https://доставкакитай.рф
Description: Customized theme imported 1-to-1 from Tilda for Qilin
Author: Antigravity AI
Version: 1.0
*/
"""
    with open(os.path.join(THEME_DIR, "style.css"), "w", encoding="utf-8") as f:
        f.write(style_css)
    print("Created style.css")
    
    # 4. Write functions.php
    functions_php = """<?php
// Qilin Theme Functions
add_action('wp_enqueue_scripts', 'qilin_enqueue_styles_and_scripts');

function qilin_enqueue_styles_and_scripts() {
    // We already load them directly in index.php for a 1-to-1 match.
    // If needed, standard WP enqueues can be registered here.
}
?>"""
    with open(os.path.join(THEME_DIR, "functions.php"), "w", encoding="utf-8") as f:
        f.write(functions_php)
    print("Created functions.php")
    
    # 5. Write sendmail.php (AJAX Mail Handler)
    sendmail_php = """<?php
header('Content-Type: application/json; charset=utf-8');

// Target email
$to_email = "sales@доставкакитай.рф";
$subject = "Новая заявка с сайта ДоставкаКитай.рф (Ци Линь)";

// Retrieve form values
$name = isset($_POST['Name']) ? trim(strip_tags($_POST['Name'])) : '';
$email = isset($_POST['Email']) ? trim(strip_tags($_POST['Email'])) : '';
$phone = isset($_POST['Phone']) ? trim(strip_tags($_POST['Phone'])) : '';
$message_text = isset($_POST['message']) ? trim(strip_tags($_POST['message'])) : ''; // Tilda text area name

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
$headers = "MIME-Version: 1.0" . "\\r\\n";
$headers .= "Content-Type: text/plain; charset=UTF-8" . "\\r\\n";
$headers .= "From: no-reply@доставкакитай.рф" . "\\r\\n";
$headers .= "Reply-To: " . (!empty($email) ? $email : "no-reply@доставкакитай.рф") . "\\r\\n";

// Send email
$success = mail($to_email, $subject, $message, $headers);

if ($success) {
    echo json_encode(array('success' => true, 'message' => 'Спасибо! Ваша заявка успешно отправлена. Мы свяжемся с вами в ближайшее время.'));
} else {
    echo json_encode(array('success' => false, 'message' => 'Не удалось отправить сообщение. Пожалуйста, обратитесь к администратору хостинга.'));
}
?>"""
    with open(os.path.join(THEME_DIR, "sendmail.php"), "w", encoding="utf-8") as f:
        f.write(sendmail_php)
    print("Created sendmail.php")

if __name__ == "__main__":
    main()
