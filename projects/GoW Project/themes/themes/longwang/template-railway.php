<?php /* Template Name: Template Railway */
get_header();
?>

<main class="page railway-page">
    <?php $hero_main = get_field('glavnaya_sekcziya'); ?>
    <section class="railway-page__hero hero-main">
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

<div class="railway-page__advantages advantages-railway">
    <div class="advantages-railway__container">
        <?php 
        if ($second_section) {
            $second_section_items = $second_section['elementy'];
            
            if (!empty($second_section_items)) { ?>
                <div class="advantages-railway__items">
                    <?php
                    foreach ($second_section_items as $second_section_item) {
                        $image_url = !empty($second_section_item['izobrazhenie']) ? $second_section_item['izobrazhenie'] : '';
                        $img_title = !empty($second_section_item['img_title']) ? $second_section_item['img_title'] : ''; // Получаем title
                        $img_alt = !empty($second_section_item['img_alt']) ? $second_section_item['img_alt'] : ''; // Получаем alt
                        $text = !empty($second_section_item['tekst']) ? $second_section_item['tekst'] : 'Текст отсутствует';
                    ?>
                        <div class="advantages-railway__item">
                            <div class="advantages-railway__img">
                                <?php if ($image_url) : ?>
                                    <img src="<?php echo esc_url($image_url); ?>" 
                                         alt="<?php echo esc_attr($img_alt); ?>" 
                                         title="<?php echo esc_attr($img_title); ?>">
                                <?php else : ?>
                                    <p>Изображение отсутствует.</p>
                                <?php endif; ?>
                            </div>
                            <div class="advantages-railway__text">
                                <?php echo esc_html($text); ?>
                            </div>
                        </div>
                    <?php } ?>
                </div>
            <?php } else {
                echo '<p>Элементы для секции "Преимущества" не найдены.</p>';
            }
        } else {
            echo '<p>Секция "Преимущества" не найдена или не заполнена.</p>';
        }
        ?>
    </div>
</div>

    <!-- ------------------------------------------------------ End Advantages ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Time ----------------------------------------------------------------------- -->
    <?php $srok_section = get_field('srok'); ?>
    <section class="railway-page__time time-railway">
        <div class="time-railway__container">
            <h2 class="time-railway__title">
                <?php echo $srok_section['tekst']; ?> <span><?php echo $srok_section['kolichestvo']; ?></span>
            </h2>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Time ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Simple ----------------------------------------------------------------------- -->
    <?php $dejstviya_section = get_field('dejstviya'); ?>
    <section class="railway-page__simple simple-railway">
        <div class="simple-railway__container">
            <h2 class="simple-railway__title _title">
                <?php echo $dejstviya_section['zagolovok']; ?>
            </h2>
            <?php $dejstviya_section_items = $dejstviya_section['elementy']; ?>
            <div class="simple-railway__items">

                <?php
                if ($dejstviya_section_items) {
                    foreach ($dejstviya_section_items as $dejstviya_section_item) {
                ?>

                        <div class="simple-railway__item">
                            <span>
                                <?php echo $dejstviya_section_item['tekst']; ?>
                            </span>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="simple-railway__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Simple ----------------------------------------------------------------------- -->
	
	
	
    <!-- ------------------------------------------------------ Influence ----------------------------------------------------------------------- -->
    <?php $stoimost_section = get_field('stoimost'); ?>
    <section class="railway-page__influence influence-railway">
        <div class="influence-railway__container">
            <h2 class="influence-railway__title _title">
                <?php echo $stoimost_section['zagolovok']; ?>
            </h2>
            <div class="influence-railway__items">
                <div class="influence-railway__top">
                    <div class="influence-railway__item">
                        <?php echo $stoimost_section['element_1']; ?>
                    </div>
                    <div class="influence-railway__item">
                        <?php echo $stoimost_section['element_2']; ?>
                    </div>
                    <div class="influence-railway__item">
                        <?php echo $stoimost_section['element_3']; ?>
                    </div>
                </div>
                <div class="influence-railway__bottom">
                    <?php echo $stoimost_section['element_4']; ?>
                </div>
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Influence ------------------------------------------------->
	
	<!-- ------------------------------------------------------ raschet stoim ------------------------------------------------->
	
	
	<?php $stoimost_section = get_field('stoimost2'); ?>
<?php if ($stoimost_section) : ?>
    <section class="avia-page__price price-avia">
        <div class="price-avia__container">
            <h2 class="price-avia__title _title">
                <?php echo esc_html($stoimost_section['zagolovok']); ?>
            </h2>
            <?php $stoimost_section_items = $stoimost_section['elementy']; ?>
            <div class="price-avia__items">

                <?php if ($stoimost_section_items) : ?>
                    <?php foreach ($stoimost_section_items as $stoimost_section_item) : ?>
                        <div class="price-avia__item">
                            <div class="price-avia__price">
                                <?php echo esc_html($stoimost_section_item['tekst']); ?>
                            </div>
                            <button class="price-avia__btn _btn" data-goto=".consult">
                                Рассчитать
                            </button>
                        </div>
                    <?php endforeach; ?>
                <?php else : ?>
                    <p>Цены уточняйте у менеджеров по указанным контактам.</p>
                <?php endif; ?>

            </div>
        </div>
    </section>
<?php endif; ?>
<!-- ------------------------------------------------------end raschet stoim ------------------------------------------------->
	
	
	
	
	
	
	
	
	
	
	
	
    <!-- ------------------------------------------------------ Why ----------------------------------------------------------------------- -->
    <?php $prichiny_section = get_field('prichiny'); ?>
    <section class="railway-page__why why-railway">
        <div class="why-railway__container">
            <h2 class="why-railway__title _title">
                <?php echo $prichiny_section['zagolovok']; ?>
            </h2>
            <?php $prichiny_section_items = $prichiny_section['elementy']; ?>
            <div class="why-railway__items">

                <?php
                if ($prichiny_section_items) {
                    foreach ($prichiny_section_items as $prichiny_section_item) {
                ?>

                        <div class="why-railway__item item-why-railway">
                            <div class="item-why-railway__title">
                                <?php echo $prichiny_section_item['element']['zagolovok']; ?>
                            </div>
                            <div class="item-why-railway__text">
                                <?php echo $prichiny_section_item['element']['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="why-railway__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Why ----------------------------------------------------------------------- -->
	
	<!--text start--->
	
	<?php
// Получаем данные из поля ACF
$tekstovyj_blok_faq = get_field('tekstovyj_blok_faq');

// Проверяем, заполнено ли поле
if ($tekstovyj_blok_faq) :
?>
    <section class="faq-text-block">
        <div class="faq-text-block__container">
            <?php echo $tekstovyj_blok_faq; // Выводим текстовый блок ?>
        </div>
    </section>
<?php endif; ?>

	<!--text finish--->

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
    <!-- ------------------------------------------------------ Projects--------------------------------------------------- -->
    <?php
	/*
	$args = array(
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
    <?php wp_reset_query(); 
	*/
	?>
    <!-- ------------------------------------------------------ End Projects------------------------------------------------------------ -->
    <!-- ------------------------------------------------------ Trust ---------------------------------------->
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
                    if ($logos) {
                        foreach ($logos as $logo) {
                            // Проверяем структуру массива и наличие URL
                            $image_url = is_array($logo['logo']) ? $logo['logo']['url'] : $logo['logo'];
                            $image_alt = is_array($logo['logo']) ? $logo['logo']['alt'] : ''; // Используем alt, если доступен
							$image_title = isset($logo['logo']['title']) ? $logo['logo']['title'] : '';
                            
                            if (!empty($image_url)): ?>
                                <div class="trust-main__slide swiper-slide">
                                    <img src="<?php echo esc_url($image_url); ?>" alt="<?php echo esc_attr($image_alt); ?>" title="<?php echo esc_attr($image_title); ?>">
                                </div>
                            <?php else: ?>
                                <div class="trust-main__slide swiper-slide">
                                    <p>Изображение отсутствует</p>
                                </div>
                            <?php endif; ?>
                        <?php
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

    <!-- ------------------------------------------------------ End Trust ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Offices ----------------------------------------------------------------------- -->
  <?php $main_offices = get_field('ofisy', 7); ?>
<section class="main-page__offices offices-main">
    <div class="offices-main__container">
        <h2 class="offices-main__title _title">
            <?php echo esc_html($main_offices['zagolovok']); ?>
        </h2>
        <div class="offices-main__items">

            <?php $offices = $main_offices['ofis']; ?>
            <?php
            if ($offices) {
                foreach ($offices as $office) {
                    // Проверяем, является ли 'izobrazhenie' массивом, и получаем URL корректно
                    $image_url = is_array($office['izobrazhenie']) ? $office['izobrazhenie']['url'] : $office['izobrazhenie'];
                    $image_alt = is_array($office['izobrazhenie']) && isset($office['izobrazhenie']['alt']) ? $office['izobrazhenie']['alt'] : ''; // Получаем alt, если он есть
					$image_title = is_array($office['izobrazhenie']) && isset($office['izobrazhenie']['title']) ? $office['izobrazhenie']['title'] : '';

                    // Проверка на наличие изображения
                    if (!empty($image_url)): ?>
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
                    <?php else: ?>
                        <p>Изображение отсутствует для офиса: <?php echo esc_html($office['gorod']); ?></p>
                    <?php endif;
                }
            } else {
                echo '<p>Офисы не найдены.</p>';
            }
            ?>

        </div>
    </div>
</section>
  <!---offises finish ----------------------------------------------------------------------- -->
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
