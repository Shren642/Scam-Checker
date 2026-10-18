// Scam-Check Web Application & WhatsApp Simulator Script
// Implements Senior Accessibility, Dynamic Multilingual Switching & Step-by-Step Recovery

document.addEventListener('DOMContentLoaded', async () => {
  // Elements
  const languageSelect = document.getElementById('languageSelect');
  const btnFontNormal = document.getElementById('btnFontNormal');
  const btnFontLarge = document.getElementById('btnFontLarge');
  const btnFontXLarge = document.getElementById('btnFontXLarge');
  const btnSettingsGuide = document.getElementById('btnSettingsGuide');
  const lblYoureNotAlone = document.getElementById('lblYoureNotAlone');

  // Tabs / Action Cards
  const tabText = document.getElementById('tabText');
  const tabImage = document.getElementById('tabImage');
  const tabVoice = document.getElementById('tabVoice');
  const paneText = document.getElementById('paneText');
  const paneImage = document.getElementById('paneImage');
  const paneVoice = document.getElementById('paneVoice');

  // Inputs
  const messageInput = document.getElementById('messageInput');
  const btnAttachImage = document.getElementById('btnAttachImage');
  const imageInput = document.getElementById('imageInput');
  const imageDropzone = document.getElementById('imageDropzone');
  const imagePreviewContainer = document.getElementById('imagePreviewContainer');
  const imagePreview = document.getElementById('imagePreview');
  const btnRemoveImage = document.getElementById('btnRemoveImage');

  // Voice Recording
  const btnRecordToggle = document.getElementById('btnRecordToggle');
  const recordBtnText = document.getElementById('recordBtnText');
  const recordStatus = document.getElementById('recordStatus');
  const audioPlayback = document.getElementById('audioPlayback');

  // Actions
  const btnCheckNow = document.getElementById('btnCheckNow');
  const btnClearForm = document.getElementById('btnClearForm');
  const loadingState = document.getElementById('loadingState');

  // Results Card
  const resultPlaceholder = document.getElementById('resultPlaceholder');
  const resultCard = document.getElementById('resultCard');
  const resultRiskBanner = document.getElementById('resultRiskBanner');
  const resultBadgeIcon = document.getElementById('resultBadgeIcon');
  const resultTitle = document.getElementById('resultTitle');
  const resultRiskBadge = document.getElementById('resultRiskBadge');
  const resultScamType = document.getElementById('resultScamType');
  const btnListenAdvice = document.getElementById('btnListenAdvice');
  const listenBtnLabel = document.getElementById('listenBtnLabel');
  const whyHeaderIcon = document.getElementById('whyHeaderIcon');
  const resultWhyHdr = document.getElementById('resultWhyHdr');
  const resultWhySubtitle = document.getElementById('resultWhySubtitle');
  const resultWhyList = document.getElementById('resultWhyList');
  const doHeaderIcon = document.getElementById('doHeaderIcon');
  const resultDoHdr = document.getElementById('resultDoHdr');
  const resultDoList = document.getElementById('resultDoList');
  const resultDontBox = document.getElementById('resultDontBox');
  const resultDontHdr = document.getElementById('resultDontHdr');
  const resultDontList = document.getElementById('resultDontList');
  const resultReassuranceBox = document.getElementById('resultReassuranceBox');
  const resultReassurance = document.getElementById('resultReassurance');
  const legitResetBar = document.getElementById('legitResetBar');
  const btnCheckAnotherLegitText = document.getElementById('btnCheckAnotherLegitText');

  // Step-by-Step Recovery Elements
  const alreadyActedPromptBox = document.getElementById('alreadyActedPromptBox');
  const btnAlreadyYes = document.getElementById('btnAlreadyYes');
  const btnAlreadyNo = document.getElementById('btnAlreadyNo');
  const noActionBox = document.getElementById('noActionBox');
  const btnCheckAnotherNoAction = document.getElementById('btnCheckAnotherNoAction');

  const recoverySelectBox = document.getElementById('recoverySelectBox');
  const btnRecoveryVoice = document.getElementById('btnRecoveryVoice');
  const recoveryVoiceStatus = document.getElementById('recoveryVoiceStatus');
  const lblRecoverySpeak = document.getElementById('lblRecoverySpeak');
  const somethingElseBox = document.getElementById('somethingElseBox');
  const somethingElseInput = document.getElementById('somethingElseInput');
  const btnSubmitSomethingElse = document.getElementById('btnSubmitSomethingElse');

  const targetedAdviceBox = document.getElementById('targetedAdviceBox');
  const targetedAdviceTitle = document.getElementById('targetedAdviceTitle');
  const targetedAdvicePoints = document.getElementById('targetedAdvicePoints');
  const lblHelplineTitle = document.getElementById('lblHelplineTitle');
  const lblHelplineBank = document.getElementById('lblHelplineBank');
  const lblHelplineFraud = document.getElementById('lblHelplineFraud');
  const lblHelplinePolice = document.getElementById('lblHelplinePolice');
  const btnBackToRecovery = document.getElementById('btnBackToRecovery');
  const btnCheckAnotherFromAdvice = document.getElementById('btnCheckAnotherFromAdvice');

  // Guide Modal
  const guideModal = document.getElementById('guideModal');
  const btnCloseGuide = document.getElementById('btnCloseGuide');
  const guideContentBox = document.getElementById('guideContentBox');
  const guideTabBtns = document.querySelectorAll('.guide-tab-btn');

  // State
  let activeTab = 'text';
  let recordedAudioBlob = null;
  let mediaRecorder = null;
  let audioChunks = [];
  let isRecording = false;
  let isRecoveryRecording = false;
  let recoveryMediaRecorder = null;
  let recoveryAudioChunks = [];
  let currentSpeechUtterance = null;
  let currentTtsText = '';
  let currentTranslations = {};

  // Load current translations from server
  async function loadTranslations(lang) {
    try {
      const res = await fetch(`/api/translations?lang=${lang}`);
      const data = await res.json();
      if (data.success) {
        currentTranslations = data.translations;
      }
    } catch (e) {
      console.error('Error loading translations:', e);
    }
  }

  await loadTranslations(languageSelect.value);

  // 1. Accessibility: Font Size Switcher
  function setFontSize(sizeClass) {
    document.body.classList.remove('font-size-normal', 'font-size-large', 'font-size-xlarge');
    document.body.classList.add(sizeClass);
    btnFontNormal.classList.toggle('active', sizeClass === 'font-size-normal');
    btnFontLarge.classList.toggle('active', sizeClass === 'font-size-large');
    btnFontXLarge.classList.toggle('active', sizeClass === 'font-size-xlarge');
    localStorage.setItem('scamCheckFontSize', sizeClass);
  }

  btnFontNormal.addEventListener('click', () => setFontSize('font-size-normal'));
  btnFontLarge.addEventListener('click', () => setFontSize('font-size-large'));
  btnFontXLarge.addEventListener('click', () => setFontSize('font-size-xlarge'));

  const savedFont = localStorage.getItem('scamCheckFontSize');
  if (savedFont) setFontSize(savedFont);

  // Settings / Help Guide Trigger
  if (btnSettingsGuide) {
    btnSettingsGuide.addEventListener('click', () => {
      guideModal.classList.remove('hidden');
      showGuideTab('message');
    });
  }

  if (lblYoureNotAlone) {
    lblYoureNotAlone.addEventListener('click', (e) => {
      e.preventDefault();
      guideModal.classList.remove('hidden');
      showGuideTab('message');
    });
  }

  // 2. Language Switcher: Full immediate interface language change
  languageSelect.addEventListener('change', async (e) => {
    const selectedLang = e.target.value;
    try {
      const res = await fetch('/api/set-language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: selectedLang })
      });
      const data = await res.json();
      if (data.success) {
        currentTranslations = data.translations;
        // Reload page to allow clean server-side rendering of all templates in selected language
        window.location.reload();
      }
    } catch (err) {
      console.error('Error setting language:', err);
      window.location.reload();
    }
  });

  // 3. Tab Switching
  function switchTab(tabName) {
    activeTab = tabName;
    tabText.classList.toggle('active', tabName === 'text');
    tabImage.classList.toggle('active', tabName === 'image');
    tabVoice.classList.toggle('active', tabName === 'voice');

    paneText.classList.toggle('hidden', tabName !== 'text');
    paneImage.classList.toggle('hidden', tabName !== 'image');
    paneVoice.classList.toggle('hidden', tabName !== 'voice');
  }

  tabText.addEventListener('click', () => switchTab('text'));
  tabImage.addEventListener('click', () => switchTab('image'));
  tabVoice.addEventListener('click', () => switchTab('voice'));

  // Quick attachment icon on textarea
  if (btnAttachImage) {
    btnAttachImage.addEventListener('click', () => {
      switchTab('image');
      imageInput.click();
    });
  }

  // 4. Quick Scenario Chips (Uses localized sample text from currentTranslations)
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const scenarioKey = btn.dataset.scenario;
      const sampleKey = `sample_text_${scenarioKey}`;
      const sampleText = currentTranslations[sampleKey];
      if (sampleText) {
        switchTab('text');
        messageInput.value = sampleText;
        messageInput.focus();
        btnCheckNow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        // Automatically run check for instant responsiveness
        btnCheckNow.click();
      }
    });
  });

  // 5. Image Dropzone & Preview
  imageDropzone.addEventListener('click', () => imageInput.click());

  imageDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    imageDropzone.classList.add('drag-over');
  });

  imageDropzone.addEventListener('dragleave', () => {
    imageDropzone.classList.remove('drag-over');
  });

  imageDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    imageDropzone.classList.remove('drag-over');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageSelected(e.dataTransfer.files[0]);
    }
  });

  imageInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleImageSelected(e.target.files[0]);
    }
  });

  function handleImageSelected(file) {
    if (!file.type.startsWith('image/')) {
      alert(currentTranslations['dropzone_formats'] || 'Please choose an image file (PNG, JPG, WEBP).');
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      imagePreviewContainer.classList.remove('hidden');
      imageDropzone.classList.add('hidden');
    };
    reader.readAsDataURL(file);
  }

  btnRemoveImage.addEventListener('click', () => {
    imageInput.value = '';
    imagePreview.src = '';
    imagePreviewContainer.classList.add('hidden');
    imageDropzone.classList.remove('hidden');
  });

  // 6. Voice Recording (Microphone via MediaRecorder for Main Checker)
  btnRecordToggle.addEventListener('click', async () => {
    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
          recordedAudioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          const audioUrl = URL.createObjectURL(recordedAudioBlob);
          audioPlayback.src = audioUrl;
          audioPlayback.classList.remove('hidden');
          recordStatus.textContent = currentTranslations['voice_status_saved'] || 'Voice recording saved! Press Check This Now.';
        };

        mediaRecorder.start();
        isRecording = true;
        btnRecordToggle.classList.add('recording');
        recordBtnText.textContent = currentTranslations['voice_stop_btn'] || '⏹️ Stop Recording';
        recordStatus.textContent = currentTranslations['voice_status_listening'] || 'Listening... Speak clearly.';
      } catch (err) {
        console.error('Microphone error:', err);
        recordStatus.textContent = currentTranslations['voice_status_error'] || 'Microphone access denied. Please type.';
      }
    } else {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
      }
      isRecording = false;
      btnRecordToggle.classList.remove('recording');
      recordBtnText.textContent = currentTranslations['voice_record_again_btn'] || '🎤 Record Again';
    }
  });

  // 7. Clear Form & Reset State
  function resetAll() {
    messageInput.value = '';
    imageInput.value = '';
    imagePreview.src = '';
    imagePreviewContainer.classList.add('hidden');
    imageDropzone.classList.remove('hidden');
    recordedAudioBlob = null;
    audioPlayback.src = '';
    audioPlayback.classList.add('hidden');
    recordStatus.textContent = currentTranslations['voice_status_ready'] || 'Microphone ready.';
    recordBtnText.textContent = currentTranslations['voice_record_btn'] || 'Tap to start speaking';
    stopTextToSpeech();

    // Reset results to legitimate default card
    displayDefaultLegitResult();
    messageInput.focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function displayDefaultLegitResult() {
    resultCard.classList.remove('hidden');
    resultPlaceholder.classList.add('hidden');
    resultRiskBanner.className = 'risk-status-card risk-green';
    resultBadgeIcon.textContent = '✓';
    resultTitle.textContent = currentTranslations['risk_legitimate'] || 'PROBABLY LEGITIMATE';
    if (resultRiskBadge) {
      resultRiskBadge.textContent = currentTranslations['risk_low_badge'] || 'LOW RISK';
      resultRiskBadge.className = 'risk-pill-badge badge-green';
    }
    resultScamType.classList.add('hidden');

    // Why box (Legit)
    if (whyHeaderIcon) whyHeaderIcon.textContent = 'ℹ️';
    resultWhyHdr.textContent = currentTranslations['legit_no_signs_found'] || 'No obvious scam signs were found.';
    if (resultWhySubtitle) {
      resultWhySubtitle.textContent = currentTranslations['legit_desc'] || "This looks like a genuine message, but it's always good to be careful.";
      resultWhySubtitle.classList.remove('hidden');
    }
    resultWhyList.classList.add('hidden');

    // Do box (Legit)
    if (doHeaderIcon) doHeaderIcon.textContent = '✓';
    resultDoHdr.textContent = currentTranslations['legit_before_acting'] || 'Before acting:';
    resultDoList.innerHTML = `
      <li>${currentTranslations['legit_check_sender'] || 'Check the sender (name and number or email address).'}</li>
      <li>${currentTranslations['legit_official_app'] || "Use the organisation's official app or website."}</li>
      <li>${currentTranslations['legit_never_share_otp'] || 'Never share your OTP or PIN.'}</li>
    `;

    resultDontBox.classList.add('hidden');
    alreadyActedPromptBox.classList.add('hidden');
    noActionBox.classList.add('hidden');
    recoverySelectBox.classList.add('hidden');
    targetedAdviceBox.classList.add('hidden');
    somethingElseBox.classList.add('hidden');
    legitResetBar.classList.remove('hidden');
  }

  btnClearForm.addEventListener('click', resetAll);
  if (legitResetBar) legitResetBar.addEventListener('click', resetAll);
  if (btnCheckAnotherNoAction) btnCheckAnotherNoAction.addEventListener('click', resetAll);
  if (btnCheckAnotherFromAdvice) btnCheckAnotherFromAdvice.addEventListener('click', resetAll);

  // 8. Submit Check
  btnCheckNow.addEventListener('click', async () => {
    const text = messageInput.value.trim();
    const hasImage = imageInput.files && imageInput.files[0];
    const hasAudio = recordedAudioBlob != null;

    if (!text && !hasImage && !hasAudio) {
      alert(currentTranslations['input_message_hint'] || 'Please enter a message, upload a screenshot, or record voice.');
      return;
    }

    loadingState.classList.remove('hidden');
    resultCard.classList.add('hidden');
    alreadyActedPromptBox.classList.add('hidden');
    noActionBox.classList.add('hidden');
    recoverySelectBox.classList.add('hidden');
    targetedAdviceBox.classList.add('hidden');
    legitResetBar.classList.add('hidden');
    btnCheckNow.disabled = true;
    stopTextToSpeech();

    const formData = new FormData();
    formData.append('lang', languageSelect.value);
    if (text) formData.append('text', text);
    if (hasImage) formData.append('image', imageInput.files[0]);
    if (hasAudio) formData.append('audio', recordedAudioBlob, 'voice_recording.wav');

    try {
      const response = await fetch('/api/check', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();

      if (data.success) {
        displayResults(data.analysis, data.tts_text);
      } else {
        alert(data.error || currentTranslations['fallback_error'] || 'Could not analyse message.');
        displayDefaultLegitResult();
      }
    } catch (err) {
      console.error('Error during scam check:', err);
      alert(currentTranslations['fallback_error'] || 'Network error. Please try again.');
      displayDefaultLegitResult();
    } finally {
      loadingState.classList.add('hidden');
      btnCheckNow.disabled = false;
    }
  });

  // 9. Display Analysis Results (Strictly enforces conditional rendering)
  function displayResults(analysis, ttsText) {
    resultCard.classList.remove('hidden');
    resultPlaceholder.classList.add('hidden');

    currentTtsText = ttsText || '';
    const risk = analysis.risk_level || 'suspicious';
    resultRiskBanner.classList.remove('risk-red', 'risk-amber', 'risk-green');

    // Hide all recovery containers initially
    alreadyActedPromptBox.classList.add('hidden');
    noActionBox.classList.add('hidden');
    recoverySelectBox.classList.add('hidden');
    targetedAdviceBox.classList.add('hidden');
    somethingElseBox.classList.add('hidden');
    legitResetBar.classList.add('hidden');

    if (risk === 'very_likely_scam') {
      resultRiskBanner.className = 'risk-status-card risk-red';
      resultBadgeIcon.textContent = '🚨';
      resultTitle.textContent = currentTranslations['risk_very_likely'] || 'VERY LIKELY A SCAM';
      if (resultRiskBadge) {
        resultRiskBadge.textContent = currentTranslations['risk_high_badge'] || 'HIGH RISK';
        resultRiskBadge.className = 'risk-pill-badge badge-red';
      }
      resultScamType.classList.remove('hidden');
      resultScamType.textContent = (analysis.scam_type || 'General Review').replace(/_/g, ' ').toUpperCase();

      // Why box
      if (whyHeaderIcon) whyHeaderIcon.textContent = '⚠️';
      resultWhyHdr.textContent = currentTranslations['why_heading'] || 'Why it looks suspicious:';
      if (resultWhySubtitle) resultWhySubtitle.classList.add('hidden');
      resultWhyList.classList.remove('hidden');
      resultWhyList.innerHTML = '';
      (analysis.why || []).forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        resultWhyList.appendChild(li);
      });

      // Do box
      if (doHeaderIcon) doHeaderIcon.textContent = '🛡️';
      resultDoHdr.textContent = currentTranslations['do_now_heading'] || 'What to do:';
      resultDoList.innerHTML = '';
      (analysis.do_now || []).forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        resultDoList.appendChild(li);
      });

    } else if (risk === 'suspicious') {
      resultRiskBanner.className = 'risk-status-card risk-amber';
      resultBadgeIcon.textContent = '⚠️';
      resultTitle.textContent = currentTranslations['risk_suspicious'] || 'SUSPICIOUS';
      if (resultRiskBadge) {
        resultRiskBadge.textContent = currentTranslations['risk_medium_badge'] || 'MEDIUM RISK';
        resultRiskBadge.className = 'risk-pill-badge badge-amber';
      }
      resultScamType.classList.remove('hidden');
      resultScamType.textContent = (analysis.scam_type || 'General Review').replace(/_/g, ' ').toUpperCase();

      // Why box
      if (whyHeaderIcon) whyHeaderIcon.textContent = '⚠️';
      resultWhyHdr.textContent = currentTranslations['why_heading'] || 'Warning signs:';
      if (resultWhySubtitle) resultWhySubtitle.classList.add('hidden');
      resultWhyList.classList.remove('hidden');
      resultWhyList.innerHTML = '';
      (analysis.why || []).forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        resultWhyList.appendChild(li);
      });

      // Do box
      if (doHeaderIcon) doHeaderIcon.textContent = '🛡️';
      resultDoHdr.textContent = currentTranslations['do_now_heading'] || 'What to do:';
      resultDoList.innerHTML = '';
      (analysis.do_now || []).forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        resultDoList.appendChild(li);
      });

    } else {
      // Legitimate
      resultRiskBanner.className = 'risk-status-card risk-green';
      resultBadgeIcon.textContent = '✓';
      resultTitle.textContent = currentTranslations['risk_legitimate'] || 'PROBABLY LEGITIMATE';
      if (resultRiskBadge) {
        resultRiskBadge.textContent = currentTranslations['risk_low_badge'] || 'LOW RISK';
        resultRiskBadge.className = 'risk-pill-badge badge-green';
      }
      resultScamType.classList.add('hidden');

      // Why box (Legit: Calm info card)
      if (whyHeaderIcon) whyHeaderIcon.textContent = 'ℹ️';
      resultWhyHdr.textContent = currentTranslations['legit_no_signs_found'] || 'No obvious scam signs were found.';
      if (resultWhySubtitle) {
        resultWhySubtitle.textContent = currentTranslations['legit_desc'] || "This looks like a genuine message, but it's always good to be careful.";
        resultWhySubtitle.classList.remove('hidden');
      }
      resultWhyList.classList.add('hidden');

      // Do box (Legit: Before acting)
      if (doHeaderIcon) doHeaderIcon.textContent = '✓';
      resultDoHdr.textContent = currentTranslations['legit_before_acting'] || 'Before acting:';
      resultDoList.innerHTML = `
        <li>${currentTranslations['legit_check_sender'] || 'Check the sender (name and number or email address).'}</li>
        <li>${currentTranslations['legit_official_app'] || "Use the organisation's official app or website."}</li>
        <li>${currentTranslations['legit_never_share_otp'] || 'Never share your OTP or PIN.'}</li>
      `;
    }

    // Conditional: What NOT to do (Must be HIDDEN for legitimate notices)
    const showWhatNotToDo = Boolean(analysis.show_what_not_to_do && analysis.do_not_do && analysis.do_not_do.length > 0);
    if (showWhatNotToDo) {
      resultDontList.innerHTML = '';
      analysis.do_not_do.forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        resultDontList.appendChild(li);
      });
      resultDontBox.classList.remove('hidden');
    } else {
      resultDontBox.classList.add('hidden');
    }

    // Conditional: "Have you already sent something?" (Must be HIDDEN for legitimate notices)
    const showAlreadyActed = Boolean(analysis.show_already_acted);
    if (showAlreadyActed) {
      alreadyActedPromptBox.classList.remove('hidden');
      legitResetBar.classList.add('hidden');
    } else {
      alreadyActedPromptBox.classList.add('hidden');
      legitResetBar.classList.remove('hidden');
    }

    // Scroll smoothly to results
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // 10. Text-to-Speech: "Hear this advice"
  btnListenAdvice.addEventListener('click', () => {
    if ('speechSynthesis' in window) {
      if (window.speechSynthesis.speaking) {
        stopTextToSpeech();
        return;
      }

      if (!currentTtsText) {
        currentTtsText = `${resultTitle.textContent}. ${resultWhyHdr.textContent}. ${resultDoHdr.textContent}. ${resultDoList.innerText}`;
      }

      currentSpeechUtterance = new SpeechSynthesisUtterance(currentTtsText);
      currentSpeechUtterance.rate = 0.9;
      currentSpeechUtterance.pitch = 1.0;

      const langMapping = {
        en: 'en-GB',
        pa: 'pa-IN',
        pl: 'pl-PL',
        ro: 'ro-RO',
        pt: 'pt-PT'
      };
      currentSpeechUtterance.lang = langMapping[languageSelect.value] || 'en-GB';

      currentSpeechUtterance.onstart = () => {
        listenBtnLabel.textContent = currentTranslations['stop_audio_btn'] || 'Stop reading';
      };

      currentSpeechUtterance.onend = () => {
        listenBtnLabel.textContent = currentTranslations['hear_advice_btn'] || 'Hear this advice';
      };

      currentSpeechUtterance.onerror = () => {
        listenBtnLabel.textContent = currentTranslations['hear_advice_btn'] || 'Hear this advice';
      };

      window.speechSynthesis.speak(currentSpeechUtterance);
    } else {
      alert('Read-aloud feature is not supported in this browser.');
    }
  });

  btnListenAdvice.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      btnListenAdvice.click();
    }
  });

  function stopTextToSpeech() {
    if ('speechSynthesis' in window && window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      listenBtnLabel.textContent = currentTranslations['hear_advice_btn'] || 'Hear this advice';
    }
  }

  // 11. STEP-BY-STEP RECOVERY FLOW HANDLERS

  // User clicked NO -> Safe! Show brief reassurance & reset
  btnAlreadyNo.addEventListener('click', () => {
    alreadyActedPromptBox.classList.add('hidden');
    recoverySelectBox.classList.add('hidden');
    targetedAdviceBox.classList.add('hidden');
    noActionBox.classList.remove('hidden');
    noActionBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });

  // User clicked YES -> Reveal "What did you send or do?" options
  btnAlreadyYes.addEventListener('click', () => {
    alreadyActedPromptBox.classList.add('hidden');
    noActionBox.classList.add('hidden');
    targetedAdviceBox.classList.add('hidden');
    recoverySelectBox.classList.remove('hidden');
    recoverySelectBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });

  // User clicks one of the 8 options
  document.querySelectorAll('.recovery-option-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const category = btn.dataset.cat;
      if (category === 'something_else') {
        somethingElseBox.classList.remove('hidden');
        somethingElseInput.focus();
        somethingElseBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        await loadTargetedAdvice(category);
      }
    });
  });

  // Submit custom text for "Something else"
  btnSubmitSomethingElse.addEventListener('click', async () => {
    const text = somethingElseInput.value.trim();
    await loadTargetedAdvice('something_else', text);
  });

  // Voice recording inside recovery flow: "Tell me what you sent"
  btnRecoveryVoice.addEventListener('click', async () => {
    if (!isRecoveryRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recoveryMediaRecorder = new MediaRecorder(stream);
        recoveryAudioChunks = [];

        recoveryMediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) recoveryAudioChunks.push(event.data);
        };

        recoveryMediaRecorder.onstop = async () => {
          const blob = new Blob(recoveryAudioChunks, { type: 'audio/wav' });
          recoveryVoiceStatus.textContent = currentTranslations['loading_title'] || 'Processing voice...';
          
          const fd = new FormData();
          fd.append('audio', blob, 'recovery_voice.wav');
          fd.append('lang', languageSelect.value);

          try {
            const res = await fetch('/api/recovery-voice', { method: 'POST', body: fd });
            const data = await res.json();
            if (data.success) {
              displayTargetedAdvice(data.advice);
            } else {
              alert(data.error || 'Could not understand voice message.');
            }
          } catch (e) {
            console.error('Voice recovery error:', e);
          } finally {
            recoveryVoiceStatus.classList.add('hidden');
          }
        };

        recoveryMediaRecorder.start();
        isRecoveryRecording = true;
        btnRecoveryVoice.classList.add('recording');
        lblRecoverySpeak.textContent = currentTranslations['voice_stop_btn'] || '⏹️ Stop speaking';
        recoveryVoiceStatus.textContent = currentTranslations['voice_status_listening'] || 'Listening... Tell what was sent.';
        recoveryVoiceStatus.classList.remove('hidden');
      } catch (err) {
        console.error('Recovery mic error:', err);
        alert(currentTranslations['voice_status_error'] || 'Microphone access denied.');
      }
    } else {
      if (recoveryMediaRecorder && recoveryMediaRecorder.state !== 'inactive') {
        recoveryMediaRecorder.stop();
        recoveryMediaRecorder.stream.getTracks().forEach(track => track.stop());
      }
      isRecoveryRecording = false;
      btnRecoveryVoice.classList.remove('recording');
      lblRecoverySpeak.textContent = currentTranslations['recovery_speak_btn'] || '🎤 Tell me what you sent';
    }
  });

  // Fetch and display targeted advice for a specific category
  async function loadTargetedAdvice(category, text = '') {
    stopTextToSpeech();
    try {
      const res = await fetch('/api/recovery-advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: category,
          text: text,
          lang: languageSelect.value
        })
      });
      const data = await res.json();
      if (data.success) {
        displayTargetedAdvice(data.advice);
      }
    } catch (e) {
      console.error('Error fetching recovery advice:', e);
    }
  }

  function displayTargetedAdvice(advice) {
    recoverySelectBox.classList.add('hidden');
    targetedAdviceBox.classList.remove('hidden');

    targetedAdviceTitle.textContent = advice.title || 'ACT NOW';
    targetedAdvicePoints.innerHTML = '';
    (advice.points || []).forEach(p => {
      const li = document.createElement('li');
      li.textContent = p;
      targetedAdvicePoints.appendChild(li);
    });

    lblHelplineTitle.textContent = advice.official_contacts_title || '';
    lblHelplineBank.textContent = `• ${advice.official_bank_line || ''}`;
    lblHelplineFraud.textContent = `• ${advice.official_action_fraud || ''}`;
    lblHelplinePolice.textContent = `• ${advice.official_police_101 || ''}`;

    targetedAdviceBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Back button from targeted advice -> returns to selection options
  btnBackToRecovery.addEventListener('click', () => {
    targetedAdviceBox.classList.add('hidden');
    recoverySelectBox.classList.remove('hidden');
    recoverySelectBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });

  // 12. Guide Modal Instructions
  if (btnCloseGuide) {
    btnCloseGuide.addEventListener('click', () => {
      guideModal.classList.add('hidden');
    });
  }

  guideTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const guideKey = btn.dataset.guide;
      showGuideTab(guideKey);
    });
  });

  function showGuideTab(guideKey) {
    guideTabBtns.forEach(b => b.classList.toggle('active', b.dataset.guide === guideKey));
    
    // Build localized guide instructions from currentTranslations
    let content = '';
    if (guideKey === 'message') {
      content = `${currentTranslations['guide_msg_h'] || ''}\n\n1️⃣ ${currentTranslations['guide_msg_s1'] || ''}\n2️⃣ ${currentTranslations['guide_msg_s2'] || ''}\n3️⃣ ${currentTranslations['guide_msg_s3'] || ''}\n4️⃣ ${currentTranslations['guide_msg_s4'] || ''}\n5️⃣ ${currentTranslations['guide_msg_s5'] || ''}\n6️⃣ ${currentTranslations['guide_msg_s6'] || ''}\n\n${currentTranslations['guide_msg_tip'] || ''}`;
    } else if (guideKey === 'screenshot') {
      content = `${currentTranslations['guide_pic_h'] || ''}\n\n1️⃣ ${currentTranslations['guide_pic_s1'] || ''}\n2️⃣ ${currentTranslations['guide_pic_s2'] || ''}\n3️⃣ ${currentTranslations['guide_pic_s3'] || ''}\n4️⃣ ${currentTranslations['guide_pic_s4'] || ''}\n5️⃣ ${currentTranslations['guide_pic_s5'] || ''}\n6️⃣ ${currentTranslations['guide_pic_s6'] || ''}\n\n${currentTranslations['guide_pic_tip'] || ''}`;
    } else if (guideKey === 'voice') {
      content = `${currentTranslations['guide_mic_h'] || ''}\n\n1️⃣ ${currentTranslations['guide_mic_s1'] || ''}\n2️⃣ ${currentTranslations['guide_mic_s2'] || ''}\n3️⃣ ${currentTranslations['guide_mic_s3'] || ''}\n4️⃣ ${currentTranslations['guide_mic_s4'] || ''}\n\n${currentTranslations['guide_mic_tip'] || ''}`;
    } else if (guideKey === 'call') {
      content = `${currentTranslations['guide_phone_h'] || ''}\n\n${currentTranslations['guide_phone_notice'] || ''}\n\n1️⃣ ${currentTranslations['guide_phone_s1'] || ''}\n2️⃣ ${currentTranslations['guide_phone_s2'] || ''}\n3️⃣ ${currentTranslations['guide_phone_s3'] || ''}`;
    }
    guideContentBox.textContent = content;
  }
});
