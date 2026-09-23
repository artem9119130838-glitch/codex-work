<?php /* Template Name: Template Turnkey */
get_header();
?>

<main class="page import-page">
    <?php $hero_main = get_field('glavnaya_sekcziya'); ?>
    <section class="import-page__hero hero-main">
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
                        <?php echo $hero_main['zagolovok']; ?>
                    </h1>
                    <p class="hero-main__subtitle">
                        <?php echo $hero_main['podzagolovok']; ?>
                    </p>
                    <button class="hero-main__btn _btn" data-goto=".consult">
                        Оставить заявку
                    </button>
                </div>
                <div class="hero-main__hexagons">
                    <div class="hero-main__hexagon-img">
                        <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                            <pattern id="img-main" patternContentUnits="objectBoundingBox" width="100%" height="100%">
                                <image height="1" width="1" preserveAspectRatio="xMidYMid slice" xlink:href="<?php echo $hero_main['izobrazhenie']; ?>" />
                            </pattern>
                            <path fill="url(#img-main)" d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
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
    <!-- ------------------------------------------------------ Advantages ----------------------------------------------------------------------- -->
    <?php $second_section = get_field('vtoraya_sekcziya'); ?>
    <div class="import-page__advantages advantages-import">
        <div class="advantages-import__container">
            <?php $second_section_items = $second_section['elementy']; ?>
            <div class="advantages-import__items">

                <?php
                if ($second_section_items) {
                    foreach ($second_section_items as $second_section_item) {
                ?>

                        <div class="advantages-import__item">
                            <div class="advantages-import__img">
                                <img src="<?php echo $second_section_item['izobrazhenie']; ?>" alt="">
                            </div>
                            <div class="advantages-import__text">
                                <?php echo $second_section_item['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
        </div>
    </div>
    <!-- ------------------------------------------------------ End Advantages ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Services ----------------------------------------------------------------------- -->
    <?php $services_section = get_field('uslugi'); ?>
    <section class="import-page__services services-import">
        <div class="services-import__container">
            <h2 class="services-import__title _title">
                <?php echo $services_section['zagolovok']; ?>
            </h2>
            <?php $services_section_items = $services_section['kartochki']; ?>
            <div class="services-import__items">

                <?php
                if ($services_section_items) {
                    foreach ($services_section_items as $services_section_item) {
                ?>

                        <?php $card = $services_section_item['kartochka']; ?>

                        <div class="services-import__item item-service-import">
                            <div class="item-service-import__title">
                                <?php echo $card['zagolovok']; ?>
                            </div>
                            <?php $card_items = $card['punkty']; ?>
                            <ul class="item-service-import__items">

                                <?php
                                if ($card_items) {
                                    foreach ($card_items as $card_item) {
                                ?>

                                        <div class="item-service-import__item">
                                            <?php echo $card_item['tekst']; ?>
                                        </div>

                                <?php
                                    }
                                }
                                ?>

                            </ul>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="services-import__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Services ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Help ----------------------------------------------------------------------- -->
    <?php $pomoshh_section = get_field('pomoshh'); ?>
    <section class="import-page__help help-import">
        <div class="help-import__container">
            <h2 class="help-import__title">
                <?php echo $pomoshh_section['zagolovok']; ?>
            </h2>
            <div class="help-import__text">
                <?php echo $pomoshh_section['tekst']; ?>
            </div>
            <?php $pomoshh_section_items = $pomoshh_section['punkty']; ?>
            <ul class="help-import__ul">

                <?php
                if ($pomoshh_section_items) {
                    foreach ($pomoshh_section_items as $pomoshh_section_item) {
                ?>

                        <li class="help-import__li">
                            <?php echo $pomoshh_section_item['punkt']; ?>
                        </li>

                <?php
                    }
                }
                ?>

            </ul>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Help ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Stages ----------------------------------------------------------------------- -->
    <?php $etapy_section = get_field('etapy'); ?>
    <section class="import-page__stages stages-import">
        <div class="stages-import__container">
            <h2 class="stages-import__title">
                <?php echo $etapy_section['zagolovok']; ?>
            </h2>
            <?php $etapy_section_items = $etapy_section['punkty']; ?>
            <div class="stages-import__items">

                <?php
                if ($etapy_section_items) {
                    foreach ($etapy_section_items as $etapy_section_item) {
                ?>

                        <div class="stages-import__item">
                            <?php echo $etapy_section_item['punkt']; ?>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="stages-import__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Stages ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Conditions ----------------------------------------------------------------------- -->
    <?php $usloviya_section = get_field('usloviya'); ?>
    <section class="import-page__conditions conditions-import">
        <div class="conditions-import__container">
            <h2 class="conditions-import__title _title">
                <?php echo $usloviya_section['zagolovok']; ?>
            </h2>
            <?php $usloviya_section_items = $usloviya_section['elementy']; ?>
            <div class="conditions-import__items">

                <?php
                if ($usloviya_section_items) {
                    foreach ($usloviya_section_items as $usloviya_section_item) {
                ?>

                        <div class="conditions-import__item">
                            <div class="conditions-import__img">
                                <img src="<?php echo $usloviya_section_item['ikonka']; ?>" alt="">
                            </div>
                            <div class="conditions-import__text">
                                <?php echo $usloviya_section_item['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Conditions ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Variants ----------------------------------------------------------------------- -->
    <?php $varianty_section = get_field('varianty'); ?>
    <section class="import-page__variants variants-import">
        <div class="variants-import__container">
            <h2 class="variants-import__title _title">
                <?php echo $varianty_section['zagolovok']; ?>
            </h2>
            <?php $varianty_section_items = $varianty_section['kartochki']; ?>
            <div class="variants-import__items">

                <?php
                if ($varianty_section_items) {
                    foreach ($varianty_section_items as $varianty_section_item) {
                ?>

                        <?php $varianty_section_card = $varianty_section_item['kartochka']; ?>
                        <div class="variants-import__item item-variant-import">
                            <?php $varianty_section_left = $varianty_section_card['sleva']; ?>
                            <div class="item-variant-import__left">

                                <?php
                                if ($varianty_section_left) {
                                    foreach ($varianty_section_left as $varianty_section_text) {
                                ?>

                                        <span>
                                            <?php echo $varianty_section_text['tekst']; ?>
                                        </span>

                                <?php
                                    }
                                }
                                ?>

                            </div>
                            <?php $varianty_section_right = $varianty_section_card['sprava']; ?>
                            <div class="item-variant-import__right">

                                <?php
                                if ($varianty_section_right) {
                                    foreach ($varianty_section_right as $varianty_section_text) {
                                ?>

                                        <span>
                                            <?php echo $varianty_section_text['tekst']; ?>
                                        </span>

                                <?php
                                    }
                                }
                                ?>

                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Variants ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Which ----------------------------------------------------------------------- -->
    <?php $vidy_tovarov_section = get_field('vidy_tovarov'); ?>
    <section class="import-page__which which-import">
        <div class="which-import__container">
            <h2 class="which-import__title _title">
                <?php echo $vidy_tovarov_section['zagolovok']; ?>
            </h2>
            <?php $vidy_tovarov_section_items = $vidy_tovarov_section['punkty']; ?>
            <div class="which-import__items">

                <?php
                if ($vidy_tovarov_section_items) {
                    foreach ($vidy_tovarov_section_items as $vidy_tovarov_section_item) {
                ?>

                        <div class="which-import__item">
                            <?php echo $vidy_tovarov_section_item['punkt']; ?>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <div class="which-import__btn _btn" data-goto=".consult">
                Оставить заявку
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Which ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Key ----------------------------------------------------------------------- -->
    <?php $vybirayut_section = get_field('vybirayut'); ?>
    <section class="import-page__key key-import">
        <div class="key-import__container">
            <h2 class="key-import__title _title">
                <?php echo $vybirayut_section['zagolovok']; ?>
            </h2>
            <?php $vybirayut_section_items = $vybirayut_section['kartochki']; ?>
            <div class="key-import__items">

                <?php
                if ($vybirayut_section_items) {
                    foreach ($vybirayut_section_items as $vybirayut_section_item) {
                ?>

                        <div class="key-import__item">
                            <span>
                                <?php echo $vybirayut_section_item['tekst']; ?>
                            </span>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Key ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Projects ----------------------------------------------------------------------- -->
    <?php $args = array(
        'post_type'        => 'projects',
    );
    $the_query = new WP_Query($args); ?>

    <?php if ($the_query->have_posts()) : ?>

        <section class="project-page__projects real-projects">
            <div class="real-projects__container">
                <h2 class="real-projects__title _title">
                    Реализованные проекты
                </h2>
                <div class="real-projects__block">
                    <button type="button" class="real-projects__btn-slider real-projects__btn-prev">
                        <svg xmlns="http://www.w3.org/2000/svg" width="21" height="34" viewBox="0 0 21 34" fill="none">
                            <path d="M17.5156 0.000167847C17.0674 -0.00106812 16.6244 0.0790024 16.2194 0.234486C15.8144 0.389969 15.4576 0.616917 15.1752 0.898655L0.682587 15.4687C0.241262 15.9032 0 16.4482 0 17.0107C0 17.5732 0.241262 18.1182 0.682587 18.5527L15.6853 33.1228C16.1946 33.6187 16.9265 33.9305 17.7199 33.9897C18.5133 34.0489 19.3033 33.8506 19.916 33.4384C20.5288 33.0263 20.9142 32.434 20.9873 31.7918C21.0605 31.1497 20.8154 30.5104 20.3061 30.0145L6.8937 16.9986L19.856 3.98265C20.223 3.6262 20.456 3.19216 20.5277 2.73187C20.5993 2.27158 20.5066 1.80431 20.2603 1.38535C20.0141 0.966396 19.6248 0.613289 19.1384 0.367805C18.652 0.122326 18.0888 -0.00525284 17.5156 0.000167847Z" fill="#B4B9C3" />
                        </svg>
                    </button>
                    <div class="real-projects__slider swiper">
                        <div class="real-projects__wrapper swiper-wrapper">

                            <?php while ($the_query->have_posts()) : $the_query->the_post(); ?>

                                <a href="<?php echo esc_url(get_permalink()); ?>" class="real-projects__slide swiper-slide">
                                    <div class="item-real-proj">
                                        <div class="item-real-proj__title">
                                            <?php the_title(); ?>
                                        </div>
                                        <div class="item-real-proj__hex">
                                            <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                                                <pattern id="img-<?php echo $post->ID; ?>" patternContentUnits="objectBoundingBox" width="100%" height="100%">
                                                    <image height="1" width="1" preserveAspectRatio="xMidYMid slice" xlink:href="<?php echo the_post_thumbnail_url(); ?>" />
                                                </pattern>
                                                <path fill="url(#img-<?php echo $post->ID; ?>)" d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
                                            </svg>
                                        </div>
                                    </div>
                                </a>

                            <?php endwhile; ?>

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

    <?php endif; ?>
    <?php wp_reset_query(); ?>
    <!-- ------------------------------------------------------ End Projects ----------------------------------------------------------------------- -->
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
    <!-- ------------------------------------------------------ FAQ ----------------------------------------------------------------------- -->
    <?php $faq = get_field('voprosy'); ?>
    <?php if (isset($faq['spojlery'][0]['vopros'])) { ?>
        <section class="faq">
            <div class="faq__container">
                <div class="faq__body">
                    <h2 class="faq__title">
                        Часто задаваемые вопросы
                    </h2>
                    <div class="faq__block">
                        <div data-spollers class="spollers faq__spollers">

                            <?php $spollers = $faq['spojlery']; ?>
                            <?php
                            if ($spollers) {
                                foreach ($spollers as $spoller) {
                            ?>

                                    <div class="spollers__item faq__spoller-item">
                                        <button type="button" data-spoller class="spollers__title faq__spoller-title">
                                            <?php echo $spoller['vopros']; ?>
                                        </button>
                                        <div class="spollers__body faq__spoller-body">
                                            <?php echo $spoller['otvet']; ?>
                                        </div>
                                    </div>

                            <?php
                                }
                            }
                            ?>

                        </div>
                    </div>
                </div>
            </div>
        </section>
    <?php } ?>
    <!-- ------------------------------------------------------ End FAQ ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Consult ----------------------------------------------------------------------- -->
    <section class="consult">
        <div class="consult__container">
            <h2 class="consult__title">
                Заявка на консультацию
            </h2>
            <?php echo do_shortcode('[contact-form-7 id="f76ef2f" title="Контактная форма" html_class="form consult-form"]'); ?>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Consult ----------------------------------------------------------------------- -->
</main>

<?php
get_footer();
