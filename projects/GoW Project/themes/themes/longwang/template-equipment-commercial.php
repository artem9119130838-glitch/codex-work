<?php
/*
Template Name: Equipment Commercial Page
*/

defined('ABSPATH') || exit;

get_header();

$page_id = get_queried_object_id();

if (!function_exists('lw_eq_get_field')) {
    function lw_eq_get_field($field_name, $default = null, $post_id = false) {
        if (!function_exists('get_field')) {
            return $default;
        }

        $value = get_field($field_name, $post_id);

        if ($value === null || $value === false || $value === '') {
            return $default;
        }

        return $value;
    }
}

if (!function_exists('lw_eq_get_subvalue')) {
    function lw_eq_get_subvalue($array, $key, $default = '') {
        return (is_array($array) && isset($array[$key]) && $array[$key] !== '' && $array[$key] !== null)
            ? $array[$key]
            : $default;
    }
}

if (!function_exists('lw_eq_get_image_data')) {
    function lw_eq_get_image_data($value, $default_alt = '') {
        $result = [
            'url'   => '',
            'alt'   => $default_alt,
            'title' => '',
        ];

        if (empty($value)) {
            return $result;
        }

        if (is_string($value)) {
            $result['url'] = $value;
            return $result;
        }

        if (is_numeric($value)) {
            $attachment_id = (int) $value;
            $url = wp_get_attachment_image_url($attachment_id, 'full');
            if ($url) {
                $result['url'] = $url;
            }

            $alt = get_post_meta($attachment_id, '_wp_attachment_image_alt', true);
            $title = get_the_title($attachment_id);

            if (!empty($alt)) {
                $result['alt'] = $alt;
            }

            if (!empty($title)) {
                $result['title'] = $title;
            }

            return $result;
        }

        if (is_array($value)) {
            if (!empty($value['url'])) {
                $result['url'] = (string) $value['url'];
            }

            if (!empty($value['alt'])) {
                $result['alt'] = (string) $value['alt'];
            }

            if (!empty($value['title'])) {
                $result['title'] = (string) $value['title'];
            }

            return $result;
        }

        return $result;
    }
}

if (!function_exists('lw_eq_split_lines')) {
    function lw_eq_split_lines($text) {
        $text = is_string($text) ? trim($text) : '';

        if ($text === '') {
            return [];
        }

        $text = str_replace(['<br />', '<br/>', '<br>'], "\n", $text);
        $text = wp_strip_all_tags($text);

        $lines = preg_split('/\r\n|\r|\n/', $text);

        if (!is_array($lines)) {
            return [];
        }

        $lines = array_map('trim', $lines);
        $lines = array_filter($lines, static function ($line) {
            return $line !== '';
        });

        return array_values($lines);
    }
}

if (!function_exists('lw_eq_render_wysiwyg')) {
    function lw_eq_render_wysiwyg($html, $fallback = '') {
        $html = is_string($html) ? trim($html) : '';

        if ($html === '') {
            if ($fallback === '') {
                return '';
            }

            return '<p>' . esc_html($fallback) . '</p>';
        }

        return wp_kses_post($html);
    }
}

$hero       = lw_eq_get_field('hero', [], $page_id);
$advantages = lw_eq_get_field('advantages', [], $page_id);
$models     = lw_eq_get_field('equipment_models', [], $page_id);
$desc       = lw_eq_get_field('category_description', '', $page_id);
$specs      = lw_eq_get_field('specs_table', '', $page_id);
$options    = lw_eq_get_field('options', [], $page_id);
$features   = lw_eq_get_field('features', [], $page_id);
$faq        = lw_eq_get_field('faq', [], $page_id);
$section_titles = lw_eq_get_field('section_titles', [], $page_id);

$advantages_title = isset($section_titles['advantages_title']) && $section_titles['advantages_title'] !== ''
    ? $section_titles['advantages_title']
    : 'Преимущества';

$specs_title = isset($section_titles['specs_title']) && $section_titles['specs_title'] !== ''
    ? $section_titles['specs_title']
    : 'Характеристики';

$options_title = isset($section_titles['options_title']) && $section_titles['options_title'] !== ''
    ? $section_titles['options_title']
    : 'Варианты поставки и опции';

$features_title = isset($section_titles['features_title']) && $section_titles['features_title'] !== ''
    ? $section_titles['features_title']
    : 'Преимущества и особенности';
$models_title = isset($section_titles['models_title']) && $section_titles['models_title'] !== ''
    ? $section_titles['models_title']
    : 'Модельный ряд';

$hero_title    = lw_eq_get_subvalue($hero, 'zagolovok', get_the_title($page_id));
$hero_subtitle = lw_eq_get_subvalue($hero, 'podzagolovok', '');
$hero_image    = lw_eq_get_image_data(lw_eq_get_subvalue($hero, 'izobrazhenie', ''), $hero_title);

$form_title    = 'Заявка на консультацию';
$form_shortcode = '[contact-form-7 id="9071" title="Контактная форма" html_class="eq-form__cf7"]';
?>

<main class="eq-page">
 <section class="eq-hero hero-main">
<div class="breadcrumbs">
    <div class="breadcrumbs__container">
        <p id="breadcrumbs">
            <span>
                <span><a href="<?php echo esc_url(home_url('/')); ?>">Главная страница</a></span>
                <?php
                $ancestors = array_reverse(get_post_ancestors($page_id));

                if (!empty($ancestors)) {
                    foreach ($ancestors as $ancestor_id) {
                        echo ' » <span><a href="' . esc_url(get_permalink($ancestor_id)) . '">' . esc_html(get_the_title($ancestor_id)) . '</a></span>';
                    }
                }
                ?>
                » <span class="breadcrumb_last" aria-current="page"><?php echo esc_html(get_the_title($page_id)); ?></span>
            </span>
        </p>
    </div>
</div>

    <div class="hero-main__container eq-hero__container">
        <div class="hero-main__top eq-hero__top">
            <div class="hero-main__offer eq-hero__offer">
                <?php if (!empty($hero_title)) : ?>
                    <h1 class="hero-main__title eq-hero__title"><?php echo esc_html($hero_title); ?></h1>
                <?php endif; ?>

                <?php if (!empty($hero_subtitle)) : ?>
                    <div class="hero-main__subtitle eq-hero__subtitle">
                        <p><?php echo esc_html($hero_subtitle); ?></p>
                    </div>
                <?php endif; ?>

                <a class="hero-main__btn _btn eq-hero__btn" href="#eq-form">Оставить заявку</a>
            </div>

            <div class="hero-main__hexagons eq-hero__hexagons">
                <?php if (!empty($hero_image['url'])) : ?>
                    <div class="hero-main__hexagon-img eq-hero__hexagon-img">
                        <img
                            src="<?php echo esc_url($hero_image['url']); ?>"
                            alt="<?php echo esc_attr($hero_image['alt']); ?>"
                            title="<?php echo esc_attr($hero_image['title']); ?>"
                            class="hero-main__hexagon-media"
                            width="337"
                            height="389"
                            fetchpriority="high"
                            loading="eager"
                            decoding="async"
                        >
                    </div>
                <?php else : ?>
                    <div class="hero-main__hexagon-img eq-hero__hexagon-img eq-hero__hexagon-img--empty">
                        <div class="eq-hero__placeholder">Изображение оборудования</div>
                    </div>
                <?php endif; ?>

                <div class="hero-main__hexagon-middle eq-hero__hexagon-middle">
                    <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                        <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
                    </svg>
                </div>

                <div class="hero-main__hexagon-big eq-hero__hexagon-big">
                    <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                        <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
                    </svg>
                </div>

                <div class="hero-main__hexagon-small eq-hero__hexagon-small">
                    <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                        <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
                    </svg>
                </div>
            </div>
        </div>
    </div>
</section>

    <?php
    $has_advantages = is_array($advantages) && !empty($advantages);
    if ($has_advantages) :
    ?>
        <section class="eq-section eq-advantages">
            <div class="eq-container">
<?php if (!empty($advantages_title)) : ?>
    <div class="eq-section-head">
        <h2 class="eq-section-title"><?php echo esc_html($advantages_title); ?></h2>
    </div>
<?php endif; ?>
                <div class="eq-advantages__grid">
                    <?php foreach ($advantages as $item) : ?>
                        <?php
                        if (!is_array($item)) {
                            continue;
                        }

                        $item_text  = lw_eq_get_subvalue($item, 'tekst', '');
                        $item_alt   = lw_eq_get_subvalue($item, 'img_alt', $item_text);
                        $item_title = lw_eq_get_subvalue($item, 'img_title', '');
                        $item_img   = lw_eq_get_image_data(lw_eq_get_subvalue($item, 'ikonka', ''), $item_alt);

                        if ($item_text === '' && empty($item_img['url'])) {
                            continue;
                        }
                        ?>
                        <article class="eq-adv-card">
                            <div class="eq-adv-card__inner">
                                <?php if (!empty($item_img['url'])) : ?>
                                    <div class="eq-adv-card__icon">
                                        <img
                                            src="<?php echo esc_url($item_img['url']); ?>"
                                            alt="<?php echo esc_attr($item_alt); ?>"
                                            <?php echo !empty($item_title) ? 'title="' . esc_attr($item_title) . '"' : ''; ?>
                                            loading="lazy"
                                            decoding="async"
                                        >
                                    </div>
                                <?php endif; ?>

                                <?php if ($item_text !== '') : ?>
                                    <div class="eq-adv-card__text"><?php echo esc_html($item_text); ?></div>
                                <?php endif; ?>
                            </div>
                        </article>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <?php
    $has_models = is_array($models) && !empty($models);
    if ($has_models) :
    ?>
        <section class="eq-section eq-models">
            <div class="eq-container">
                <div class="eq-section-head">
                    <h2 class="eq-section-title"><?php echo esc_html($models_title); ?></h2>
                </div>

                <div class="eq-models__grid">
                    <?php foreach ($models as $model) : ?>
                        <?php
                        if (!is_array($model)) {
                            continue;
                        }

                        $model_name      = lw_eq_get_subvalue($model, 'nazvanie', '');
                        $model_alt       = lw_eq_get_subvalue($model, 'img_alt', $model_name);
                        $model_title     = lw_eq_get_subvalue($model, 'img_title', '');
                        $model_image     = lw_eq_get_image_data(lw_eq_get_subvalue($model, 'izobrazhenie', ''), $model_alt);
                        $model_lines     = lw_eq_split_lines((string) lw_eq_get_subvalue($model, 'harakteristiki', ''));

                        if ($model_name === '' && empty($model_image['url']) && empty($model_lines)) {
                            continue;
                        }
                        ?>
                        <article class="eq-model-card">
                            <div class="eq-model-card__media">
                                <?php if (!empty($model_image['url'])) : ?>
                                    <img
                                        class="eq-model-card__image"
                                        src="<?php echo esc_url($model_image['url']); ?>"
                                        alt="<?php echo esc_attr($model_alt); ?>"
                                        <?php echo !empty($model_title) ? 'title="' . esc_attr($model_title) . '"' : ''; ?>
                                        loading="lazy"
                                        decoding="async"
                                    >
                                <?php else : ?>
                                    <div class="eq-model-card__placeholder">Фото модели</div>
                                <?php endif; ?>
                            </div>

                            <div class="eq-model-card__body">
                                <?php if ($model_name !== '') : ?>
                                    <h3 class="eq-model-card__title"><?php echo esc_html($model_name); ?></h3>
                                <?php endif; ?>

                                <?php if (!empty($model_lines)) : ?>
                                    <ul class="eq-model-card__list">
                                        <?php foreach ($model_lines as $line) : ?>
                                            <li><?php echo esc_html($line); ?></li>
                                        <?php endforeach; ?>
                                    </ul>
                                <?php endif; ?>
                            </div>
                        </article>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <section class="eq-section eq-models-cta">
        <div class="eq-container">
            <div class="eq-models-cta__wrap">
                <a class="eq-btn" href="#eq-form">Оставить заявку</a>
            </div>
        </div>
    </section>

    <section class="eq-section eq-description">
        <div class="eq-container">
            <div class="eq-wysiwyg">
                <?php echo lw_eq_render_wysiwyg($desc, 'Информация о категории оборудования уточняется.'); ?>
            </div>
        </div>
    </section>

    <?php if (!empty(trim((string) $specs))) : ?>
        <section class="eq-section eq-specs">
            <div class="eq-container">
                <div class="eq-section-head">
                    <h2 class="eq-section-title"><?php echo esc_html($specs_title); ?></h2>
                </div>

                <div class="eq-wysiwyg eq-wysiwyg--specs">
                    <?php echo lw_eq_render_wysiwyg($specs); ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <?php
    $has_options = is_array($options) && !empty($options);
    if ($has_options) :
    ?>
        <section class="eq-section eq-options">
            <div class="eq-container">
                <div class="eq-section-head">
                    <h2 class="eq-section-title"><?php echo esc_html($options_title); ?></h2>
                </div>

                <div class="eq-options__grid">
                    <?php foreach ($options as $item) : ?>
                        <?php
                        if (!is_array($item)) {
                            continue;
                        }

                        $item_text = lw_eq_get_subvalue($item, 'tekst', '');
                        $item_img  = lw_eq_get_image_data(lw_eq_get_subvalue($item, 'ikonka', ''), $item_text);
			$item_alt   = lw_eq_get_subvalue($item, 'img_alt', $item_text);
			$item_title = lw_eq_get_subvalue($item, 'title', '');

                        if ($item_text === '' && empty($item_img['url'])) {
                            continue;
                        }
                        ?>
                        <article class="eq-option-card">
                            <?php if (!empty($item_img['url'])) : ?>
                                <div class="eq-option-card__icon">
                                    <img
                                        src="<?php echo esc_url($item_img['url']); ?>"
                                        alt="<?php echo esc_attr($item_alt); ?>"
    					<?php echo !empty($item_title) ? 'title="' . esc_attr($item_title) . '"' : ''; ?>
                                        loading="lazy"
                                        decoding="async"
                                    >
                                </div>
                            <?php endif; ?>

                            <?php if ($item_text !== '') : ?>
                                <div class="eq-option-card__text"><?php echo esc_html($item_text); ?></div>
                            <?php endif; ?>
                        </article>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <section class="eq-section eq-models-cta">
        <div class="eq-container">
            <div class="eq-models-cta__wrap">
                <a class="eq-btn" href="#eq-form">Оставить заявку</a>
            </div>
        </div>
    </section>

    <?php
    $has_features = is_array($features) && !empty($features);
    if ($has_features) :
    ?>
        <section class="eq-section eq-features">
            <div class="eq-container">
                <div class="eq-section-head">
                    <h2 class="eq-section-title"><?php echo esc_html($features_title); ?></h2>
                </div>

                <div class="eq-features__grid">
                    <?php foreach ($features as $item) : ?>
                        <?php
                        if (!is_array($item)) {
                            continue;
                        }

                        $item_title = lw_eq_get_subvalue($item, 'zagolovok', '');
                        $item_text  = lw_eq_get_subvalue($item, 'tekst', '');

                        if ($item_title === '' && $item_text === '') {
                            continue;
                        }
                        ?>
                        <article class="eq-feature-card">
                            <?php if ($item_title !== '') : ?>
                                <h3 class="eq-feature-card__title"><?php echo esc_html($item_title); ?></h3>
                            <?php endif; ?>

                            <?php if ($item_text !== '') : ?>
                                <div class="eq-feature-card__text">
                                    <p><?php echo nl2br(esc_html($item_text)); ?></p>
                                </div>
                            <?php endif; ?>
                        </article>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>
    <!-- ------------------------------------------------------ Trust ------------------------------------------------------------ -->
   <?php $partners = get_field('partnery', 7); ?>
<section class="main-page__trust trust-main">
    <div class="trust-main__container">
        <h2 class="trust-main__title _title">
            <?php echo esc_html($partners['zagolovok']); ?>
        </h2>

        <div class="trust-main__body">
            <button type="button" class="trust-main__btn-slider trust-main__btn-prev">
                <img src="<?php echo get_stylesheet_directory_uri(); ?>/assets/img/icons/arrow-grey.svg" alt="Previous">
            </button>
            <div class="trust-main__slider swiper">
                <div class="trust-main__wrapper swiper-wrapper">

                    <?php $logos = $partners['logos']; ?>
                    <?php
                    if ($logos && is_array($logos)) {
                        foreach ($logos as $logo) {
                            // Проверяем, что ключи 'url', 'alt' и 'title' существуют
                            $image_url = isset($logo['logo']['url']) ? $logo['logo']['url'] : '';
                            $image_alt = isset($logo['logo']['alt']) ? $logo['logo']['alt'] : 'Логотип';
                            $image_title = isset($logo['logo']['title']) ? $logo['logo']['title'] : '';

                            if ($image_url) {
                                ?>
                                <div class="trust-main__slide swiper-slide">
                                    <img src="<?php echo esc_url($image_url); ?>" alt="<?php echo esc_attr($image_alt); ?>" title="<?php echo esc_attr($image_title); ?>">
                                </div>
                                <?php
                            } else {
                                echo '<p>Ошибка: изображение отсутствует.</p>';
                            }
                        }
                    } else {
                        echo '<p>Логотипы не найдены</p>';
                    }
                    ?>

                </div>
            </div>
            <button type="button" class="trust-main__btn-slider trust-main__btn-next">
                <img src="<?php echo get_stylesheet_directory_uri(); ?>/assets/img/icons/arrow-grey.svg" alt="Next">
            </button>
        </div>
    </div>
</section>

    <!-- ------------------------------------------------------ End Trust-------------------------------------------------- -->
    <!-- ------------------------------------------------------ Offices----------------------------------------------------------- -->
   <?php $main_offices = get_field('ofisy', 7); ?>
<section class="main-page__offices offices-main">
    <div class="offices-main__container">
        <h2 class="offices-main__title _title">
            <?php echo esc_html($main_offices['zagolovok']); ?>
        </h2>
        <div class="offices-main__items">

            <?php $offices = $main_offices['ofis']; ?>
            <?php
            if ($offices && is_array($offices)) {
                foreach ($offices as $office) {
                    // Получаем данные изображения из массива
                    $image_url = isset($office['izobrazhenie']['url']) ? $office['izobrazhenie']['url'] : '';
                    $image_alt = isset($office['izobrazhenie']['alt']) ? $office['izobrazhenie']['alt'] : 'Офис';
                    $image_title = isset($office['izobrazhenie']['title']) ? $office['izobrazhenie']['title'] : '';

                    // Проверяем наличие изображения
                    if ($image_url) {
                        ?>
                        <div class="offices-main__item item-office-main">
                            <div class="item-office-main__img">
                                <img src="<?php echo esc_url($image_url); ?>" alt="<?php echo esc_attr($image_alt); ?>" title="<?php echo esc_attr($image_title); ?>">
                            </div>
                            <div class="item-office-main__name">
                                <?php echo esc_html($office['gorod']); ?>
                            </div>
                            <div class="item-office-main__contacts">
                                <p class="item-office-main__address">
                                    <?php echo esc_html($office['adres']); ?>
                                </p>
                                <a href="mailto:<?php echo esc_attr($office['pochta']); ?>" class="item-office-main__mail">
                                    <?php echo esc_html($office['pochta']); ?>
                                </a>
                                <a href="tel:<?php echo esc_attr($office['telefon_bez_probelov_i_znakov']); ?>" class="item-office-main__tel">
                                    <?php echo esc_html($office['telefon']); ?>
                                </a>
                            </div>
                        </div>
                        <?php
                    } else {
                        echo '<p>Ошибка: изображение для офиса отсутствует.</p>';
                    }
                }
            } else {
                echo '<p>Офисы не найдены.</p>';
            }
            ?>

        </div>
    </div>
</section>

    <!-- ------------------------------------------------------ End Offices --------------------------------------------------------- -->
    <?php
    $has_faq = is_array($faq) && !empty($faq);
    if ($has_faq) :
    ?>
        <section class="eq-section eq-faq">
            <div class="eq-container">
                <div class="eq-section-head">
                    <h2 class="eq-section-title">Часто задаваемые вопросы</h2>
                </div>

                <div class="eq-faq__list">
                    <?php foreach ($faq as $item) : ?>
                        <?php
                        if (!is_array($item)) {
                            continue;
                        }

                        $question = lw_eq_get_subvalue($item, 'vopros', '');
                        $answer   = lw_eq_get_subvalue($item, 'otvet', '');

                        if ($question === '' && $answer === '') {
                            continue;
                        }
                        ?>
                        <details class="eq-faq-item">
                            <summary class="eq-faq-item__question">
                                <span><?php echo esc_html($question !== '' ? $question : 'Вопрос'); ?></span>
                            </summary>

                     <div class="eq-faq-item__answer">
    <?php if ($answer !== '') : ?>
        <?php echo wp_kses_post(wpautop($answer)); ?>
    <?php else : ?>
        <p>Ответ уточняется.</p>
    <?php endif; ?>
	</div>
                        </details>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <section class="eq-section eq-form" id="eq-form">
        <div class="eq-container">
            <div class="eq-form__wrap">
                <div class="eq-section-head">
                    <h2 class="eq-section-title"><?php echo esc_html($form_title); ?></h2>
                </div>

                <div class="eq-form__body">
                    <?php echo do_shortcode($form_shortcode); ?>
                </div>
            </div>
        </div>
    </section>
</main>

<?php get_footer(); ?>
