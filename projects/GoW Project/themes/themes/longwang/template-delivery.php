<?php /* Template Name: Template Delivery */
get_header();
?>

<main class="page delivery-page">
    <?php $hero_main = get_field('glavnaya_sekcziya'); ?>
    <section class="about-page__hero hero-main">
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
   <!-- ------------------------------------------------------ Advantages------------------------------------------------------ -->
<!-- ------------------------------------------------------ Advantages------------------------------------------------------ -->
<?php $second_section = get_field('vtoraya_sekcziya'); ?>
<div class="delivery-page__advantages adv-delivery">
    <div class="adv-delivery__container">

        <?php $second_section_items = $second_section['elementy']; ?>

        <div class="adv-delivery__items">

            <?php
            if ($second_section_items) {
                foreach ($second_section_items as $second_section_item) {
                    // Проверяем поля и задаем значения по умолчанию
                    $image_url = isset($second_section_item['izobrazhenie']) ? $second_section_item['izobrazhenie'] : '';
                    $image_alt = isset($second_section_item['img_alt']) ? $second_section_item['img_alt'] : '';
                    $image_title = isset($second_section_item['img_title']) ? $second_section_item['img_title'] : '';

                    // Выводим блок только если изображение задано
                    if (!empty($image_url)) {
            ?>

                        <div class="adv-delivery__item">
                            <div class="adv-delivery__img">
                                <img 
                                    src="<?php echo esc_url($image_url); ?>" 
                                    alt="<?php echo esc_attr($image_alt); ?>" 
                                    title="<?php echo esc_attr($image_title); ?>"
                                >
                            </div>
                            <div class="adv-delivery__text">
                                <?php echo esc_html($second_section_item['tekst']); ?>
                            </div>
                        </div>

            <?php
                    } else {
                        // Если изображение отсутствует
                        echo '<p>Изображение отсутствует.</p>';
                    }
                }
            } else {
                echo '<p>Элементы отсутствуют.</p>';
            }
            ?>

        </div>
    </div>
</div>
<!-- ------------------------------------------------------ End Advantages ---------------------- -->


<!-- ------------------------------------------------------ End Advantages --------------------------------------------------- -->

    <!-- ------------------------------------------------------ Kinds ----------------------------------------------------------------------- -->
    <?php $kinds_section = get_field('vidy_dostavki'); ?>
    <section class="delivery-page__kinds kinds-delivery">
        <div class="kinds-delivery__container">
            <h2 class="kinds-delivery__title _title">
                Виды доставки
            </h2>
            <div class="kinds-delivery__block">
                <?php $kinds_section_cargo = $kinds_section['dostavka_kargo']; ?>
                <div class="kinds-delivery__cargo cargo-kinds">
                    <?php $kinds_section_cargo_items = $kinds_section_cargo['kartochka']; ?>
                    <div class="cargo-kinds__items">

                        <?php
                        if ($kinds_section_cargo_items) {
                            foreach ($kinds_section_cargo_items as $kinds_section_cargo_item) {
                        ?>

                                <div class="cargo-kinds__item cargo-kind">
                                    <div class="cargo-kind__left">
                                        <div class="cargo-kind__title">
                                            <?php echo $kinds_section_cargo_item['nazvanie']; ?>
                                        </div>
                                        <div class="cargo-kind__weight">
                                            <?php echo $kinds_section_cargo_item['stoimost']; ?>
                                        </div>
                                        <div class="cargo-kind__time">
                                            <?php echo $kinds_section_cargo_item['srok']; ?>
                                        </div>
                                    </div>
                                    <div class="cargo-kind__right">
                                      <a href="<?php echo $kinds_section_cargo_item['link']; ?>" title="<?php echo $kinds_section_cargo_item['link_title']; ?>"> 
                                    <img src="<?php echo $kinds_section_cargo_item['ikonka']; ?>" 
                                    alt="<?php echo $kinds_section_cargo_item['img_alt']; ?>" 
                                    title="<?php echo $kinds_section_cargo_item['img_title']; ?>">
                                </a>
							<div class="cargo-kind__details">
								<a href="<?php echo $kinds_section_cargo_item['link']; ?>" title="<?php echo $kinds_section_cargo_item['link_title']; ?>">
                                <span>Подробнее</span>
									</a>
                            </div>
                                    </div>
                                </div>

                        <?php
                            }
                        }
                        ?>

                    </div>
                </div>
                <div class="kinds-delivery__multimodal multimodal-kinds">
                    <div class="multimodal-kinds__title">
                        МУЛЬТИМОДАЛЬНЫЕ ПЕРЕВОЗКИ
                    </div>
                    <button class="multimodal-kinds__btn _btn" data-goto=".consult">
                        Оставить заявку
                    </button>
                </div>
                <?php $kinds_section_tamozh = $kinds_section['tamozhennoe_oformlenie']; ?>
                <div class="kinds-delivery__custom custom-kinds">	
                    <div class="custom-kinds__title">
						<a href="<?php echo $kinds_section_tamozh['link']; ?>" title="<?php echo $kinds_section_tamozh['link_title']; ?>">
                        <?php echo $kinds_section_tamozh['zagolovok']; ?>
						</a>	
                    </div>
                    <?php $kinds_section_tamozh_items = $kinds_section_tamozh['punkty']; ?>
                    <ul class="custom-kinds__list">
                        <?php
                        if ($kinds_section_tamozh_items) {
                            foreach ($kinds_section_tamozh_items as $kinds_section_tamozh_item) {
                        ?>
                                <li class="custom-kinds__li">
                                    <?php echo $kinds_section_tamozh_item['tekst']; ?>
                                </li>
                        <?php
                            }
                        }
                        ?>
                    </ul>
					
                </div>
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Kinds ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Packs ----------------------------------------------------------------------- -->
    <?php $packs_section = get_field('vidy_upakovki'); ?>
    <div class="delivery-page__packs packs-delivery">
        <div class="packs-delivery__container">
            <h2 class="packs-delivery__title _title">
                <?php echo $packs_section['zagolovok']; ?>
            </h2>
            <?php $packs_section_items = $packs_section['kartochki']; ?>
            <div class="packs-delivery__items">

                <?php
                if ($packs_section_items) {
                    foreach ($packs_section_items as $packs_section_item) {
                ?>

                        <div class="packs-delivery__item item-del-pack">
                            <div class="item-del-pack__top">
                                <div class="item-del-pack__title">
                                    <?php echo $packs_section_item['nazvanie']; ?>
                                </div>
                                <div class="item-del-pack__img">
                                    <img src="<?php echo $packs_section_item['izobrazhenie']; ?>" alt="<?php echo $packs_section_item['img_alt']; ?>" title="<?php echo $packs_section_item['img_title']; ?>">
                                </div>
                            </div>
                            <div class="item-del-pack__bottom">
                                <?php echo $packs_section_item['czena']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
        </div>
    </div>
    <!-- ------------------------------------------------------ End Packs ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Reasons ----------------------------------------------------------------------- -->
    <?php $reasons_section = get_field('prichiny'); ?>
    <div class="delivery-page__reasons reasons-delivery">
        <div class="reasons-delivery__container">
            <h2 class="reasons-delivery__title _title">
                <?php echo $reasons_section['zagolovok']; ?>
            </h2>
            <?php $reasons_section_items = $reasons_section['elementy']; ?>
            <div class="reasons-delivery__items">

                <?php
                if ($reasons_section_items) {
                    foreach ($reasons_section_items as $reasons_section_item) {
                ?>

                        <div class="reasons-delivery__item item-delivery-reasons">
                            <div class="item-delivery-reasons__num">
                                <?php echo $reasons_section_item['nomer']; ?>
                            </div>
                            <div class="item-delivery-reasons__text">
                                <?php echo $reasons_section_item['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="reasons-delivery__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </div>
    <!-- ------------------------------------------------------ End Reasons ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Projects---------------------------------------------------------- -->
   
    <!-- ------------------------------------------------------ End Projects------------------------------------------------------ -->
    <!-- ------------------------------------------------------ Trust ----------------------------------------------------------- -->
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

    <!-- ------------------------------------------------------ End Trust------------------------------------------------------------ -->
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
 
    <!-- ------------------------------------------------------ End Offices------------------------------------------------------ -->
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
