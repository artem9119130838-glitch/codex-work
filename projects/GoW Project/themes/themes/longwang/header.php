<?php
/**
 * The header for our theme
 *
 * This is the template that displays all of the <head> section and everything up until <div id="content">
 *
 * @link https://developer.wordpress.org/themes/basics/template-files/#template-partials
 *
 * @package longwang
 */

?>

<!DOCTYPE html> <!-- DOCTYPE должен быть первым в коде -->

<html <?php language_attributes(); ?> prefix="og: http://ogp.me/ns# article: http://ogp.me/ns/article#">

<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="format-detection" content="telephone=no">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

   <?php wp_head(); ?>

    <!-- Zadarma / Novofon telephony: delayed to reduce first render cost -->
    <script>
        (function (w, d) {
            (w.zTrackerCallbacks = w.zTrackerCallbacks || []).push(function () {
                new zTracker({
                    id: "919a9230c44df4207f9037656e8b257014307",
                    metrics: { metrika: "88077504" }
                });
            });

            var telephonyLoaded = false;
            var telephonySources = [
                { id: "zd_ct_phone_script", src: "https://my.novofon.com/js/ct_phone.min.js" },
                { id: "novofon_widget_script", src: "https://widget.novofon.ru/novofon.js?k=5VbK8Dh6V8lCOKr99Gxw4G11_W8G5oou" }
            ];

            function injectScript(config) {
                if (d.getElementById(config.id)) {
                    return;
                }

                var script = d.createElement("script");
                script.id = config.id;
                script.src = config.src;
                script.async = true;
                d.head.appendChild(script);
            }

            function loadTelephony() {
                if (telephonyLoaded) {
                    return;
                }

                telephonyLoaded = true;
                telephonySources.forEach(injectScript);
            }

            ["pointerdown", "scroll", "keydown", "touchstart"].forEach(function (eventName) {
                w.addEventListener(eventName, loadTelephony, { once: true, passive: true });
            });

            w.addEventListener("load", function () {
                w.setTimeout(loadTelephony, 3500);
            }, { once: true });
        })(window, document);
    </script>
    <!-- End Zadarma / Novofon telephony -->

    <meta name="google-site-verification" content="l88-64LCEcybHL0sgI5Zji-EBOAKtiFjPuGBGyv1haU">  

  <!-- Yandex.Metrika counter  -->
<script>
    (function (d, w, c) {
        (w[c] = w[c] || []).push(function() {
            try {
                w.yaCounter88077504 = new Ya.Metrika({
                    id:88077504,
                    clickmap:true,
                    trackLinks:true,
                    accurateTrackBounce:true,
                    webvisor:true
                });
            } catch(e) { }
        });

        var n = d.getElementsByTagName("script")[0],
            x = "https://mc.yandex.ru/metrika/watch.js",
            s = d.createElement("script"),
            f = function () { n.parentNode.insertBefore(s, n); }
        for (var i = 0; i < document.scripts.length; i++) {
            if (document.scripts[i].src === x) { return; }
        }
        s.type = "text/javascript";
        s.async = true;
        s.src = x;

        if (w.opera == "[object Opera]") {
            d.addEventListener("DOMContentLoaded", f, false);
        } else { f(); }
    })(document, window, "yandex_metrika_callbacks");
</script>
<!-- /Yandex.Metrika counter -->

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-1X7RDEXT7H"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-1X7RDEXT7H');
</script>
<!-- Google tag (gtag.js) -->	
		
<link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="shortcut icon" href="/favicon.ico" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<meta name="apple-mobile-web-app-title" content="LongWang" />
<!--  <script src="https://integrations.1cdialog.com/integration/webchat/690605:ZnDZNmIiUeCkBQikGj1fVrX7bjXy1ATV" async></script> -->
</head>
<!---zamena--->	
<body>
    <div class="wrapper">
        <header class="header">
            <div class="header__wrapper">
                <div class="header__container">
                    <a href="<?php echo get_home_url(); ?>" class="header__logo">
                        <img src="<?php echo get_stylesheet_directory_uri(); ?>/assets/img/logo.png" alt="Фирменный логотип компании longwang" title="Знак качества и доверия LongWang">
                    </a>
                    <!-- Правый блок -->
                    <div class="header__right">
                        <!-- Меню -->
                        <div class="header__menu menu">
                            <nav class="menu__body">
                                <?php my_nav_menu(['theme_location' => 'header_nav']); ?>
                            </nav>
                        </div>
                        <button type="button" class="menu__icon icon-menu"></button>
                    </div>
                    <!-- Контактный блок -->
                    <div class="block-sv">
                        <!-- Телефон -->
                        <div class="header__tel">
                            <a href="tel:<?php echo get_option('site_telephone_call'); ?>" class="header__icon" aria-label="Телефон">
                                <img src="/wp-content/uploads/2024/11/phone-icone3.png" alt="Телефон" title="+7 (812) 509 12 45" width="40" height="40">
                            </a>
                        </div>
                        <!-- Telegram -->
                        <div class="header__tel">
                            <a href="https://t.me/LongWangBot" class="header__icon" target="_blank" aria-label="Telegram">
                                <img src="/wp-content/uploads/2024/11/telegram-icon3.png" alt="Telegram" title="Написать в Telegram" width="40" height="40">
                            </a>
                        </div>
                        <!-- Почта -->
                        <div class="header__tel">
                            <a href="mailto:sales@longwang.ru" class="header__icon" aria-label="Почта">
                                <img src="/wp-content/uploads/2024/11/email-icon3.png" alt="Email" title="sales@longwang.ru" width="40" height="40">
                            </a>
                        </div>
                        <!-- Иконка поиска -->
                        <div class="header__tel header_search">
                            <a href="#" class="header__icon search-trigger" aria-label="Поиск">
                                <img src="/wp-content/uploads/2024/11/search-icon3.png" alt="Поиск" title="Искать" width="40" height="40">
                            </a>
                        </div>
                        <!-- Выпадающая форма поиска -->
                        <div class="header-search" style="display: none;">
                            <form role="search" method="get" class="search-form" action="/">
                                <label>
                                    <input type="search" class="search-field" placeholder="Введите запрос..." name="s" />
                                </label>
                                <button type="submit" class="search-submit">Искать</button>
                            </form>
                        </div>
                    </div> <!-- Закрытие block-sv -->
                </div> <!-- Закрытие header__container -->
            </div> <!-- Закрытие header__wrapper -->
        </header>
  
