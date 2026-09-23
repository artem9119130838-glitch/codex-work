import os
import ftplib
import requests

host = "185.26.122.79"
user = "host1847090_qilinftp"
password = "qilin_ftp"
local_theme_dir = "C:/Codex_Personal/projects/tilda_migration/qilin-theme"
remote_theme_dir = "htdocs/www/wp-content/themes/qilin-theme"

def upload_dir(ftp, local_dir, remote_dir):
    print(f"Uploading {local_dir} to {remote_dir}...")
    
    # Get relative files/dirs
    for root, dirs, files in os.walk(local_dir):
        # Calculate relative path
        rel_path = os.path.relpath(root, local_dir)
        if rel_path == ".":
            target_dir = remote_dir
        else:
            # Replace windows slashes with ftp slashes
            rel_path_ftp = rel_path.replace("\\", "/")
            target_dir = f"{remote_dir}/{rel_path_ftp}"
            
        # Try to create directory on FTP
        try:
            ftp.mkd(target_dir)
            print(f"Created remote directory: {target_dir}")
        except Exception as e:
            # Directory probably already exists
            pass
            
        # Upload files in this directory
        for file in files:
            local_file_path = os.path.join(root, file)
            remote_file_path = f"{target_dir}/{file}"
            
            # Print upload progress for large images
            # print(f"Uploading file: {file} -> {remote_file_path}")
            try:
                with open(local_file_path, "rb") as f:
                    ftp.storbinary(f"STOR {remote_file_path}", f)
            except Exception as e:
                print(f"Failed to upload {file}: {e}")

def create_activation_script():
    script_content = """<?php
// WordPress Auto-Activation & Admin Creation Script
require_once('wp-load.php');

echo "WordPress Loaded successfully.\\n";

// 1. Programmatically activate our theme
$theme_name = 'qilin-theme';
update_option('template', $theme_name);
update_option('stylesheet', $theme_name);
echo "Theme 'qilin-theme' activated.\\n";

// 2. Programmatically create admin user
$username = 'qilin_admin';
$password = 'QilinAdmin2026!';
$email = 'sales@доставкакитай.рф';

if (!username_exists($username)) {
    $user_id = wp_create_user($username, $password, $email);
    if (is_wp_error($user_id)) {
        echo "Error creating user: " . $user_id->get_error_message() . "\\n";
    } else {
        $user = new WP_User($user_id);
        $user->set_role('administrator');
        echo "Admin user 'qilin_admin' created successfully! Password: " . $password . "\\n";
    }
} else {
    $user = get_user_by('login', $username);
    wp_set_password($password, $user->ID);
    echo "Admin user 'qilin_admin' already exists. Password updated to: " . $password . "\\n";
}

// Self-destruct for security
unlink(__FILE__);
echo "Script self-destructed successfully.\\n";
?>"""
    script_path = "C:/Codex_Personal/projects/tilda_migration/activate_qilin.php"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    print("Created activation script locally.")
    return script_path

def main():
    # 1. Connect FTP
    ftp = ftplib.FTP()
    ftp.connect(host)
    ftp.login(user, password)
    
    # 2. Upload theme files
    upload_dir(ftp, local_theme_dir, remote_theme_dir)
    
    # 3. Create and upload activation script
    script_local = create_activation_script()
    script_remote = "htdocs/www/activate_qilin.php"
    print(f"Uploading activation script to {script_remote}...")
    with open(script_local, "rb") as f:
        ftp.storbinary(f"STOR {script_remote}", f)
        
    ftp.quit()
    print("FTP operations complete.")
    
    # 4. Trigger activation script via HTTP request with Host header
    domain = "xn--80aaagi1aieb9a7amg.xn--p1ai" # доставкакитай.рф
    activation_url = f"http://{host}/activate_qilin.php"
    print(f"Triggering activation script at {activation_url} with Host header '{domain}'...")
    
    try:
        r = requests.get(activation_url, headers={'Host': domain}, timeout=15)
        print("Response status:", r.status_code)
        print("Response body:\n", r.text)
    except Exception as e:
        print("HTTP request trigger failed:", e)
        print("You can try requesting http://доставкакитай.рф/activate_qilin.php manually in your browser.")

if __name__ == "__main__":
    main()
