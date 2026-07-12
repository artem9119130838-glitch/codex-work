<?php
// Qilin Theme Functions
add_action('wp_enqueue_scripts', 'qilin_enqueue_styles_and_scripts');

function qilin_enqueue_styles_and_scripts() {
    // We already load them directly in index.php for a 1-to-1 match.
    // If needed, standard WP enqueues can be registered here.
}
?>