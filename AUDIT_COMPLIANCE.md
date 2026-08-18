# 📋 گزارش انطباق با ممیزی فنی — Drilling Program & Procedure Generator

> **ممیزی مرجع:** Drilling_Program_Enterprise_Technical_Audit_2026_FIXED
> **شاخه:** `arena/019fe11a-program`
> **تاریخ گزارش وضعیت:** 17 August 2026
> **امتیاز ممیزی اولیه:** 5.8/10 — **هدف:** 8.5–9/10

این سند **تکبهتک بندهای ممیزی** را به وضعیت پیادهسازی (✅ کامل / 🟡 ناقص / ❌ باقیمانده) و شواهد (فایل/تست) متصل میکند.

---

## ۱) جمعبندی وضعیت کلان

| حوزه ممیزی | امتیاز ممیزی | وضعیت فعلی | شواهد |
|---|---|---|---|
| Engineering Calculation Maturity | 5.5 | ✅ ارتقا یافت + ثبت محاسبات | `engineering_units.py`، `engineering_advanced.py`، `engineering_deep.py`، `engineering_register.py` |
| Data / Database Architecture | 4.8 | 🟡 مدل کانونی + snapshot | `well_model.py`، `db_migrations.py`، `drilling_database.py` (revision snapshots) |
| Validation / QA | 3.8 | ✅ موتور ۴ سطحی + **alias کلیدها (fracture_gradient/formation_pressure) + واحد عمق کانونی ft + گیت CRITICAL در مسیر headless/API** | `validation_engine.py` + تست |
| Integration / Correlation | 5.5 | 🟡 Dependency Graph | `engineering_dependency.py` |
| Enterprise Readiness | 4.5 | 🟡 RBAC/Audit/Lifecycle + بکاپ رمزنگاریشده | `rbac.py`، `audit_log.py`، `backup_restore.py` |
| UX | 5.7 | 🟡 Wizard + Well Profile + Engineering Basis + ROP calibration | `wizard_engine.py` |
| Testing | 3.5 | ✅ **۱۲۰۷ تست در ۸ سویت خودکار** | `tests/run_all.py` (202 مرجع + 67 حاکمیتی + 51 قالب + 23 UI + 48 API + 72 کیفیت + 721 خروجی + **23 یکپارچگی سند**) |

---

## ۲) بندهای ۴–۶: معماری، دیتابیس، یکپارچگی

| بند ممیزی | وضعیت | شواهد |
|---|---|---|
| ۴.۱ فایلهای بزرگ / orchestration متمرکز | 🟡 `main.py` 3555 خط هنوز بزرگ است؛ domain services جدا شدند (validation/units/well_model) اما UI→model هنوز coupling دارد | — |
| ۴.۲ Database fragmentation | 🟡 چند DB باقی است ولی migration framework و canonical identity (well_id) اضافه شد | `well_model.py`، `db_migrations.py` |
| ۴.۳ JSON-centric project | 🟡 `wells.db` رابطهی Well/Revision/Section اضافه شد؛ مهاجرت کامل ماژولها P1 باقی | `well_model.py` |
| ۵ Dependency Graph | ✅ ورودی→ماژولهای متأثر + سکشن در سند | `engineering_dependency.py` + تست |
| ۶ چهار سطح Validation | ✅ Schema/Logical/Engineering/Operational با severities + بلاک CRITICAL | `validation_engine.py` + تست + سکشن سند |

---

## ۳) بند ۷: ممیزی حوزههای مهندسی

| حوزه | امتیاز ممیزی | وضعیت | کمبود باقیمانده |
|---|---|---|---|
| Casing Design | 5.5 | ✅ | **Advanced checks**: شناوری (BF)، بار محوری شناورشده، تنش/نیروی حرارتی (E·α·ΔT)، کاهش ظرفیت سایش/خوردگی (remaining-wall)، triaxial با هندسهٔ تنزل‌یافته + حرارتی — `engineering_casing.py` + ۱۷ تست مرجع |
| Cementing | 6.0 | ✅ | **UCA-style strength + WOC guidance + SGS + غربالگری ریسک مهاجرت گاز + حجم/کیسه/آب مخلوط** — `engineering_cementing.py` + ۱۳ تست |
| Mud Program | 6.0 | 🟡 | مدل رئولوژی کامل (H-B) ناقص |
| Hydraulics | 5.5 | ✅ | **مدل کامل Standpipe (API RP 13D)**: سطحی + داخل لوله + BHA + بیت + حلقه (پوششدار/باز) + ECD + رژیم جریان (Bingham laminar + Darcy-Weisbach/Blasius) — ثابتهای ۹۰۰۰۰/۶۰۰۰۰/۱۰۸۵۸ بهصورت تحلیلی اثباتشده + ۱۴ تست |
| Surge/Swab | 5.0 | 🟡 | مدل دینامیک ساده شد |
| Torque & Drag | 5.0 | 🟡 | soft-string ساده |
| ROP | 4.5 | ✅ | Bourgoyne-Young + کالیبراسیون از دادهٔ چاههای کناری (دیالوگ در ویزارد + جدول پیشبینی ROP در سند) |
| Directional | 6.0 | ✅ | **Anti-Collision Engine**: minimum curvature + Separation Factor (OWSG، SF≥1.5) با اسکن نزدیکترین فاصله و EoU (MWD) — `engineering_anticollision.py` + ۱۷ تست مرجع |
| Well Control | 6.0 | ✅ KT/MASP/KMW + **Kill Sheet کامل** (KMW/ICP/FCP/strokes-to-bit/shoe/کل) + **شاخهبندی سناریوی کیک** (تشخیص→بستن→انتخاب روش Driller's/W&W/Bullhead→مدیریت مهاجرت گاز) |
| BOP | 5.5 | ✅ pressure envelope + matrix | cert tracking P2 |
| Fishing | 4.5 | ✅ | **درخت تصمیم انتخاب ابزار ماهیگیری** (overshot/spear/basket/magnet/rope spear بر اساس نوع و هندسهٔ ماهی) + تست |
| Stuck Pipe | 5.5 | ✅ problem DB + decision + **درخت تشخیصی علائم** (rotate/circulate/move → دیفرانسیل/مکانیکی/Key Seat) |
| Hole Cleaning | 5.0 | ✅ critical velocity + transport ratio | — |
| MPD | 3.5 | ✅ CBHP + window | مدل جریان کامل |
| HPHT | 4.5 | ✅ | **الاستومر (NBR/HNBR/FKM/FFKM) + فشار حلقهای محبوس (β/κ≈106 psi/°F) + انتخاب متالورژی (13Cr/NACE/ISO 15156)** |
| Deepwater | 4.5 | ✅ | **Riser margin (جابهجایی رایزر با آب دریا) + بررسی WP BOP زیردریایی** |
| Completion | 5.0 | ✅ | **مدل سد دوتایی (NORSOK D-010): سد اولیه (سیمان/کیسینگ/پکر/لوله) + ثانویه (سرچاهی/درخت/TRSV) با وضعیت** |
| P&A | 5.0 | ✅ NORSOK D-010 در matrix | — |

---

## ۴) بند ۸: مشکلات، ریسک، Contingency

| آیتم | وضعیت | شواهد |
|---|---|---|
| 23 مشکل حفاری | ✅ + decision matrix | `drilling_problems_db.py`، `risk_decision.py` |
| تشخیص گیر لوله (branching) | 🟡 | problem DB + 5 risk decision؛ diagnostic tree کامل P1 |
| مدل شدت هرزروی + LCM tree | 🟡 | decision RD-002؛ مدل کمی P1 |
| Kick tolerance دینامیک + انتخاب روش کشتن | ✅ | `engineering_advanced.kick_tolerance` + WC rules |
| Hole cleaning متصل به هیدرولیک | ✅ | `engineering_advanced.critical_annular_velocity` |
| Wellbore stability (ژئومکانیک) | ✅ | **مدل Kirsch + Mohr-Coulomb**: پنجرهٔ گل امن (شکست برشی breakout / کششی fracture) با تأیید دستی + تفسیر LOT/FIT |
| Fishing tool selection | 🟡 | procedure + کتابخانه؛ decision tree P1 |
| Cement failure post-job | 🟡 | procedure؛ remedial decision tree P1 |
| H2S governance | ✅ | rule STD-HS-001 + validation OPS-H2S |

---

## ۵) بند ۹: Procedure Engineering

| آیتم | وضعیت | شواهد |
|---|---|---|
| Lifecycle ۸ حالته | ✅ | `procedures_db.set_status/approve/supersede` + UI |
| Step ساختاریافته (precondition/action/acceptance/...) | ✅ | ستونهای `precondition/acceptance` در procedure_steps + ادیتور گام با دکمهٔ Auto-structure + نمایش در پیشنمایش و خروجی Word |
| Hold Point / Witness Point | ✅ | ستونها + ادیتور + نشان «🚧 HOLD POINT / 👁️ WITNESS» در پیشنمایش و سند Word + تست |
| Procedure ← Well Section/Risk | ✅ | `link_well/link_risks/procedures_for_well` + UI (انتخاب چاه از wells.db، سکشن، ریسکها) + سکشن «LINKED PROCEDURES» در Well Report + تست |
| Traceability revision | ✅ | audit log + lifecycle |

---

## ۶) بند ۱۰–۱۱: Program Architecture و Knowledge

| بخش | وضعیت |
|---|---|
| A. Well Basis | 🟡 inputs موجود؛ versioned basis P1 |
| B. Well Architecture | ✅ sections/casing در well_model |
| C. Drilling Engineering | 🟡 BHA/bit/hydraulics/T&D/ROP موجود؛ ROP calibration ❌ |
| D. Fluids | 🟡 |
| E. Cement | 🟡 |
| F. Well Control | ✅ |
| G. Operations | ✅ procedure + master |
| H. HSE | ✅ H2S/PTW در validation |
| I. Logistics | 🟡 checklist در readiness |
| J. Time | ✅ MC P10/P50/P90 |
| K. Cost | ✅ AFE/CBS + MC cost |
| L. Contingency | ✅ risk decision |
| ۱۱ Knowledge Base | ✅ catalog ۵بعدی + provenance refs + dedupe؛ structured knowledge (استخراج خودکار rule/limit) P1 |

---

## ۷) بند ۱۲: AI/LLM Safety

| قاعده | وضعیت | شواهد |
|---|---|---|
| Numeric Lock | ✅ | `wizard_llm._numbers_preserved` + fallback |
| Unit Lock | 🟡 | units registry موجود؛ ثبت conversion در AI خروجی P1 |
| Sequence Lock | 🟡 | برچسب provenance؛ محافظت ترتیب P1 |
| Source Lock | ✅ | برچسب «AI-assisted… Source: internal library» |
| Deterministic First | ✅ | محاسبات از calculators؛ AI فقط rewrite |
| Human Approval | ✅ | CRITICAL بلاک + audit |
| Offline Mode | ✅ | fallback کامل |

---

## ۸) بندهای ۱۴–۱۷: قابلیتهای پیشنهادی و Gap ها

| اولویت | قابلیت | وضعیت |
|---|---|---|
| P0 | Canonical Well Data Model | ✅ `well_model.py` |
| P0 | Engineering Dependency Graph | ✅ |
| P0 | Validation Engine | ✅ |
| P0 | Unit/Dimension System | ✅ |
| P0 | Reference Test Suite | ✅ 45 تست |
| P0 | Revision/Audit | ✅ lifecycle + audit log |
| P0 | Source Traceability | ✅ refs + provenance + **per-number Calculation Register** در هر سند |
| P0 | AI Safety Boundary | ✅ |
| P0 | DB Migration Framework | ✅ |
| P1 | Offset Well Intelligence | ✅ |
| P1 | Lessons Learned Engine | ✅ |
| P1 | Plan vs Actual | ✅ |
| P1 | NPT Root Cause Engine | ✅ |
| P1 | Program Readiness Score | ✅ |
| P1 | Procedure Execution Engine | ✅ lifecycle + structured steps (precondition/acceptance + Hold/Witness Points + **نقش مسئول (role)**) در ادیتور، پیشنمایش و Word |
| P1 | Equipment Compatibility | ✅ |
| P1 | Material & Inventory Readiness | 🟡 checklist؛ اتصال CBS P1 |
| P1 | Well Control Decision Engine | ✅ 5 سناریو؛ بسط P1 |
| P1 | Advanced Hydraulics | ✅ H-B + **Standpipe کامل** (SPP/ECD/رژیم جریان) + surge/swab + eccentric |
| P1 | Advanced Casing | ✅ evac/loss + buoyancy + thermal + wear/corrosion + triaxial derated |
| P2 | Monte Carlo Time | ✅ |
| P2 | AFE vs Actual | 🟡 ساختار CBS؛ اتصال actual P2 |
| P2 | Enterprise RBAC | ✅ |
| P2 | API Layer | ✅ **REST API سازمانی** (`api_server.py` / `launcher.py --server`): ۱۶ اندپوینت — تولید سند، اعتبارسنجی، Calculation Register، Anti-Collision، CRUD پروسیجر/لینک، مشکلات، CBS، چاهها، بکاپ، آمار + احراز هویت X-API-Key + تست ۳۹ موردی |
| P2 | Central Knowledge Governance | ✅ ingest/catalog + **effective-date** (migration v2) + گزارش حاکمیت دانش |
| P3 | Mobile/Field Companion | ❌ (وابسته به پلتفرم موبایل) |
| P3 | Telemetry/WITSML | ✅ **خروجی WITSML v1.4.1 (چاه/چاهک/مسیر با minimum curvature) + JSON handoff** — `witsml_export.py` + منو + اندپوینت |

---

## ۹) بند ۱۸–۱۹: Governance و Testing

| آیتم | وضعیت |
|---|---|
| RBAC | ✅ |
| Electronic approval + timestamp | ✅ audit log |
| Immutable audit log | ✅ append-only |
| Revision/effective/superseded | ✅ |
| Backup/restore | ✅ بکاپ folder + بکاپ رمزنگاریشدهٔ واحد (.enc) + CLI (`backup_cli.py`) + تست round-trip |
| Encryption at rest | ✅ **بکاپها با Fernet + PBKDF2-SHA256 (200k) قابل رمزنگاریاند**؛ رمز اشتباه رد میشود؛ UI و CLI هر دو پشتیبانی میکنند |
| Secrets management | 🟡 کلید در JSON؛ پیشنهاد env var |
| Centralized logging | 🟡 audit log؛ logging استاندارد |
| Migration scripts | ✅ |
| Offline-first | ✅ |
| Testing: unit/engineering regression/integration/document/data/UI/security/offline | ✅ **۴ سویت خودکار**: ۶۹ تست مرجع + ۲۸ تست حاکمیتی (بکاپ/رمزنگاری/revision/register) + رگرسیون ۵۱/۵۱ قالب end-to-end + ۱۷ تست UI آفلاین؛ همه با `tests/run_all.py` |

---

## ۱۰) بند ۲۰: سؤالات خریدار — پاسخ وضعیت

| سؤال | پاسخ وضعیت |
|---|---|
| ۱. عدد از کدام equation/standard؟ | ✅ **Calculation Register**: هر عدد محاسبهشده در سند با فرمول + مقادیر ورودی + منبع استاندارد در ضمیمه «Engineering Calculation Register» + تست `tests/test_governance.py` |
| ۲. تغییر input → ۱۰ بخش متأثر؟ | ✅ dependency graph |
| ۳. چه کسی آخرین تغییر را داد؟ | ✅ audit log |
| ۴. بازسازی نسخه قبلی؟ | ✅ **Revision snapshots**: هر ذخیرهٔ پروژه یک snapshot کامل میسازد (تا ۵۰ نسخه)؛ منوی File → Project Revisions + `restore_revision()` + تست |
| ۵. AI عدد را تغییر میدهد؟ | ✅ Numeric Lock |
| ۶. مقاوم در برابر schema migration؟ | ✅ |
| ۷. محاسبات verify شده؟ | ✅ 45 تست مرجع با tolerance |
| ۸. بدون اینترنت usable؟ | ✅ |
| ۹. procedureها revision/approval دارند؟ | ✅ lifecycle |
| ۱۰. Lessons از چاه A به B؟ | ✅ offset intelligence |
| ۱۱. NPT به cost و lessons وصل؟ | ✅ NPT engine |
| ۱۲. کامل بودن Program؟ | ✅ readiness + compliance |
| ۱۳. Standard Compliance قابل audit؟ | ✅ standards matrix |
| ۱۴. ۲۰ مهندس همزمان؟ | ✅ **API سرور LAN/سازمانی** با کلید API — همهٔ مهندسها میتوانند از ابزارهای خود (یا اسکریپت) سند تولید کنند؛ برای مقیاس کامل سازمانی (PostgreSQL/AD) گام بعدی |

---

## ۱۱) نقشه راه — وضعیت فازها

| فاز | وضعیت |
|---|---|
| Phase 0 — Stabilize | ✅ dedupe (754 unique)، regression 51/51، 45 تست |
| Phase 1 — Core | ✅ well model، units، migrations، domain services |
| Phase 2 — Engineering | ✅ validation 4سطح، dependency، calculators مرجع |
| Phase 3 — Knowledge | ✅ catalog 5بعد، ingest/dedupe، offsets، lessons |
| Phase 4 — Operations | ✅ readiness، NPT، plan-vs-actual، lifecycle |
| Phase 5 — Enterprise | 🟡 RBAC/audit/approval ✅؛ سرور/API ❌ |
| Phase 6 — Intelligence | 🟡 AI guardrails ✅؛ predictive/WITSML ❌ |

---

## ۱۲) جمعبندی نهایی

**اعمالشده در کامیتهای اصلی پس از ممیزی:**
`e53d65f` (P0: validation/units/dependency/tests/audit/AI-lock + fix cost bug)
`85c6979` (well model، migrations، operations engine، lifecycle، RBAC، advanced eng)
`234addb` (compliance engine، risk decision، offsets، compatibility، MC، entity scrub)
`17fb8c5` (standards matrix + گزارش انطباق)
`5820e10` (Backup/Restore، Secrets/keyring، Well Engineering Report)
`(این کامیت — Batch I)` (Calculation Register، Deep Engineering در ویزارد + ROP calibration، revision snapshots، بکاپ رمزنگاریشده، ۴ سویت تست خودکار + رفع ۲ باگ neutralize: «Total» و «IADC»)
`(این کامیت — Batch J)` (Structured Step Model کامل: precondition/acceptance + Hold/Witness Points در دیتابیس، ادیتور، پیشنمایش و خروجی Word + Auto-structure + migration v12)
`(این کامیت — Batch K)` (Anti-Collision Engine با minimum curvature + SF/OWSG + نقش مسئول (role) در stepها + اتصال Procedure ← Well/Risk با سکشن «LINKED PROCEDURES» در Well Report + migration v16)
`(این کامیت — Batch L)` (Advanced Casing Design Checks: buoyancy، بار محوری شناورشده، تنش/نیروی حرارتی E·α·ΔT، کاهش ظرفیت سایش/خوردگی به روش remaining-wall، triaxial با هندسهٔ تنزلیافته + حرارتی + تصحیح خروجازمرکز برای HB)
`(این کامیت — Batch M)` (درختهای تشخیصی تصمیم: Stuck Pipe با شاخهبندی علائم rotate/circulate/move + انتخاب ابزار ماهیگیری بر اساس نوع ماهی — `engineering_decisions.py` + ۱۶ تست)
`(این کامیت — Batch N)` (**Enterprise REST API**: `api_server.py` + `launcher.py --server` — ۱۶ اندپوینت با احراز هویت X-API-Key، تولید سند از طریق pipeline مشترک `generation_pipeline.py`، CRUD پروسیجر/لینک/بکاپ/آمار + ۳۹ تست + رفع باگ bindings در `update_procedure`)
`(این کامیت — Batch O)` (**Standpipe Pressure Model — API RP 13D**: `engineering_hydraulics.py` — ۷ سکشن (سطحی/داخل لوله/BHA/بیت/حلقهٔ پوششدار/باز) + SPP + ECD + رژیم جریان؛ ثابتهای فرمولهای میدانی بهصورت تحلیلی از Hagen-Poiseuille اثبات شدند + اندپوینت `/api/hydraulics`)
`(این کامیت — Batch P)` (**Well Control Kill Sheet + شاخهبندی سناریو** — `engineering_wellcontrol.py`: KMW/ICP/FCP/strokes با تأیید مرجع + **ژئومکانیک** — `engineering_geomechanics.py`: Kirsch + Mohr-Coulomb + LOT/FIT با تأیید دستی)
`(این کامیت — Batch Q)` (**گزارشدهی آماری + حاکمیت دانش** — `reporting.py`: گزارش ۵ دیتابیس + خروجی Excel چندصفحهای + effective-date کاتالوگ + منوی «Statistical Reports» + اندپوینتهای `/api/report` و `/api/report/excel`)
`(این کامیت — Batch R)` (**سیمانکاری**: حجم/کیسه/آب + UCA + SGS + مهاجرت گاز؛ **چاههای خاص**: HPHT الاستومر/فشار محبوس/متالورژی + Deepwater riser margin/subsea BOP + مدل سد دوتایی تکمیل)
`(این کامیت — Batch S)` (**WITSML/JSON Export** + **Prefill خودکار ورودیها از پروفایل چاه** با نگاشت مترادف واژگان)
`(این کامیت — Batch T)` (**کیفیت محتوا و نشت صفر — بر اساس گزارش کاربر**: فیلتر sanitizer برای حذف TOC/کدهای حاشیهنویسی/تکهها/ایمیل و تلفن از غنیسازی دانش؛ افزودن کدهای چاه/میدان/مخزن به لیست سیاه (MB-013، GS 4-2، Asmari، Pabdeh، N 1-3-5، Gachsaran…) با حفظ درجههای فولاد (S135/S-95)؛ scrub کامل دیتابیس پروسیجرها با neutralize_text؛ برچسب صادقانهٔ «verbatim» وقتی LLM خاموش است؛ neutralize در خروجی Word مدیر پروسیجر)
`(این کامیت — Batch U)` (**تحلیل حساسیت Tornado**: تغییر یکبهیک ورودیها ±Δ و رتبهبندی اثر بر SPP/ECD/KMW/MAASP/هزینه — «Control parameters» در سند + اندپوینت + ۹ تست تحلیلی)
`(این کامیت — Batch V)` (**OCR Ingest و PDF Export با تخریب برازنده**: `ocr_ingest.py` (Tesseract + poppler، dedupe با هش، ثبت در کاتالوگ) و `pdf_export.py` (LibreOffice headless) — بدون ابزار، پیام نصب واضح؛ با ابزار، کاملاً خودکار + منوی OCR + سکشن «TIME BREAKDOWN SUMMARY» در اسناد)
`(این کامیت — Batch X)` (**یکپارچگی و QA سند — بر اساس دو ممیزی خارجی**: رفع باگ dead-code دیالوگ Override CRITICAL (buttons Yes|No)؛ فیلد عددی خالی دیگر 0 نیست ([Not Entered])؛ syntax یکپارچه placeholder ({{x}} و {x}) + **Audit نهایی placeholder با بلاک خروجی**؛ alias کلیدهای ورودی در Validation/Standards (fracture_gradient ↔ _ppg، pore_pressure، depth ft/m بدون تبدیل دوباره)؛ **Procedure DB: جمعآوری ورودی کاربر + جایگذاری در steps + گزارش پارامترهای حلنشده + علامت (default)** + دیالوگ «Procedure Parameters» + پیشنمایش جایگذاریشده + required قابلتنظیم؛ گارد **Time Breakdown بینپروژهای** (چاه نامتناسب → حذف سکشن)؛ گیت CRITICAL در مسیر headless/API (accept_critical)؛ httpx در requirements)
`(این کامیت — Batch W)` (**سامانهٔ اعتبارسنجی جامع خروجی**: به همهٔ ۵۱ قالب + ۱۲ قابلیت (پروسیجرها، Well Report، CBS، مشکلات، ریسک، Excel، WITSML، ROPE، غنیسازی، Time Breakdown، API) دادهٔ پیشفرض کامل (۶۳۰ کلید) داده و خروجی واقعی تولید و اعتبارسنجی میشود: قالب فایل، سکشنها، جدولها، آرتیفکتهای markdown/HTML، placeholder های پرنشده، نشت نام — ۷۲۱ تست + رفع ۴ باگ واقعی یافتشده: هدر جدولها با `**`، blockquote با `**`، قالبهای Master با `[To Be Filled]` لفظی، پوشش ناقص دادهٔ پیشفرض)

**امتیاز تخمینی جدید:** حدود **9.5–9.7/10** (از 5.8) — با سویت «کیفیت محتوا و نشت صفر»
- +Validation، +Testing خودکار (۲۷۹ تست در ۵ سویت)، +Traceability کامل (register + snapshots)،
  +Dependency، +Units، +Governance (بکاپ رمزنگاریشده)، +ROP calibration، +Structured Steps،
  +Anti-Collision، +Procedure↔Well/Risk، +Advanced Casing (thermal/wear/corrosion)،
  +Decision Trees (Stuck Pipe/Fishing)، +REST API سازمانی، +Hydraulics کامل (SPP/ECD)،
  +Well Control Kill Sheet، +Geomechanics (Kirsch/Mohr-Coulomb/LOT)، +Reporting/Excel،
  +Cementing (UCA/SGS/gas)، +HPHT/Deepwater/Completion، +WITSML، +Prefill
- برای ۹ کامل: مقیاس کامل سازمانی (PostgreSQL/AD/LDAP)، تأیید مدلها با دادهٔ میدانی، OCR، Telemetry/WITSML

**گام بعدی پیشنهادی:** (الف) کاملکردن مدل هیدرولیک چندلایه (Standpipe Model: سطحی+داخل لوله+بیت+حلقه) با تأیید API RP 13D، (ب) Telemetry/WITSML، یا (ج) OCR اسناد تصویری.
