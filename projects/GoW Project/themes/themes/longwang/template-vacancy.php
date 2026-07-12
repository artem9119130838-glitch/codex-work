<?php /* Template Name: Template Vacancy */
get_header();
?>

<main class="page vacancy-page">
    <section class="vacancy-page__hero hero-main hero-main--narrow">
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

    <div class="vacancy-page__body body-vacancy">
        <div class="body-vacancy__container">
            <?php $vakansii = get_field('vakansii'); ?>


            <?php
            if ($vakansii) {
                foreach ($vakansii as $vakansya) {
            ?>
                    <div class="body-vacancy__block">
                        <div class="body-vacancy__content page-content">
                            <div class="body-vacancy__vacancy">
                                <?php echo $vakansya['vakansiya']; ?>
                            </div>
                        </div>
                        <button class="hero-main__btn _btn" data-goto=".consult">
                            Откликнуться на вакансию
                        </button>
                    </div>
            <?php
                }
            }
            ?>


        </div>
    </div>
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
