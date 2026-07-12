<?php /* Template Name: Template Market */
get_header();
?>

<main class="page market-page">
    <!-- ------------------------------------------------------ Hero ----------------------------------------------------------------------- -->
    <?php
    $main_section = get_field('market-hero-section');
    ?>
    <section class="market-page__hero hero-main">
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
                        <?php echo $main_section['title']; ?>
                    </h1>
                    <div class="hero-main__subtitle">
                        <?php echo $main_section['subtitle']; ?>
                    </div>
                    <button class="hero-main__btn _btn" data-goto=".consult">
                        Оставить заявку
                    </button>
                </div>
                <div class="hero-main__hexagons">
                    <div class="hero-main__hexagon-img">
                        <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                            <pattern id="img" patternContentUnits="objectBoundingBox" width="100%" height="100%">
                                <image height="1" width="1" preserveAspectRatio="xMidYMid slice" xlink:href="<?php echo $main_section['img']; ?>" />
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
    <!-- ------------------------------------------------------ End Hero ----------------------------------------------------------------------- -->
<!-- ------------------------------------------------------ Advantages -------------------------------------------------- -->
<?php
$advantages_section = get_field('market-hero-advantages');
?>

<div class="market-page__advantages advantages-market">
    <div class="advantages-market__container">
        
        <?php 
        // Заголовок секции из первого элемента
        $section_title = !empty($advantages_section[0]['zagolovok']) ? $advantages_section[0]['zagolovok'] : '';
        if (!empty($section_title)): 
        ?>
            <h2 class="advantages-market__title _title">
                <?php echo esc_html($section_title); ?>
            </h2>
        <?php endif; ?>

        <div class="advantages-market__items">
            <?php
            if (!empty($advantages_section) && is_array($advantages_section)) {
                foreach ($advantages_section as $advantages_item) {
                    // Проверяем, что есть данные в группе 'item'
                    if (empty($advantages_item['item']) || !is_array($advantages_item['item'])) {
                        continue;
                    }
                    
                    $item_data = $advantages_item['item'];
                    
                    // Получаем URL изображения
                    $img_url = $item_data['img'] ?? '';
                    
                    // !!! ВАЖНО: Убираем HTML теги из текста !!!
                    // Используем strip_tags, чтобы удалить <p>, <br> и другие теги
                    $title = !empty($item_data['title']) ? strip_tags($item_data['title']) : '';
                    $subtitle = !empty($item_data['subtitle']) ? strip_tags($item_data['subtitle']) : '';
                    
                    // Alt и title для изображения (если есть)
                    $img_alt = !empty($item_data['img_alt']) ? $item_data['img_alt'] : $title; // Если alt нет, используем заголовок
                    $img_title = !empty($item_data['img_title']) ? $item_data['img_title'] : '';
            ?>
                    <div class="advantages-market__item item-market-adv">
                        <?php if (!empty($img_url)): ?>
                        <div class="item-market-adv__img">
                            <img src="<?php echo esc_url($img_url); ?>"
                                 alt="<?php echo esc_attr($img_alt); ?>" 
                                 title="<?php echo esc_attr($img_title); ?>"
                                 loading="lazy"
                                 decoding="async">
                        </div>
                        <?php endif; ?>
                        
                        <?php if (!empty($title)): ?>
                        <div class="item-market-adv__title">
                            <?php echo esc_html($title); ?>
                        </div>
                        <?php endif; ?>
                        
                        <?php if (!empty($subtitle)): ?>
                        <div class="item-market-adv__text">
                            <?php echo esc_html($subtitle); ?>
                        </div>
                        <?php endif; ?>
                    </div>
            <?php
                }
            }
            ?>
        </div>
    </div>
</div>
<!-- ------------------------------------------------------ End Advantages -------------------------------------------------- -->

    <!-- ------------------------------------------------------ Stages ----------------------------------------------------------------------- -->
    <?php
    $stages_section = get_field('market-hero-stages');
    ?>
    <section class="market-page__stages stages-market">
        <div class="stages-market__container">
            <h2 class="stages-market__title _title">
                <?php echo $stages_section['title']; ?>
            </h2>
            <?php $stages_section_stages = $stages_section['stages']; ?>
            <div class="stages-market__rows">
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo $stages_section_stages['stage_1']['title']; ?>
                    </div>
                    <div class="stages-market__right">
                        <?php echo $stages_section_stages['stage_1']['description']; ?>
                    </div>
                </div>
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo $stages_section_stages['stage_2']['title']; ?>
                    </div>
                    <div class="stages-market__right">
                        <?php echo $stages_section_stages['stage_2']['description']; ?>
                    </div>
                </div>
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo $stages_section_stages['stage_3']['title']; ?>
                    </div>
                    <div class="stages-market__right">
                        <?php $stages_section_cards = $stages_section_stages['stage_3']['kartochki']['kartochka']; ?>
                        <div class="stages-market__packs">

                            <?php
                            if ($stages_section_cards) {
                                foreach ($stages_section_cards as $stages_section_card) {
                            ?>

                                    <div class="stages-market__pack pack-stages-market">
                                        <div class="pack-stages-market__top">
                                            <div class="pack-stages-market__title">
                                                <?php echo $stages_section_card['title']; ?>
                                            </div>
                                            <div class="pack-stages-market__img">
                                                <img src="<?php echo $stages_section_card['izobrazhenie']; ?>"
									alt="<?php echo $stages_section_card['img_alt'] ?>" 
                                    title="<?php echo $stages_section_card['img_title'] ?>"
                                    loading="lazy"
                                    decoding="async">
                                            </div>
                                        </div>
                                        <div class="pack-stages-market__bottom">
                                            от <?php echo $stages_section_card["price"]; ?> <span>₽</span>
                                        </div>
                                    </div>

                            <?php
                                }
                            }
                            ?>

                        </div>
                    </div>
                </div>
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo $stages_section_stages['stage_4']['title']; ?>
                    </div>
                    <div class="stages-market__right">
                        <div class="stages-market__delivery delivery-market">
                            <div class="delivery-market__items">
                                <?php $stages_section4_cards = $stages_section_stages['stage_4']['kartochki']['kartochka']; ?>

                                <?php
                                if ($stages_section4_cards) {
                                    foreach ($stages_section4_cards as $stages_section_card) {
                                ?>
                                        <div class="delivery-market__item">
                                            <div class="delivery-market__top">
                                                <div class="delivery-market__title">
                                                    <?php echo $stages_section_card['title']; ?>
                                                </div>
                                                <div class="delivery-market__img">
                                                    <img src="<?php echo $stages_section_card['img']; ?>"
									alt="<?php echo $stages_section_card['img_alt'] ?>" 
                                    title="<?php echo $stages_section_card['img_title'] ?>"
                                    loading="lazy"
                                    decoding="async">
                                                </div>
                                            </div>
                                            <div class="delivery-market__bottom">
                                                <p class="delivery-market__price">
                                                    от <?php echo $stages_section_card['price']; ?> <span>₽/кг</span>
                                                </p>
                                                <p class="delivery-market__time">
                                                    <?php echo $stages_section_card['srok']; ?>
                                                </p>
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
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo $stages_section_stages['stage_5']['title']; ?>
                    </div>
                    <div class="stages-market__right">
                        <?php echo $stages_section_stages['stage_5']['description']; ?>
                    </div>
                </div>
                <div class="stages-market__row">
                    <div class="stages-market__left">
                        <?php echo $stages_section_stages['stage_6']['title']; ?>
                    </div>
                    <div class="stages-market__right">
                        <?php echo $stages_section_stages['stage_6']['description']; ?>
                    </div>
                </div>
            </div>
            <div class="stages-market__bottom bottom-market-stages">
                <div class="bottom-market-stages__img">
                    <img src="<?php echo $stages_section['nizhnij_blok_sekczii']['img']; ?>" alt="Асболюная безопасность сделки" title="Грузы полностью страхуются от всех рисков" loading="lazy" decoding="async">
                </div>
                <div class="bottom-market-stages__text">
                    <div class="bottom-market-stages__title">
                        <?php echo $stages_section['nizhnij_blok_sekczii']['title']; ?>
                    </div>
                    <div class="bottom-market-stages__subtitle">
                        <?php echo $stages_section['nizhnij_blok_sekczii']['subtitle']; ?>
                    </div>
                </div>
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End Stages ----------------------------------------------------------------------- -->
	    <!-- ------------------------------------------------------ FAQ1 ----------------------------------------------------------------------- -->
    <?php $faq = get_field('faq'); ?>
    <?php if (isset($faq['spojlery'][0]['vopros'])) { ?>
        <section class="faq">
            <div class="faq__container">
                <div class="faq__body">
                    <h2 class="faq__title">
                        Что вас волнует, и как мы это решаем
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
    <!-- ------------------------------------------------------ End FAQ1 ----------------------------------------------------------------------- -->

    <!-- ------------------------------------------------------ FullPrice ----------------------------------------------------------------------- -->
    <?php
    $fullprice_section = get_field('market-section-fullprice');
    ?>
    <section class="market-page__price price-market">
        <div class="price-market__container">
            <div class="price-market__block">
                <h2 class="price-market__title">
                    <?php echo $fullprice_section['title']; ?>
                </h2>
                <div class="price-market__items">
                    <div class="price-market__item item-price-market">
                        <div class="item-price-market__bg">
                            <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                                <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z">
                                </path>
                            </svg>
                        </div>
                        <div class="item-price-market__text">
                            <?php echo $fullprice_section['blok_1']; ?>
                        </div>
                    </div>
                    <div class="price-market__plus">
                        <svg id="Layer_4" data-name="Layer 4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 55.88 55.88">
                            <line x1="27.94" y1="1.5" x2="27.94" y2="54.38" style="fill:none;stroke:#1d2951;stroke-linecap:round;stroke-linejoin:round;stroke-width:3px" />
                            <line x1="1.5" y1="27.94" x2="54.38" y2="27.94" style="fill:none;stroke:#1d2951;stroke-linecap:round;stroke-linejoin:round;stroke-width:3px" />
                        </svg>
                    </div>
                    <div class="price-market__item item-price-market">
                        <div class="item-price-market__bg">
                            <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                                <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z">
                                </path>
                            </svg>
                        </div>
                        <div class="item-price-market__text">
                            <?php echo $fullprice_section['blok_2']; ?>
                        </div>
                    </div>
                    <div class="price-market__plus">
                        <svg id="Layer_4" data-name="Layer 4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 55.88 55.88">
                            <line x1="27.94" y1="1.5" x2="27.94" y2="54.38" style="fill:none;stroke:#1d2951;stroke-linecap:round;stroke-linejoin:round;stroke-width:3px" />
                            <line x1="1.5" y1="27.94" x2="54.38" y2="27.94" style="fill:none;stroke:#1d2951;stroke-linecap:round;stroke-linejoin:round;stroke-width:3px" />
                        </svg>
                    </div>
                    <div class="price-market__item item-price-market">
                        <div class="item-price-market__bg">
                            <svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
                                <path d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z">
                                </path>
                            </svg>
                        </div>
                        <div class="item-price-market__text">
                            <?php echo $fullprice_section['blok_3']; ?>
                        </div>
                    </div>
                </div>
                <button class="hero-main__btn _btn" data-goto=".consult">
                        Оставить заявку
                    </button>
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ End FullPrice ----------------------------------------------------------------------- -->
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
