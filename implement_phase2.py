#!/usr/bin/env python3
"""Phase 2 implementation — buttons & toasts i18n (Scope A reduced).
Line-targeted edits with hard assertions; CRLF preserved; no backticks added."""
import sys

PATH = 'index.html'
raw = open(PATH, encoding='utf-8', newline='').read()
BASE_BT = raw.count('`')
lines = raw.split('\r\n')
L = lambda n: lines[n-1]

def edit(n, old, new):
    assert old in lines[n-1], f'L{n}: NOT FOUND: {old[:60]!r} in {lines[n-1][:90]!r}'
    assert lines[n-1].count(old) == 1, f'L{n}: not unique on line: {old[:60]!r}'
    lines[n-1] = lines[n-1].replace(old, new)

# ----------------------------------------------------------------
# A. Wiring edits (original line numbers — content edits don't shift lines)
# ----------------------------------------------------------------
E = edit
# Toasts / alerts
E(2276, "showToast('⚠️ Storage full — your progress may not be saved. Free up space or contact your teacher.')", "showToast(t('toast_storage_full'))")
E(2396, "showToast('✓ You\\'re on the leaderboard — good luck!')", "showToast(t('toast_lb_joined'))")
E(2417, "showToast('You\\'ve left the leaderboard — your progress is kept.')", "showToast(t('toast_lb_left'))")
E(6340, "alert('No freeze tokens available. You earn 1 per 7 days.')", "alert(t('no_freeze_tokens'))")
# Home / lesson nav
E(6467, '>Start Assessment</button>', ">${t('start_assessment')}</button>")
E(6468, '>Skip</button>', ">${t('skip_btn')}</button>")
E(6479, "continueBtn.textContent = '🏆 View Course Certificate';", "continueBtn.textContent = t('view_course_cert');")
E(6482, "continueBtn.textContent = '🚀 Start First Module';", "continueBtn.textContent = t('start_first_module');")
E(6485, "continueBtn.textContent = '▶ Continue Learning';", "continueBtn.textContent = t('continue_learning');")
E(6492, "courseComplete ? '✅ All Modules Complete' : completedMods === 0 && state.lessonsCompleted === 0 ? 'Get Started' : 'In Progress'", "courseComplete ? t('all_modules_complete') : completedMods === 0 && state.lessonsCompleted === 0 ? t('get_started') : t('in_progress')")
E(6759, "ctaBtn.textContent = 'Got it';", "ctaBtn.textContent = t('got_it');")
E(6861, "stage < totalStages ? 'Continue →' : (lessonState.quizPassed ? '✓ Complete Lesson' : '🔒 Complete Lesson')", "stage < totalStages ? t('continue_arrow') : (lessonState.quizPassed ? t('complete_lesson') : t('complete_lesson_locked'))")
E(6896, "nextBtn.textContent = 'Run Lab to Continue →';", "nextBtn.textContent = t('run_lab_continue');")
E(6917, "nextBtn.textContent = 'Submit Answer';", "nextBtn.textContent = t('submit_answer');")
E(6940, "lessonState.quizPassed ? '🏠 Back to Home' : '🔒 Back to Home'", "lessonState.quizPassed ? t('back_home') : t('back_home_locked')")
E(10369, "nextBtn.textContent = 'Lab Complete! Continue →';", "nextBtn.textContent = t('lab_complete_continue');")
E(10518, "nextBtn.textContent = 'Submit Answer';", "nextBtn.textContent = t('submit_answer');")
E(10610, 'aria-label="Continue to next stage">Next →</button>', "aria-label=\"${t('aria_continue_next')}\">${t('next_arrow')}</button>")
E(10630, "setAttribute('aria-label', 'Submit answer');", "setAttribute('aria-label', t('submit_answer'));")
E(10666, "correct ? 'Correct! 🎉' : 'Not quite…'", "correct ? t('correct_celebrate') : t('not_quite')")
E(10791, "textContent = 'Next →';", "textContent = t('next_arrow');")
E(10796, "nextBtn.textContent = 'Continue →';", "nextBtn.textContent = t('continue_arrow');")
E(11237, "nextBtn.textContent = 'Submit Answer';", "nextBtn.textContent = t('submit_answer');")
E(11286, "nextBtn.textContent = '✓ Complete Revisit';", "nextBtn.textContent = t('complete_revisit');")
E(11512, '>Close</button>', ">${t('close_btn')}</button>")
E(11513, '>Submit Answer</button>', ">${t('submit_answer')}</button>")
E(11704, '>Maybe later</button>', ">${t('maybe_later')}</button>")
E(12061, "btn.textContent = '🎉 +10 XP & Badge Earned!';", "btn.textContent = t('xp_badge_earned');")
E(12152, "preview.textContent = 'No cohort group assigned yet';", "preview.textContent = t('no_cohort_group');")
# Sync / backup
E(12302, "el.textContent = 'Last backed up: ' + friendlyTime;", "el.textContent = t('last_backed_up') + ' ' + friendlyTime;")
E(12303, "textContent = 'Last sync: ' + new Date(state.lastSync).toLocaleTimeString();", "textContent = t('last_sync') + ' ' + new Date(state.lastSync).toLocaleTimeString();")
E(12306, "el.textContent = 'Never backed up';", "el.textContent = t('never_backed_up');")
E(12954, "syncEl.textContent = 'Sync unavailable (no server)';", "syncEl.textContent = t('sync_unavailable');")
E(12958, "syncEl.textContent = 'Syncing…';", "syncEl.textContent = t('syncing');")
E(12996, "syncEl.textContent = 'Synced just now ✓';", "syncEl.textContent = t('synced_just_now');")
E(13002, "syncEl.textContent = 'Offline — progress saved locally';", "syncEl.textContent = t('offline_saved_local');")
# Diagnostic / TLX
E(13329, '>Explore all modules first</button>', ">${t('explore_modules_first')}</button>")
E(13472, '>Submit Rating →</button>', ">${t('submit_rating')}</button>")
E(13473, '>Skip (data will not be recorded)</button>', ">${t('skip_no_record')}</button>")
# Auth screen
E(14372, '>Sign In</button>', ">${t('sign_in_tab')}</button>")
E(14373, '>Register</button>', ">${t('register_tab')}</button>")
E(14378, '>Email</label>', ">${t('lbl_email')}</label>")
E(14382, '>Password</label>', ">${t('lbl_password')}</label>")
E(14389, '>Sign In →</button>', ">${t('sign_in_btn')}</button>")
E(14392, '>Name</label>', ">${t('lbl_name')}</label>")
E(14393, 'placeholder="Your full name"', "placeholder=\"${t('ph_full_name')}\"")
E(14396, '>Email</label>', ">${t('lbl_email')}</label>")
E(14400, '>Password</label>', ">${t('lbl_password')}</label>")
E(14402, 'placeholder="Min 8 characters"', "placeholder=\"${t('ph_min8')}\"")
E(14407, 'Class Code <span style="color:var(--muted);font-weight:400;text-transform:none">(optional — given by your teacher)</span>', "${t('lbl_class_code')} <span style=\"color:var(--muted);font-weight:400;text-transform:none\">${t('class_code_optional')}</span>")
E(14408, 'placeholder="e.g. FALL2026"', "placeholder=\"${t('ph_class_code')}\"")
E(14412, '>Create Account →</button>', ">${t('create_account_btn')}</button>")
E(14416, '>Continue as Guest (local only)</button>', ">${t('guest_btn')}</button>")
E(14432, "busy ? 'Signing in…' : 'Sign In →'", "busy ? t('signing_in') : t('sign_in_btn')")
E(14461, "el.textContent = 'Your account has been suspended. Contact your teacher.';", "el.textContent = t('account_suspended');")
E(14490, "busy ? 'Creating account…' : 'Create Account →'", "busy ? t('creating_account') : t('create_account_btn')")
E(14710, "showToast('✓ Email verified — welcome!')", "showToast(t('email_verified'))")
E(14720, "errEl.textContent = 'Please enter the full 6-digit code.';", "errEl.textContent = t('code_enter_full');")
E(14735, "errEl.textContent = 'Code has expired — tap Resend to get a new one.';", "errEl.textContent = t('code_expired');")
E(14742, "errEl.textContent = 'Incorrect code — check your email and try again.';", "errEl.textContent = t('code_incorrect');")
E(14747, "errEl.textContent = 'Verification error — try again.';", "errEl.textContent = t('code_error');")
E(14755, "errEl.textContent = 'No pending code found — tap Resend to get a new one.';", "errEl.textContent = t('code_none');")
E(14771, "errEl.textContent = 'No internet connection — check connection and try again.';", "errEl.textContent = t('no_internet');")
E(14932, "showToast('Your account has been suspended. Contact your teacher.')", "showToast(t('account_suspended'))")
E(15003, 'placeholder="Choose a password…"', "placeholder=\"${t('ph_choose_pw')}\"")
E(15007, 'placeholder="Repeat password…"', "placeholder=\"${t('ph_repeat_pw')}\"")
E(15011, '>Set Password & Continue →</button>', ">${t('set_pw_btn')}</button>")
E(15020, "err.textContent = 'Password must be at least 6 characters.';", "err.textContent = t('pw_too_short');")
E(15021, "err.textContent = 'Passwords do not match.';", "err.textContent = t('pw_mismatch');")
# Engagement / misc
E(16055, '>Mark as Read ✓</button>', ">${t('mark_read')}</button>")
E(16533, '>Continue Learning →</button>', ">${t('continue_learning_arrow')}</button>")
E(16551, '>Join Leaderboard</button>', ">${t('join_leaderboard')}</button>")
E(16954, '>Got it ✓</button>', ">${t('got_it_check')}</button>")
E(17541, "alert('Text-to-speech is not supported in this browser.')", "alert(t('tts_unsupported'))")
# Semester (student side)
E(20987, '>Join Semester</button>', ">${t('join_semester_btn')}</button>")
E(21001, '>Leave Semester</button>', ">${t('leave_semester_btn')}</button>")
E(21024, "showToast('Semester not found')", "showToast(t('semester_not_found'))")
E(21041, "showToast('📅 Enrolled in ' + sem.name);", "showToast(t('enrolled_in') + ' ' + sem.name);")
E(21078, '>Skip for now</button>', ">${t('skip_for_now')}</button>")
E(21124, 'placeholder="Enter join code"', "placeholder=\"${t('ph_join_code')}\"")
E(21127, '>Join</button>', ">${t('join_btn')}</button>")
E(21140, "errEl.textContent = 'Enter the join code first.';", "errEl.textContent = t('join_code_empty');")
E(21141, "errEl.textContent = 'Wrong code — check with your teacher and try again.';", "errEl.textContent = t('join_code_wrong');")
E(21162, "errEl.textContent = 'Could not connect to server — check your connection.';", "errEl.textContent = t('server_unreachable');")
E(21203, "errEl.textContent = 'Code not found — check your code or ask your teacher.';", "errEl.textContent = t('class_code_not_found');")
E(21226, "showToast('Left semester')", "showToast(t('left_semester'))")
E(22491, "showToast('Please enter the plaintext')", "showToast(t('enter_plaintext'))")
E(23785, "showToast('Text-to-speech not supported on this device')", "showToast(t('tts_unsupported_device'))")
# Interactive diagram step navs (string-concatenated, student-facing)
E(23715, ">&#x2039; Prev</button>'", ">' + t('prev_chevron') + '</button>'")
E(23716, ">Next &#x203a;</button>'", ">' + t('next_chevron') + '</button>'")
E(24553, ">&#x2039; Prev</button>'", ">' + t('prev_chevron') + '</button>'")
E(24155, "isDone ? 'Done ✓' : 'Next ›'", "isDone ? t('done_check') : t('next_chevron')")
# Static HTML: data-i18n hooks
E(1749, 'type="search" placeholder="Search modules…"', 'type="search" placeholder="Search modules…" data-i18n-placeholder="ph_search_modules"')
E(1998, '<div style="font-size:14px;color:var(--text2);line-height:1.5;margin-bottom:14px">', '<div style="font-size:14px;color:var(--text2);line-height:1.5;margin-bottom:14px" data-i18n="sync_student_expl">')
E(2002, 'onclick="triggerSync()" style="width:auto">📤 Back up now</button>', 'onclick="triggerSync()" style="width:auto" data-i18n="backup_now_btn">📤 Back up now</button>')
E(2003, '<div id="sync-time-student" style="font-size:12px;color:var(--muted)">Checking…</div>', '<div id="sync-time-student" style="font-size:12px;color:var(--muted)" data-i18n="checking">Checking…</div>')
# Track auth tab for re-render on language change
E(14341, 'function showAuthScreen(tab) {', "function showAuthScreen(tab) {\r\n  window._authTab = tab || window._authTab || 'login';\r\n  tab = window._authTab;")

print(f'Wiring edits applied: OK')

# ----------------------------------------------------------------
# B. New i18n keys (find anchors dynamically post-edit; lines unchanged in dict zone)
# ----------------------------------------------------------------
EN_KEYS = """    // — Phase 2: buttons & toasts (auth) —
    auth_tagline: 'Offline-first cryptography education',
    sign_in_tab: 'Sign In', register_tab: 'Register',
    sign_in_btn: 'Sign In →', signing_in: 'Signing in…',
    create_account_btn: 'Create Account →', creating_account: 'Creating account…',
    guest_btn: 'Continue as Guest (local only)',
    lbl_email: 'Email', lbl_password: 'Password', lbl_name: 'Name', lbl_class_code: 'Class Code',
    class_code_optional: '(optional — given by your teacher)',
    ph_full_name: 'Your full name', ph_min8: 'Min 8 characters', ph_class_code: 'e.g. FALL2026',
    ph_choose_pw: 'Choose a password…', ph_repeat_pw: 'Repeat password…',
    set_pw_btn: 'Set Password & Continue →',
    pw_too_short: 'Password must be at least 6 characters.', pw_mismatch: 'Passwords do not match.',
    code_enter_full: 'Please enter the full 6-digit code.',
    code_expired: 'Code has expired — tap Resend to get a new one.',
    code_incorrect: 'Incorrect code — check your email and try again.',
    code_error: 'Verification error — try again.',
    code_none: 'No pending code found — tap Resend to get a new one.',
    no_internet: 'No internet connection — check connection and try again.',
    email_verified: '✓ Email verified — welcome!',
    account_suspended: 'Your account has been suspended. Contact your teacher.',
    class_code_not_found: 'Code not found — check your code or ask your teacher.',
    // — Phase 2: lesson navigation & quiz —
    start_assessment: 'Start Assessment', skip_btn: 'Skip',
    view_course_cert: '🏆 View Course Certificate', start_first_module: '🚀 Start First Module',
    all_modules_complete: '✅ All Modules Complete', get_started: 'Get Started',
    complete_lesson: '✓ Complete Lesson', complete_lesson_locked: '🔒 Complete Lesson',
    run_lab_continue: 'Run Lab to Continue →', submit_answer: 'Submit Answer',
    back_home: '🏠 Back to Home', back_home_locked: '🔒 Back to Home',
    next_arrow: 'Next →', next_chevron: 'Next ›', prev_chevron: '‹ Prev', done_check: 'Done ✓',
    aria_continue_next: 'Continue to next stage',
    correct_celebrate: 'Correct! 🎉', not_quite: 'Not quite…', close_btn: 'Close',
    lab_complete_continue: 'Lab Complete! Continue →', complete_revisit: '✓ Complete Revisit',
    explore_modules_first: 'Explore all modules first',
    continue_arrow: 'Continue →', continue_learning_arrow: 'Continue Learning →',
    got_it: 'Got it', got_it_check: 'Got it ✓', maybe_later: 'Maybe later',
    // — Phase 2: toasts & engagement —
    toast_storage_full: '⚠️ Storage full — your progress may not be saved. Free up space or contact your teacher.',
    toast_lb_joined: '✓ You\\'re on the leaderboard — good luck!',
    toast_lb_left: 'You\\'ve left the leaderboard — your progress is kept.',
    no_freeze_tokens: 'No freeze tokens available. You earn 1 per 7 days.',
    xp_badge_earned: '🎉 +10 XP & Badge Earned!',
    tts_unsupported: 'Text-to-speech is not supported in this browser.',
    tts_unsupported_device: 'Text-to-speech not supported on this device',
    enter_plaintext: 'Please enter the plaintext', mark_read: 'Mark as Read ✓',
    // — Phase 2: sync & backup —
    sync_unavailable: 'Sync unavailable (no server)', syncing: 'Syncing…',
    synced_just_now: 'Synced just now ✓', offline_saved_local: 'Offline — progress saved locally',
    last_backed_up: 'Last backed up:', last_sync: 'Last sync:', never_backed_up: 'Never backed up',
    backup_now_btn: '📤 Back up now', checking: 'Checking…',
    sync_student_expl: 'Your progress is saved on this device. When you have internet, tap below to back it up so it\\'s safe even if you switch devices.',
    // — Phase 2: semester (student) —
    join_semester_btn: 'Join Semester', leave_semester_btn: 'Leave Semester',
    skip_for_now: 'Skip for now', ph_join_code: 'Enter join code', join_btn: 'Join',
    join_code_empty: 'Enter the join code first.',
    join_code_wrong: 'Wrong code — check with your teacher and try again.',
    server_unreachable: 'Could not connect to server — check your connection.',
    semester_not_found: 'Semester not found', enrolled_in: '📅 Enrolled in',
    left_semester: 'Left semester', no_cohort_group: 'No cohort group assigned yet',
    // — Phase 2: surveys & misc —
    submit_rating: 'Submit Rating →', skip_no_record: 'Skip (data will not be recorded)',
    ph_search_modules: 'Search modules…',"""

AR_KEYS = """    // — Phase 2: buttons & toasts (auth) —
    auth_tagline: 'تعليم التشفير دون اتصال بالإنترنت',
    sign_in_tab: 'تسجيل الدخول', register_tab: 'إنشاء حساب',
    sign_in_btn: 'تسجيل الدخول ←', signing_in: 'جارٍ تسجيل الدخول…',
    create_account_btn: 'إنشاء الحساب ←', creating_account: 'جارٍ إنشاء الحساب…',
    guest_btn: 'المتابعة كضيف (على هذا الجهاز فقط)',
    lbl_email: 'البريد الإلكتروني', lbl_password: 'كلمة المرور', lbl_name: 'الاسم', lbl_class_code: 'رمز الصف',
    class_code_optional: '(اختياري — يقدّمه معلمك)',
    ph_full_name: 'اسمك الكامل', ph_min8: '٨ أحرف على الأقل', ph_class_code: 'مثال: FALL2026',
    ph_choose_pw: 'اختر كلمة مرور…', ph_repeat_pw: 'أعد كتابة كلمة المرور…',
    set_pw_btn: 'تعيين كلمة المرور والمتابعة ←',
    pw_too_short: 'يجب ألا تقل كلمة المرور عن ٦ أحرف.', pw_mismatch: 'كلمتا المرور غير متطابقتين.',
    code_enter_full: 'الرجاء إدخال الرمز المكوَّن من ٦ أرقام كاملاً.',
    code_expired: 'انتهت صلاحية الرمز — اضغط «إعادة الإرسال» للحصول على رمز جديد.',
    code_incorrect: 'الرمز غير صحيح — تحقق من بريدك الإلكتروني وحاول مجددًا.',
    code_error: 'خطأ في التحقق — حاول مجددًا.',
    code_none: 'لا يوجد رمز قيد الانتظار — اضغط «إعادة الإرسال» للحصول على رمز جديد.',
    no_internet: 'لا يوجد اتصال بالإنترنت — تحقق من الاتصال وحاول مجددًا.',
    email_verified: '✓ تم التحقق من البريد الإلكتروني — أهلاً بك!',
    account_suspended: 'تم إيقاف حسابك. تواصل مع معلمك.',
    class_code_not_found: 'الرمز غير موجود — تحقق من الرمز أو اسأل معلمك.',
    // — Phase 2: lesson navigation & quiz —
    start_assessment: 'ابدأ التقييم', skip_btn: 'تخطٍّ',
    view_course_cert: '🏆 عرض شهادة الدورة', start_first_module: '🚀 ابدأ الوحدة الأولى',
    all_modules_complete: '✅ اكتملت جميع الوحدات', get_started: 'ابدأ الآن',
    complete_lesson: '✓ إنهاء الدرس', complete_lesson_locked: '🔒 إنهاء الدرس',
    run_lab_continue: 'شغّل المختبر للمتابعة ←', submit_answer: 'إرسال الإجابة',
    back_home: '🏠 العودة للرئيسية', back_home_locked: '🔒 العودة للرئيسية',
    next_arrow: 'التالي ←', next_chevron: 'التالي ›', prev_chevron: '‹ السابق', done_check: 'تم ✓',
    aria_continue_next: 'المتابعة إلى المرحلة التالية',
    correct_celebrate: 'إجابة صحيحة! 🎉', not_quite: 'ليست الإجابة الصحيحة…', close_btn: 'إغلاق',
    lab_complete_continue: 'اكتمل المختبر! تابع ←', complete_revisit: '✓ إنهاء المراجعة',
    explore_modules_first: 'استكشف جميع الوحدات أولاً',
    continue_arrow: 'متابعة ←', continue_learning_arrow: 'تابع التعلم ←',
    got_it: 'فهمت', got_it_check: 'فهمت ✓', maybe_later: 'لاحقًا ربما',
    // — Phase 2: toasts & engagement —
    toast_storage_full: '⚠️ مساحة التخزين ممتلئة — قد لا يُحفَظ تقدمك. حرّر مساحة أو تواصل مع معلمك.',
    toast_lb_joined: '✓ أنت الآن على لوحة المتصدرين — حظًا موفقًا!',
    toast_lb_left: 'غادرت لوحة المتصدرين — تقدمك محفوظ.',
    no_freeze_tokens: 'لا توجد رموز تجميد متاحة. تحصل على رمز واحد كل ٧ أيام.',
    xp_badge_earned: '🎉 +١٠ نقاط ووسام جديد!',
    tts_unsupported: 'تحويل النص إلى كلام غير مدعوم في هذا المتصفح.',
    tts_unsupported_device: 'تحويل النص إلى كلام غير مدعوم على هذا الجهاز',
    enter_plaintext: 'الرجاء إدخال النص الأصلي', mark_read: 'وضع علامة كمقروء ✓',
    // — Phase 2: sync & backup —
    sync_unavailable: 'المزامنة غير متاحة (لا يوجد خادم)', syncing: 'جارٍ المزامنة…',
    synced_just_now: 'تمت المزامنة للتو ✓', offline_saved_local: 'غير متصل — تقدمك محفوظ على الجهاز',
    last_backed_up: 'آخر نسخ احتياطي:', last_sync: 'آخر مزامنة:', never_backed_up: 'لم يتم النسخ الاحتياطي بعد',
    backup_now_btn: '📤 انسخ احتياطيًا الآن', checking: 'جارٍ التحقق…',
    sync_student_expl: 'يُحفَظ تقدمك على هذا الجهاز. عند توفر الإنترنت، اضغط أدناه لنسخه احتياطيًا حتى يبقى آمنًا حتى لو غيّرت جهازك.',
    // — Phase 2: semester (student) —
    join_semester_btn: 'الانضمام للفصل الدراسي', leave_semester_btn: 'مغادرة الفصل الدراسي',
    skip_for_now: 'تخطَّ الآن', ph_join_code: 'أدخل رمز الانضمام', join_btn: 'انضمام',
    join_code_empty: 'أدخل رمز الانضمام أولاً.',
    join_code_wrong: 'الرمز خاطئ — راجع معلمك وحاول مجددًا.',
    server_unreachable: 'تعذّر الاتصال بالخادم — تحقق من اتصالك.',
    semester_not_found: 'الفصل الدراسي غير موجود', enrolled_in: '📅 تم التسجيل في',
    left_semester: 'غادرت الفصل الدراسي', no_cohort_group: 'لم تُعيَّن مجموعة بعد',
    // — Phase 2: surveys & misc —
    submit_rating: 'إرسال التقييم ←', skip_no_record: 'تخطٍّ (لن تُسجَّل البيانات)',
    ph_search_modules: 'ابحث في الوحدات…',"""

def insert_after_line_containing(needle, block, label):
    idx = [i for i, ln in enumerate(lines) if needle in ln]
    assert len(idx) == 1, f'{label}: anchor not unique ({len(idx)}): {needle!r}'
    lines[idx[0]+1:idx[0]+1] = block.split('\n')
    print(f'{label}: inserted after line {idx[0]+1}')

# Insert AR first (higher line number), then EN — avoids index shift issues
insert_after_line_containing("ltr_label: 'من اليسار إلى اليمين'", AR_KEYS, 'AR keys')
insert_after_line_containing("ltr_label: 'Left-to-Right'", EN_KEYS, 'EN keys')

# ----------------------------------------------------------------
# C. setLanguage extensions: placeholder support + auth re-render guard
# ----------------------------------------------------------------
src = '\r\n'.join(lines)

old_block = """  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const str = (i18n[lang] && i18n[lang][key]) || i18n.en[key];
    if (str !== undefined) el.textContent = str;
  });""".replace('\n', '\r\n')
new_block = old_block + """
  // Placeholder translations (Phase 2)
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    const str = (i18n[lang] && i18n[lang][key]) || i18n.en[key];
    if (str !== undefined) el.setAttribute('placeholder', str);
  });""".replace('\n', '\r\n')
assert src.count(old_block) == 1, 'setLanguage data-i18n block not unique'
src = src.replace(old_block, new_block)

old_nav = """  if (typeof currentScreen !== 'undefined' && typeof navigate === 'function') {
    navigate(currentScreen);
  }""".replace('\n', '\r\n')
new_nav = """  // Re-render: auth screen if visible (pre-login), else active screen (PR11)
  const _authEl = document.getElementById('auth-screen');
  if (_authEl && _authEl.style.display !== 'none' && typeof showAuthScreen === 'function') {
    showAuthScreen(window._authTab || 'login');
  } else if (typeof currentScreen !== 'undefined' && typeof navigate === 'function') {
    navigate(currentScreen);
  }""".replace('\n', '\r\n')
assert src.count(old_nav) == 1, 'setLanguage navigate block not unique'
src = src.replace(old_nav, new_nav)
print('setLanguage extensions: OK')

# ----------------------------------------------------------------
# D. Auth screen: tagline via t() + language toggle
# ----------------------------------------------------------------
old_sub = '<div style="font-size:13px;color:var(--muted)">Offline-first cryptography education</div>'
new_sub = ("""<div style="font-size:13px;color:var(--muted)">${t('auth_tagline')}</div>
      <div style="margin-top:12px;display:flex;gap:8px;justify-content:center">
        <button onclick="setLanguage('en')" style="padding:5px 14px;border-radius:14px;border:1px solid rgba(255,255,255,0.25);font-size:12px;font-weight:700;cursor:pointer;font-family:var(--font);background:${(state.language||'en')==='en'?'rgba(255,255,255,0.92)':'transparent'};color:${(state.language||'en')==='en'?'var(--text)':'rgba(255,255,255,0.75)'}">EN</button>
        <button onclick="setLanguage('ar')" style="padding:5px 14px;border-radius:14px;border:1px solid rgba(255,255,255,0.25);font-size:12px;font-weight:700;cursor:pointer;font-family:'Segoe UI',Tahoma,sans-serif;background:${state.language==='ar'?'rgba(255,255,255,0.92)':'transparent'};color:${state.language==='ar'?'var(--text)':'rgba(255,255,255,0.75)'}">العربية</button>
      </div>""").replace('\n', '\r\n')
assert src.count(old_sub) == 1, 'auth tagline not unique'
src = src.replace(old_sub, new_sub)
print('Auth language toggle: OK')

# ----------------------------------------------------------------
# E. Screen-reader fix: lang="en" on lesson content containers
# ----------------------------------------------------------------
n = src.count('class="lesson-content"')
assert n == 4, f'lesson-content count changed: {n}'
src = src.replace('class="lesson-content"', 'class="lesson-content" lang="en"')
print(f'lang="en" applied to {n} lesson-content containers')

# ----------------------------------------------------------------
# F. Integrity checks & write
# ----------------------------------------------------------------
assert src.count('`') == BASE_BT, f'BACKTICK COUNT CHANGED: {BASE_BT} -> {src.count(chr(96))}'
assert src.count('`') % 2 == 0, 'backtick count odd'
open(PATH, 'w', encoding='utf-8', newline='').write(src)
print(f'\nWritten. Backticks: {src.count(chr(96))} (unchanged, even). New length: {len(src)}')
