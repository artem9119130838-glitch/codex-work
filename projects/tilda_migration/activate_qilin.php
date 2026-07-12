<?php
// WordPress Auto-Activation & Admin Creation Script
require_once('wp-load.php');

echo "WordPress Loaded successfully.\n";

// 1. Programmatically activate our theme
$theme_name = 'qilin-theme';
update_option('template', $theme_name);
update_option('stylesheet', $theme_name);
echo "Theme 'qilin-theme' activated.\n";

// 2. Programmatically create admin user
$username = 'qilin_admin';
$password = 'QilinAdmin2026!';
$email = 'sales@доставкакитай.рф';

if (!username_exists($username)) {
    $user_id = wp_create_user($username, $password, $email);
    if (is_wp_error($user_id)) {
        echo "Error creating user: " . $user_id->get_error_message() . "\n";
    } else {
        $user = new WP_User($user_id);
        $user->set_role('administrator');
        echo "Admin user 'qilin_admin' created successfully! Password: " . $password . "\n";
    }
} else {
    $user = get_user_by('login', $username);
    wp_set_password($password, $user->ID);
    echo "Admin user 'qilin_admin' already exists. Password updated to: " . $password . "\n";
}

// Self-destruct for security
unlink(__FILE__);
echo "Script self-destructed successfully.\n";
?>