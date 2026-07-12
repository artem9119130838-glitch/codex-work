<?php

/**
 * The template for displaying all single posts
 *
 * @link https://developer.wordpress.org/themes/basics/template-hierarchy/#single-post
 *
 * @package longwang
 */

get_header();
?>

<main id="primary" class="site-main">
	<section class="news-page__hero hero-main hero-main--narrow">
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
						<?php the_title(); ?>
					</h1>
				</div>
			</div>
		</div>
	</section>
	<div class="site-main__container page-content news-content">
		<div class="news-content__container">

			<?php
			while (have_posts()) :
				the_post();

				the_content();

				the_post_navigation(
					array(
						'prev_text' => '<svg xmlns="http://www.w3.org/2000/svg" width="21" height="16" viewBox="0 0 21 16" fill="none">
						<path d="M0.292892 7.2929C-0.0976315 7.68342 -0.0976314 8.31658 0.292893 8.70711L6.65686 15.0711C7.04738 15.4616 7.68054 15.4616 8.07107 15.0711C8.46159 14.6805 8.46159 14.0474 8.07107 13.6569L2.41421 8L8.07107 2.34315C8.46159 1.95262 8.46159 1.31946 8.07107 0.928933C7.68054 0.538409 7.04738 0.538409 6.65685 0.928933L0.292892 7.2929ZM21 7L1 7L1 9L21 9L21 7Z" fill="#293B6E"/>
					  </svg>&nbsp; <p>Предыдущая запись</p>',
						'next_text' => '<p>Следующая запись</p> &nbsp;<svg xmlns="http://www.w3.org/2000/svg" width="21" height="16" viewBox="0 0 21 16" fill="none">
						<path d="M20.7071 8.70711C21.0976 8.31658 21.0976 7.68342 20.7071 7.29289L14.3431 0.928932C13.9526 0.538408 13.3195 0.538408 12.9289 0.928932C12.5384 1.31946 12.5384 1.95262 12.9289 2.34315L18.5858 8L12.9289 13.6569C12.5384 14.0474 12.5384 14.6805 12.9289 15.0711C13.3195 15.4616 13.9526 15.4616 14.3431 15.0711L20.7071 8.70711ZM0 9H20V7H0V9Z" fill="#293B6E"/>
					  </svg>',
					)
				);

			// If comments are open or we have at least one comment, load up the comment template.
			// if (comments_open() || get_comments_number()) :
			// 	comments_template();
			// endif;

			endwhile; // End of the loop.
			?>
		</div>
	</div>
</main><!-- #main -->

<?php
get_footer();
