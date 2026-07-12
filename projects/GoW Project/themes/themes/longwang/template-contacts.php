<?php /* Template Name: Template Contacts */
get_header();
?>
<main class="page contacts-page">
    <section class="contacts-page__hero hero-main hero-main--narrow">
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
                        контакты
                    </h1>
                </div>
            </div>
        </div>
    </section>
    <!-- ------------------------------------------------------ Offices ----------------------------------------------------------------------- -->

    <div class="contacts-page__container">
        <?php $ofisy = get_field('ofisy'); ?>
        <div class="contacts-page__items">

            <?php
            if ($ofisy && is_array($ofisy)) {
                foreach ($ofisy as $index => $ofis) {
                    $coordinates = explode(',', $ofis['koordinaty']); // Разделение координат
                    $latitude = isset($coordinates[0]) ? trim($coordinates[0]) : '0';
                    $longitude = isset($coordinates[1]) ? trim($coordinates[1]) : '0';
            ?>

                    <div class="contacts-page__item item-contacts">
                        <div class="item-contacts__title">
                            <?php echo esc_html($ofis['zagolovok']); ?>
                        </div>
                        <div class="item-contacts__contacts">
                            <div class="item-contacts__contact">
                                <span><?php echo esc_html($ofis['adres']); ?></span>
                            </div>
                            <a href="mailto:<?php echo esc_attr($ofis['pochta']); ?>" class="item-contacts__contact">
                                <span><?php echo esc_html($ofis['pochta']); ?></span>
                            </a>
                            <a href="tel:<?php echo esc_attr($ofis['telefon_bez']); ?>" class="item-contacts__contact">
                                <span><?php echo esc_html($ofis['telefon_dlya']); ?></span>
                            </a>
                        </div>
                        <div class="item-contacts__map" id="map-<?php echo $index; ?>" style="width:100%; height:400px;" data-lat="<?php echo esc_attr($latitude); ?>" data-lng="<?php echo esc_attr($longitude); ?>"></div>
                    </div>

            <?php
                }
            } else {
                echo '<p>Офисы не найдены.</p>';
            }
            ?>

        </div>
    </div>
    <!-- ------------------------------------------------------ End Offices ----------------------------------------------------------------------- -->

    <!-- Подключение карт Google Maps -->
    <script src="https://maps.googleapis.com/maps/api/js?key=ВАШ_API_КЛЮЧ"></script>
    <script type="text/javascript">
        document.addEventListener("DOMContentLoaded", function () {
            const maps = document.querySelectorAll('.item-contacts__map');
            
            maps.forEach((mapElement) => {
                const lat = parseFloat(mapElement.getAttribute('data-lat'));
                const lng = parseFloat(mapElement.getAttribute('data-lng'));

                if (!isNaN(lat) && !isNaN(lng)) {
                    const map = new google.maps.Map(mapElement, {
                        center: { lat: lat, lng: lng },
                        zoom: 12,
                    });

                    new google.maps.Marker({
                        position: { lat: lat, lng: lng },
                        map: map,
                        title: mapElement.previousElementSibling?.querySelector('.item-contacts__title')?.textContent || 'Офис',
                    });
                } else {
                    console.error('Некорректные координаты:', lat, lng);
                }
            });
        });
    </script>

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
?>

