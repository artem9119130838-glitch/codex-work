<?php /* Template Name: Template Services */
get_header();
?>

<main class="page services-page">
    <?php $hero_main = get_field('glavnaya_sekcziya'); ?>
    <section class="services-page__hero hero-main">
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
    <div class="services-page__advantages advantages-services">
        <div class="advantages-services__container">
            <h2 class="advantages-services__title _title">
                <?php echo $second_section['zagolovok']; ?>
            </h2>
            <?php $second_section_items = $second_section['elementy']; ?>
            <div class="advantages-services__items">

                <?php
                if ($second_section_items) {
                    foreach ($second_section_items as $second_section_item) {
                ?>

                        <div class="advantages-services__item">
                            <div class="advantages-services__img">
                                <img src="<?php echo $second_section_item['izobrazhenie']; ?>" 
									 alt="<?php echo $second_section_item['img_alt']; ?>" 
									 title="<?php echo $second_section_item['img_title']; ?>">
                            </div>
                            <div class="advantages-services__text">
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
    <!-- ------------------------------------------------------ Representative ----------------------------------------------------------------------- -->
    <?php $preimushhestva_section = get_field('preimushhestva'); ?>
    <section class="services-page__representative representative-services">
        <div class="representative-services__container">
            <h2 class="representative-services__title _title">
                <?php echo $preimushhestva_section['zagolovok']; ?>
            </h2>
            <?php $preimushhestva_section_items = $preimushhestva_section['punkty']; ?>
            <div class="representative-services__items">

                <?php
                if ($preimushhestva_section_items) {
                    foreach ($preimushhestva_section_items as $preimushhestva_section_item) {
                ?>

                        <div class="representative-services__item item-services-representative">
                            <div class="item-services-representative__title">
                                <?php echo $preimushhestva_section_item['zagolovok']; ?>
                            </div>
                            <div class="item-services-representative__text">
                                <?php echo $preimushhestva_section_item['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="representative-services__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Representative ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Complex ----------------------------------------------------------------------- -->
    <?php $kompleksnye_section = get_field('kompleksnye'); ?>
    <section class="services-page__complex complex-services">
        <div class="complex-services__container">
            <h2 class="complex-services__title _title">
                <?php echo $kompleksnye_section['zagolovok']; ?>
            </h2>
            <div class="complex-services__body">
                <button type="button" class="complex-services__btn-slider complex-services__btn-prev">
                    <svg xmlns="http://www.w3.org/2000/svg" width="21" height="29" viewBox="0 0 21 29" fill="none">
                        <path d="M17.5156 0.000141144C17.0674 -0.000911713 16.6244 0.0673809 16.2194 0.199999C15.8144 0.332619 15.4576 0.526194 15.1752 0.766499L0.682587 13.1939C0.241262 13.5645 0 14.0294 0 14.5091C0 14.9889 0.241262 15.4538 0.682587 15.8244L15.6853 28.2518C16.1946 28.6747 16.9265 28.9407 17.7199 28.9912C18.5133 29.0417 19.3033 28.8726 19.916 28.521C20.5288 28.1695 20.9142 27.6643 20.9873 27.1166C21.0605 26.5689 20.8154 26.0236 20.3061 25.6006L6.8937 14.4988L19.856 3.39696C20.223 3.09294 20.456 2.72272 20.5277 2.33012C20.5993 1.93752 20.5066 1.53897 20.2603 1.18162C20.0141 0.82428 19.6248 0.523098 19.1384 0.313717C18.652 0.104336 18.0888 -0.00448227 17.5156 0.000141144Z" fill="#B4B9C3" />
                    </svg>
                </button>
                <div class="complex-services__slider swiper">
                    <div class="complex-services__wrapper swiper-wrapper">

                        <?php $kompleksnye_section_items = $kompleksnye_section['kartochki']; ?>
                        <?php
                        if ($kompleksnye_section_items) {
                            foreach ($kompleksnye_section_items as $kompleksnye_section_item) {
                        ?>

                                <div class="complex-services__slide swiper-slide">
							<a href="<?php echo $kompleksnye_section_item['link']; ?>" title="<?php echo $kompleksnye_section_item['link_title']; ?>">
							        <div class="complex-services__item item-complex-services">									
                                        <div class="item-complex-services__title">
                                            <?php echo $kompleksnye_section_item['zagolovok']; ?>
                                        </div>
                                        <div class="item-complex-services__text">
                                            <?php echo $kompleksnye_section_item['tekst']; ?>
                                        </div>							
                                    </div>
							</a>
                                </div>

                        <?php
                            }
                        }
                        ?>

                    </div>
                </div>
                <button type="button" class="complex-services__btn-slider complex-services__btn-next">
                    <svg xmlns="http://www.w3.org/2000/svg" width="21" height="29" viewBox="0 0 21 29" fill="none">
                        <path d="M3.48438 28.9999C3.93264 29.0009 4.37555 28.9326 4.78057 28.8C5.18558 28.6674 5.54239 28.4738 5.8248 28.2335L20.3174 15.8061C20.7587 15.4355 21 14.9706 21 14.4909C21 14.0111 20.7587 13.5462 20.3174 13.1756L5.31471 0.748237C4.8054 0.325256 4.07354 0.0592593 3.28012 0.00876309C2.4867 -0.0417331 1.69671 0.127408 1.08395 0.478976C0.471189 0.830544 0.0858477 1.33574 0.012697 1.88343C-0.0604556 2.43112 0.184572 2.97643 0.69388 3.39941L14.1063 14.5012L1.14396 25.603C0.777044 25.9071 0.543971 26.2773 0.47232 26.6699C0.400668 27.0625 0.493436 27.461 0.739648 27.8184C0.98586 28.1757 1.37521 28.4769 1.86163 28.6863C2.34805 28.8957 2.91118 29.0045 3.48438 28.9999Z" fill="#B4B9C3" />
                    </svg>
                </button>
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Complex ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Base ----------------------------------------------------------------------- -->
    <?php $baza_section = get_field('baza'); ?>
    <section class="services-page__base base-services">
        <div class="base-services__container">
            <h2 class="base-services__title _title">
                <?php echo $baza_section['zagolovok']; ?>
            </h2>
            <div class="base-services__text">
                <?php echo $baza_section['tekst']; ?>
            </div>
            <button class="base-services__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Base ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Pluses ----------------------------------------------------------------------- -->
    <?php $plyusy_section = get_field('plyusy'); ?>
    <section class="services-page__pluses pluses-services">
        <div class="pluses-services__container">
            <h2 class="pluses-services__title _title">
                <?php echo $plyusy_section['zagolovok']; ?>
            </h2>
            <?php $plyusy_section_items = $plyusy_section['punkty']; ?>
            <div class="pluses-services__items">

                <?php
                if ($plyusy_section_items) {
                    foreach ($plyusy_section_items as $plyusy_section_item) {
                ?>

                        <div class="pluses-services__item item-pluses-services">
                            <div class="item-pluses-services__title">
                                <?php echo $plyusy_section_item['zagolovok']; ?>
                            </div>
                            <div class="item-pluses-services__text">
                                <?php echo $plyusy_section_item['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="pluses-services__btn _btn">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Pluses ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Projects----------------------------------------------------------- -->
  
    <!-- ------------------------------------------------------ End Projects------------------------------------------------------ -->
    <!-- ------------------------------------------------------ Trust -------------------------------------------------------- -->
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
    <!-- ------------------------------------------------------ Offices---------------------------------------------------------- -->
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
   
    <!-- ------------------------------------------------------ End Offices-------------------------------------------------------- -->
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
                                            <p><?php echo $spoller['otvet']; ?></p>
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
