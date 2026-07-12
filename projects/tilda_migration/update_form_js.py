import os
import ftplib

BASE_DIR = "C:/Codex_Personal/projects/tilda_migration"
INDEX_PHP = os.path.join(BASE_DIR, "qilin-theme", "index.php")

# FTP Config
host = "185.26.122.79"
user = "host1847090_qilinftp"
password = "qilin_ftp"

def update_form_js():
    with open(INDEX_PHP, "r", encoding="utf-8") as f:
        content = f.read()
        
    new_js = """
    <!-- Custom WordPress Form Handler -->
    <script type="text/javascript">
    $(document).ready(function() {
        // Intercept submit button click to prevent Tilda scripts from hijacking the form
        $(document).on('click', '.t-form .t-submit', function(e) {
            var $btn = $(this);
            var $form = $btn.closest('.t-form');
            
            // Basic validation check
            var hasError = false;
            $form.find('.js-tilda-rule').each(function() {
                var $input = $(this);
                var val = $input.val().trim();
                var req = $input.attr('data-tilda-req') === '1';
                var rule = $input.attr('data-tilda-rule');
                
                if (req && val === '') {
                    $input.addClass('js-error-control');
                    $input.closest('.t-input-group').find('.t-input-error').text('Поле обязательно для заполнения').show();
                    $input.closest('.t-input-group').find('.t-input-error').addClass('t-input-error_active');
                    hasError = true;
                } else {
                    $input.removeClass('js-error-control');
                    $input.closest('.t-input-group').find('.t-input-error').hide();
                    $input.closest('.t-input-group').find('.t-input-error').removeClass('t-input-error_active');
                }
                
                if (val !== '' && rule === 'email') {
                    var emailReg = /^([\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4})?$/;
                    if (!emailReg.test(val)) {
                        $input.addClass('js-error-control');
                        $input.closest('.t-input-group').find('.t-input-error').text('Некорректный email').show();
                        $input.closest('.t-input-group').find('.t-input-error').addClass('t-input-error_active');
                        hasError = true;
                    }
                }
            });
            
            if (hasError) {
                e.preventDefault();
                e.stopImmediatePropagation();
                return false;
            }
            
            // Prevent standard submit and stop other Tilda click handlers
            e.preventDefault();
            e.stopImmediatePropagation();
            
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
                    alert('Произошла ошибка при отправке запроса. Пожалуйста, проверьте SSL-сертификат домена.');
                }
            });
            
            return false;
        });
    });
    </script>
    """
    
    # Check if there is already a custom script handler and remove it
    if "<!-- Custom WordPress Form Handler -->" in content:
        # Split content before the handler tag
        parts = content.split("<!-- Custom WordPress Form Handler -->")
        # Find </body> in the second part and split it
        second_part = parts[1]
        body_parts = second_part.split("</body>")
        # Reconstruct without the old script
        content_updated = parts[0] + new_js + "\n</body>" + body_parts[1]
    else:
        # Just insert before </body>
        content_updated = content.replace("</body>", f"{new_js}\n</body>")
        
    with open(INDEX_PHP, "w", encoding="utf-8") as f:
        f.write(content_updated)
    print("index.php updated with new form JS via split/join method.")
    
    # Upload to FTP
    print("Uploading updated index.php to FTP...")
    ftp = ftplib.FTP()
    ftp.connect(host)
    ftp.login(user, password)
    
    with open(INDEX_PHP, "rb") as f:
        ftp.storbinary("STOR htdocs/www/wp-content/themes/qilin-theme/index.php", f)
        
    ftp.quit()
    print("FTP upload complete.")

if __name__ == "__main__":
    update_form_js()
