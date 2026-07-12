<?php /* Template Name: New Chinese Page */
get_header();

wp_enqueue_style(
    'new-chinese-page',
    get_stylesheet_directory_uri() . '/assets/css/new-chinese-page.css',
    array(),
    '1.0.0'
);

if (!function_exists('new_chinese_page_prepare_image')) {
    function new_chinese_page_prepare_image($image, $fallback_alt = '', $fallback_title = '')
    {
        if (is_array($image)) {
            return array(
                'url' => $image['url'] ?? '',
                'alt' => $fallback_alt ?: ($image['alt'] ?? ''),
                'title' => $fallback_title ?: ($image['title'] ?? ''),
            );
        }

        return array(
            'url' => is_string($image) ? $image : '',
            'alt' => $fallback_alt,
            'title' => $fallback_title,
        );
    }
}

$hero_section = get_field('market-hero-section');
$advantages_section = get_field('market-hero-advantages');
$compare_section = get_field('china-comparison-section');
$stages_section = get_field('market-hero-stages');
$why_section = get_field('prichiny');
$faq = get_field('voprosy');

$hero_image = new_chinese_page_prepare_image(
    $hero_section['img'] ?? '',
    $hero_section['img_alt'] ?? '',
    $hero_section['img_title'] ?? ''
);

$compare_left = new_chinese_page_prepare_image(
    $compare_section['left_image'] ?? '',
    $compare_section['left_img_alt'] ?? '',
    $compare_section['left_img_title'] ?? ''
);

$compare_right = new_chinese_page_prepare_image(
    $compare_section['right_image'] ?? '',
    $compare_section['right_img_alt'] ?? '',
    $compare_section['right_img_title'] ?? ''
);

$current_page_id = get_queried_object_id();

$stages_bottom_image = new_chinese_page_prepare_image(
    $stages_section['nizhnij_blok_sekczii']['img'] ?? '',
    $stages_section['nizhnij_blok_sekczii']['img_alt'] ?? '',
    $stages_section['nizhnij_blok_sekczii']['img_title'] ?? ''
);
?>

<main class="page market-page new-chinese-page">
    <section class="market-page__hero hero-main">
        <div class="breadcrumbs">
            <div class="breadcrumbs__container">
                <?php
                if (function_exists('yoast_breadcrumb')) {
                    yoast_breadcrumb('<p id="breadcrumbs">', '</p>');
                }
                ?>
            </div>
        </div>
        <div class="hero-main__container">
            <div class="hero-main__top">
                <div class="hero-main__offer">
                    <h1 class="hero-main__title">
                        <?php echo esc_html($hero_section['title'] ?? ''); ?>
                    </h1>
                    <div class="hero-main__subtitle">
                        <?php echo wp_kses_post($hero_section['subtitle'] ?? ''); ?>
                    </div>
                    <button class="hero-main__btn _btn" data-goto=".consult">
                        提交申请
                    </button>
                </div>
                <div class="hero-main__hexagons">
                    <div class="hero-main__hexagon-img">
                        <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                            <pattern id="img-china-page" patternContentUnits="objectBoundingBox" width="100%" height="100%">
                                <image height="1" width="1" preserveAspectRatio="xMidYMid slice" xlink:href="<?php echo esc_url($hero_image['url']); ?>" />
                            </pattern>
                            <path fill="url(#img-china-page)" d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
                            <?php if (!empty($hero_image['title'])) { ?>
                                <title><?php echo esc_html($hero_image['title']); ?></title>
                            <?php } ?>
                        </svg>
                    </div>
                    <div class="hero-main__hexagon-middle">
                        <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                            <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
                        </svg>
                    </div>
                    <div class="hero-main__hexagon-big">
                        <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                            <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
                        </svg>
                    </div>
                    <div class="hero-main__hexagon-small">
                        <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                            <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
                        </svg>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section class="market-page__advantages advantages-market">
        <div class="advantages-market__container">
            <?php
            $advantages_title = !empty($advantages_section[0]['zagolovok']) ? $advantages_section[0]['zagolovok'] : '';
            if (!empty($advantages_title)) {
            ?>
                <h2 class="advantages-market__title _title">
                    <?php echo esc_html($advantages_title); ?>
                </h2>
            <?php } ?>

            <div class="advantages-market__items">
                <?php
                if (!empty($advantages_section) && is_array($advantages_section)) {
                    foreach ($advantages_section as $advantages_item) {
                        if (empty($advantages_item['item']) || !is_array($advantages_item['item'])) {
                            continue;
                        }

                        $item_data = $advantages_item['item'];
                        $item_image = new_chinese_page_prepare_image(
                            $item_data['img'] ?? '',
                            $item_data['img_alt'] ?? '',
                            $item_data['img_title'] ?? ''
                        );
                        $item_title = !empty($item_data['title']) ? strip_tags($item_data['title']) : '';
                        $item_subtitle = !empty($item_data['subtitle']) ? strip_tags($item_data['subtitle']) : '';
                ?>
                        <div class="advantages-market__item item-market-adv">
                            <?php if (!empty($item_image['url'])) { ?>
                                <div class="item-market-adv__img">
                                    <img src="<?php echo esc_url($item_image['url']); ?>"
                                        alt="<?php echo esc_attr($item_image['alt']); ?>"
                                        title="<?php echo esc_attr($item_image['title']); ?>">
                                </div>
                            <?php } ?>
                            <?php if (!empty($item_title)) { ?>
                                <div class="item-market-adv__title">
                                    <?php echo esc_html($item_title); ?>
                                </div>
                            <?php } ?>
                            <?php if (!empty($item_subtitle)) { ?>
                                <div class="item-market-adv__text">
                                    <?php echo esc_html($item_subtitle); ?>
                                </div>
                            <?php } ?>
                        </div>
                <?php
                    }
                }
                ?>
            </div>
        </div>
    </section>

    <section class="market-page__price price-market china-vs">
        <div class="price-market__container">
            <div class="price-market__block">
                <h2 class="price-market__title china-vs__title">
                    <?php echo esc_html($compare_section['title'] ?? ''); ?>
                </h2>
                <div class="china-vs__layout">
                    <figure class="china-vs__card china-vs__card--left">
                        <img src="<?php echo esc_url($compare_left['url']); ?>"
                            alt="<?php echo esc_attr($compare_left['alt']); ?>"
                            title="<?php echo esc_attr($compare_left['title']); ?>"
                            loading="lazy">
                    </figure>
                    <div class="china-vs__divider">
                        <?php echo esc_html($compare_section['vs_text'] ?? 'VS'); ?>
                    </div>
                    <figure class="china-vs__card china-vs__card--right">
                        <img src="<?php echo esc_url($compare_right['url']); ?>"
                            alt="<?php echo esc_attr($compare_right['alt']); ?>"
                            title="<?php echo esc_attr($compare_right['title']); ?>"
                            loading="lazy">
                    </figure>
                </div>
                <?php if (!empty($compare_section['subtitle'])) { ?>
                    <div class="china-vs__subtitle">
                        <?php echo wp_kses_post($compare_section['subtitle']); ?>
                    </div>
                <?php } ?>
                <div class="china-vs__actions">
                    <button class="hero-main__btn _btn" data-goto=".consult">
                        提交申请
                    </button>
                </div>
            </div>
        </div>
    </section>

    <section class="market-page__stages stages-market">
        <div class="stages-market__container">
            <h2 class="stages-market__title _title">
                <?php echo esc_html($stages_section['title'] ?? ''); ?>
            </h2>
            <?php $stages_rows = $stages_section['stages'] ?? array(); ?>
            <div class="stages-market__rows">
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo wp_kses_post($stages_rows['stage_1']['title'] ?? ''); ?>
                    </div>
                    <div class="stages-market__right">
                        <?php echo wp_kses_post($stages_rows['stage_1']['description'] ?? ''); ?>
                    </div>
                </div>
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo wp_kses_post($stages_rows['stage_2']['title'] ?? ''); ?>
                    </div>
                    <div class="stages-market__right">
                        <?php echo wp_kses_post($stages_rows['stage_2']['description'] ?? ''); ?>
                    </div>
                </div>
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo wp_kses_post($stages_rows['stage_3']['title'] ?? ''); ?>
                    </div>
                    <div class="stages-market__right">
                        <?php
                        $stage_3_description = $stages_rows['stage_3']['description'] ?? '';
                        if ($stage_3_description === '') {
                            $stage_3_description = $stages_rows['stage_3']['opisanie'] ?? '';
                        }
                        if ($stage_3_description === '' && $current_page_id) {
                            $stage_3_description = get_post_meta($current_page_id, 'market-hero-stages_stages_stage_3_description', true);
                        }
                        if ($stage_3_description === '' && $current_page_id) {
                            $stage_3_description = get_post_meta($current_page_id, 'market-hero-stages_stages_stage_3_opisanie', true);
                        }
                        $stage_3_cards = $stages_rows['stage_3']['kartochki']['kartochka'] ?? array();
                        if (!is_array($stage_3_cards)) {
                            $stage_3_cards = array();
                        }
                        ?>
                        <?php if (!empty($stage_3_description)) { ?>
                            <div class="stages-market__description">
                                <?php echo wp_kses_post($stage_3_description); ?>
                            </div>
                        <?php } ?>
                        <?php if (!empty($stage_3_cards)) { ?>
                            <div class="stages-market__packs">
                                <?php foreach ($stage_3_cards as $card) {
                                    $card_image = new_chinese_page_prepare_image(
                                        $card['izobrazhenie'] ?? '',
                                        $card['img_alt'] ?? '',
                                        $card['img_title'] ?? ''
                                    );
                                ?>
                                    <div class="stages-market__pack pack-stages-market">
                                        <div class="pack-stages-market__top">
                                            <div class="pack-stages-market__title">
                                                <?php echo wp_kses_post($card['title'] ?? ''); ?>
                                            </div>
                                        <?php if (!empty($card_image['url'])) { ?>
    <div class="pack-stages-market__img">
        <img src="<?php echo esc_url($card_image['url']); ?>"
            alt="<?php echo esc_attr($card_image['alt']); ?>"
            title="<?php echo esc_attr($card_image['title']); ?>">
    </div>
<?php } ?>

                                        </div>
                                        <div class="pack-stages-market__bottom">
                                            <?php echo esc_html($card['price'] ?? ''); ?> <span></span>
                                        </div>
                                    </div>
                                <?php } ?>
                            </div>
                        <?php } ?>
                    </div>
                </div>
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo wp_kses_post($stages_rows['stage_4']['title'] ?? ''); ?>
                    </div>
                    <div class="stages-market__right">
                        <?php
                        $stage_4_description = $stages_rows['stage_4']['description'] ?? '';
                        if ($stage_4_description === '') {
                            $stage_4_description = $stages_rows['stage_4']['opisanie'] ?? '';
                        }
                        if ($stage_4_description === '' && $current_page_id) {
                            $stage_4_description = get_post_meta($current_page_id, 'market-hero-stages_stages_stage_4_description', true);
                        }
                        if ($stage_4_description === '' && $current_page_id) {
                            $stage_4_description = get_post_meta($current_page_id, 'market-hero-stages_stages_stage_4_opisanie', true);
                        }
                        $stage_4_cards = $stages_rows['stage_4']['kartochki']['kartochka'] ?? array();
                        if (!is_array($stage_4_cards)) {
                            $stage_4_cards = array();
                        }
                        ?>
                        <?php if (!empty($stage_4_description)) { ?>
                            <div class="stages-market__description">
                                <?php echo wp_kses_post($stage_4_description); ?>
                            </div>
                        <?php } ?>
                        <?php if (!empty($stage_4_cards)) { ?>
                            <div class="stages-market__delivery delivery-market">
                                <div class="delivery-market__items">
                                    <?php foreach ($stage_4_cards as $card) {
                                        $card_image = new_chinese_page_prepare_image(
                                            $card['img'] ?? '',
                                            $card['img_alt'] ?? '',
                                            $card['img_title'] ?? ''
                                        );
                                    ?>
                                        <div class="delivery-market__item">
                                            <div class="delivery-market__top">
                                                <div class="delivery-market__title">
                                                    <?php echo wp_kses_post($card['title'] ?? ''); ?>
                                                </div>
                                        <?php if (!empty($card_image['url'])) { ?>
    <div class="delivery-market__img">
        <img src="<?php echo esc_url($card_image['url']); ?>"
            alt="<?php echo esc_attr($card_image['alt']); ?>"
            title="<?php echo esc_attr($card_image['title']); ?>">
    </div>
<?php } ?>

                                            </div>
                                            <div class="delivery-market__bottom">
                                                <p class="delivery-market__price">
                                                    <?php echo esc_html($card['price'] ?? ''); ?> <span></span>
                                                </p>
                                                <p class="delivery-market__time">
                                                    <?php echo esc_html($card['srok'] ?? ''); ?>
                                                </p>
                                            </div>
                                        </div>
                                    <?php } ?>
                                </div>
                            </div>
                        <?php } ?>
                    </div>
                </div>
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo wp_kses_post($stages_rows['stage_5']['title'] ?? ''); ?>
                    </div>
                    <div class="stages-market__right">
                        <?php echo wp_kses_post($stages_rows['stage_5']['description'] ?? ''); ?>
                    </div>
                </div>
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo wp_kses_post($stages_rows['stage_6']['title'] ?? ''); ?>
                    </div>
                    <div class="stages-market__right">
                        <?php echo wp_kses_post($stages_rows['stage_6']['description'] ?? ''); ?>
                    </div>
                </div>
            </div>
            <div class="stages-market__bottom bottom-market-stages">
                <div class="bottom-market-stages__img">
                    <img src="<?php echo esc_url($stages_bottom_image['url']); ?>"
                        alt="交易与交付安全保障"
                        title="俄罗斯与中国之间的交易全额保险">
                </div>
                <div class="bottom-market-stages__text">
                    <div class="bottom-market-stages__title">
                        <?php echo wp_kses_post($stages_section['nizhnij_blok_sekczii']['title'] ?? ''); ?>
                    </div>
                    <div class="bottom-market-stages__subtitle">
                        <?php echo wp_kses_post($stages_section['nizhnij_blok_sekczii']['subtitle'] ?? ''); ?>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section class="parallel-page__why why-parallel">
        <div class="why-parallel__container">
            <h2 class="why-parallel__title _title">
                <?php echo esc_html($why_section['zagolovok'] ?? ''); ?>
            </h2>
            <?php $why_items = $why_section['elementy'] ?? array(); ?>
            <div class="why-parallel__items">
                <?php foreach ($why_items as $why_item) { ?>
                    <div class="why-parallel__item item-why-parallel">
                        <div class="item-why-parallel__text">
                            <?php echo esc_html($why_item['tekst'] ?? ''); ?>
                        </div>
                    </div>
                <?php } ?>
            </div>
            <button class="why-parallel__btn _btn" data-goto=".consult">
                提交申请
            </button>
        </div>
    </section>

    <?php $partners = get_field('partnery', 7); ?>
    <?php if (!empty($partners)) { ?>
        <section class="main-page__trust trust-main">
            <div class="trust-main__container">
                <h2 class="trust-main__title _title">
                    <?php echo esc_html($partners['zagolovok'] ?? ''); ?>
                </h2>

                <div class="trust-main__body">
                    <button type="button" class="trust-main__btn-slider trust-main__btn-prev">
                        <img src="<?php echo esc_url(get_stylesheet_directory_uri()); ?>/assets/img/icons/arrow-grey.svg" alt="Previous">
                    </button>
                    <div class="trust-main__slider swiper">
                        <div class="trust-main__wrapper swiper-wrapper">
                            <?php $logos = $partners['logos'] ?? array(); ?>
                            <?php foreach ($logos as $logo) {
                                $logo_image = new_chinese_page_prepare_image($logo['logo'] ?? '', '合作伙伴标志', '');
                                if (empty($logo_image['url'])) {
                                    continue;
                                }
                            ?>
                                <div class="trust-main__slide swiper-slide">
                                    <img src="<?php echo esc_url($logo_image['url']); ?>"
                                        alt="<?php echo esc_attr($logo_image['alt']); ?>"
                                        title="<?php echo esc_attr($logo_image['title']); ?>">
                                </div>
                            <?php } ?>
                        </div>
                    </div>
                    <button type="button" class="trust-main__btn-slider trust-main__btn-next">
                        <img src="<?php echo esc_url(get_stylesheet_directory_uri()); ?>/assets/img/icons/arrow-grey.svg" alt="Next">
                    </button>
                </div>
            </div>
        </section>
    <?php } ?>

    <?php
    $projects_query = new WP_Query(array(
        'post_type' => 'projects',
    ));
    ?>
    <?php if ($projects_query->have_posts()) { ?>
        <section class="project-page__projects real-projects">
            <div class="real-projects__container">
                <h2 class="real-projects__title _title">
                    已完成项目
                </h2>
                <div class="real-projects__block">
                    <button type="button" class="real-projects__btn-slider real-projects__btn-prev">
                        <svg xmlns="http://www.w3.org/2000/svg" width="21" height="34" viewBox="0 0 21 34" fill="none">
                            <path d="M17.5156 0.000167847C17.0674 -0.00106812 16.6244 0.0790024 16.2194 0.234486C15.8144 0.389969 15.4576 0.616917 15.1752 0.898655L0.682587 15.4687C0.241262 15.9032 0 16.4482 0 17.0107C0 17.5732 0.241262 18.1182 0.682587 18.5527L15.6853 33.1228C16.1946 33.6187 16.9265 33.9305 17.7199 33.9897C18.5133 34.0489 19.3033 33.8506 19.916 33.4384C20.5288 33.0263 20.9142 32.434 20.9873 31.7918C21.0605 31.1497 20.8154 30.5104 20.3061 30.0145L6.8937 16.9986L19.856 3.98265C20.223 3.6262 20.456 3.19216 20.5277 2.73187C20.5993 2.27158 20.5066 1.80431 20.2603 1.38535C20.0141 0.966396 19.6248 0.613289 19.1384 0.367805C18.652 0.122326 18.0888 -0.00525284 17.5156 0.000167847Z" fill="#B4B9C3" />
                        </svg>
                    </button>
                    <div class="real-projects__slider swiper">
                        <div class="real-projects__wrapper swiper-wrapper">
                            <?php while ($projects_query->have_posts()) {
                                $projects_query->the_post();
                                $project_image_url = get_the_post_thumbnail_url(get_the_ID(), 'full');
                            ?>
                                <a href="<?php echo esc_url(get_permalink()); ?>" class="real-projects__slide swiper-slide">
                                    <div class="item-real-proj">
                                        <div class="item-real-proj__title">
                                            <?php the_title(); ?>
                                        </div>
                                        <div class="item-real-proj__hex">
                                            <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                                                <pattern id="img-<?php echo esc_attr(get_the_ID()); ?>" patternContentUnits="objectBoundingBox" width="100%" height="100%">
                                                    <image height="1" width="1" preserveAspectRatio="xMidYMid slice" xlink:href="<?php echo esc_url($project_image_url); ?>" />
                                                </pattern>
                                                <path fill="url(#img-<?php echo esc_attr(get_the_ID()); ?>)" d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
                                            </svg>
                                        </div>
                                    </div>
                                </a>
                            <?php } ?>
                        </div>
                    </div>
                    <button type="button" class="real-projects__btn-slider real-projects__btn-next">
                        <svg xmlns="http://www.w3.org/2000/svg" width="21" height="34" viewBox="0 0 21 34" fill="none">
                            <path d="M3.48438 33.9998C3.93264 34.0011 4.37555 33.921 4.78057 33.7655C5.18558 33.61 5.54239 33.3831 5.8248 33.1013L20.3174 18.5313C20.7587 18.0968 21 17.5518 21 16.9893C21 16.4268 20.7587 15.8818 20.3174 15.4473L5.31471 0.877243C4.8054 0.381335 4.07354 0.0694764 3.28012 0.010274C2.4867 -0.0489284 1.69671 0.149375 1.08395 0.561558C0.471189 0.973741 0.0858477 1.56604 0.012697 2.20816C-0.0604556 2.85028 0.184572 3.48961 0.69388 3.98552L14.1063 17.0014L1.14396 30.0174C0.777044 30.3738 0.543971 30.8078 0.47232 31.2681C0.400668 31.7284 0.493436 32.1957 0.739648 32.6146C0.98586 33.0336 1.37521 33.3867 1.86163 33.6322C2.34805 33.8777 2.91118 34.0053 3.48438 33.9998Z" fill="#B4B9C3" />
                        </svg>
                    </button>
                </div>
            </div>
        </section>
    <?php } ?>
    <?php wp_reset_postdata(); ?>

    <?php if (!empty($faq['spojlery'][0]['vopros'])) { ?>
        <section class="faq">
            <div class="faq__container">
                <div class="faq__body">
                    <h2 class="faq__title">
                        <?php echo esc_html($faq['zagolovok'] ?? '常见问题'); ?>
                    </h2>
                    <div class="faq__block">
                        <div data-spollers class="spollers faq__spollers">
                            <?php foreach (($faq['spojlery'] ?? array()) as $spoller) { ?>
                                <div class="spollers__item faq__spoller-item">
                                    <button type="button" data-spoller class="spollers__title faq__spoller-title">
                                        <?php echo esc_html($spoller['vopros'] ?? ''); ?>
                                    </button>
                                    <div class="spollers__body faq__spoller-body">
                                        <?php echo wp_kses_post($spoller['otvet'] ?? ''); ?>
                                    </div>
                                </div>
                            <?php } ?>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    <?php } ?>

    <section class="consult">
        <div class="consult__container">
            <h2 class="consult__title">
                获取咨询方案
            </h2>
            <?php echo do_shortcode('[contact-form-7 id="f76ef2f" title="Контактная форма" html_class="form consult-form"]'); ?>
        </div>
    </section>
</main>

<?php
get_footer();