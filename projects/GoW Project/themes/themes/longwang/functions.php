<?php

/**
 * longwang functions and definitions
 *
 * @link https://developer.wordpress.org/themes/basics/theme-functions/
 *
 * @package longwang
 */

if (!defined('_S_VERSION')) {
	// Replace the version number of the theme on each release.
	define('_S_VERSION', '1.0.0');
}

function lw_asset_version($relative_path, $fallback = _S_VERSION)
{
	$file_path = get_template_directory() . $relative_path;

	if (file_exists($file_path)) {
		return (string) filemtime($file_path);
	}

	return $fallback;
}

function lw_enqueue_scripts()
{
	wp_enqueue_style('lw-style', get_template_directory_uri() . '/assets/css/style.min.css', array(), lw_asset_version('/assets/css/style.min.css'), 'all');

	wp_enqueue_style('lw-customstyle', get_template_directory_uri() . '/assets/css/custom.css', array(), lw_asset_version('/assets/css/custom.css'), 'all');

	wp_enqueue_script('lw-script', get_template_directory_uri() . '/assets/js/app.min.js', array(), lw_asset_version('/assets/js/app.min.js'), true);

	wp_enqueue_script('lw-customscript', get_template_directory_uri() . '/assets/js/custom.js', array(), lw_asset_version('/assets/js/custom.js'), true);
}

add_action('wp_enqueue_scripts', 'lw_enqueue_scripts');

/**
 * Sets up theme defaults and registers support for various WordPress features.
 *
 * Note that this function is hooked into the after_setup_theme hook, which
 * runs before the init hook. The init hook is too late for some features, such
 * as indicating support for post thumbnails.
 */
function longwang_setup()
{
	/*
		* Make theme available for translation.
		* Translations can be filed in the /languages/ directory.
		* If you're building a theme based on longwang, use a find and replace
		* to change 'longwang' to the name of your theme in all the template files.
		*/
	load_theme_textdomain('longwang', get_template_directory() . '/languages');

	// Add default posts and comments RSS feed links to head.
	add_theme_support('automatic-feed-links');

	/*
		* Let WordPress manage the document title.
		* By adding theme support, we declare that this theme does not use a
		* hard-coded <title> tag in the document head, and expect WordPress to
		* provide it for us.
		*/
	add_theme_support('title-tag');

	/*
		* Enable support for Post Thumbnails on posts and pages.
		*
		* @link https://developer.wordpress.org/themes/functionality/featured-images-post-thumbnails/
		*/
	add_theme_support('post-thumbnails');

	// This theme uses wp_nav_menu() in one location.
	register_nav_menus(
		array(
			'menu-1' => esc_html__('Primary', 'longwang'),
		)
	);

	/*
		* Switch default core markup for search form, comment form, and comments
		* to output valid HTML5.
		*/
	add_theme_support(
		'html5',
		array(
			'search-form',
			'comment-form',
			'comment-list',
			'gallery',
			'caption',
			'style',
			'script',
		)
	);

	// Set up the WordPress core custom background feature.
	add_theme_support(
		'custom-background',
		apply_filters(
			'longwang_custom_background_args',
			array(
				'default-color' => 'ffffff',
				'default-image' => '',
			)
		)
	);

	// Add theme support for selective refresh for widgets.
	add_theme_support('customize-selective-refresh-widgets');

	/**
	 * Add support for core custom logo.
	 *
	 * @link https://codex.wordpress.org/Theme_Logo
	 */
	add_theme_support(
		'custom-logo',
		array(
			'height'      => 250,
			'width'       => 250,
			'flex-width'  => true,
			'flex-height' => true,
		)
	);
	register_nav_menus(array(
		'header_nav' => 'Header Navigation',
		'footer_nav' => 'Footer Navigation'
	));
}
add_action('after_setup_theme', 'longwang_setup');

/**
 * Set the content width in pixels, based on the theme's design and stylesheet.
 *
 * Priority 0 to make it available to lower priority callbacks.
 *
 * @global int $content_width
 */
function longwang_content_width()
{
	$GLOBALS['content_width'] = apply_filters('longwang_content_width', 640);
}
add_action('after_setup_theme', 'longwang_content_width', 0);

/**
 * Register widget area.
 *
 * @link https://developer.wordpress.org/themes/functionality/sidebars/#registering-a-sidebar
 */
function longwang_widgets_init()
{
	register_sidebar(
		array(
			'name'          => esc_html__('Sidebar', 'longwang'),
			'id'            => 'sidebar-1',
			'description'   => esc_html__('Add widgets here.', 'longwang'),
			'before_widget' => '<section id="%1$s" class="widget %2$s">',
			'after_widget'  => '</section>',
			'before_title'  => '<h2 class="widget-title">',
			'after_title'   => '</h2>',
		)
	);
}
add_action('widgets_init', 'longwang_widgets_init');

/**
 * Enqueue scripts and styles.
 */
function longwang_scripts()
{
	wp_enqueue_style('longwang-style', get_stylesheet_uri(), array(), lw_asset_version('/style.css'));
	wp_style_add_data('longwang-style', 'rtl', 'replace');

	wp_enqueue_script('longwang-navigation', get_template_directory_uri() . '/js/navigation.js', array(), lw_asset_version('/js/navigation.js'), true);

	if (is_singular() && comments_open() && get_option('thread_comments')) {
		wp_enqueue_script('comment-reply');
	}
}
add_action('wp_enqueue_scripts', 'longwang_scripts');

function lw_defer_theme_scripts($tag, $handle, $src)
{
	$deferred_handles = array(
		'lw-script',
		'lw-customscript',
		'longwang-navigation',
	);

	if (is_admin() || !in_array($handle, $deferred_handles, true)) {
		return $tag;
	}

	if (strpos($tag, ' defer') !== false) {
		return $tag;
	}

	return str_replace('<script ', '<script defer ', $tag);
}
add_filter('script_loader_tag', 'lw_defer_theme_scripts', 10, 3);

function lw_external_resource_hints($urls, $relation_type)
{
	$domains = array(
		'https://mc.yandex.ru',
		'https://www.googletagmanager.com',
		'https://my.novofon.com',
		'https://widget.novofon.ru',
	);

	if ('preconnect' === $relation_type) {
		foreach ($domains as $domain) {
			$urls[] = array(
				'href'        => $domain,
				'crossorigin' => 'anonymous',
			);
		}
	}

	if ('dns-prefetch' === $relation_type) {
		foreach ($domains as $domain) {
			$urls[] = $domain;
		}
	}

	return $urls;
}
add_filter('wp_resource_hints', 'lw_external_resource_hints', 10, 2);

/**
 * Implement the Custom Header feature.
 */
require get_template_directory() . '/inc/custom-header.php';

/**
 * Custom template tags for this theme.
 */
require get_template_directory() . '/inc/template-tags.php';

/**
 * Functions which enhance the theme by hooking into WordPress.
 */
require get_template_directory() . '/inc/template-functions.php';

/**
 * Customizer additions.
 */
require get_template_directory() . '/inc/customizer.php';

/**
 * Load Jetpack compatibility file.
 */
if (defined('JETPACK__VERSION')) {
	require get_template_directory() . '/inc/jetpack.php';
}

add_filter('wpcf7_autop_or_not', '__return_false');
add_filter('wpcf7_form_elements', function ($content) {
	$content = preg_replace('/<(span).*?class="\s*(?:.*\s)?wpcf7-form-control-wrap(?:\s[^"]+)?\s*"[^\>]*>(.*)<\/\1>/i', '\2', $content);
	return $content;
});

// COLORS ------------------------------------------------------------------------------------------------------------

add_action('after_setup_theme', 'truemisha_color_palette');

function truemisha_color_palette()
{
	add_theme_support(
		'editor-color-palette',
		array(
			array(
				'name'  => 'Красный',
				'slug'  => 'cust-red',
				'color'	=> '#CC2034',
			),
			array(
				'name'  => 'Синий',
				'slug'  => 'cust-blue',
				'color' => '#293B6E',
			),
		)
	);
}

// ======================================================================================================================

add_theme_support('align-wide');

// Clear Title Tag ======================================================================================================

add_filter('get_the_archive_title', function ($title) {
	return preg_replace('~^[^:]+: ~', '', $title);
});

// ======================================================================================================================

add_filter('excerpt_more', fn () => '...');

function hwl_home_pagesize($query)
{
	if (is_post_type_archive('news')) {
		$query->set('posts_per_page', 6);
		return;
	}
}

add_action('pre_get_posts', 'hwl_home_pagesize', 1);

// MENU =================================================================================================================

class My_Walker_Nav_Menu extends Walker_Nav_Menu
{

	// add classes to ul sub-menus
	function start_lvl(&$output, $depth = 0, $args = NULL)
	{
		// depth dependent classes
		$indent = ($depth > 0  ? str_repeat("\t", $depth) : ''); // code indent
		$display_depth = ($depth + 1); // because it counts the first submenu as 0
		$classes = array(
			'sub-menu menu__submenu',
			($display_depth % 2  ? 'menu-odd' : 'menu-even'),
			($display_depth >= 2 ? 'sub-sub-menu' : ''),
			'menu-depth-' . $display_depth
		);
		$class_names = implode(' ', $classes);

		// build html
		$output .= "\n" . $indent . '<ul class="' . $class_names . '">' . "\n";
	}

	// add main/sub classes to li's and links
	function start_el(&$output, $data_object, $depth = 0, $args = null, $current_object_id = 0)
	{
		global $wp_query;

		// Restores the more descriptive, specific name for use within this method.
		$item = $data_object;

		$indent = ($depth > 0 ? str_repeat("\t", $depth) : ''); // code indent

		// depth dependent classes
		$depth_classes = array(
			($depth == 0 ? 'main-menu-item' : 'sub-menu-item'),
			($depth >= 2 ? 'sub-sub-menu-item' : ''),
			($depth % 2 ? 'menu-item-odd' : 'menu-item-even'),
			'menu-item-depth-' . $depth
		);
		$depth_class_names = esc_attr(implode(' ', $depth_classes));

		// passed classes
		$classes = empty($item->classes) ? array() : (array) $item->classes;
		$class_names = esc_attr(implode(' ', apply_filters('nav_menu_css_class', array_filter($classes), $item)));

		// build html
		if ($args->walker->has_children) {
			$output .= $indent . '<li id="nav-menu-item-' . $item->ID . '" class="' . $depth_class_names . ' ' . $class_names . ' menu__item menu__item--hassub"><div class="menu__btn">';
		} else {
			$output .= $indent . '<li id="nav-menu-item-' . $item->ID . '" class="' . $depth_class_names . ' ' . $class_names . ' menu__item"><div class="menu__btn">';
		}


		// link attributes
		$attributes  = !empty($item->attr_title) ? ' title="'  . esc_attr($item->attr_title) . '"' : '';
		$attributes .= !empty($item->target)     ? ' target="' . esc_attr($item->target) . '"' : '';
		$attributes .= !empty($item->xfn)        ? ' rel="'    . esc_attr($item->xfn) . '"' : '';
		$attributes .= !empty($item->url)        ? ' href="'   . esc_attr($item->url) . '"' : '';
		$attributes .= ' class="menu__link ' . ($depth > 0 ? 'sub-menu-link' : 'main-menu-link') . '"';

		$item_output = sprintf(
			'%1$s<a%2$s><div><p>%3$s%4$s%5$s</p></div></a>%6$s',
			$args->before,
			$attributes,
			$args->link_before,
			apply_filters('the_title', $item->title, $item->ID),
			$args->link_after,
			$args->after
		);

		// build html
		$output .= apply_filters('walker_nav_menu_start_el', $item_output, $item, $depth, $args);
		if ($args->walker->has_children) {
			$output .= '<button class="menu__drop-arrow">
			<svg xmlns="http://www.w3.org/2000/svg" width="10" height="5" viewBox="0 0 10 5"
				fill="none">
				<path d="M5 5L9.33013 0.5H0.669873L5 5Z" fill="#4A494E" />
			</svg>
		</button></div>';
		} else {
			$output .= '</div>';
		}
	}
}

function my_nav_menu($args)
{

	$args = array_merge([
		'container'       => false,
		'menu_class'      => 'menu__list',
		'echo'            => false,
		'items_wrap'      => '<ul id="%1$s" class="%2$s">%3$s</ul>',
		'depth'           => 10,
		'walker'          => new My_Walker_Nav_Menu()
	], $args);

	echo wp_nav_menu($args);
}


// ==================================================================================================================

function mytheme_customize_register($wp_customize)
{
	/*
	Добавляем секцию в настройки темы
	*/
	$wp_customize->add_section(
		// ID
		'data_site_section',
		// Массив аргументов
		array(
			'title' => 'Телефон и соц. сети',
			'capability' => 'edit_theme_options',
			'description' => "Тут можно указать контактные данные"
		)
	);

	$wp_customize->add_setting(
		// ID
		'site_vk',
		// Массив аргументов
		array(
			'default' => '',
			'type' => 'option'
		)
	);
	$wp_customize->add_control(
		// ID
		'site_vk_control',
		// Массив аргументов
		array(
			'type' => 'text',
			'label' => "Ссылка на ВК",
			'section' => 'data_site_section',
			'settings' => 'site_vk'
		)
	);

	$wp_customize->add_setting(
		// ID
		'site_telega',
		// Массив аргументов
		array(
			'default' => '',
			'type' => 'option'
		)
	);
	$wp_customize->add_control(
		// ID
		'site_telega_control',
		// Массив аргументов
		array(
			'type' => 'text',
			'label' => "Ссылка на Telegram",
			'section' => 'data_site_section',
			'settings' => 'site_telega'
		)
	);

	// Site Tel
	$wp_customize->add_setting(
		// ID
		'site_telephone',
		// Массив аргументов
		array(
			'default' => '',
			'type' => 'option'
		)
	);
	$wp_customize->add_control(
		// ID
		'site_telephone_control',
		// Массив аргументов
		array(
			'type' => 'text',
			'label' => "Телефон для вывода на сайте",
			'section' => 'data_site_section',
			'settings' => 'site_telephone'
		)
	);
	$wp_customize->add_setting(
		// ID
		'site_telephone_call',
		// Массив аргументов
		array(
			'default' => '',
			'type' => 'option'
		)
	);
	$wp_customize->add_control(
		// ID
		'site_telephone_call_control',
		// Массив аргументов
		array(
			'type' => 'text',
			'label' => "Телефон без пробелов",
			'section' => 'data_site_section',
			'settings' => 'site_telephone_call'
		)
	);

	$wp_customize->add_setting(
		// ID
		'site_email',
		// Массив аргументов
		array(
			'default' => '',
			'type' => 'option'
		)
	);
	$wp_customize->add_control(
		// ID
		'site_email_control',
		// Массив аргументов
		array(
			'type' => 'text',
			'label' => "Почта",
			'section' => 'data_site_section',
			'settings' => 'site_email'
		)
	);
}
add_action('customize_register', 'mytheme_customize_register');
// Добавление файла css для комм страниц оборудования из Китая
add_action('wp_enqueue_scripts', function () {
    if (is_page_template('template-equipment-commercial.php')) {
        wp_enqueue_style(
            'lw-equipment-commercial',
            get_stylesheet_directory_uri() . '/assets/css/template-equipment-commercial.css',
            [],
            filemtime(get_stylesheet_directory() . '/assets/css/template-equipment-commercial.css')
        );
    }
});
// Добавление номера страницы в заголовок и мета-описание для пагинации
add_filter('wpseo_metadesc', 'custom_paginated_description');

function custom_paginated_description($description) {
    if (is_paged()) {
        $paged = get_query_var('paged');
        $description .= ' | Страница ' . $paged;
    }
    return $description;
}

// Отключаем вывод разметки поиска (SearchAction) в Yoast SEO
add_filter( 'disable_wpseo_json_ld_search', '__return_true' );
// Добавление микроразметки FAQPage (унифицированная версия)
add_action('wp_head', 'add_dynamic_faq_schema');
function add_dynamic_faq_schema() {
    if ( ! ( is_front_page() || is_singular() ) ) {
        return;
    }

    $post_id = is_front_page() ? get_option('page_on_front') : get_the_ID();
    $faq = get_field('voprosy', $post_id);

    if ( empty( $faq ) || empty( $faq['spojlery'] ) || ! is_array( $faq['spojlery'] ) ) {
        return;
    }

    $questions = array();
    foreach ( $faq['spojlery'] as $item ) {
        if ( empty( $item['vopros'] ) || empty( $item['otvet'] ) ) {
            continue;
        }
        $answer = wp_strip_all_tags( $item['otvet'] );
        $questions[] = array(
            '@type' => 'Question',
            'name'   => $item['vopros'],
            'acceptedAnswer' => array(
                '@type' => 'Answer',
                'text'  => $answer,
            ),
        );
    }

    if ( empty( $questions ) ) {
        return;
    }

    $schema = array(
        '@context'   => 'https://schema.org',
        '@type'      => 'FAQPage',
        'mainEntity' => $questions,
    );

echo '<script type="application/ld+json">' . wp_json_encode( $schema, JSON_UNESCAPED_UNICODE ) . '</script>' . "\n";
}

/**
 * Keep selected archive sections indexable and self-canonicalised.
 * Fixes Yoast warnings for paginated news/useful archive URLs.
 */
function lw_should_force_archive_indexing() {
    if ( is_home() ) {
        return true;
    }

    if ( is_category( array( 'useful-articles', 'international', 'novosti-iz-kitaya', 'novosti-is-kitaya' ) ) ) {
        return true;
    }

    return false;
}

function lw_get_current_archive_canonical() {
    global $wp;

    if ( empty( $wp->request ) ) {
        return home_url( '/' );
    }

    return home_url( user_trailingslashit( $wp->request ) );
}

add_filter( 'wpseo_robots', function( $robots ) {
    if ( lw_should_force_archive_indexing() ) {
        return 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1';
    }

    return $robots;
} );

add_filter( 'wpseo_canonical', function( $canonical ) {
    if ( lw_should_force_archive_indexing() ) {
        return lw_get_current_archive_canonical();
    }

    return $canonical;
} );
