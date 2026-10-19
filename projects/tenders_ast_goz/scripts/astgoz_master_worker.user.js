// ==UserScript==
// @name         AST-GOZ CONTROL 4.1 (Firefox Master-Worker)
// @namespace    http://tampermonkey.net/
// @version      4.1
// @description  Надежная автоматизация выгрузки лотов АСТ ГОЗ для Mozilla Firefox с активной вкладкой, сквозной телеметрией и обходом таймаутов
// @author       Mikhail / Artem / Codex
// @match        https://223.astgoz.ru/*
// @grant        GM_openInTab
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_deleteValue
// @grant        GM_setClipboard
// @grant        window.close
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    const CONFIG = {
        maxLots: 30,            // Максимум лотов за один прогон
        lotDelayMs: 3000,       // Пауза между лотами (мс)
        workerTimeoutMs: 75000  // Таймаут ожидания скачивания одного лота (мс)
    };

    const currentUrl = window.location.href;
    const isRegistry = currentUrl.includes('/registry/view/pr_lots_all') ||
                       currentUrl.includes('/registry/view/pr_all') ||
                       currentUrl.includes('/customer/p/purchase/registry');

    // =========================================================================
    // ВЕТКА 1: МАСТЕР (Вкладка реестра лотов)
    // =========================================================================
    if (isRegistry) {
        console.log('[AST-GOZ 4.1 Master] Реестр обнаружен. Инициализация панели управления...');

        let isRunning = false;
        let shouldStop = false;

        // Внедряем стили панели
        const style = document.createElement('style');
        style.innerHTML = `
            #goz-panel {
                position: fixed; top: 15px; right: 15px; z-index: 999999;
                background: #1a252f; color: #ecf0f1; padding: 14px;
                border-radius: 8px; box-shadow: 0 6px 20px rgba(0,0,0,0.6);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
                width: 340px; font-size: 12px;
            }
            .goz-title {
                font-size: 13px; font-weight: bold; margin-bottom: 8px;
                text-align: center; color: #3498db; letter-spacing: 0.5px;
            }
            .goz-btn {
                display: block; width: 100%; margin: 5px 0; padding: 8px 10px;
                cursor: pointer; border: none; border-radius: 4px;
                font-weight: bold; font-size: 11px; color: white;
                transition: background 0.2s;
            }
            .btn-auto { background: #27ae60; font-size: 12px; padding: 10px; }
            .btn-auto:hover { background: #2ecc71; }
            .btn-stop { background: #e74c3c; display: none; }
            .btn-stop:hover { background: #c0392b; }
            .btn-manual-group { margin-top: 8px; border-top: 1px solid #34495e; padding-top: 6px; }
            .btn-main { background: #2980b9; }
            .btn-action { background: #16a085; }
            .btn-filter { background: #f39c12; color: #000; }
            #goz-log {
                background: #0d1117; color: #58a6ff; font-family: 'Courier New', monospace;
                font-size: 11px; height: 150px; overflow-y: auto; margin-top: 8px;
                padding: 6px; border: 1px solid #30363d; border-radius: 4px; line-height: 1.4;
            }
            .log-err { color: #f85149; font-weight: bold; }
            .log-ok { color: #3fb950; font-weight: bold; }
            .log-info { color: #79c0ff; }
            .log-worker { color: #e3b341; font-style: italic; }
            .lot-badge-done { background: #238636; color: #fff; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 6px; font-weight: bold; }
            .lot-badge-err { background: #da3633; color: #fff; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 6px; font-weight: bold; }
        `;
        document.head.appendChild(style);

        // Создаем интерфейс панели
        const panel = document.createElement('div');
        panel.id = 'goz-panel';
        panel.innerHTML = `
            <div class="goz-title">🦊 AST-GOZ CONTROL 4.1 (Firefox)</div>
            <button id="goz-btn-auto" class="goz-btn btn-auto">🚀 ПОЛНЫЙ АВТОМАТ (Master-Worker)</button>
            <button id="goz-btn-stop" class="goz-btn btn-stop">⏹ ОСТАНОВИТЬ</button>
            
            <div class="btn-manual-group">
                <div style="font-size:10px; color:#8b949e; margin-bottom:4px; text-align:center;">Диагностика и помощь:</div>
                <button id="goz-diag" class="goz-btn btn-main" style="background:#8e44ad; padding:5px; font-size:11px;">🔍 ДИАГНОСТИКА СТРОК</button>
                <button id="goz-copy-log" class="goz-btn btn-main" style="background:#4a69bd; padding:5px; font-size:11px;">📋 СКОПИРОВАТЬ ЛОГ</button>
            </div>

            <div id="goz-log">--- Готов к работе ---</div>
            <button id="goz-reset" class="goz-btn" style="background:#484f58; font-size:9px; height:22px; padding:0; margin-top:5px;">Очистить лог</button>
        `;
        document.body.appendChild(panel);

        function log(msg, type = '') {
            const logger = document.getElementById('goz-log');
            if (!logger) return;
            const timeStr = new Date().toLocaleTimeString().split(' ')[0];
            let colorClass = '';
            if (type === 'error') colorClass = 'log-err';
            else if (type === 'ok') colorClass = 'log-ok';
            else if (type === 'info') colorClass = 'log-info';
            else if (type === 'worker') colorClass = 'log-worker';
            
            logger.innerHTML += `<div>[${timeStr}] <span class="${colorClass}">${msg}</span></div>`;
            logger.scrollTop = logger.scrollHeight;
        }

        document.getElementById('goz-reset').onclick = () => {
            const logger = document.getElementById('goz-log');
            if (logger) logger.innerHTML = '--- Лог очищен ---';
        };

        document.getElementById('goz-copy-log').onclick = () => {
            const logger = document.getElementById('goz-log');
            if (logger) {
                const text = logger.innerText || '';
                try {
                    GM_setClipboard(text);
                    log('Лог скопирован в буфер обмена!', 'ok');
                } catch (e) {
                    navigator.clipboard.writeText(text).then(() => {
                        log('Лог скопирован в буфер обмена!', 'ok');
                    });
                }
            }
        };

        // Кнопка остановки
        const stopBtn = document.getElementById('goz-btn-stop');
        const autoBtn = document.getElementById('goz-btn-auto');

        stopBtn.onclick = () => {
            shouldStop = true;
            log('Получена команда остановки. Завершение текущего лота...', 'error');
            stopBtn.disabled = true;
        };

        // Главный цикл автомата
        autoBtn.onclick = async () => {
            if (isRunning) return;
            isRunning = true;
            shouldStop = false;
            autoBtn.style.display = 'none';
            stopBtn.style.display = 'block';
            stopBtn.disabled = false;

            log('Старт автоматического цикла выгрузки...', 'info');

            try {
                await runMasterLoop();
            } catch (err) {
                log(`Критический сбой цикла: ${err.message}`, 'error');
            } finally {
                isRunning = false;
                autoBtn.style.display = 'block';
                stopBtn.style.display = 'none';
                log('Цикл обработки завершен.', 'info');
            }
        };

        async function runMasterLoop() {
            // Диагностика текущей вкладки
            const isLotsRegistry = currentUrl.includes('pr_lots_all');
            if (!isLotsRegistry) {
                log('⚠️ ВНИМАНИЕ: Вы находитесь в "Общем реестре процедур"!', 'error');
                log('👉 Документация привязана к лотам. Перейдите в меню: "Лоты" ➔ "Реестр лотов" (pr_lots_all)', 'ok');
            }

            let rows = [...document.querySelectorAll('table tbody tr')].filter(tr => (tr.innerText || '').trim().length > 0);
            if (rows.length === 0) {
                rows = [...document.querySelectorAll('table tr')].filter(tr => (tr.innerText || '').trim().length > 0 && !tr.querySelector('th'));
            }
            if (rows.length === 0) {
                rows = [...document.querySelectorAll('.grid-view tr, [role="row"]')].filter(tr => (tr.innerText || '').trim().length > 0 && !tr.querySelector('th'));
            }
            log(`Найдено строк в таблице: ${rows.length}`, 'info');

            if (rows.length === 0) {
                log('❌ Таблица не найдена в DOM! Проверьте, загрузилась ли страница полностью.', 'error');
                return;
            }

            let processedCount = 0;

            for (let i = 0; i < rows.length; i++) {
                if (shouldStop) {
                    log('Обработка прервана пользователем.', 'error');
                    break;
                }
                if (processedCount >= CONFIG.maxLots) {
                    log(`Достигнут лимит лотов за прогон (${CONFIG.maxLots}).`, 'ok');
                    break;
                }

                const row = rows[i];
                const text = row.innerText || '';

                // 1. Поиск номера лота/процедуры
                const lotMatch = text.match(/\b26\d{13}\b/) || text.match(/\b\d{8,15}\b/);
                const lotId = lotMatch ? lotMatch[0] : `Лот_${i + 1}`;

                // 2. Ищем ссылку на запрос документации
                let requestLink = row.querySelector('a[href*="request_documents"], a[href*="request_doc"], a[href*="action=request"]');
                if (!requestLink) {
                    const links = [...row.querySelectorAll('a, button')];
                    requestLink = links.find(a => {
                        const t = (a.innerText || a.textContent || a.title || '').toLowerCase();
                        return t.includes('запрос документации') || t.includes('запросить документацию') || t.includes('запрос документов');
                    });
                }

                // 3. А также проверяем: вдруг документация УЖЕ запрошена ранее и доступна ссылка «Выгрузить»?
                let unloadLink = null;
                if (!requestLink) {
                    const links = [...row.querySelectorAll('a, button')];
                    unloadLink = links.find(a => {
                        const t = (a.innerText || a.textContent || a.title || '').toLowerCase();
                        const h = (a.getAttribute('href') || '').toLowerCase();
                        return t.includes('выгрузить') || h.includes('action=unload') || h.includes('purchase/view');
                    });
                }

                const targetLink = requestLink || unloadLink;
                const isDirectUnload = !requestLink && !!unloadLink;

                if (targetLink && targetLink.href && !targetLink.href.startsWith('javascript:')) {
                    const actionName = isDirectUnload ? 'Скачивание готового архива' : 'Запрос документации';
                    log(`[${processedCount + 1}] ${actionName} для лота ${lotId}...`, 'info');

                    // Сбрасываем общее состояние воркера перед запуском
                    GM_setValue('goz_worker_active', true);
                    GM_setValue('goz_worker_status', 'PENDING');
                    GM_setValue('goz_worker_step', 'Запуск вкладки...');
                    GM_setValue('goz_worker_error', '');
                    GM_setValue('goz_current_lot', lotId);

                    // ВАЖНО: Открываем вкладку АКТИВНОЙ ({ active: true }), чтобы избежать троттлинга таймеров в Firefox
                    // и чтобы модальные окна КриптоПро/PIN-код были видны пользователю!
                    const workerTab = GM_openInTab(targetLink.href, { active: true, insert: true });
                    const success = await waitForWorkerLive(lotId, CONFIG.workerTimeoutMs, log);

                    if (success) {
                        processedCount++;
                        log(`Лот ${lotId} успешно обработан!`, 'ok');
                        addBadgeToRow(row, `✔ Выгружен`, 'lot-badge-done');

                        // Шаг: простановка статусной метки «Подготовить документы» (если есть)
                        const prepLink = row.querySelector('a[href*="action=set_documents"]');
                        if (prepLink && prepLink.href) {
                            try {
                                const prepTab = GM_openInTab(prepLink.href, { active: false, insert: true });
                                await new Promise(r => setTimeout(r, 2000));
                                if (prepTab) prepTab.close();
                                log(`Метка установлена для ${lotId}`, 'ok');
                            } catch (ePrep) {
                                console.warn('Ошибка закрытия метки:', ePrep);
                            }
                        }
                    } else {
                        const errReason = GM_getValue('goz_worker_error') || 'Таймаут или сбой на странице лота';
                        log(`Сбой при выгрузке лота ${lotId}: ${errReason}`, 'error');
                        addBadgeToRow(row, `✖ Сбой`, 'lot-badge-err');
                        if (workerTab) {
                            try { workerTab.close(); } catch(e) {}
                        }
                    }

                    // Сбрасываем флаг активности
                    GM_setValue('goz_worker_active', false);

                    log(`Пауза ${CONFIG.lotDelayMs / 1000} сек перед следующим лотом...`);
                    await new Promise(r => setTimeout(r, CONFIG.lotDelayMs));
                } else {
                    console.log(`[AST-GOZ] Строка ${i + 1} (${lotId}) пропущена: нет кнопок 'Запрос документации' или 'Выгрузить'.`);
                }
            }

            // По окончании пачки — обновляем фильтры реестра
            if (processedCount > 0) {
                log('Обновление фильтров реестра...', 'info');
                await applyRegistryFilters();
            }

            alert(`AST-GOZ CONTROL 4.1: Обработка завершена!\nУспешно выгружено лотов: ${processedCount}`);
        }

        // Ожидание воркера со сквозным выводом шагов в лог панели в реальном времени
        function waitForWorkerLive(lotId, timeoutMs, logFn) {
            return new Promise((resolve) => {
                const startTime = Date.now();
                let lastLoggedStep = '';

                const timer = setInterval(() => {
                    // Читаем текущий шаг воркера для живого отображения в панели
                    const currentStep = GM_getValue('goz_worker_step') || '';
                    if (currentStep && currentStep !== lastLoggedStep) {
                        lastLoggedStep = currentStep;
                        logFn(`↳ ${currentStep}`, 'worker');
                    }

                    const status = GM_getValue('goz_worker_status');
                    if (status === 'DONE') {
                        clearInterval(timer);
                        resolve(true);
                    } else if (status === 'ERROR') {
                        clearInterval(timer);
                        resolve(false);
                    } else if (Date.now() - startTime > timeoutMs) {
                        clearInterval(timer);
                        logFn(`Превышен лимит ожидания (${timeoutMs / 1000} сек) для лота ${lotId}`, 'error');
                        resolve(false);
                    }
                }, 500);
            });
        }

        function addBadgeToRow(row, text, className) {
            const firstCell = row.querySelector('td');
            if (firstCell) {
                const badge = document.createElement('span');
                badge.className = className;
                badge.innerText = text;
                firstCell.appendChild(badge);
            }
        }

        async function applyRegistryFilters() {
            const applyBtn = [...document.querySelectorAll('button, input, a')].find(el => {
                const val = (el.innerText || el.textContent || el.value || '').trim();
                return val === 'Применить фильтры' || val === 'Применить';
            });
            if (applyBtn) {
                applyBtn.click();
                log('Кнопка "Применить фильтры" нажата.', 'ok');
            } else {
                log('Кнопка фильтров не найдена в DOM.', 'error');
            }
        }

        // Диагностика таблицы реестра
        document.getElementById('goz-diag').onclick = () => {
            log('Запуск диагностики DOM таблицы...', 'info');
            let rows = [...document.querySelectorAll('table tbody tr')].filter(tr => (tr.innerText || '').trim().length > 0);
            if (rows.length === 0) {
                rows = [...document.querySelectorAll('table tr')].filter(tr => (tr.innerText || '').trim().length > 0 && !tr.querySelector('th'));
            }
            if (rows.length === 0) {
                rows = [...document.querySelectorAll('.grid-view tr, [role="row"]')].filter(tr => (tr.innerText || '').trim().length > 0 && !tr.querySelector('th'));
            }
            log(`Найдено строк: ${rows.length}`, rows.length > 0 ? 'ok' : 'error');
            if (rows.length === 0) {
                log('Таблица не найдена! Проверьте, загрузилась ли таблица.', 'error');
                return;
            }
            for (let i = 0; i < Math.min(3, rows.length); i++) {
                const r = rows[i];
                const txt = (r.innerText || '').replace(/\s+/g, ' ').slice(0, 60);
                const links = [...r.querySelectorAll('a, button')].map(a => `"${(a.innerText || a.textContent || a.title || '').trim()}" [${a.getAttribute('href') || a.tagName}]`).filter(s => !s.startsWith('""'));
                log(`[Строка ${i + 1}]: ${txt}...`, 'info');
                log(`Кнопки/ссылки ${i + 1}: ${links.slice(0, 4).join(', ') || 'нет'}`, 'ok');
            }
        };
    }

    // =========================================================================
    // ВЕТКА 2: ВОРКЕР (Любая вкладка лота при активной задаче выгрузки)
    // =========================================================================
    else {
        // Проверяем: запущена ли задача Мастером
        const isWorkerActive = GM_getValue('goz_worker_active');
        if (!isWorkerActive) {
            // Вкладка открыта вручную пользователем, скрипт не вмешивается
            return;
        }

        console.log(`[AST-GOZ 4.1 Worker] Вкладка запущена: ${location.pathname}`);
        GM_setValue('goz_worker_status', 'IN_PROGRESS');
        GM_setValue('goz_worker_step', `Открыта страница: ${location.pathname}`);

        // Автоматически подтверждаем системные диалоги confirm / alert если появятся
        try {
            window.confirm = () => true;
            window.alert = () => true;
        } catch (e) {}

        // Запуск адаптивного обработчика страницы лота
        runWorkerHandler();
    }

    async function runWorkerHandler() {
        try {
            // Даем DOM стабилизироваться
            await new Promise(r => setTimeout(r, 1200));

            // Проверяем: нет ли явной ошибки доступа/блокировки на странице
            const bodyText = (document.body.innerText || '').toLowerCase();
            if (bodyText.includes('доступ запрещен') || bodyText.includes('ошибка 403') || bodyText.includes('ошибка 500')) {
                GM_setValue('goz_worker_error', 'Ошибка доступа или ошибка сервера на площадке');
                GM_setValue('goz_worker_status', 'ERROR');
                return;
            }

            // ШАГ А: Проверяем, есть ли уже на странице кнопка «Выгрузить» или прямая ссылка на скачивание архива
            const unloadBtn = findUnloadElement();
            if (unloadBtn) {
                await triggerDownloadAndFinish(unloadBtn);
                return;
            }

            // ШАГ Б: Если кнопки «Выгрузить» нет, проверяем форму «Запрос документации»
            GM_setValue('goz_worker_step', 'Поиск формы согласия и кнопки подписания...');

            // 1. Поиск чекбокса согласия
            let cb = document.querySelector('input[type="checkbox"]');
            if (!cb) {
                cb = await waitForElement('input[type="checkbox"]', 8000);
            }

            if (cb) {
                if (!cb.checked) {
                    cb.checked = true;
                    cb.dispatchEvent(new Event('input', { bubbles: true }));
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                }
                GM_setValue('goz_worker_step', 'Чекбокс согласия активирован');
                await new Promise(r => setTimeout(r, 600));
            } else {
                console.log('[AST-GOZ Worker] Чекбокс согласия не найден или не требуется на этой форме.');
            }

            // 2. Поиск кнопки отправки запроса («Подписать и отправить» / «Отправить» / «Запросить»)
            const submitBtn = findSubmitButton();
            if (submitBtn) {
                const btnLabel = (submitBtn.innerText || submitBtn.value || 'Подписать и отправить').trim();
                GM_setValue('goz_worker_step', `Нажата кнопка '${btnLabel}'`);
                submitBtn.click();

                // 3. Ожидание модального окна подтверждения
                GM_setValue('goz_worker_step', 'Ожидание модального подтверждения / ЭЦП...');
                await handleModalConfirmation();

                // 4. После подтверждения страница либо обновится на карточку с кнопкой «Выгрузить», либо обновит DOM
                GM_setValue('goz_worker_step', 'Ожидание появления кнопки "Выгрузить"...');
                await waitForUnloadButtonAndDownload(35000);
            } else {
                // Если не найдена ни кнопка отправки, ни чекбокс — ищем кнопку скачивания еще раз (вдруг отрендерилась)
                GM_setValue('goz_worker_step', 'Повторный поиск кнопки скачивания...');
                await waitForUnloadButtonAndDownload(15000);
            }

        } catch (err) {
            console.error('[AST-GOZ Worker] Ошибка:', err);
            GM_setValue('goz_worker_error', err.message || 'Ошибка выполнения воркера');
            GM_setValue('goz_worker_status', 'ERROR');
        }
    }

    // Поиск элемента выгрузки архива документации
    function findUnloadElement() {
        const candidates = [...document.querySelectorAll('a, button, input[type="button"], input[type="submit"]')];
        return candidates.find(el => {
            const t = (el.innerText || el.textContent || el.value || el.title || '').trim().toLowerCase();
            const h = (el.getAttribute('href') || '').toLowerCase();
            return t.includes('выгрузить') || 
                   t.includes('скачать документацию') || 
                   t.includes('скачать архив') || 
                   t.includes('скачать все') || 
                   h.includes('action=unload') || 
                   h.includes('/download');
        });
    }

    // Поиск кнопки отправки/подписания формы
    function findSubmitButton() {
        const candidates = [...document.querySelectorAll('button, a, input[type="submit"], input[type="button"]')];
        return candidates.find(el => {
            const t = (el.innerText || el.textContent || el.value || '').trim().toLowerCase();
            return t.includes('подписать и отправить') || 
                   t.includes('подписать и направить') || 
                   t.includes('отправить запрос') || 
                   t.includes('запросить документацию') || 
                   t.includes('запросить') || 
                   (t === 'подписать');
        });
    }

    // Обработка модального окна подтверждения подписания
    async function handleModalConfirmation() {
        const modalContainer = await waitForElement('#modal, .modal, [role="dialog"], .swal2-container, .popup, div[class*="dialog"]', 15000);
        if (modalContainer) {
            await new Promise(r => setTimeout(r, 800));
            const modalBtns = [...modalContainer.querySelectorAll('button, a, input[type="button"]')];
            const confirmBtn = modalBtns.find(el => {
                const t = (el.innerText || el.textContent || el.value || '').trim().toLowerCase();
                return t.includes('подписать') || t.includes('согласие') || t.includes('да') || t.includes('подтвердить') || t === 'ок' || t === 'ok';
            });

            if (confirmBtn) {
                confirmBtn.click();
                GM_setValue('goz_worker_step', 'Модальное окно подтверждено, ЭЦП отправлена');
                console.log('[AST-GOZ Worker] Модальное окно подтверждено.');
                await new Promise(r => setTimeout(r, 2000));
            } else {
                console.log('[AST-GOZ Worker] Кнопка подтверждения в модалке не найдена, возможно автосабмит.');
            }
        }
    }

    // Ожидание появления кнопки «Выгрузить» и запуск скачивания
    async function waitForUnloadButtonAndDownload(timeoutMs) {
        const startTime = Date.now();
        while (Date.now() - startTime < timeoutMs) {
            const btn = findUnloadElement();
            if (btn) {
                await triggerDownloadAndFinish(btn);
                return;
            }
            await new Promise(r => setTimeout(r, 1000));
        }

        // Если за время таймаута кнопка так и не появилась:
        // Проверяем: возможно запрос успешно принят площадкой (статус "Запрос подан")
        const pageText = (document.body.innerText || '').toLowerCase();
        if (pageText.includes('запрос зарегистрирован') || pageText.includes('запрос подан') || pageText.includes('документация сформирована')) {
            GM_setValue('goz_worker_step', 'Запрос успешно зарегистрирован площадкой');
            GM_setValue('goz_worker_status', 'DONE');
            GM_setValue('goz_worker_active', false);
            setTimeout(() => window.close(), 2000);
            return;
        }

        GM_setValue('goz_worker_error', 'Кнопка "Выгрузить" не появилась после отправки запроса');
        GM_setValue('goz_worker_status', 'ERROR');
    }

    // Клик по кнопке скачивания, ожидание запуска загрузки браузером и закрытие вкладки
    async function triggerDownloadAndFinish(unloadBtn) {
        const btnText = (unloadBtn.innerText || unloadBtn.value || 'Выгрузить').trim();
        GM_setValue('goz_worker_step', `Нажата кнопка '${btnText}'. Запуск скачивания архива...`);
        console.log(`[AST-GOZ Worker] Клик по кнопке скачивания: ${btnText}`);
        
        unloadBtn.click();

        GM_setValue('goz_worker_step', 'Архив отправлен на скачивание. Завершение...');
        
        // Даем 4 секунды браузеру Firefox на инициализацию потока скачивания архива
        await new Promise(r => setTimeout(r, 4000));

        // Сигнализируем Мастеру об успешном завершении
        GM_setValue('goz_worker_status', 'DONE');
        GM_setValue('goz_worker_active', false);

        // Закрываем вкладку (фокус автоматически вернется в реестр Мастера)
        window.close();
    }

    // Утилита реактивного ожидания элементов через MutationObserver
    function waitForElement(selector, timeoutMs = 15000) {
        return new Promise(resolve => {
            const el = document.querySelector(selector);
            if (el) return resolve(el);

            const observer = new MutationObserver(() => {
                const found = document.querySelector(selector);
                if (found) {
                    observer.disconnect();
                    resolve(found);
                }
            });

            observer.observe(document.body, { childList: true, subtree: true });
            setTimeout(() => {
                observer.disconnect();
                resolve(null);
            }, timeoutMs);
        });
    }

})();
