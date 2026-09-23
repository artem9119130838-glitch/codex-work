<?php

/**
 * The main template file
 *
 * This is the most generic template file in a WordPress theme
 * and one of the two required files for a theme (the other being style.css).
 * It is used to display a page when nothing more specific matches a query.
 * E.g., it puts together the home page when no home.php file exists.
 *
 * @link https://developer.wordpress.org/themes/basics/template-hierarchy/
 *
 * @package longwang
 */

get_header();
?>

<main class="page news-page">

    <?php 
    // ------------------------------------------------------
    // Начало определения функции для получения ID изображения по URL
    // ------------------------------------------------------
    function get_image_id_by_url($image_url) {
        global $wpdb;
        $attachment_id = $wpdb->get_var($wpdb->prepare(
            "SELECT ID FROM {$wpdb->posts} WHERE guid = %s AND post_type = 'attachment'",
            $image_url
        ));
        return $attachment_id;
    }

    // Функция для получения alt-текста изображения по URL
    function get_image_alt_by_url($image_url) {
        $image_id = get_image_id_by_url($image_url);
        return $image_id ? get_post_meta($image_id, '_wp_attachment_image_alt', true) : '';
    }
    // ------------------------------------------------------
    // Конец определения функции для получения ID и alt изображения по URL
    // ------------------------------------------------------
    ?>

	<section class="news-arch-page__hero hero-main hero-main--narrow">
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
				 
					
				
   <!--h1 start--->
					
				<h1 class="hero-main__title">
    <?php
    // Статичный заголовок
    $title = 'новости из китая';

    // Получаем текущий номер страницы (если это пагинация)
    $paged = get_query_var('paged') ? get_query_var('paged') : 1;

    // Добавляем номер страницы, если это не первая страница
    if ($paged > 1) {
        echo $title . ' - Страница ' . $paged;
    } else {
        echo $title;
    }
    ?>
</h1>

	<!--h1end--->			
					
					
					
				
					
					
					
					
				</div>
			</div>
		</div>
	</section>

	<div class="news-page__body">
		<div class="news-page__container">
			<div class="news-page__left">
				<div class="news-page__items">

					<?php if (have_posts()) : ?>

					<?php
						/* Start the Loop */
						while (have_posts()) :
							the_post();
							get_template_part('template-parts/content', get_post_type());
						endwhile;
						
						$args = array(
							'show_all'     => false,
							'prev_next'    => true,
							'prev_text'    => '<svg xmlns="http://www.w3.org/2000/svg" width="6" height="10" viewBox="0 0 6 10" fill="none">
								<path d="M5.00446 0.500044C4.87639 0.499718 4.74984 0.520913 4.63412 0.562069C4.51841 0.603227 4.41646 0.663302 4.33577 0.737879L0.195025 4.59466C0.0689325 4.70968 4.06171e-07 4.85395 3.93155e-07 5.00283C3.80139e-07 5.15172 0.0689324 5.29599 0.195025 5.41101L4.48151 9.26779C4.62703 9.39906 4.83613 9.48161 5.06282 9.49728C5.28952 9.51295 5.51523 9.46046 5.6903 9.35135C5.86537 9.24225 5.97547 9.08546 5.99637 8.91549C6.01727 8.74552 5.94726 8.57628 5.80175 8.44501L1.96963 4.99962L5.67315 1.55423C5.77799 1.45988 5.84458 1.34498 5.86505 1.22314C5.88552 1.1013 5.85902 0.977612 5.78867 0.866711C5.71833 0.755811 5.60708 0.662342 5.46811 0.597361C5.32913 0.532381 5.16824 0.49861 5.00446 0.500044Z" fill="#293B6E" />
							</svg>',
							'next_text'    => '<svg xmlns="http://www.w3.org/2000/svg" width="6" height="10" viewBox="0 0 6 10" fill="none">
								<path d="M0.995538 9.49996C1.12361 9.50028 1.25016 9.47909 1.36588 9.43793C1.48159 9.39677 1.58354 9.3367 1.66423 9.26212L5.80498 5.40534C5.93107 5.29032 6 5.14605 6 4.99717C6 4.84828 5.93107 4.70401 5.80498 4.58899L1.51849 0.732212C1.37297 0.600942 1.16387 0.518391 0.937177 0.50272C0.710485 0.487049 0.484775 0.539541 0.3097 0.648648C0.134626 0.757755 0.0245285 0.914541 0.00362778 1.08451C-0.0172729 1.25449 0.0527353 1.42372 0.198252 1.55499L4.03037 5.00038L0.326847 8.44577C0.222013 8.54012 0.155421 8.65502 0.13495 8.77686C0.114478 8.8987 0.140983 9.02239 0.211329 9.13329C0.281675 9.24419 0.392918 9.33766 0.531895 9.40264C0.670871 9.46762 0.831765 9.50139 0.995538 9.49996Z" fill="#293B6E" />
							</svg>',
							'add_args'     => false,
							'add_fragment' => '',
							'screen_reader_text' => __('Posts navigation'),
							'class'        => 'news-page__pagination',
						);
						the_posts_pagination($args);

					else :
						get_template_part('template-parts/content', 'none');
					endif;
					?>

				</div>
			</div>
			<div class="news-page__categories categories-news">
				<?php
				$args = array(
					'show_option_all'    => '',
					'show_option_none'   => __('No categories'),
					'orderby'            => 'name',
					'order'              => 'ASC',
					'style'              => 'list',
					'show_count'         => 1,
					'hide_empty'         => 1,
					'use_desc_for_title' => 0,
					'child_of'           => 0,
					'feed'               => '',
					'feed_type'          => '',
					'feed_image'         => '',
					'exclude'            => '',
					'exclude_tree'       => '',
					'include'            => '',
					'hierarchical'       => true,
					'title_li'           => '<div class="categories-news__title">Рубрики</div>',
					'number'             => NULL,
					'echo'               => 1,
					'depth'              => 0,
					'current_category'   => 0,
					'pad_counts'         => 0,
					'taxonomy'           => 'category',
					'walker'             => 'Walker_Category',
					'hide_title_if_empty' => false,
					'separator'          => '<br />',
				);

				echo '<ul>';
				wp_list_categories($args);
				echo '</ul>'; ?>
			</div>
		</div>
	</div>

	<!-- ------------------------------------------------------ Trust ----------------------------------------------------------------------- -->
	<?php $partners = get_field('partnery', 7); ?>
<section class="main-page__trust trust-main">
    <div class="trust-main__container">
        <h2 class="trust-main__title _title">
            <?php echo $partners['zagolovok']; ?>
        </h2>

        <div class="trust-main__body">
            <button type="button" class="trust-main__btn-slider trust-main__btn-prev">
                <img src="<?php echo get_stylesheet_directory_uri(); ?>/assets/img/icons/arrow-grey.svg" alt="">
            </button>
            <div class="trust-main__slider swiper">
                <div class="trust-main__wrapper swiper-wrapper">

                    <?php $logos = $partners['logos']; ?>
                    <?php
                    if ($logos) {
                        foreach ($logos as $logo) {
                            // Проверяем, что URL изображения корректно извлечен
                            $image_url = is_array($logo['logo']) ? $logo['logo']['url'] : '';
                            $image_alt = get_image_alt_by_url($image_url); // Получаем alt из медиатеки

                            // Выводим URL для отладки
                            echo '<!-- Отладка URL изображения: ' . esc_url($image_url) . ' -->';

                            if ($image_url): ?>
                                <div class="trust-main__slide swiper-slide">
                                    <img src="<?php echo esc_url($image_url); ?>" alt="<?php echo esc_attr($image_alt); ?>">
                                </div>
                            <?php endif; ?>
                        <?php
                        }
                    } else {
                        echo '<!-- Отладка: Логотипы не найдены -->';
                    }
                    ?>

                </div>
            </div>
            <button type="button" class="trust-main__btn-slider trust-main__btn-next">
                <img src="<?php echo get_stylesheet_directory_uri(); ?>/assets/img/icons/arrow-grey.svg" alt="">
            </button>
        </div>
    </div>
</section>

	<!-- ------------------------------------------------------ End Trust ----------------------------------------------------------------------- -->

	<!-- ------------------------------------------------------ Offices2 ----------------------------------------------------------------------- -->
	<?php $main_offices = get_field('ofisy', 7); ?>
<section class="main-page__offices offices-main">
    <div class="offices-main__container">
        <h2 class="offices-main__title _title">
            <?php echo esc_html($main_offices['zagolovok']); ?>
        </h2>
        <div class="offices-main__items">

            <?php $offices = $main_offices['ofis']; ?>
            <?php
            if ($offices) {
                foreach ($offices as $office) {
                    // Проверяем, является ли 'izobrazhenie' массивом, и получаем URL корректно
                    $image_url = is_array($office['izobrazhenie']) ? $office['izobrazhenie']['url'] : $office['izobrazhenie'];
                    $image_alt = $image_url ? get_image_alt_by_url($image_url) : '';

                    // Отладка: вывод URL изображения
                    echo '<!-- Отладка URL изображения: ' . esc_url($image_url) . ' -->';
            ?>

                    <div class="offices-main__item item-office-main">
                        <div class="item-office-main__img">
                            <img src="<?php echo esc_url($image_url); ?>" alt="<?php echo esc_attr($image_alt); ?>">
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
                            <a href="tel:+7<?php echo esc_attr($office['telefon_bez_probelov_i_znakov']); ?>" class="item-office-main__tel">
                                <?php echo esc_html($office['telefon']); ?>
                            </a>
                        </div>
                    </div>

            <?php
                }
            } else {
                echo '<!-- Отладка: Офисы не найдены -->';
            }
            ?>

        </div>
    </div>
</section>

	<!-- ------------------------------------------------------ End Offices ----------------------------------------------------------------------- -->

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

</main><!-- #main -->

<?php
get_footer();
