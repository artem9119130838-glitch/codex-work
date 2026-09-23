const CONFIG = {
  folderId: '1SX1tVGJhF_RXszMwERi5glEr9j07GUzE',
  geminiApiKey: 'PASTE_GEMINI_API_KEY_HERE',
  geminiModel: 'gemini-2.5-flash',
  dryRun: false,
  maxFilesPerRun: 20,
  pauseMsBetweenAiCalls: 4000,
  geminiRetryCount: 2,
  geminiRetryDelayMs: 10000,
  stopOnQuotaExceeded: true,
  processImages: false,
  statePrefix: 'gdr_state_v1_',
  cursorKey: 'gdr_cursor_v1',
  textPreviewLimit: 4000,
  normalizedPrefixPattern: /^[^_]+_[^_]+_[^_]+_[^_]+_[^_]+/,
  allowedTags: [
    'ВЭД',
    'Китай',
    'СНГ',
    'Импорт',
    'Экспорт',
    'Продажи',
    'Логистика',
    'Обучение',
    'Инструкция',
    'Тендер',
    'Финансы',
    'Таможня',
    'Внутренний',
    'Управление'
  ]
};

function previewRenameFiles() {
  runRenamePipeline_(true);
}

function renameFiles() {
  runRenamePipeline_(false);
}

function resetRenameState() {
  const props = PropertiesService.getScriptProperties();
  const all = props.getProperties();

  Object.keys(all).forEach(function(key) {
    if (key.indexOf(CONFIG.statePrefix) === 0 || key === CONFIG.cursorKey) {
      props.deleteProperty(key);
    }
  });

  Logger.log('[RESET] saved rename state cleared');
}

function runRenamePipeline_(forceDryRun) {
  validateConfig_();

  const isDryRun = forceDryRun || CONFIG.dryRun;
  const props = PropertiesService.getScriptProperties();
  const savedCursor = props.getProperty(CONFIG.cursorKey);

  let files;
  if (savedCursor) {
    try {
      files = DriveApp.continueFileIterator(savedCursor);
    } catch (error) {
      files = DriveApp.getFolderById(CONFIG.folderId).getFiles();
      props.deleteProperty(CONFIG.cursorKey);
      Logger.log('[WARN] saved cursor expired, restarted folder scan');
    }
  } else {
    files = DriveApp.getFolderById(CONFIG.folderId).getFiles();
  }

  const summary = {
    scanned: 0,
    renamed: 0,
    skipped: 0,
    failed: 0,
    stoppedOnQuota: false
  };

  while (files.hasNext() && summary.scanned < CONFIG.maxFilesPerRun) {
    const file = files.next();
    summary.scanned += 1;

    try {
      const result = processFile_(file, isDryRun);
      if (result.status === 'renamed') {
        summary.renamed += 1;
      } else {
        summary.skipped += 1;
      }
    } catch (error) {
      if (CONFIG.stopOnQuotaExceeded && isQuotaError_(error)) {
        summary.stoppedOnQuota = true;
        saveFileState_(getFileStateKey_(file), {
          signature: getFileSignature_(file),
          status: 'quota',
          message: String(error.message || error)
        });
        Logger.log('[STOP] quota exceeded on %s', file.getName());
        break;
      }

      summary.failed += 1;
      saveFileState_(getFileStateKey_(file), {
        signature: getFileSignature_(file),
        status: 'failed',
        message: String(error.message || error)
      });
      Logger.log('[ERROR] %s -> %s', file.getName(), error.message || error);
    }
  }

  if (files.hasNext()) {
    props.setProperty(CONFIG.cursorKey, files.getContinuationToken());
  } else {
    props.deleteProperty(CONFIG.cursorKey);
  }

  Logger.log(
    '[SUMMARY] scanned=%s renamed=%s skipped=%s failed=%s dryRun=%s stoppedOnQuota=%s',
    summary.scanned,
    summary.renamed,
    summary.skipped,
    summary.failed,
    isDryRun,
    summary.stoppedOnQuota
  );
}

function processFile_(file, isDryRun) {
  const oldName = file.getName();
  const mimeType = file.getMimeType();
  const stateKey = getFileStateKey_(file);
  const currentSignature = getFileSignature_(file);
  const savedState = readFileState_(stateKey);

  if (savedState && savedState.signature === currentSignature && savedState.status === 'previewed' && savedState.newName) {
    if (isDryRun) {
      Logger.log('[SKIP] cached preview: %s -> %s', oldName, savedState.newName);
      return { status: 'skipped' };
    }

    file.setName(savedState.newName);
    saveFileState_(stateKey, {
      signature: getFileSignature_(file),
      status: 'renamed',
      newName: savedState.newName
    });
    Logger.log('[RENAMED] %s -> %s', oldName, savedState.newName);
    return { status: 'renamed' };
  }

  if (savedState && savedState.signature === currentSignature && shouldSkipCachedState_(savedState.status)) {
    Logger.log('[SKIP] cached state: %s (%s)', oldName, savedState.status);
    return { status: 'skipped' };
  }

  if (isAlreadyNormalized_(oldName)) {
    saveFileState_(stateKey, {
      signature: currentSignature,
      status: 'normalized'
    });
    Logger.log('[SKIP] already normalized: %s', oldName);
    return { status: 'skipped' };
  }

  if (!isSupportedMimeType_(mimeType, oldName)) {
    saveFileState_(stateKey, {
      signature: currentSignature,
      status: 'unsupported'
    });
    Logger.log('[SKIP] unsupported type: %s (%s)', oldName, mimeType);
    return { status: 'skipped' };
  }

  const extractedText = extractText_(file, mimeType, oldName);
  if (!extractedText || extractedText.trim().length < 30) {
    saveFileState_(stateKey, {
      signature: currentSignature,
      status: 'no_text'
    });
    Logger.log('[SKIP] no usable text: %s', oldName);
    return { status: 'skipped' };
  }

  Utilities.sleep(CONFIG.pauseMsBetweenAiCalls);
  const metadata = requestMetadataFromGemini_(extractedText, oldName);

  const creator = getCreatorLabel_(file);
  const extension = getOriginalExtension_(oldName, mimeType);
  const newName = buildNormalizedName_(creator, metadata, extension);

  if (newName === oldName) {
    saveFileState_(stateKey, {
      signature: currentSignature,
      status: 'same_name'
    });
    Logger.log('[SKIP] same name: %s', oldName);
    return { status: 'skipped' };
  }

  if (isDryRun) {
    saveFileState_(stateKey, {
      signature: currentSignature,
      status: 'previewed',
      newName: newName
    });
    Logger.log('[PREVIEW] %s -> %s', oldName, newName);
    return { status: 'renamed' };
  }

  file.setName(newName);
  saveFileState_(stateKey, {
    signature: getFileSignature_(file),
    status: 'renamed',
    newName: newName
  });
  Logger.log('[RENAMED] %s -> %s', oldName, newName);
  return { status: 'renamed' };
}

function extractText_(file, mimeType, oldName) {
  if (mimeType === MimeType.GOOGLE_DOCS) {
    return DocumentApp.openById(file.getId()).getBody().getText();
  }

  if (isDocx_(mimeType, oldName)) {
    return extractTextViaDriveImport_(file, oldName, false);
  }

  if (isDoc_(mimeType, oldName)) {
    return extractTextViaDriveImport_(file, oldName, false);
  }

  if (mimeType === MimeType.PDF || isImage_(mimeType, oldName)) {
    return extractTextViaDriveImport_(file, oldName, true);
  }

  return '';
}

function extractTextViaDriveImport_(file, oldName, enableOcr) {
  let tempDocId = null;

  try {
    const resource = {
      title: 'tmp_extract_' + new Date().getTime(),
      parents: [{ id: CONFIG.folderId }]
    };

    const options = {
      convert: true
    };

    if (enableOcr) {
      options.ocr = true;
      options.ocrLanguage = 'ru';
    }

    const imported = Drive.Files.insert(resource, file.getBlob(), options);
    tempDocId = imported.id;

    const text = DocumentApp.openById(tempDocId).getBody().getText();
    return text || '';
  } catch (error) {
    throw new Error('text extraction failed for "' + oldName + '": ' + error);
  } finally {
    if (tempDocId) {
      try {
        DriveApp.getFileById(tempDocId).setTrashed(true);
      } catch (cleanupError) {
        Logger.log('[WARN] temp cleanup failed for %s: %s', oldName, cleanupError);
      }
    }
  }
}

function requestMetadataFromGemini_(text, oldName) {
  const url =
    'https://generativelanguage.googleapis.com/v1beta/models/' +
    encodeURIComponent(CONFIG.geminiModel) +
    ':generateContent?key=' +
    encodeURIComponent(CONFIG.geminiApiKey);

  const prompt =
    'Проанализируй текст документа компании. ' +
    'Верни строго одну строку без markdown в формате ' +
    'ТипДокумента|Дата|Тег1|Тег2.\n\n' +
    'Правила:\n' +
    '1. Тип документа: 1-2 слова.\n' +
    '2. Дата: YYYY-MM-DD, если есть точная дата; YYYY, если известен только год; Текущий, если даты нет.\n' +
    '3. Теги: выбери ровно два разных тега только из списка [' +
    CONFIG.allowedTags.join(', ') +
    '].\n' +
    '4. Не добавляй пояснений.\n\n' +
    'Имя файла: ' +
    oldName +
    '\n\n' +
    'Текст:\n' +
    text.substring(0, CONFIG.textPreviewLimit);

  const payload = {
    contents: [
      {
        parts: [{ text: prompt }]
      }
    ]
  };

  let lastError = null;

  for (let attempt = 1; attempt <= CONFIG.geminiRetryCount; attempt += 1) {
    const response = UrlFetchApp.fetch(url, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    const body = response.getContentText();
    const statusCode = response.getResponseCode();

    if (statusCode >= 200 && statusCode < 300) {
      const parsed = JSON.parse(body);
      const rawText =
        parsed &&
        parsed.candidates &&
        parsed.candidates[0] &&
        parsed.candidates[0].content &&
        parsed.candidates[0].content.parts &&
        parsed.candidates[0].content.parts[0] &&
        parsed.candidates[0].content.parts[0].text;

      if (!rawText) {
        throw new Error('Gemini returned empty content for "' + oldName + '"');
      }

      const cleanText = rawText.replace(/[`"']/g, '').trim();
      const parts = cleanText.split('|');
      if (parts.length !== 4) {
        throw new Error('Gemini returned invalid format for "' + oldName + '": ' + cleanText);
      }

      const metadata = {
        docType: sanitizePart_(parts[0]),
        date: normalizeDatePart_(parts[1]),
        tag1: sanitizePart_(parts[2]),
        tag2: sanitizePart_(parts[3])
      };

      if (!isAllowedTag_(metadata.tag1) || !isAllowedTag_(metadata.tag2) || metadata.tag1 === metadata.tag2) {
        throw new Error('Gemini returned invalid tags for "' + oldName + '": ' + cleanText);
      }

      return metadata;
    }

    lastError = new Error('Gemini HTTP ' + statusCode + ': ' + body);

    if (statusCode === 429 && body.indexOf('GenerateRequestsPerDayPerProjectPerModel-FreeTier') !== -1) {
      saveQuotaState_(oldName, body);
      throw new Error('QUOTA_EXCEEDED: ' + body);
    }

    if ((statusCode === 429 || statusCode === 503) && attempt < CONFIG.geminiRetryCount) {
      Logger.log('[WARN] Gemini retry %s for %s after HTTP %s', attempt, oldName, statusCode);
      Utilities.sleep(CONFIG.geminiRetryDelayMs * attempt);
      continue;
    }

    throw lastError;
  }

  throw lastError || new Error('Gemini request failed for "' + oldName + '"');
}

function getCreatorLabel_(file) {
  try {
    const owner = file.getOwner();
    if (!owner) {
      return 'Сотрудник';
    }

    const label = owner.getName() || owner.getEmail().split('@')[0] || 'Сотрудник';
    return sanitizePart_(label);
  } catch (error) {
    return 'Сотрудник';
  }
}

function buildNormalizedName_(creator, metadata, extension) {
  const parts = [creator, metadata.docType, metadata.date, metadata.tag1, metadata.tag2];
  const baseName = parts.map(sanitizePart_).join('_');
  return baseName + extension;
}

function sanitizePart_(value) {
  return String(value || '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\u0400-\u04FF.-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^[-_.]+|[-_.]+$/g, '') || 'Пусто';
}

function normalizeDatePart_(value) {
  const text = String(value || '').trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(text)) {
    return text;
  }
  if (/^\d{4}$/.test(text)) {
    return text;
  }
  return 'Текущий';
}

function isAllowedTag_(tag) {
  return CONFIG.allowedTags.indexOf(tag) !== -1;
}

function getOriginalExtension_(oldName, mimeType) {
  const match = oldName.match(/(\.[^.]+)$/);
  if (match) {
    return match[1];
  }

  if (mimeType === MimeType.GOOGLE_DOCS) {
    return '';
  }
  if (mimeType === MimeType.PDF) {
    return '.pdf';
  }
  if (mimeType === MimeType.PNG) {
    return '.png';
  }
  if (mimeType === MimeType.JPEG) {
    return '.jpg';
  }
  if (mimeType === MimeType.GIF) {
    return '.gif';
  }
  return '';
}

function isSupportedMimeType_(mimeType, oldName) {
  return (
    mimeType === MimeType.GOOGLE_DOCS ||
    mimeType === MimeType.PDF ||
    isDocx_(mimeType, oldName) ||
    isDoc_(mimeType, oldName) ||
    (CONFIG.processImages && isImage_(mimeType, oldName))
  );
}

function isDocx_(mimeType, oldName) {
  return mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || /\.docx$/i.test(oldName);
}

function isDoc_(mimeType, oldName) {
  return mimeType === MimeType.MICROSOFT_WORD || /\.doc$/i.test(oldName);
}

function isImage_(mimeType, oldName) {
  return mimeType === MimeType.PNG || mimeType === MimeType.JPEG || mimeType === MimeType.GIF || /\.(png|jpe?g|gif)$/i.test(oldName);
}

function isAlreadyNormalized_(fileName) {
  return CONFIG.normalizedPrefixPattern.test(fileName);
}

function shouldSkipCachedState_(status) {
  return ['renamed', 'normalized', 'unsupported', 'no_text', 'same_name'].indexOf(status) !== -1;
}

function getFileStateKey_(file) {
  return CONFIG.statePrefix + file.getId();
}

function getFileSignature_(file) {
  return [file.getName(), file.getLastUpdated().getTime(), file.getSize()].join('|');
}

function readFileState_(stateKey) {
  const raw = PropertiesService.getScriptProperties().getProperty(stateKey);
  return raw ? JSON.parse(raw) : null;
}

function saveFileState_(stateKey, value) {
  PropertiesService.getScriptProperties().setProperty(stateKey, JSON.stringify(value));
}

function saveQuotaState_(oldName, body) {
  PropertiesService.getScriptProperties().setProperty(
    CONFIG.statePrefix + 'quota_last',
    JSON.stringify({
      name: oldName,
      at: new Date().toISOString(),
      body: body
    })
  );
}

function isQuotaError_(error) {
  return String(error && error.message || error).indexOf('QUOTA_EXCEEDED:') !== -1;
}

function validateConfig_() {
  if (!CONFIG.folderId || CONFIG.folderId === 'PASTE_FOLDER_ID_HERE') {
    throw new Error('CONFIG.folderId is not set');
  }

  if (!CONFIG.geminiApiKey || CONFIG.geminiApiKey === 'PASTE_GEMINI_API_KEY_HERE') {
    throw new Error('CONFIG.geminiApiKey is not set');
  }

  if (typeof Drive === 'undefined' || !Drive.Files || typeof Drive.Files.insert !== 'function') {
    throw new Error('Enable Advanced Google Services: Drive API');
  }
}
