<?php
/**
 * The template for displaying search results pages
 *
 * @package longwang
 */

get_header();
?>

<main id="primary" class="site-main">
    <?php if ( have_posts() ) : ?>
        <header class="page-header">
            <h1 class="page-title">
                <?php
                /* translators: %s: search query. */
                printf( esc_html__( 'Search Results for: %s', 'longwang' ), '<span>' . get_search_query() . '</span>' );
                ?>
            </h1>
        </header><!-- .page-header -->

        <div class="search-results-list">
            <?php
            /* Start the Loop */
            while ( have_posts() ) :
                the_post();
                
                // Закомментировано, т.к. не используется:
                // get_template_part( 'template-parts/content', 'search' );

                /* НАЧАЛО ВСТАВКИ: Вывод заголовка и обрезанного текста */
                ?>
                <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                    <header class="entry-header">
                        <h2 class="entry-title">
                            <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                        </h2>
                    </header><!-- .entry-header -->

                    <div class="entry-summary">
                        <p>
                            <?php
                            // Обрезаем текст до 200 символов
                            echo wp_trim_words(get_the_excerpt(), 30, '...');
                            ?>
                        </p>
                    </div><!-- .entry-summary -->
                </article><!-- #post-<?php the_ID(); ?> -->
                <!-- КОНЕЦ ВСТАВКИ -->
                
            <?php
            endwhile;
            ?>
        </div>

        <?php the_posts_navigation(); ?>

    <?php else : ?>

        <p><?php esc_html_e( 'Sorry, no results were found.', 'longwang' ); ?></p>

    <?php endif; ?>
</main><!-- #main -->

<?php
get_footer();
