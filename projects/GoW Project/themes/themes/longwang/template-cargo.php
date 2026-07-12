<?php /* Template Name: Template Cargo */
get_header();
?>

<main class="page cargo-page">
    <?php 
	
	// ------------------------------------------------------
    // Начало определения функции для получения ID изображения по URL
    // ------------------------------------------------------
    function get_image_id_by_url($image_url) {
        global $wpdb;
        $attachment_id = $wpdb->get_var($wpdb->prepare(
            "SELECT ID FROM {$wpdb->posts} WHERE guid = %s AND post_type = 'attachment'",
            $image_url
        ));
        return $attachment_id;
    }

    // Начало функции для получения alt-текста по URL изображения
    function get_image_alt_by_url($image_url) {
        $image_id = get_image_id_by_url($image_url);
        return $image_id ? get_post_meta($image_id, '_wp_attachment_image_alt', true) : '';
    }
    // ------------------------------------------------------
    // Конец определения функции для получения ID и alt изображения по URL
    // ------------------------------------------------------
	
		
	$hero_main = get_field('glavnaya_sekcziya'); ?>
<section class="cargo-page__hero hero-main">
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
                    <?php 
                    // ----------------------------------------------
                    // Начало правки: получаем alt для SVG из медиатеки
                    // ----------------------------------------------
                    $image_url = $hero_main['izobrazhenie'];
                    $image_alt = get_image_alt_by_url($image_url); // Используем функцию для alt
					
                    // ----------------------------------------------
                    // Конец правки
                    // ----------------------------------------------
                    ?>
                    <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg" aria-label="<?php echo esc_attr($image_alt); ?>">
                        <pattern id="img-main" patternContentUnits="objectBoundingBox" width="100%" height="100%">
                            <image height="1" width="1" preserveAspectRatio="xMidYMid slice" xlink:href="<?php echo esc_url($image_url); ?>" />
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

    <!-- ------------------------------------------------------ Advantages11------------------------------------------------------------- -->
  <?php
// Получаем данные из ACF
$second_section = get_field('vtoraya_sekcziya');
?>

<div class="cargo-page__advantages advantages-cargo">
    <div class="advantages-cargo__container">

        <?php if ($second_section && !empty($second_section['elementy'])) : // Проверяем, что поле существует и в нем есть элементы ?>
            <div class="advantages-cargo__items">

                <?php foreach ($second_section['elementy'] as $second_section_item) : 
                    // Получаем URL изображения
                    $image_url = isset($second_section_item['izobrazhenie']) ? $second_section_item['izobrazhenie'] : ''; 

                    // Получаем ID изображения из URL (если это изображение из медиатеки)
                    $image_id = attachment_url_to_postid($image_url);
                    
                    // Получаем alt и title для изображения
                    $image_alt = get_post_meta($image_id, '_wp_attachment_image_alt', true); // alt
                    $image_title = get_the_title($image_id); // title
                ?>
                    <div class="advantages-cargo__item">
                        <div class="advantages-cargo__img">
                            <img src="<?php echo esc_url($image_url); ?>" alt="<?php echo esc_attr($image_alt); ?>" title="<?php echo esc_attr($image_title); ?>" >
                        </div>
                        <div class="advantages-cargo__text">
                            <?php echo esc_html($second_section_item['tekst']); ?>
                        </div>
                    </div>
                <?php endforeach; ?>

            </div>
        <?php endif; ?>

    </div>
</div>
<!-- ------------------------------------------------------ End dvantages11--------------------------------------------------------- -->
    <!-- ------------------------------------------------------ How ----------------------------------------------------------------------- -->
    <?php $how_section = get_field('kak_rabotaet'); ?>
    <section class="cargo-page__how how-cargo">
        <div class="how-cargo__container">
            <h2 class="how-cargo__title _title">
                <?php echo $how_section['zagolovok']; ?>
            </h2>
            <?php $how_section_items = $how_section['ryady']; ?>
            <div class="how-cargo__items">

                <?php
                if ($how_section_items) {
                    foreach ($how_section_items as $how_section_item) {
                ?>

                        <div class="how-cargo__row">
                            <div class="how-cargo__left">
                                <?php echo $how_section_item['nazvanie']; ?>
                            </div>
                            <div class="how-cargo__right">
                                <?php echo $how_section_item['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="how-cargo__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End How ----------------------------------------------------------------------- -->
   
	<!-- ------------------------- Начало раздела кликабельных карточек для способов перевозки ------------------------- -->

<?php $methods_section = get_field('sposoby_perevozki'); ?>
<section class="cargo-page__methods methods-cargo">
    <div class="methods-cargo__container">
        <h2 class="methods-cargo__title _title">
            <?php echo esc_html($methods_section['zagolovok']); ?>
        </h2>
        <?php $methods_section_items = $methods_section['kartochka']; ?>
        <div class="cargo-kinds__items">
            <?php
            if ($methods_section_items) {
                foreach ($methods_section_items as $methods_section_item) {
                    // Получаем ссылку и название ссылки
                    $link = $methods_section_item['link']['url'] ?? null;
                    $link_title = $methods_section_item['link_title'] ?? $methods_section_item['nazvanie'];

                    // Получаем URL изображения и атрибуты из медиатеки
                    $image_url = $methods_section_item['ikonka'];
                    $image_id = attachment_url_to_postid($image_url); // Получаем ID изображения
                    $image_alt = get_post_meta($image_id, '_wp_attachment_image_alt', true); // alt
                    $image_title = get_the_title($image_id); // title
            ?>
                    <?php if (!empty($link)): ?>
                        <a href="<?php echo esc_url($link); ?>" title="<?php echo esc_attr($link_title); ?>" target="_blank" class="cargo-kinds__item cargo-kind">
                    <?php else: ?>
                        <div class="cargo-kinds__item cargo-kind">
                    <?php endif; ?>
                    
                        <div class="cargo-kind__left">
                            <div class="cargo-kind__title">
                                <?php echo esc_html($methods_section_item['nazvanie']); ?>
                            </div>
                            <div class="cargo-kind__weight">
                                <?php echo esc_html($methods_section_item['stoimost']); ?>
                            </div>
                            <div class="cargo-kind__time">
                                <?php echo esc_html($methods_section_item['srok']); ?>
                            </div>
                        </div>
                        <div class="cargo-kind__right">
                            <img src="<?php echo esc_url($image_url); ?>" 
                                 alt="<?php echo esc_attr($image_alt); ?>" 
                                 title="<?php echo esc_attr($image_title); ?>" 
                                 width="110" height="110">
                            <div class="cargo-kind__details">
                                <span>Подробнее</span>
                            </div>
                        </div>

                    <?php if (!empty($link)): ?>
                        </a>
                    <?php else: ?>
                        </div>
                    <?php endif; ?>
            <?php
                }
            }
            ?>
        </div>
    </div>
</section>

<!-- ------------------------- Конец раздела кликабельных карточек для способов перевозки ------------------------- -->

	
	
    <!-- ------------------------------------------------------ Price ----------------------------------------------------------------------- -->
   <?php $price_section = get_field('stoimost'); ?>
<section class="cargo-page__price price-cargo">
    <div class="price-cargo__container">
        <h2 class="price-cargo__title _title">
            <?php echo esc_html($price_section['zagolovok']); ?>
        </h2>
        <div class="price-cargo__items">
            <?php
            // Проверяем наличие карточек
            if ($price_section['kartochka_1'] && $price_section['kartochka_2'] && $price_section['kartochka_3']) :
                // Проходим по всем картам и выводим для каждой
                for ($i = 1; $i <= 3; $i++) :
                    $price_section_item = $price_section['kartochka_' . $i]; // Динамически выбираем карточку
            ?>
                    <div class="price-cargo__item">
                        <div class="price-cargo__img">
                            <?php 
                            // Получаем URL изображения
                            $image_url = $price_section_item['ikonka'];

                            // Получаем ID изображения из URL
                            $image_id = attachment_url_to_postid($image_url);

                            // Получаем alt и title для изображения из медиатеки
                            $image_alt = get_post_meta($image_id, '_wp_attachment_image_alt', true); // alt
                            $image_title = get_the_title($image_id); // title
                            ?>
                            <img src="<?php echo esc_url($image_url); ?>" alt="<?php echo esc_attr($image_alt); ?>" title="<?php echo esc_attr($image_title); ?>">
                        </div>
                        <div class="price-cargo__text">
                            <?php echo esc_html($price_section_item['tekst']); ?>
                        </div>
                    </div>
            <?php
                endfor;
            endif;
            ?>
        </div>
    </div>
</section>

    <!-- ------------------------------------------------------ End Price ---------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ AdvChoose ----------------------------------------------------------------------- -->
    <?php $preimushhestva_section = get_field('preimushhestva'); ?>
    <section class="cargo-page__advchoose advchoose-cargo">
        <div class="advchoose-cargo__container">
            <h2 class="advchoose-cargo__title _title">
                <?php echo $preimushhestva_section['zagolovok']; ?>
            </h2>
            <?php $preimushhestva_section_items = $preimushhestva_section['elementy']; ?>
            <div class="advchoose-cargo__items">

                <?php
                if ($preimushhestva_section_items) {
                    foreach ($preimushhestva_section_items as $preimushhestva_section_item) {
                ?>

                        <div class="advchoose-cargo__item item-advchoose">
                            <div class="item-advchoose__num">
                                <?php echo $preimushhestva_section_item['nomer']; ?>
                            </div>
                            <div class="item-advchoose__text">
                                <?php echo $preimushhestva_section_item['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="advchoose-cargo__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End AdvChoose ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Projects ----------------------------------------------------------------------- -->
 <!-- ------------------------------------------------------ Projects ----------------------------------------------------------------------- -->
<?php 
/*
$args = array(
    'post_type'        => 'projects',
);
$the_query = new WP_Query($args); 

if ($the_query->have_posts()) : ?>
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
<?php endif; 
wp_reset_query();
*/
?>
<!-- ------------------------------------------------------ End Projects ----------------------------------------------------------------------- -->

    <!-- ------------------------------------------------------ Trust ------------------------------------------------------- -->
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

    <!-- ------------------------------------------------------ End Trust---------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Offices------------------------------------------------------------- -->
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
 
    <!-- ------------------------------------------------------ End Offices------------------------------------------------------------- -->
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
