<?php

/**
 * Template part for displaying posts
 *
 * @link https://developer.wordpress.org/themes/basics/template-hierarchy/
 *
 * @package longwang
 */

?>

<div class="news-page__item item-news">
	<div class="item-news__title">
		<?php the_title(); ?>
	</div>
	<div class="item-news__text">
		<?php the_excerpt(); ?>
	</div>
	<div class="item-news__bottom">
		<div class="item-news__date">
			<?php echo get_the_date(); ?>
		</div>
		<a href="<?php the_permalink(); ?>" class="item-news__read">
			Читать далее »
		</a>
	</div>
</div>