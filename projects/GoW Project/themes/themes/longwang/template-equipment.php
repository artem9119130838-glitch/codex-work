<?php /* Template Name: Template Equipment */
get_header();
?>

<main class="page equipment-page">
    <?php $hero_main = get_field('glavnaya_sekcziya'); ?>
    <section class="equipment-page__hero hero-main">
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
                echo '';
            }
            ?>

        </div>
    </div>
</div>
<!-- ------------------------------------------------------ End Advantages ---------------------- -->

	
	<!-- ----------------------------------- Manufacturers Logos ------------------------------------------------------ -->
<?php
$manufacturers_title = get_field('manufacturers_title');
$manufacturers_logos = get_field('logo_manufactura');

if (!empty($manufacturers_logos)) :
?>
<section class="equipment-page__manufacturers manufacturers-equipment">
    <div class="manufacturers-equipment__container">
        <?php if ($manufacturers_title): ?>
            <h2 class="manufacturers-equipment__title _title"><?php echo esc_html($manufacturers_title); ?></h2>
        <?php endif; ?>

        <div class="manufacturers-equipment__items">
            <?php
            foreach ($manufacturers_logos as $manufacturer_logo) {
                $image = $manufacturer_logo['img_logo'];
                $link = isset($manufacturer_logo['link_logo']['url']) ? $manufacturer_logo['link_logo']['url'] : '#';
                $link_title = isset($manufacturer_logo['link_title']) ? $manufacturer_logo['link_title'] : '';
                $img_alt = isset($manufacturer_logo['img_alt']) ? $manufacturer_logo['img_alt'] : '';
                $img_title = isset($manufacturer_logo['img_title']) ? $manufacturer_logo['img_title'] : '';
                $name = isset($manufacturer_logo['logo_manufactura']) ? $manufacturer_logo['logo_manufactura'] : '';

                if ($image && isset($image['url'])) {
                    $width = isset($image['width']) ? $image['width'] : 'auto';
                    $height = isset($image['height']) ? $image['height'] : 'auto';
                    ?>
                    <div class="manufacturers-equipment__item">
                        <a href="<?php echo esc_url($link); ?>" 
                           title="<?php echo esc_attr($link_title); ?>" 
                           target="_blank" 
                           rel="noopener noreferrer">
                            <img src="<?php echo esc_url($image['url']); ?>" 
                                 alt="<?php echo esc_attr($img_alt); ?>" 
                                 title="<?php echo esc_attr($img_title); ?>" 
                                 class="manufacturers-equipment__logo" 
                                 width="<?php echo esc_attr($width); ?>" 
                                 height="<?php echo esc_attr($height); ?>">
                        </a>
                        <div class="manufacturers-equipment__name"><?php echo esc_html($name); ?></div>
                    </div>
                    <?php
                }
            }
            ?>
        </div>
    </div>
</section>
<?php endif; ?>



<!-- ------------------------------------------------------ End Manufacturers Logos--------------------------------------------- -->
    <!-- ------------------------------------------------------ Which ----------------------------------------------------------------------- -->
    <?php $oborudovanie = get_field('oborudovanie'); ?>
    <section class="equipment-page__which which-equipment">
        <div class="which-equipment__container">
            <h2 class="which-equipment__title _title">
                <?php echo $oborudovanie['zagolovok']; ?>
            </h2>
            <div class="which-equipment__text page-content">
                <?php echo $oborudovanie['tekst']; ?>
            </div>
            <?php $oborudovanie_items = $oborudovanie['kartochki']; ?>
            <div class="which-equipment__items">

                <?php
                if ($oborudovanie_items) {
                    foreach ($oborudovanie_items as $oborudovanie_item) {
                ?>

                        <div class="which-equipment__item item-which">
                            <div class="item-which__title">
                                <?php echo $oborudovanie_item['kartochka']['zagolovok']; ?>
                            </div>
                            <div class="item-which__text">
                                <?php echo $oborudovanie_item['kartochka']['tekst']; ?>
                            </div>
                        </div>

                <?php
                    }
                }
                ?>
				</div>
            </div>
    </section>
    <!-- ------------------------------------------------------ End Which ------------------------------------------------------ -->	
    <!-- ------------------------------------------------------ What ----------------------------------------------------------------------- -->
    <?php $predlozheniya = get_field('predlozheniya'); ?>
    <section class="equipment-page__what what-equipment">
        <div class="what-equipment__container">
            <h2 class="what-equipment__title _title">
                <?php echo $predlozheniya['zagolovok']; ?>
            </h2>
            <?php $predlozheniya_items = $predlozheniya['punkty']; ?>
            <div class="what-equipment__items">

                <?php
                if ($predlozheniya_items) {
                    foreach ($predlozheniya_items as $predlozheniya_item) {
                ?>

                        <div class="what-equipment__item">
                            <?php echo $predlozheniya_item['punkt']; ?>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End What ------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Advantages ----------------------------------------------------------------------- -->
    <?php $preimushhestva = get_field('preimushhestva'); ?>
    <section class="equipment-page__advantages advantages-equipment">
        <div class="advantages-equipment__container">
            <h2 class="advantages-equipment__title _title">
                <?php echo $preimushhestva['zagolovok']; ?>
            </h2>
            <?php $preimushhestva_items = $preimushhestva['punkty']; ?>
            <div class="advantages-equipment__items">

                <?php
                if ($preimushhestva_items) {
                    foreach ($preimushhestva_items as $preimushhestva_item) {
                ?>

                        <div class="advantages-equipment__item">
                            <?php echo $preimushhestva_item['punkt']; ?>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <button class="advantages-equipment__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Advantages ------------------------------------------------------------------- -->
		
    <!-- ------------------------------------------------------ About ----------------------------------------------------------------------- -->
    <?php $opisanie = get_field('opisanie'); ?>
    <div class="equipment-page__about about-equipment">
        <div class="about-equipment__container">
			<h2 class="about-equipment__title _title">
                <?php echo $opisanie['title']; ?>
            </h2>
            <div class="about-equipment__text page-content">
                <?php echo $opisanie['tekst']; ?>
            </div>
        </div>
    </div>
    <!-- ------------------------------------------------------ End About ------------------------------------------------------------------- -->

    <!-- ------------------------------------------------------ Stages ----------------------------------------------------------------------- -->
    <?php $text_bottom = get_field('tekst_bottom'); ?>
    <div class="equipment-page__stages stages-equipment">
        <div class="stages-equipment__container">
            <div class="stages-equipment__text page-content">
                <?php echo $text_bottom; ?>
            </div>
        </div>
    </div>
    <!-- ------------------------------------------------------ End Stages ------------------------------------------------------------------- -->
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
