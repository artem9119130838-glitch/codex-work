<?php /* Template Name: Template Сustoms Сlearance */
get_header();
?>

<main class="page customs-clearance-page">
    <?php $hero_main = get_field('glavnaya_sekcziya'); ?>
    <section class="customs-clearance-page__hero hero-main">
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
<!-- ------------------------------------------------------ Advantages second -------------------------------------------------- -->
<?php $second_section = get_field('vtoraya_sekcziya'); ?>
<section class="customs-clearance-page__advantages advantages-outsorcing">
    <div class="advantages-outsorcing__container">
        <?php if (!empty($second_section['zagolovok'])): ?>
            <h2 class="advantages-outsorcing__title _title">
                <?php echo esc_html($second_section['zagolovok']); ?>
            </h2>
        <?php endif; ?>

        <?php $second_section_items = $second_section['elementy']; ?>
        <div class="advantages-outsorcing__items">
            <?php
            if (!empty($second_section_items)) {
                foreach ($second_section_items as $second_section_item) {
                    $img_url   = $second_section_item['izobrazhenie'] ?? '';
                    $img_alt   = $second_section_item['img_alt'] ?? '';
                    $img_title = $second_section_item['img_title'] ?? '';
                    $text      = $second_section_item['tekst'] ?? '';

                    if (!empty($img_url)) {
            ?>
                        <div class="advantages-outsorcing__item">
                            <div class="advantages-outsorcing__img">
                                <img
                                    src="<?php echo esc_url($img_url); ?>"
                                    alt="<?php echo esc_attr($img_alt); ?>"
                                    title="<?php echo esc_attr($img_title); ?>">
                            </div>
                            <div class="advantages-outsorcing__text">
                                <?php echo esc_html($text); ?>
                            </div>
                        </div>
            <?php
                    } else {
                        echo '<p>Изображение отсутствует.</p>';
                    }
                }
            } else {
                echo '<p>Элементы не найдены.</p>';
            }
            ?>
        </div>
    </div>
</section>

<!-- ------------------------------------------------------ End Advantages second--------------------------------------------------------- -->
<!-- ------------------------------------------------------ Stages ----------------------------------------------------------------------- -->
    <?php $etapy_section = get_field('etapy'); ?>
    <section class="customs-clearance-page__stages stages-customs-clearance">
        <div class="stages-customs-clearance__container">
            <h2 class="stages-customs-clearance__title _title">
                <?php echo $etapy_section['zagolovok']; ?>
            </h2>
            <?php $etapy_section_items = $etapy_section['punkty']; ?>
            <div class="stages-customs-clearance__items">

                <?php
                if ($etapy_section_items) {
                    foreach ($etapy_section_items as $etapy_section_item) {
                ?>

                        <div class="stages-customs-clearance__item">
                            <?php echo $etapy_section_item['tekst']; ?>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Stages ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Documents ----------------------------------------------------------------------- -->
<?php $dokumenty_section = get_field('dokumenty'); ?>
<section class="customs-clearance-page__bussines bussines-outsorcing">
    <div class="bussines-outsorcing__container">
        <h2 class="bussines-outsorcing__title _title">
            <?php echo esc_html($dokumenty_section['zagolovok']); ?>
        </h2>

        <?php $dokumenty_section_items = $dokumenty_section['kartochki']; ?>
        <div class="bussines-outsorcing__cards">
            <div class="bussines-outsorcing__items">
                <?php
                if ($dokumenty_section_items) {
                    foreach ($dokumenty_section_items as $dokumenty_section_item) {
                ?>
                    <div class="bussines-outsorcing__item item-outsorcing-bus">
                        <div class="item-outsorcing-bus__title">
                            <?php echo esc_html($dokumenty_section_item['zagolovok']); ?>
                        </div>
                        <div class="item-outsorcing-bus__text">
                            <?php echo wp_kses_post($dokumenty_section_item['tekst']); ?>
                        </div>
                    </div>
                <?php
                    }
                }
                ?>
            </div>
        </div>

        <button class="bussines-outsorcing__btn _btn" data-goto=".consult">
            Оставить заявку
        </button>
    </div>
</section>
    <!-- ------------------------------------------------------ End Documents ----------------------------------------------------------------------- -->
    
    <!-- ------------------------------------------------------ AdvTrust ----------------------------------------------------------------------- -->
    <?php $pochemu_section = get_field('pochemu'); ?>
    <section class="customs-clearance-page__advtrust advtrust-customs-clearance">
        <div class="advtrust-customs-clearance__container">
            <h2 class="advtrust-customs-clearance__title _title">
                <?php echo $pochemu_section['zagolovok']; ?>
            </h2>
            <?php $pochemu_section_items = $pochemu_section['kartochki']; ?>
            <div class="advtrust-customs-clearance__items">

                <?php
                if ($pochemu_section_items) {
                    foreach ($pochemu_section_items as $pochemu_section_item) {
                ?>

                        <div class="advtrust-customs-clearance__item item-advtrust">
                            <div class="item-advtrust__num">
                                <?php echo $pochemu_section_item['nomer']; ?>
                            </div>
                            <div class="item-advtrust__text">
                                <?php echo $pochemu_section_item['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="advtrust-customs-clearance__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End AdvTrust ----------------------------------------------------------------------- -->
	<!-- ------------------------------------------------------ Price ----------------------------------------------------------------------- -->
    <?php $czena_section = get_field('czena'); ?>
<section class="customs-clearance-page__price variants-parallel">
    <div class="variants-parallel__container">
        <h2 class="variants-parallel__title _title">
            <?php echo esc_html($czena_section['zagolovok']); ?>
        </h2>

        <?php $czena_section_items = $czena_section['kartochka']; ?>
        <div class="variants-parallel__items">
            <?php
            if (!empty($czena_section_items)) {
                foreach ($czena_section_items as $czena_section_item) {
            ?>
                    <div class="variants-parallel__item">
                        <?php echo $czena_section_item['tekst']; ?>
                    </div>
            <?php
                }
            }
            ?>
        </div>

    </div>
</section>
    <!-- ------------------------------------------------------ End Price ----------------------------------------------------------------------- -->
		
    <!-- ------------------------------------------------------ Projects ------------------------------------------------------- -->
  
    <!-- ------------------------------------------------------ End Projects ---------------------------------------------------- -->
    <!-- ------------------------------------------------------ Trust --------------------------------------------------------- -->
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
    <!-- ------------------------------------------------------ End Trust------------------------------------------------------ -->
    <!-- ------------------------------------------------------ Offices ------------------------------------------------------- -->
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
