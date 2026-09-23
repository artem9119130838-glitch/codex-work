<?php /* Template Name: Template Caterpillar */
get_header();
?>

<main class="page caterpillar-page">
    <?php $hero_main = get_field('glavnaya_sekcziya'); ?>
    <section class="caterpillar-page__hero hero-main">
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
                    <button class="hero-main__btn _btn" data-goto=".consult">
                        Оставить заявку
                    </button>
                </div>
                <div class="hero-main__hexagons">
                    <div class="hero-main__hexagon-img">
                        <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                            <pattern id="img" patternContentUnits="objectBoundingBox" width="100%" height="100%">
                                <image height="1" width="1" preserveAspectRatio="xMidYMid slice" xlink:href="<?php echo $hero_main['izobrazhenie']; ?>" />
                            </pattern>
                            <path fill="url(#img)" d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
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
    <div class="caterpillar-page__advantages advantages-brevini">
        <div class="advantages-brevini__container">
            <?php $second_section_items = $second_section['elementy']; ?>
            <div class="advantages-brevini__items">
<?php
            if (!empty($second_section_items)) {
                foreach ($second_section_items as $second_section_item) {
                    // Данные
                    $img_url = $second_section_item['izobrazhenie'] ?? '';
                    $img_alt = $second_section_item['img_alt'] ?? '';
                    $img_title = $second_section_item['img_title'] ?? '';
                    $text = $second_section_item['tekst'] ?? '';

                    // Проверяем наличие URL изображения
                    if (!empty($img_url)) {
            ?>
                        <div class="advantages-brevini__item">
                            <div class="advantages-brevini__img">
                                <img src="<?php echo esc_url($img_url); ?>" 
                                    alt="<?php echo esc_attr($img_alt); ?>" 
                                    title="<?php echo esc_attr($img_title); ?>">
                            </div>
                            <div class="advantages-brevini__text">
                                <?php echo $second_section_item['tekst']; ?>
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
    </div>
    <!-- ------------------------------------------------------ End Advantages ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ About ----------------------------------------------------------------------- -->
    <?php $opisanie_section = get_field('opisanie'); ?>
    <div class="caterpillar-page__about about-caterpillar">
        <div class="about-caterpillar__container">
            <div class="about-caterpillar__text page-content">
                <?php echo $opisanie_section['tekst']; ?>
            </div>
        </div>
    </div>
    <!-- ------------------------------------------------------ End About ------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Production ---------------------------------------------------------------- -->
   <?php $produkcziya_section = get_field('produkcziya'); ?>
<?php if ($produkcziya_section): ?>
    <div class="caterpillar-page__production production-caterpillar">
        <div class="production-caterpillar__container">
            <h2 class="production-caterpillar__title _title">
                <?php echo esc_html($produkcziya_section['zagolovok'] ?? ''); ?>
            </h2>
            <div class="production-caterpillar__img">
                <?php 
                $image_url = $produkcziya_section['izobrazhenie'] ?? '';
                if ($image_url): ?>
                    <img src="<?php echo esc_url($image_url); ?>" alt="Поставки напрямую от производителя" title="Оригинальная продукция от официального дистрибьютера">
                <?php else: ?>
                    <p>Изображение отсутствует</p>
                <?php endif; ?>
            </div>
            <?php $produkcziya_section_items = $produkcziya_section['punkty'] ?? []; ?>
            <ul class="production-caterpillar__items">
                <?php if (!empty($produkcziya_section_items) && is_array($produkcziya_section_items)): ?>
                    <?php foreach ($produkcziya_section_items as $produkcziya_section_item): ?>
                        <?php 
                        $punkt = $produkcziya_section_item['punkt'] ?? '';
                        if ($punkt): ?>
                            <li class="production-caterpillar__item">
                                <?php echo esc_html($punkt); ?>
                            </li>
                        <?php else: ?>
                            <li class="production-caterpillar__item">Данные отсутствуют</li>
                        <?php endif; ?>
                    <?php endforeach; ?>
                <?php else: ?>
                    <li class="production-caterpillar__item">Элементы не найдены</li>
                <?php endif; ?>
            </ul>
            <button class="production-caterpillar__btn _btn" data-goto=".consult">
                Заказать оборудование
            </button>
        </div>
    </div>
<?php else: ?>
    <p>Данные для раздела продукции отсутствуют.</p>
<?php endif; ?>

    <!-- ------------------------------------------------------ End Production ------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Stages ----------------------------------------------------------------------- -->
    <?php $etapy_raboty_section = get_field('etapy_raboty'); ?>
    <section class="import-page__stages search-why">
        <div class="search-why__container">
            <h2 class="search-why__title _title">
                <?php echo $etapy_raboty_section['zagolovok']; ?>
            </h2>
            <div class="search-why__block">
                <?php $etapy_raboty_section_items = $etapy_raboty_section['punkty']; ?>
                <div class="search-why__items">

                    <?php
                    if ($etapy_raboty_section_items) {
                        foreach ($etapy_raboty_section_items as $etapy_raboty_section_item) {
                    ?>

                            <div class="search-why__item">
                                <?php echo $etapy_raboty_section_item['punkt']; ?>
                            </div>

                    <?php
                        }
                    }
                    ?>

                </div>
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Stages ------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Why ----------------------------------------------------------------------- -->
    <?php $pochemu_section = get_field('pochemu'); ?>
    <section class="caterpillar-page__why why-brevini">
        <div class="why-brevini__container">
            <h2 class="why-brevini__title _title">
                <?php echo $pochemu_section['zagolovok']; ?>
            </h2>
            <?php $pochemu_section_items = $pochemu_section['punkty']; ?>
            <ul class="why-brevini__ul">

                <?php
                if ($pochemu_section_items) {
                    foreach ($pochemu_section_items as $pochemu_section_item) {
                ?>

                        <li class="why-brevini__li">
                            <?php echo $pochemu_section_item['punkt']; ?>
                        </li>

                <?php
                    }
                }
                ?>

            </ul>
            <button class="why-brevini__btn _btn" data-goto=".consult">
                Заказать оборудование
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Why ------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Repair ----------------------------------------------------------------------- -->
    <?php $o_zapchastyah_section = get_field('o_zapchastyah'); ?>
    <div class="caterpillar-page__repair repair-caterpillar">
        <div class="repair-caterpillar__container">
            <div class="repair-caterpillar__body">
                <div class="repair-caterpillar__img">
                    <img src="<?php echo $o_zapchastyah_section['izobrazhenie']; ?>" alt="Гарантия качества и лучшей цены" title="Доставка в срок до вашего склада">
                </div>
                <div class="repair-caterpillar__text">
                    <?php echo $o_zapchastyah_section['tekst']; ?>
                </div>
            </div>
        </div>
    </div>
    <!-- ------------------------------------------------------ End Repair ------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Trust ------------------------------------------------------------------ -->
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

    <!-- ------------------------------------------------------ End Trust ------------------------------------------------------------ -->
    <!-- ------------------------------------------------------ Offices--------------------------------------------------------------- -->
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
   
    <!-- ------------------------------------------------------ End Offices-------------------------------------------------------------- -->
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
