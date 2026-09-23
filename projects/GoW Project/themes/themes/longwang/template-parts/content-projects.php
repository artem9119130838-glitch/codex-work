<?php

/**
 * Template part for displaying posts
 *
 * @link https://developer.wordpress.org/themes/basics/template-hierarchy/
 *
 * @package longwang
 */

?>

<a href="<?php echo esc_url(get_permalink()); ?>" class="projects-page__item item-proj-page">
	<div class="item-proj-page__bg"></div>
	<div class="item-proj-page__title">
	<?php the_title(); ?>
	</div>
	<div class="item-proj-page__arrow">
		<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 17 17" fill="none">
			<path d="M16.5208 2.00018C16.5208 1.17175 15.8492 0.500181 15.0208 0.500182L1.52082 0.500181C0.692388 0.500181 0.020815 1.17175 0.0208153 2.00018C0.0208157 2.82861 0.692388 3.50018 1.52082 3.50018H13.5208V15.5002C13.5208 16.3286 14.1924 17.0002 15.0208 17.0002C15.8492 17.0002 16.5208 16.3286 16.5208 15.5002L16.5208 2.00018ZM4.06066 15.0817L16.0815 3.06084L13.9602 0.939521L1.93934 12.9603L4.06066 15.0817Z" fill="white" />
		</svg>
	</div>
	<div class="item-proj-page__hex">
		<svg viewBox="1.823 1.158 407.138 448.436" xmlns="http://www.w3.org/2000/svg">
			<pattern id="img-<?php the_ID(); ?>" patternContentUnits="objectBoundingBox" width="100%" height="100%">
				<image height="1" width="1" preserveAspectRatio="xMidYMid slice" xlink:href="<?php the_post_thumbnail_url(); ?>" />
			</pattern>
			<path fill="url(#img-<?php the_ID(); ?>)" d="M 205.392 1.158 L 408.961 113.267 L 408.961 337.485 L 205.392 449.594 L 1.823 337.485 L 1.823 113.267 Z" />
		</svg>
	</div>
</a>