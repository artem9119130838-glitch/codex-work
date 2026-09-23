<?php /* Template Name: Template Documents */
get_header();
?>

<main class="page documents-page">
    <section class="documents-page__hero hero-main hero-main--narrow">
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
    <div class="documents-page__body">
        <div class="documents-page__container">
            <?php $docs = get_field('ssylki'); ?>
            <div class="documents-page__items">

                <?php
                if ($docs) {
                    foreach ($docs as $doc) {
                ?>

                        <a href="<?php echo $doc['fajl']; ?>" class="documents-page__item" download>
                            <?php echo $doc['nazvanie_fajla']; ?>
                        </a>

                <?php
                    }
                }
                ?>

            </div>
            <div class="documents-page__bottom">
                <?php echo get_field('tekst'); ?>
            </div>
        </div>
    </div>
</main>

<?php
get_footer();
