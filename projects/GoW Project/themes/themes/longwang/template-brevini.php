<?php /* Template Name: Template Brevini */
get_header();
?>

<main class="page brevini-page">
    <?php $hero_main = get_field('glavnaya_sekcziya'); ?>
    <section class="brevini-page__hero hero-main">
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
                        <img
                            src="<?php echo esc_url($hero_main['izobrazhenie']); ?>"
                            alt="<?php echo esc_attr($hero_main['zagolovok']); ?>"
                            title="<?php echo esc_attr($hero_main['zagolovok']); ?>"
                            class="hero-main__hexagon-media"
                            width="337"
                            height="389"
                            fetchpriority="high"
                            loading="eager"
                            decoding="async"
                        >
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
    <!-- ------------------------------------------------------ Production ----------------------------------------------------------------------- -->

    <?php $produkcziya_section = get_field('produkcziya'); ?>
    <section class="brevini-page__production production-brevini">
        <div class="production-brevini__container">
            <h2 class="production-brevini__title _title">
                <?php echo $produkcziya_section['zagolovok']; ?>
            </h2>
            <div class="production-brevini__body">
                <button type="button" class="production-brevini__btn-slider production-brevini__btn-prev">
                    <svg xmlns="http://www.w3.org/2000/svg" width="21" height="34" viewBox="0 0 21 34" fill="none">
                        <path d="M17.5156 0.000167847C17.0674 -0.00106812 16.6244 0.0790024 16.2194 0.234486C15.8144 0.389969 15.4576 0.616917 15.1752 0.898655L0.682587 15.4687C0.241262 15.9032 0 16.4482 0 17.0107C0 17.5732 0.241262 18.1182 0.682587 18.5527L15.6853 33.1228C16.1946 33.6187 16.9265 33.9305 17.7199 33.9897C18.5133 34.0489 19.3033 33.8506 19.916 33.4384C20.5288 33.0263 20.9142 32.434 20.9873 31.7918C21.0605 31.1497 20.8154 30.5104 20.3061 30.0145L6.8937 16.9986L19.856 3.98265C20.223 3.6262 20.456 3.19216 20.5277 2.73187C20.5993 2.27158 20.5066 1.80431 20.2603 1.38535C20.0141 0.966396 19.6248 0.613289 19.1384 0.367805C18.652 0.122326 18.0888 -0.00525284 17.5156 0.000167847Z" fill="#B4B9C3" />
                    </svg>
                </button>
                <?php $produkcziya_section_slides = $produkcziya_section['kartochki']; ?>
                <div class="production-brevini__slider swiper">
                    <div class="production-brevini__wrapper swiper-wrapper">

                        <?php
                        if ($produkcziya_section_slides) {
                            foreach ($produkcziya_section_slides as $produkcziya_section_slide) {
                        ?>

                                <?php $produkcziya_section_slide_item = $produkcziya_section_slide['kartochka']; ?>
                                <div class="production-brevini__slide swiper-slide">
                                    <div class="production-brevini__item item-prod-brevini">
                                        <div class="item-prod-brevini__title">
                                            <?php echo $produkcziya_section_slide_item['zagolovok']; ?>
                                        </div>
                                        <?php $produkcziya_section_slide_item_punkty = $produkcziya_section_slide_item['punkty']; ?>
                                        <div class="item-prod-brevini__items">

                                            <?php
                                            if ($produkcziya_section_slide_item_punkty) {
                                                foreach ($produkcziya_section_slide_item_punkty as $produkcziya_section_slide_item_punkt) {
                                            ?>

                                                    <div class="item-prod-brevini__item">
                                                        <?php echo $produkcziya_section_slide_item_punkt['punkt']; ?>
                                                    </div>

                                            <?php
                                                }
                                            }
                                            ?>

                                        </div>
                                    </div>
                                </div>

                        <?php
                            }
                        }
                        ?>

                    </div>
                </div>
                <button type="button" class="production-brevini__btn-slider production-brevini__btn-next">
                    <svg xmlns="http://www.w3.org/2000/svg" width="21" height="34" viewBox="0 0 21 34" fill="none">
                        <path d="M3.48438 33.9998C3.93264 34.0011 4.37555 33.921 4.78057 33.7655C5.18558 33.61 5.54239 33.3831 5.8248 33.1013L20.3174 18.5313C20.7587 18.0968 21 17.5518 21 16.9893C21 16.4268 20.7587 15.8818 20.3174 15.4473L5.31471 0.877243C4.8054 0.381335 4.07354 0.0694764 3.28012 0.010274C2.4867 -0.0489284 1.69671 0.149375 1.08395 0.561558C0.471189 0.973741 0.0858477 1.56604 0.012697 2.20816C-0.0604556 2.85028 0.184572 3.48961 0.69388 3.98552L14.1063 17.0014L1.14396 30.0174C0.777044 30.3738 0.543971 30.8078 0.47232 31.2681C0.400668 31.7284 0.493436 32.1957 0.739648 32.6146C0.98586 33.0336 1.37521 33.3867 1.86163 33.6322C2.34805 33.8777 2.91118 34.0053 3.48438 33.9998Z" fill="#B4B9C3" />
                    </svg>
                </button>
            </div>
            <button class="production-brevini__btn _btn" data-goto=".consult">
                Заказать оборудование
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Production ------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Variants ----------------------------------------------------------------------- -->
    <?php $varianty_section = get_field('varianty'); ?>
    <section class="brevini-page__variants variants-brevini">
        <div class="variants-brevini__container">
            <h2 class="variants-brevini__title _title">
                <?php echo $varianty_section['zagolovok']; ?>
            </h2>
            <?php $varianty_section_items = $varianty_section['element']; ?>
            <div class="variants-brevini__items">

                <?php
                if ($varianty_section_items) {
                    foreach ($varianty_section_items as $varianty_section_item) {
                ?>

                        <div class="variants-brevini__item">
                            <div class="variants-brevini__logo">
                                <img src="<?php echo $varianty_section_item['izobrazhenie'] ?? ''; ?>" 
								alt="<?php echo $varianty_section_item['img_alt'] ?? ''; ?>" 
								title="<?php echo $varianty_section_item['img_title'] ?? ''; ?>">
                            </div>
                            <div class="variants-brevini__text">
                                <?php echo $varianty_section_item['tekst'] ?? ''; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Variants ------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Why ----------------------------------------------------------------------- -->
    <?php $pochemu_section = get_field('pochemu'); ?>
    <section class="brevini-page__why why-brevini">
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
    <!-- ------------------------------------------------------ About ----------------------------------------------------------------------- -->
<?php $o_brende_section = get_field('o_brende'); ?>
<section class="brevini-page__about about-brevini">
    <div class="about-brevini__container">
        <h2 class="about-brevini__title _title">
            <?php echo $o_brende_section['zagolovok']; ?>
        </h2>
<?php
$about_image_url = $o_brende_section['izobrazhenie_1'] ?: ($o_brende_section['izobrazhenie_2'] ?? '');
$about_image_id = $about_image_url ? attachment_url_to_postid($about_image_url) : 0;
$about_image_alt = $about_image_id ? get_post_meta($about_image_id, '_wp_attachment_image_alt', true) : '';
$about_image_title = $about_image_id ? get_the_title($about_image_id) : '';
?>

<?php if (!empty($about_image_url)) { ?>
    <div class="about-brevini__imgs">
        <img src="<?php echo esc_url($about_image_url); ?>"
             alt="<?php echo esc_attr($about_image_alt); ?>"
             title="<?php echo esc_attr($about_image_title); ?>"
             width="107"
             height="65">
    </div>
<?php } ?>
            <div class="about-brevini__content">
                <?php echo $o_brende_section['tekst']; ?>
            </div>
        </div>
    </div>
</section>
    <!-- ------------------------------------------------------ End About ------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Trust -------------------------------------------------------------- -->
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

    <!-- ------------------------------------------------------ End Trust ----------------------------------------------------------------------- -->
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
