<?php /* Template Name: Template Parallel */
get_header();
?>

<main class="page parallel-page">
    <?php $hero_main = get_field('glavnaya_sekcziya'); ?>
    <section class="parallel-page__hero hero-main">
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
    <section class="parallel-page__advantages advantages-parallel">
        <div class="advantages-parallel__container">
            <h2 class="advantages-parallel__title _title">
                <?php echo $second_section['zagolovok']; ?>
            </h2>
            <?php $second_section_items = $second_section['elementy']; ?>
            <div class="advantages-parallel__items">

                <?php
                if ($second_section_items) {
                    foreach ($second_section_items as $second_section_item) {
                ?>

                        <div class="advantages-parallel__item">
                            <div class="advantages-parallel__img">
                                <img src="<?php echo $second_section_item['izobrazhenie']; ?>" 
									alt="<?php echo $second_section_item['img_alt']; ?>" 
									title="<?php echo $second_section_item['img_title']; ?>">
                            </div>
                            <div class="advantages-parallel__text">
                                <?php echo $second_section_item['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <div class="advantages-parallel__bottom">
                <?php echo $second_section['nizhnij_tekst']; ?>
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Advantages ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Why ----------------------------------------------------------------------- -->
    <?php $prichiny_section = get_field('prichiny'); ?>
    <section class="parallel-page__why why-parallel">
        <div class="why-parallel__container">
            <h2 class="why-parallel__title _title">
                <?php echo $prichiny_section['zagolovok']; ?>
            </h2>
            <?php $prichiny_section_items = $prichiny_section['elementy']; ?>
            <div class="why-parallel__items">

                <?php
                if ($prichiny_section_items) {
                    foreach ($prichiny_section_items as $prichiny_section_item) {
                ?>

                        <div class="why-parallel__item item-why-parallel">
                            <div class="item-why-parallel__text">
                                <?php echo $prichiny_section_item['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="why-parallel__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Why ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Variants ----------------------------------------------------------------------- -->
    <?php $varianty_section = get_field('varianty'); ?>
    <section class="parallel-page__variants variants-parallel">
        <div class="variants-parallel__container">
            <h2 class="variants-parallel__title _title">
                <?php echo $varianty_section['zagolovok']; ?>
            </h2>
            <?php $varianty_section_items = $varianty_section['elementy']; ?>
            <div class="variants-parallel__items">

                <?php
                if ($varianty_section_items) {
                    foreach ($varianty_section_items as $varianty_section_item) {
                ?>

                        <div class="variants-parallel__item">
                            <?php echo $varianty_section_item['tekst']; ?>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Variants ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Conditions ----------------------------------------------------------------------- -->
    <?php $usloviya_section = get_field('usloviya'); ?>
    <section class="parallel-page__conditions conditions-parallel">
        <div class="conditions-parallel__container">
            <h2 class="conditions-parallel__title _title">
                <?php echo $usloviya_section['zagolovok']; ?>
            </h2>
            <?php $usloviya_section_items = $usloviya_section['punkty']; ?>
            <ul class="conditions-parallel__items">

                <?php
                if ($usloviya_section_items) {
                    foreach ($usloviya_section_items as $usloviya_section_item) {
                ?>

                        <li class="conditions-parallel__item">
                            <?php echo $usloviya_section_item['tekst']; ?>
                        </li>

                <?php
                    }
                }
                ?>

            </ul>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Conditions ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Trust ------------------------------------------------------ -->
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

    <!-- ------------------------------------------------------ End Trust--------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Offices-------------------------------------------------------------- -->
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
 
    <!-- ------------------------------------------------------ End Offices------------------------------------------------------- -->
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
