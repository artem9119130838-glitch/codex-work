<?php /* Template Name: Template Home */
get_header();
?>

<main class="page main-page">
	
    <?php $hero_main = get_field('glavnaya_sekcziya'); ?>
    <section class="main-page__hero hero-main">
        <div class="hero-main__container">
            <div class="hero-main__top">
                <div class="hero-main__offer">
					<style>
						.hero-main__offer {
							max-width:550px;
						}
						.hero-main__title {
						font-size:56px;
							max-width: 850px;
						}
						@media(max-width:479.98px){
							.hero-main__title {
							font-size:30px;
							}
						}
					</style>
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
						 <title id="svgTitle">Импорт из Китая в Россию для бизнеса</title>  
                        </svg>
                    </div>
                    <div class="hero-main__hexagon-middle">
                        <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                            <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
							<title id="svgTitle">Оборудование для бизнеса</title>
                        </svg>
                    </div>
                    <div class="hero-main__hexagon-big">
                        <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                            <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
							 <title id="svgTitle">Параллельный импорт из Китая</title>
                        </svg>
                    </div>
                    <div class="hero-main__hexagon-small">
                        <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                            <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
							<title id="svgTitle">Все услуги по работе с Китаем</title>
                        </svg>
                    </div>
                </div>
            </div>
            <div class="hero-main__bottom">
                <?php $hero_advantages = $hero_main['preimushhestva']; ?>
                <div class="hero-main__advantages">
                    <?php $hero_adv_1 = $hero_advantages['punkt_1']; ?>
                    <div class="hero-main__advantage advantage-hero">
                        <div class="advantage-hero__img">
                            <img src="<?php echo $hero_adv_1['ikonka']; ?>" alt="Проверка китайского поставщика" title="Надёжный поставщик из Китая">
                        </div>
                        <p class="advantage-hero__text">
                            <?php echo $hero_adv_1['tekst']; ?>
                        </p>
                    </div>
                    <?php $hero_adv_2 = $hero_advantages['punkt_2']; ?>
                    <div class="hero-main__advantage advantage-hero">
                        <div class="advantage-hero__img">
                            <img src="<?php echo $hero_adv_2['ikonka']; ?>" alt="Фиксация бюджета и сроков импорта" title="Цена поставки и сроки прописаны в договоре">
                        </div>
                        <p class="advantage-hero__text">
                            <?php echo $hero_adv_2['tekst']; ?>
                        </p>
                    </div>
                    <?php $hero_adv_3 = $hero_advantages['punkt_3']; ?>
                    <div class="hero-main__advantage advantage-hero">
                        <div class="advantage-hero__img">
                            <img src="<?php echo $hero_adv_3['ikonka']; ?>" alt="Документы для импорта из Китая" title="ВЭД сопровождение">
                        </div>
                        <p class="advantage-hero__text">
                            <?php echo $hero_adv_3['tekst']; ?>
                        </p>
                    </div>
                    <?php $hero_adv_4 = $hero_advantages['punkt_4']; ?>
                    <div class="hero-main__advantage advantage-hero">
                        <div class="advantage-hero__img">
                            <img src="<?php echo $hero_adv_4['ikonka']; ?>" alt="Контроль качества в Китае" title="Инспекция товара в Китае">
                        </div>
                        <p class="advantage-hero__text">
                            <?php echo $hero_adv_4['tekst']; ?>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </section>
	
	
	
	
	
   <?php $second_section = get_field('vtoraya_sekcziya'); ?>
<section class="main-page__advantages advantages-main">
    <div class="advantages-main__container">
        
        <div class="advantages-main__img" data-da=".advantages-main__top,479.98,0">
            <?php
            // ----------------------------------------------
            // Начало правки: получаем массив данных изображения
            // ----------------------------------------------
            $image = $second_section['izobrazhenie']; // 'izobrazhenie' возвращает массив данных изображения
            // ----------------------------------------------
            // Конец правки
            // ----------------------------------------------
            
            // ----------------------------------------------
            // Начало правки: вывод изображения с alt и title
            // ----------------------------------------------
            if ($image) {
                // Выводим изображение с атрибутами alt и title, если массив не пуст
                echo '<img src="' . esc_url($image['url']) . '" alt="' . esc_attr($image['alt']) . '" title="' . esc_attr($image['title']) . '" loading="lazy" decoding="async">';
            }
            // ----------------------------------------------
            // Конец правки
            // ----------------------------------------------
            ?>
        </div>

        <div class="advantages-main__text">
            <div class="advantages-main__top">
                <h2 class="advantages-main__title _title">
                    <?php echo $second_section['zagolovok']; ?>
                </h2>
            </div>
            <?php $second_section_items = $second_section['punkty']; ?>
            <ul class="advantages-main__ul">

                <?php
                if ($second_section_items) {
                    foreach ($second_section_items as $second_section_item) {
                ?>

                        <li class="advantages-main__li">
                            <?php echo $second_section_item['punkt']; ?>
                        </li>

                <?php
                    }
                }
                ?>

            </ul>
            <button class="advantages-main__btn _btn" data-goto=".consult">
                Оставить заявку
            </button>
        </div>
    </div>
</section>

    <!-- ------------------------------------------------------ Services ----------------------------------------------------------------------- -->


	<?php $main_services = get_field('uslugi'); ?>
<section class="main-page__services services-main">
    <div class="services-main__container">
        <h2 class="services-main__title _title">
            <?php echo $main_services['zagolovok']; ?>
        </h2>
        <div class="services-main__items">
            <button type="button" class="services__btn-slider services__btn-prev">
                <img src="<?php echo get_stylesheet_directory_uri(); ?>/assets/img/icons/arrow-grey.svg" alt="Previous" title="Назад">
            </button>
            <div class="services__slider swiper">
                <div class="services__wrapper swiper-wrapper">
                    <?php $main_services_items = $main_services['usluga']; ?>
                    <?php
                    if ($main_services_items) {
                        foreach ($main_services_items as $main_services_item) {
                            
                            // ----------------------------------------------
                            // Начало правки: получение данных изображения как массива
                            // ----------------------------------------------
                            $image = $main_services_item['izobrazhenie']; // 'izobrazhenie' возвращает массив с данными изображения
                            $link = $main_services_item['usluga_link']['url'] ?? null; // Получаем URL из массива ссылки
                            $link_title = $main_services_item['usluga_link']['title'] ?? $main_services_item['tekst']; // Получаем title или используем текст по умолчанию
                            // ----------------------------------------------
                            // Конец правки
                            // ----------------------------------------------
                    ?>  
                            <div class="services__slide swiper-slide">
                                <div class="services-main__item item-serv-main">
                                    <div class="item-serv-main__img">
                                        
                                        <?php if (!empty($link)): ?>
                                            <!-- Оборачиваем изображение в ссылку с title -->
                                            <a href="<?php echo esc_url($link); ?>" title="<?php echo esc_attr($link_title); ?>">
                                        <?php endif; ?>

                                        <!-- ----------------------------------------------
                                             Начало правки: вывод изображения с атрибутами alt и title
                                             ---------------------------------------------- -->
                                        <?php if ($image): ?>
                                            <img src="<?php echo esc_url($image['url']); ?>" alt="<?php echo esc_attr($image['alt']); ?>" title="<?php echo esc_attr($image['title']); ?>" loading="lazy" decoding="async">
                                        <?php endif; ?>
                                        <!-- ----------------------------------------------
                                             Конец правки
                                             ---------------------------------------------- -->

                                        <?php if (!empty($link)): ?>
                                            </a>
                                        <?php endif; ?>
                                    </div>
                                    <p class="item-serv-main__text">
                                        <?php echo $main_services_item['tekst']; ?>
                                    </p>
                                </div>
                            </div>
                    <?php
                        }
                    }
                    ?>
                </div>
            </div>
            <button type="button" class="services__btn-slider services__btn-next">
                <img src="<?php echo get_stylesheet_directory_uri(); ?>/assets/img/icons/arrow-grey.svg" alt="Next" title="Следующий">
            </button>
        </div>
    </div>
</section>
	<p style="text-align: center; margin-top: 20px;">
    <a href="/supplies-services-china/" title="Все услуги по работе с Китаем" style="text-decoration: underline; font-weight: 500;">Все услуги по Китаю →</a>
</p>


<!-- ------------------------------------------------------ End Services ------------------------------------------------------ -->

	

    <!-- ------------------------------------------------------ Price ----------------------------------------------------------------------- -->
    <?php $main_prices = get_field('stoimost'); ?>
    <section class="main-page__price price-main">
        <div class="price-main__container">
            <div class="price-main__block">
                <h2 class="price-main__title _title">
                    <?php echo $main_prices['zagolovok']; ?>
                </h2>
                <div class="price-main__rows">
                    <?php $main_prices_items = $main_prices['row']; ?>
                    <?php
                    if ($main_prices_items) {
                        foreach ($main_prices_items as $main_prices_item) {
                    ?>

                            <div class="price-main__row">
                                <div class="price-main__left">
                                    <?php echo $main_prices_item['tekst_sleva']; ?>
                                </div>
                                <div class="price-main__right">
                                    <?php echo $main_prices_item['tekst_sprava']; ?>
                                </div>
                            </div>

                    <?php
                        }
                    }
                    ?>

                </div>
                <button class="price-main__btn _btn" data-goto=".consult">
                    Оставить заявку
                </button>
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Price ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Why ----------------------------------------------------------------------- -->
    <?php $main_benefit = get_field('vygoda'); ?>
    <section class="main-page__why why-main">
        <div class="why-main__container">
            <h2 class="why-main__title _title">
                <?php echo $main_benefit['zagolovok']; ?>
            </h2>
            <div class="why-main__ul">

                <?php $main_benefit_items = $main_benefit['punkty']; ?>
                <?php
                if ($main_benefit_items) {
                    foreach ($main_benefit_items as $main_benefit_item) {
                ?>

                        <div class="why-main__li">
                            <?php echo $main_benefit_item['punkt']; ?>
                        </div>

                <?php
                    }
                }
                ?>

            </div>
            <div class="why-main__description">
                <div class="why-main__left">
                    <b>
                        за
                    </b>
                    <span>
                        <?php echo $main_benefit['kolichestvo']; ?>
                    </span>
                </div>
                <p class="why-main__text">
                    <?php echo $main_benefit['tekst']; ?>
                </p>
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Why ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ Trust -------------------------------------------------------- -->
  <?php $partners = get_field('partnery'); ?>
<?php if (!empty($partners)) : ?>
<section class="main-page__trust trust-main">
    <div class="trust-main__container">

        <?php if (!empty($partners['zagolovok'])) : ?>
            <h2 class="trust-main__title _title">
                <?php echo esc_html($partners['zagolovok']); ?>
            </h2>
        <?php endif; ?>

        <div class="trust-main__body">
            <button type="button" class="trust-main__btn-slider trust-main__btn-prev">
                <img src="<?php echo esc_url(get_stylesheet_directory_uri()); ?>/assets/img/icons/arrow-grey.svg" alt="Previous" title="Назад">
            </button>
            <div class="trust-main__slider swiper">
                <div class="trust-main__wrapper swiper-wrapper">

                    <?php $logos = $partners['logos']; ?>
                    <?php if (!empty($logos)) : ?>
                        <?php foreach ($logos as $logo) : ?>
                            <?php 
                                // Извлечение данных логотипа
                                $logo_url = is_array($logo['logo']) ? $logo['logo']['url'] : $logo['logo'];
                                $logo_alt = $logo['logo']['alt'] ?? 'Логотип партнера';
                                $logo_title = $logo['logo']['title'] ?? '';

                                // Проверка на наличие URL
                                if (!empty($logo_url)) :
                            ?>
                                <div class="trust-main__slide swiper-slide">
                                    <img src="<?php echo esc_url($logo_url); ?>" 
                                         alt="<?php echo esc_attr($logo_alt); ?>" 
                                         title="<?php echo esc_attr($logo_title); ?>" 
                                         loading="lazy"
                                         decoding="async"
                                         width="150" 
                                         height="150">
                                </div>
                            <?php endif; ?>
                        <?php endforeach; ?>
                    <?php else : ?>
                        <p>Логотипы отсутствуют.</p>
                    <?php endif; ?>

                </div>
            </div>
            <button type="button" class="trust-main__btn-slider trust-main__btn-next">
                <img src="<?php echo esc_url(get_stylesheet_directory_uri()); ?>/assets/img/icons/arrow-grey.svg" alt="Next" title="Следующий">
            </button>
        </div>
    </div>
</section>
<?php endif; ?>

    <!-- ------------------------------------------------------ End Trust----------------------------------------------------------------- -->
	
	
	 <!-- ------------------------------------------------------ Projects------------------------------------------------------- -->
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
<!-- ------------------------------------------------------ End Projects------------------------------------------------------ -->
	
<!-- ------------------------------------------------------ Thanks ------------------------------------------------------------ -->
<?php $blago = get_field('blago'); ?>
<div class="about-us__body">
    <div class="about-us__container">
        <div class="about-us__thanks thanks-about">
            <h2 class="thanks-about__title _title">
                <?php echo esc_html($blago['zagolovok']); ?>
            </h2>
            <div class="thanks-about__slider swiper">
                <div class="thanks-about__wrapper swiper-wrapper" data-gallery>

                    <?php $blago_items = $blago['pisma']; ?>
                    <?php
                    if ($blago_items && is_array($blago_items)) {
                        foreach ($blago_items as $blago_item) {
                            // Извлекаем данные из массива
                            $image_url = isset($blago_item['pismo']['url']) ? $blago_item['pismo']['url'] : ''; // URL изображения
                            $alt_text = isset($blago_item['alt']) ? $blago_item['alt'] : ''; // Альтернативный текст
                            $title_text = isset($blago_item['title']) ? $blago_item['title'] : ''; // Тайтл изображения

                            if ($image_url): ?>
                                <a href="<?php echo esc_url($image_url); ?>" class="thanks-about__slide swiper-slide">
                                    <img 
                                        src="<?php echo esc_url($image_url); ?>" 
                                        alt="<?php echo esc_attr($alt_text); ?>" 
                                        title="<?php echo esc_attr($title_text); ?>"
                                        loading="lazy"
                                        decoding="async">
                                </a>
                            <?php else: ?>
                                <p>Изображение отсутствует</p>
                            <?php endif;
                        }
                    } else {
                        echo '<p>Отзывы отсутствуют.</p>';
                    }
                    ?>

                </div>
                <div class="thanks-about__controls">
                    <div class="thanks-about__pagination slider-pagination"></div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- ------------------------------------------------------ End Thanks ------------------------------------------------------- -->	
	
    <!-- ------------------------------------------------------ Offices ---------------------------------------------------------------- -->
   <?php $main_offices = get_field('ofisy'); ?>
<section class="main-page__offices offices-main">
    <div class="offices-main__container">
        <h2 class="offices-main__title _title">
            <?php echo $main_offices['zagolovok']; ?>
        </h2>
        <div class="offices-main__items">

            <?php $offices = $main_offices['ofis']; ?>
            <?php
            if ($offices) {
                foreach ($offices as $office) {
                    // ----------------------------------------------
                    // Начало правки: проверка, что izobrazhenie возвращает массив
                    // ----------------------------------------------
                    if (is_array($office['izobrazhenie'])) {
                        $image_url = $office['izobrazhenie']['url'];
                        $image_alt = $office['izobrazhenie']['alt'] ?? 'Изображение офиса'; // Если alt не задан, используем текст по умолчанию
                        $image_title = $office['izobrazhenie']['title'] ?? '';
                    } else {
                        $image_url = $office['izobrazhenie'];
                        $image_alt = 'Изображение офиса';
                        $image_title = '';
                    }
                    // ----------------------------------------------
                    // Конец правки
                    // ----------------------------------------------
            ?>

                    <div class="offices-main__item item-office-main">
                        <div class="item-office-main__img">
                            <img src="<?php echo esc_url($image_url); ?>" alt="<?php echo esc_attr($image_alt); ?>" title="<?php echo esc_attr($image_title); ?>" loading="lazy" decoding="async">
                        </div>
                        <div class="item-office-main__name">
                            <?php echo $office['gorod']; ?>
                        </div>
                        <div class="item-office-main__contacts">
                            <p class="item-office-main__address">
                                <?php echo $office['adres']; ?>
                            </p>
                            <a href="mailto:<?php echo esc_attr($office['pochta']); ?>" class="item-office-main__mail">
                                <?php echo $office['pochta']; ?>
                            </a>
                            <a href="tel:<?php echo esc_attr($office['telefon_bez_probelov_i_znakov']); ?>" class="item-office-main__tel">
                                <?php echo $office['telefon']; ?>
                            </a>
                        </div>
                    </div>

            <?php
                }
            }
            ?>

        </div>
    </div>
</section>

    <!-- ------------------------------------------------------ End Offices ----------------------------------------------------------------------- -->
    <!-- ------------------------------------------------------ FAQ ----------------------------------------------------------------------- -->
    <?php $faq = get_field('voprosy'); ?>
    <section class="faq">
        <div class="faq__container">
            <div class="faq__body">
                <h2 class="faq__title">
                    <?php echo $faq['zagolovok']; ?>
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
