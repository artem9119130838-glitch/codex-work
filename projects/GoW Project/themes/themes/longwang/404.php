<?php

/**
 * The template for displaying 404 pages (not found)
 *
 * @link https://codex.wordpress.org/Creating_an_Error_404_Page
 *
 * @package longwang
 */

get_header();
?>

<main class="page no-page">
	<div class="no-page__container">
		<div class="no-page__body">
			<h1 class="no-page__title">
				404
			</h1>
			<div class="no-page__text">
				Возможно вы ошиблись, такой страницы не существует
			</div>
			<a href="<?php echo get_home_url(); ?>/" class="no-page__btn _btn">
				Перейти на главную
			</a>
		</div>
	</div>
</main>

<?php
get_footer();
