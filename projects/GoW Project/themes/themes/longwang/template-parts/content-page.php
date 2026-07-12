<?php

/**
 * Template part for displaying page content in page.php
 *
 * @link https://developer.wordpress.org/themes/basics/template-hierarchy/
 *
 * @package longwang
 */

?>

<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
	<section class="documents-page__hero hero-main hero-main--narrow">
		<div class="hero-main__container">
			<div class="hero-main__top">
				<div class="hero-main__offer">
					<h1 class="hero-main__title">
						<?php the_title(); ?>
					</h1>
				</div>
			</div>
		</div>
	</section>

	<div class="page-content">
		<div class="page-content__container">
			<br>
			<br>
			<?php longwang_post_thumbnail(); ?>

			<div class="entry-content">
				<?php
				the_content();

				wp_link_pages(
					array(
						'before' => '<div class="page-links">' . esc_html__('Pages:', 'longwang'),
						'after'  => '</div>',
					)
				);
				?>
			</div><!-- .entry-content -->
			<br>
			<br>
		</div>
	</div>
</article><!-- #post-<?php the_ID(); ?> -->