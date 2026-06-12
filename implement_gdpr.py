#!/usr/bin/env python3
"""GDPR transparency layer — notice + opt-out model. Assertion-checked, CRLF-preserved, no backticks added."""

PATH = 'index.html'
src = open(PATH, encoding='utf-8', newline='').read()
BASE_BT = src.count('`')
N = lambda s: s.replace('\n', '\r\n')

def rep(old, new, label):
    global src
    old = N(old); new = N(new)
    assert src.count(old) == 1, f'{label}: anchor count {src.count(old)} != 1'
    src = src.replace(old, new)
    print(f'{label}: OK')

# 1. State defaults
rep("bypassedModules: [], leaderboardOptIn: false,",
    "bypassedModules: [], leaderboardOptIn: false, syncOptOut: false, privacyNoticeSeen: false,",
    'state defaults')

# 2. triggerSync gate (after the unavailable check, before any network call)
rep("""    if (syncEl) syncEl.textContent = t('sync_unavailable');
    return;
  }
""",
    """    if (syncEl) syncEl.textContent = t('sync_unavailable');
    return;
  }

  // UK-GDPR: student has opted out of cloud backup — nothing leaves the device
  if (state.syncOptOut) {
    if (syncEl) syncEl.textContent = t('sync_off_status');
    const stuEl = document.getElementById('sync-time-student');
    if (stuEl) stuEl.textContent = t('sync_off_status');
    return;
  }
""", 'triggerSync gate')

# 3. pullSync gate
rep("""async function pullSync() {
  const userId = currentUser?.sub;
  if (!userId) return;
""",
    """async function pullSync() {
  const userId = currentUser?.sub;
  if (!userId) return;
  if (state.syncOptOut) return; // UK-GDPR: opted out — no identifier transmitted
""", 'pullSync gate')

# 4. Login sequencing: privacy sheet first, then diagnostic
rep("""  if (_isNewStudent) {
    setTimeout(() => startDiagnostic(), 350);
  }
}
""",
    """  const _needsPrivacy = currentUser?.role === ROLES.STUDENT
    && !state.privacyNoticeSeen
    && !me?.mustChangePassword;
  if (_needsPrivacy) {
    window._pendingDiag = _isNewStudent;
    setTimeout(() => showPrivacySheet(), 600);
  } else if (_isNewStudent) {
    setTimeout(() => startDiagnostic(), 350);
  }
}
""", 'login sequencing')

# 5. applyUserSettings: restore toggle state on load
rep("  if (state.language) setLanguage(state.language);",
    """  if (state.language) setLanguage(state.language);
  updateSyncToggleUI();""", 'applyUserSettings hook')

# 6. JS functions (no template literals — backtick-safe)
rep("function showLBOptinSheet() {",
    """// ── Privacy notice & cloud-backup opt-out (UK-GDPR transparency) ──
function showPrivacySheet() {
  const sheet = document.getElementById('privacy-sheet');
  if (sheet) sheet.classList.add('show');
}
function dismissPrivacySheet() {
  const sheet = document.getElementById('privacy-sheet');
  if (sheet) sheet.classList.remove('show');
  if (!state.privacyNoticeSeen) { state.privacyNoticeSeen = true; saveState(); }
  if (window._pendingDiag) { window._pendingDiag = false; setTimeout(() => startDiagnostic(), 350); }
}
function privacySheetTurnOff() {
  state.syncOptOut = true; saveState();
  updateSyncToggleUI();
  showToast(t('backup_off_toast'));
  dismissPrivacySheet();
}
function togglePrivacySync() {
  state.syncOptOut = !state.syncOptOut; saveState();
  updateSyncToggleUI();
  showToast(state.syncOptOut ? t('backup_off_toast') : t('backup_on_toast'));
  if (!state.syncOptOut) triggerSync();
}
function updateSyncToggleUI() {
  const el = document.getElementById('toggle-sync');
  if (el) { el.classList.toggle('on', !state.syncOptOut); el.setAttribute('aria-checked', String(!state.syncOptOut)); }
}

function showLBOptinSheet() {""", 'JS functions')

# 7. CSS for the sheet (mirrors lb-optin-sheet, higher z-index)
rep("#lb-optin-sheet .sheet-card { position: relative; background: var(--surface); border-radius: 24px 24px 0 0; padding: 28px 24px 40px; display: flex; flex-direction: column; gap: 14px; max-height: 88vh; overflow-y: auto; }",
    """#lb-optin-sheet .sheet-card { position: relative; background: var(--surface); border-radius: 24px 24px 0 0; padding: 28px 24px 40px; display: flex; flex-direction: column; gap: 14px; max-height: 88vh; overflow-y: auto; }
#privacy-sheet { position: fixed; inset: 0; z-index: 230; display: flex; flex-direction: column; justify-content: flex-end; opacity: 0; pointer-events: none; transition: opacity 0.25s; }
#privacy-sheet.show { opacity: 1; pointer-events: all; }
#privacy-sheet .sheet-backdrop { position: absolute; inset: 0; background: rgba(0,0,0,0.5); }
#privacy-sheet .sheet-card { position: relative; background: var(--surface); border-radius: 24px 24px 0 0; padding: 28px 24px 40px; display: flex; flex-direction: column; gap: 12px; max-height: 88vh; overflow-y: auto; }""",
    'sheet CSS')

# 8. Sheet HTML (static, data-i18n throughout)
rep('<div id="lb-optin-sheet" role="dialog" aria-modal="true" aria-labelledby="lb-optin-title">',
    """<div id="privacy-sheet" role="dialog" aria-modal="true" aria-labelledby="privacy-sheet-title">
  <div class="sheet-backdrop" onclick="dismissPrivacySheet()"></div>
  <div class="sheet-card">
    <div style="font-size:32px;text-align:center" aria-hidden="true">🔒</div>
    <div id="privacy-sheet-title" style="font-size:18px;font-weight:800;color:var(--text);text-align:center" data-i18n="privacy_title">Your Data &amp; Cloud Backup</div>
    <div style="font-size:13.5px;color:var(--text2);line-height:1.55" data-i18n="privacy_intro">When you are online, Crypto-Course backs up your learning progress so your teacher can support you and the University of Westminster research team can evaluate the course.</div>
    <div style="font-size:13px;color:var(--text2);line-height:1.6">
      <strong data-i18n="privacy_what_lbl">What is saved</strong>: <span data-i18n="privacy_what">XP, streak, badge dates, quiz and lab results, module progress, and session length.</span><br>
      <strong data-i18n="privacy_not_lbl">Never saved</strong>: <span data-i18n="privacy_not">Your messages, your location, or details about your device.</span><br>
      <strong data-i18n="privacy_who_lbl">Who can see it</strong>: <span data-i18n="privacy_who">Only your teacher and the research team. Data is stored securely on Cloudflare infrastructure.</span><br>
      <strong data-i18n="privacy_keep_lbl">Kept until</strong>: <span data-i18n="privacy_keep">Deleted at the end of the semester.</span>
    </div>
    <div style="font-size:13px;color:var(--text2);line-height:1.55" data-i18n="privacy_rights">You can turn backup off at any time here or in your Profile, and you can ask for your data to be deleted at any time.</div>
    <div style="font-size:12.5px;color:var(--muted)"><span data-i18n="privacy_contact_lbl">Questions or deletion requests:</span> <span id="privacy-contact-email" style="font-weight:600">cryptocourse-privacy@westminster.ac.uk</span></div>
    <button class="btn btn-primary" onclick="dismissPrivacySheet()" data-i18n="got_it_check">Got it &#10003;</button>
    <button onclick="privacySheetTurnOff()" style="background:none;border:none;color:var(--muted);font-size:13px;cursor:pointer;font-family:var(--font);text-decoration:underline" data-i18n="turn_off_backup">Turn off backup</button>
  </div>
</div>
<div id="lb-optin-sheet" role="dialog" aria-modal="true" aria-labelledby="lb-optin-title">""",
    'sheet HTML')

# 9. Profile sync card: toggle row + privacy notice link
rep("""              <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
                <button class="btn btn-primary btn-sm" onclick="triggerSync()" style="width:auto" data-i18n="backup_now_btn">📤 Back up now</button>
                <div id="sync-time-student" style="font-size:12px;color:var(--muted)" data-i18n="checking">Checking…</div>
              </div>""",
    """              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
                <div style="font-size:13.5px;font-weight:600;color:var(--text)" data-i18n="sync_toggle_lbl">Cloud backup &amp; teacher sync</div>
                <button class="toggle on" id="toggle-sync" role="switch" aria-checked="true" aria-label="Cloud backup and teacher sync" onclick="togglePrivacySync()"></button>
              </div>
              <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
                <button class="btn btn-primary btn-sm" onclick="triggerSync()" style="width:auto" data-i18n="backup_now_btn">📤 Back up now</button>
                <div id="sync-time-student" style="font-size:12px;color:var(--muted)" data-i18n="checking">Checking…</div>
              </div>
              <button onclick="showPrivacySheet()" style="background:none;border:none;padding:0;color:var(--primary);font-size:12.5px;cursor:pointer;font-family:var(--font);text-decoration:underline;margin-bottom:4px" data-i18n="privacy_link">Privacy notice</button>""",
    'profile sync card')

# 10. i18n keys — EN
rep("    ph_search_modules: 'Search modules…',",
    """    ph_search_modules: 'Search modules…',
    // — Phase 2b: privacy notice & backup opt-out —
    privacy_title: 'Your Data & Cloud Backup',
    privacy_intro: 'When you are online, Crypto-Course backs up your learning progress so your teacher can support you and the University of Westminster research team can evaluate the course.',
    privacy_what_lbl: 'What is saved', privacy_what: 'XP, streak, badge dates, quiz and lab results, module progress, and session length.',
    privacy_not_lbl: 'Never saved', privacy_not: 'Your messages, your location, or details about your device.',
    privacy_who_lbl: 'Who can see it', privacy_who: 'Only your teacher and the research team. Data is stored securely on Cloudflare infrastructure.',
    privacy_keep_lbl: 'Kept until', privacy_keep: 'Deleted at the end of the semester.',
    privacy_rights: 'You can turn backup off at any time here or in your Profile, and you can ask for your data to be deleted at any time.',
    privacy_contact_lbl: 'Questions or deletion requests:',
    privacy_link: 'Privacy notice', sync_toggle_lbl: 'Cloud backup & teacher sync',
    sync_off_status: 'Backup off', turn_off_backup: 'Turn off backup',
    backup_off_toast: 'Backup turned off — your progress stays on this device only.',
    backup_on_toast: '✓ Backup turned on.',""",
    'i18n EN keys')

# 11. i18n keys — AR
rep("    ph_search_modules: 'ابحث في الوحدات…',",
    """    ph_search_modules: 'ابحث في الوحدات…',
    // — Phase 2b: privacy notice & backup opt-out —
    privacy_title: 'بياناتك والنسخ الاحتياطي السحابي',
    privacy_intro: 'عند اتصالك بالإنترنت، تنسخ منصة Crypto-Course تقدمك التعليمي احتياطيًا ليتمكن معلمك من دعمك وليتمكن فريق البحث في جامعة وستمنستر من تقييم الدورة.',
    privacy_what_lbl: 'ما يُحفَظ', privacy_what: 'النقاط، وسلسلة الأيام، وتواريخ الأوسمة، ونتائج الاختبارات والمختبرات، وتقدم الوحدات، ومدة الجلسة.',
    privacy_not_lbl: 'لا يُحفَظ أبدًا', privacy_not: 'رسائلك أو موقعك أو تفاصيل جهازك.',
    privacy_who_lbl: 'من يمكنه الاطلاع', privacy_who: 'معلمك وفريق البحث فقط. تُخزَّن البيانات بأمان على بنية Cloudflare التحتية.',
    privacy_keep_lbl: 'مدة الاحتفاظ', privacy_keep: 'تُحذَف في نهاية الفصل الدراسي.',
    privacy_rights: 'يمكنك إيقاف النسخ الاحتياطي في أي وقت من هنا أو من ملفك الشخصي، ويمكنك طلب حذف بياناتك في أي وقت.',
    privacy_contact_lbl: 'للاستفسارات أو طلبات الحذف:',
    privacy_link: 'إشعار الخصوصية', sync_toggle_lbl: 'النسخ الاحتياطي السحابي ومزامنة المعلم',
    sync_off_status: 'النسخ الاحتياطي متوقف', turn_off_backup: 'إيقاف النسخ الاحتياطي',
    backup_off_toast: 'تم إيقاف النسخ الاحتياطي — يبقى تقدمك على هذا الجهاز فقط.',
    backup_on_toast: '✓ تم تشغيل النسخ الاحتياطي.',""",
    'i18n AR keys')

# Integrity & write
assert src.count('`') == BASE_BT, f'BACKTICKS CHANGED: {BASE_BT} -> {src.count(chr(96))}'
assert src.count('`') % 2 == 0
open(PATH, 'w', encoding='utf-8', newline='').write(src)
print(f'\nWritten. Backticks: {src.count(chr(96))} (unchanged, even)')
