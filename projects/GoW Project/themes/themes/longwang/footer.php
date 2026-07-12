<?php

/**
 * The template for displaying the footer
 *
 * Contains the closing of the #content div and all content after.
 *
 * @link https://developer.wordpress.org/themes/basics/template-files/#template-partials
 *
 * @package longwang
 */

?>
</div>
<footer class="footer">
    <div class="footer__container">
        <div class="footer__top top-footer">
            <a href="<?php echo esc_url(get_home_url()); ?>" class="footer__logo">
             <img src="<?php echo esc_url(get_stylesheet_directory_uri() . '/assets/img/footer/logo.png'); ?>" alt="Фирменная эмблема компании   longwang" title="Знак качества и доверия - LongWang">
            </a>
              
      <!--pravka-->
			      <div class="top-footer__right">
                    <div class="top-footer__currency">
                    <p>RUB / CNY</p>
                    </div>
                    <div class="top-footer__item top-footer__item-buy">
                      <div class="top-footer__price">
                      <p><?php echo do_shortcode('[wpcs_code_rate code=RUB]'); ?></p>
                        </div>
                    </div>
                </div>
            </div>
        <!--pravka end-->           
    	<div class="footer__bottom bottom-footer">
            <div class="bottom-footer__columns">
                <div class="bottom-footer__column column-footer">
                    <div class="column-footer__title">О КОМПАНИИ</div>
                    <ul class="column-footer__ul">
                        <li class="column-footer__li">
                            <a href="<?php echo get_home_url(); ?>/o-nas/" class="column-footer__link" title="История и миссия Longwang">
                                О нас
                            </a>
                        </li>
                        <li class="column-footer__li">
                            <a href="<?php echo get_home_url(); ?>/dokumenty/" class="column-footer__link" title="Лицензии и разрешения компании Longwang">
                                Документы
                            </a>
                        </li>
                        <li class="column-footer__li">
                            <a href="<?php echo get_home_url(); ?>/vakansii-long-wang-llc/" class="column-footer__link" title="Набор сотрудников в компанию Longwang">
                                Вакансии
                            </a>
                        </li>
                        <li class="column-footer__li">
                            <a href="<?php echo get_home_url(); ?>/posledniye-novosti-iz-kitaya/" class="column-footer__link" title="Актуальные новости Longwang">
                                Новости
                            </a>
                        </li>
                    </ul>
                </div>
				
				<!---- uslugi-->
              <div class="bottom-footer__column column-footer">
    <div class="column-footer__title">НАШИ УСЛУГИ</div>
    <ul class="column-footer__ul">
        <li class="column-footer__li">
            <a href="<?php echo get_home_url(); ?>/supplies-services-china/dostavka-is-kitaya/" class="column-footer__link" title="Импорт товаров из Китая под ключ">
                Доставка из Китая
            </a>
        </li>
        <li class="column-footer__li">
            <a href="<?php echo get_home_url(); ?>/supplies-services-china/proverka-postavshhika-v-kitae/" class="column-footer__link" title="Проверка надежности поставщика и его товаров">
                Аудит поставщика
            </a>
        </li>
     <li class="column-footer__li">
            <a href="<?php echo get_home_url(); ?>/supplies-services-china/poisk-i-podbor-postavshika/" class="column-footer__link" title="Поиск и анализ поставщиков для бизнеса">
                Поиск поставщика
            </a>
        </li>	
        <li class="column-footer__li">
            <a href="<?php echo get_home_url(); ?>/supplies-services-china/autsorsing-ved/ved-s-kitaem/" class="column-footer__link" title="Комплексные услуги по ВЭД">
                ВЭД
            </a>
        </li>
        <li class="column-footer__li">
            <a href="<?php echo get_home_url(); ?>/supplies-services-china/tovary-optom-dlia-marketpleisa/" class="column-footer__link" title="Популярные позиции для маркетплейсов">
                Товары для маркетплейсов
            </a>
        </li>
    </ul>
</div>

					<!---- uslugi end-->
				
                <div class="bottom-footer__column column-footer">
                    <div class="column-footer__title">КОНТАКТЫ</div>
                    <ul class="column-footer__ul">
                        <?php 
                            $tel = get_option('site_telephone');
                            $telcall = get_option('site_telephone_call');
                            $mail = get_option('site_email');
                        ?>
                        <li class="column-footer__li">
                            <a href="tel:<?php echo $telcall ? $telcall : ''; ?>" class="column-footer__link">
                                <?php echo $tel ? $tel : ''; ?>
                            </a>
                        </li>
                        <li class="column-footer__li">
                            <a href="mailto:<?php echo $mail ? $mail : ''; ?>" class="column-footer__link">
                                <?php echo $mail ? $mail : ''; ?>
                            </a>
                        </li>
                        <li class="column-footer__li">
                            <span class="column-footer__link">
                               199004 Санкт-Петербург<br> линия 3-я В.О. д.24 А
                            </span>
                        </li>
                        <li class="column-footer__li">
                            <span class="column-footer__link">
                                Часы работы:<br>
                                Пн–Пт: 8:00–20:00<br>
                                Сб–Вс: выходной
                            </span>
                        </li>
                    </ul>
                </div>
                <div class="bottom-footer__column column-footer">
                    <div class="column-footer__title">ПРИСОЕДИНЯЙТЕСЬ</div>
                    <ul class="column-footer__ul">
                        <li class="column-footer__li">
                            <a href="<?php echo get_option('site_vk'); ?>"  rel="nofollow" class="column-footer__link" title="Longwang ВКонтакте" target="_blank">
                                ВКонтакте
                            </a>
                        </li>
                        <li class="column-footer__li">
                            <a href="https://t.me/LongWangBot" rel="nofollow noopener noreferrer" class="column-footer__link" title="Напишите нам в Telegram" target="_blank">Telegram</a>
                       	</li>
						<li class="column-footer__li">
                            <a href="/privacy-policy/" rel="nofollow" class="column-footer__link" title="Наша политика в отношении конфиденциальности">
                                Политика конфиденциальности
                            </a>
                        </li>
						<li class="column-footer__li">
                            <a target="_blank" href="/processing-personal-data/" rel="nofollow" class="column-footer__link" title="Защита персональных данных">
                                Персональные данные
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="bottom-footer__copy">
                Сopyright © 2025 Long Wang
            </div>
        </div>
        <a href="tel:<?php echo $telcall ? $telcall : ''; ?>" class="page-tel neiros-phone">
            <picture>
                <source srcset="<?php echo get_stylesheet_directory_uri(); ?>/assets/img/tel.webp" type="image/webp">
                <img src="<?php echo get_stylesheet_directory_uri(); ?>/assets/img/tel.png" alt="Телефон" title="Звонок в компанию Long Wang">
            </picture>
        </a>
        <button class="btn-totop" data-goto=".wrapper">
            <svg width="4" height="7" viewBox="0 0 7 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 9.75L5.25 5.5L1 1.25" stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
        </button>
    </div>
</footer>
<?php /*
<div id="popup-2" aria-hidden="true" class="popup popup-subscribe">
    <div class="popup__wrapper">
        <div class="popup__content">
            <button data-close type="button" class="popup__close">
                <img src="<?php echo get_stylesheet_directory_uri(); ?>/assets/img/icons/close.svg" alt="Закрыть">
            </button>
            <div class="popup__text">
                <?php echo do_shortcode('[mailpoet_form id="1"]'); ?>
            </div>
        </div>
    </div>
*/ ?>

<script>
	//форма поиска
document.addEventListener('DOMContentLoaded', function () {
    const searchTrigger = document.querySelector('.search-trigger');
    const searchForm = document.querySelector('.header-search');

    if (searchTrigger && searchForm) {
        // Обработка клика по иконке поиска
        searchTrigger.addEventListener('click', function (e) {
            e.preventDefault();
            searchForm.style.display = searchForm.style.display === 'none' || searchForm.style.display === '' ? 'block' : 'none';
        });

        // Скрытие формы при клике вне её
        document.addEventListener('click', function (e) {
            if (!searchForm.contains(e.target) && !searchTrigger.contains(e.target)) {
                searchForm.style.display = 'none';
            }
        });
    }
});
</script>
<?php wp_footer(); ?>
	<!-- Bitrix counter -->
<script>
	(function(w,d,u){
		var s=d.createElement('script');s.async=true;s.src=u+'?'+(Date.now()/60000|0);
		var h=d.getElementsByTagName('script')[0];h.parentNode.insertBefore(s,h);
	})(window,document,'https://cdn-ru.bitrix24.ru/b36750172/crm/tag/call.tracker.js');
</script>	
	<!-- Bitrix counter -->
 <!-- Счетчик кликов на комм страницы -->
<script>
(function() {
    function initTracking() {
        if (!window.yaCounter88077504) {
            setTimeout(initTracking, 500);
            return;
        }
        
        document.addEventListener('click', function(e) {
            var link = e.target.closest('a');
            if (!link) return;
            
            var href = link.getAttribute('href');
            
            var commercialPages = [
                '/supplies-services-china/tovary-optom-dlia-marketpleisa/',
                '/supplies-services-china/equipment-from-china/',
                '/supplies-services-china/proverka-postavshhika-v-kitae/',
                '/supplies-services-china/goods-check-china/',
                '/supplies-services-china/autsorsing-ved/',
                '/supplies-services-china/poisk-i-podbor-postavshika/',
                '/supplies-services-china/dostavka-is-kitaya/',
                '/supplies-services-china/parallelnyj-import-is-kitaya/',
                '/supplies-services-china/poisk-tovara-v-kitae/',
                '/supplies-services-china/autsorsing-ved/ved-s-kitaem/',
                '/supplies-services-china/autsorsing-ved/platezhi-v-kitai/',
                '/supplies-services-china/dostavka-is-kitaya/tamojennoe-oformlenie-china/'
            ];
            
            for (var i = 0; i < commercialPages.length; i++) {
                if (href.indexOf(commercialPages[i]) !== -1) {
                    window.yaCounter88077504.reachGoal('click_to_commercial');
                    break;
                }
            }
        });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTracking);
    } else {
        initTracking();
    }
})();
</script>
 <!-- Счетчик кликов на комм страницы -->
</body>
</html>
