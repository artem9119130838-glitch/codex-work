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

<main id="primary" class="page project-page">
	<div class="breadcrumbs">
		<div class="breadcrumbs__container">
			<?php
			if (function_exists('yoast_breadcrumb')) {
				yoast_breadcrumb('<p id="breadcrumbs">', '</p>');
			}
			?>
		</div>
	</div>
	<div class="projects-page__container">
		<div class="project-page__body">
			<div class="project-page__content page-content">
				<h1 class="projects-page__title _title">
					<?php the_title(); ?>
				</h1>

				<div class="project-page__text">
					<?php
					the_content();
					?>
				</div>

			</div>
			<div class="project-page__img">
				<div class="hero-main__hexagons">
					<div class="hero-main__hexagon-img">
						<svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
							<pattern id="img" patternContentUnits="objectBoundingBox" width="100%" height="100%">
								<image height="1" width="1" preserveAspectRatio="xMidYMid slice" xlink:href="<?php the_post_thumbnail_url(); ?>" />
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
		<a href="<?php echo get_post_type_archive_link('projects'); ?>" class="project-page__back">
			<svg xmlns="http://www.w3.org/2000/svg" width="21" height="16" viewBox="0 0 21 16" fill="none">
				<path d="M0.292892 7.29289C-0.0976315 7.68342 -0.0976315 8.31658 0.292892 8.70711L6.65685 15.0711C7.04738 15.4616 7.68054 15.4616 8.07107 15.0711C8.46159 14.6805 8.46159 14.0474 8.07107 13.6569L2.41421 8L8.07107 2.34315C8.46159 1.95262 8.46159 1.31946 8.07107 0.928932C7.68054 0.538408 7.04738 0.538408 6.65685 0.928932L0.292892 7.29289ZM21 7L1 7V9L21 9V7Z" fill="#293B6E" />
			</svg>
			<span>
				Вернуться назад
			</span>
		</a>

		<!-- ------------------------------------------------------ Projects ----------------------------------------------------------------------- -->
		<?php $args = array(
			'post_type'		=> 'projects',
			'post__not_in'  => array($post->ID),
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
		<!-- ------------------------------------------------------ End Projects ----------------------------------------------------------------------- -->
	</div>
</main><!-- #main -->


<?php
get_footer();
?>