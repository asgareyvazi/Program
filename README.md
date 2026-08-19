# 🛢️ Drilling Program & Procedure Generator — Professional Edition

سیستم یکپارچه تولید برنامه حفاری، پروسیجرهای عملیاتی، تحلیل ریسک و محاسبات مهندسی.

| | |
|---|---|
| نسخه | **3.1 (Integrated Edition)** |
| زبان رابط | انگلیسی (استاندارد صنعت نفت) |
| پلتفرم | Windows / Linux / macOS (Python + PySide6) |

---

## ✨ امکانات

- **🧙 Program & Procedure Wizard** — «یک برنامه حفاری میخوام» → انتخاب نوع سند ← **پروفایل چاه (Well Profile)**: نوع چاه (عمودی/انحرافی/افقی/ERD/HPHT/Deepwater)، محیط (خشکی/جکاپ/نیمهشناور/سکوی ثابت/کاسپین) و عملیات (حفاری/ورکاور/ری-انتری/سایدترک/تکمیل/...) ← **انتخاب سکشنها** ← ورودیها ← **تنظیمات خروجی** ← سند Word کامل
  - **دستهبندی جزئی کل کتابخانه (۷۵۴ سند یکتا)**: هر سند بر اساس ۵ بُعد دستهبندی شده (دسته/نوع چاه/محیط/عملیات/سایز حفره) — پروفایل چاه که کاربر انتخاب میکند، اسناد دانش مرتبط را فیلتر کرده و سکشن «WELL PROFILE & BASIS OF DESIGN» به ابتدای سند اضافه میشود
  - **انتخاب سکشنها:** کاربر تیک میزند کدام بخشها در سند باشد (بقیه حذف میشوند؛ سربرگ و صفحه تأیید همیشه میمانند)
  - **تنظیمات خروجی:** فونت (Calibri/Arial/Times...)، اندازه فونت، صفحه A4/Letter، جهت عمودی/افقی، حاشیهها، صفحه جلد، فهرست مطالب (فیلد واقعی Word)، متن سرصفحه/پاصفحه
  - **جستجوی اینترنت (🌐 Web Research):** برای معرفی میدان/سازند — ویکیپدیا + DuckDuckGo با دکمههای پیشنهادی، پیشنمایش، ویرایش و درج با ذکر منبع
  - **نام شرکت از ورودی کاربر:** نام اپراتور و پیمانکار که کاربر وارد میکند، در تمام خروجی (بدنه، صفحه جلد، دانش، ریسک) درج میشود؛ هر نام شرکت/برند دیگری بهطور خودکار حذف میشود (لیست سیاه گسترده + الگوریتم امن placeholder)
  - **جای خالی:** هر فیلد خالی بهصورت `[To Be Filled]` / جدول خالی در Word میماند تا کاربر بعداً کامل کند
  - **🔍 Risk Review خودکار (قبل از خروجی):** نرمافزار عملیات سند را با پایگاه دانش ریسک (۲۵۰۰+ ریسک) بررسی میکند، خطرات Critical/High را نشان میدهد، **سؤالهای تأیید از کاربر میپرسد** و سکشن «Risk Assessment & Contingency Plan» (جدول ریسکها + اقدامات Contingency + چکلیست بهترینروشها + جدول تأییدات) را به سند اضافه میکند
  - **۱۳ قالب برنامه:** حفاری چاه جدید، کار روی چاه (Workover)، ESP Workover، ترک و رهاسازی (P&A)، مهار چاه (Kill)، سیمانکاری، تست چاه، ماهیگیری (Fishing)، تحریک چاه (Stimulation)، لوله مغزی (CT)، **Re-Entry / Sidetrack (فراساحلی)**, **Offshore Workover (ESP/Completion)**, **Offshore Drilling (با هیدرولیک کامل)** — الگوبرداریشده از برنامههای میادین فراساحلی
  - **۱۹ قالب پروسیجر:** تراب، لولهگذاری Casing، **Casing Running & Cementing**, تست BOP، گردش فوران، **Kill میدانی**, گیرکردن لوله، اسلایکلاین، ESP، پکر، ترکش، DST، سرچاهی، هرزروی، **Cement Plug**, جابجایی دکل، H2S، تست فشار لوله، BHA
  - بر پایه استانداردهای جهانی: API RP 5C3/10B/13B/53/59، ISO 10400/10426، NORSOK D-010، IADC، Shell DEP، Saudi Aramco SAES
  - ورودیهای هوشمند: عدد، متن، جدول، انتخاب — فیلدهای خالی بهصورت `[To Be Filled]` در سند میمانند
- **📄 تولید برنامه کامل حفاری** — اطلاعات چاه، سازندها، Casing، گل، BHA، سیمان، جهتدار، BOP، دکل، زمانبندی → خروجی Word حرفهای
- **📋 Procedure Manager** — **۱۸۰+ پروسیجر گامبهگام با چکلیست و خروجی Word** (استخراجشده از ۶۹۰+ سند واقعی: ۱۲۷ گایدلاین بینالمللی BP UK Operations، ۴۴ پروسیجر از اسناد میدانی pp2 شامل سکوی نیمهشناور امیرکبیر/کاسپین، ری-انتری و ورکاور فراساحلی + پایه API/IADC) — همه جنرال (بدون اسم چاه/شرکت)
- **🛟 Drilling Problems DB** — دیتابیس ۲۳ مشکل حفاری (گیر لوله، هرزروی، فوران، ناپایداری دیواره، ماهیگیری، آلودگی گل...) با علائم/علل/پیشگیری/راهحلهای اولویتبندیشده؛ دیالوگ جستجو در ویزارد → سکشن «Drilling Problem Prevention & Response Plan»
- **⛽ Risk Analyzer (یکپارچه)** — تحلیل ریسک و Contingency Planning با پایگاه داده ۲۵۰۰+ ریسک + پشتیبان AI (Gemini / Ollama / HuggingFace)
- **🧮 Engineering Tools** — تبدیل واحد، هیدرولیک (API RP 13D)، صحتسنجی Casing (API RP 5C3)، سیمان، MAASP/Kick Tolerance، Torque & Drag
- **📚 Field Knowledge Library (داخلی)** — **۷۵۴ سند یکتای واقعی** (برنامهها، پروسیجرها، گایدلاینهای شرکتهای بزرگ، کتابهای مرجع و جداول قیمت) **فقط بهعنوان دانش داخلی** برای غنیسازی خروجی استفاده میشوند؛ نمایش جداگانهای در رابط کاربری ندارند (اعداد قبلی ۲۱۴/۶۹۲ مربوط به مجموعههای اولیه بودند؛ پس از deduplication عدد رسمی ۷۵۴ سند یکتاست)
- **🧠 ML Knowledge Enrichment** — موتور بازیابی (TF-IDF کلاسیک + Embedding معنایی اختیاری) مرتبطترین چکلیستها/مراحل/پروسیجرهای واقعی را برای هر نوع سند انتخاب و (پس از حذف نام شرکتها) بهصورت سکشن «Field Knowledge Enrichment» به خروجی اضافه میکند — انتخاب سطح: Brief / Moderate / Detailed
- **📋 ROPE Field Checklists** — چکلیستهای استاندارد صنعتی Rig Operations Performance Execution (BHA، Bit، Casing، Cementing، Cement Plug، Tripping، Well Control، Stuck Pipe، Coiled Tubing، Slickline، HPHT، Fishing، H2S، BOP و...) بهصورت خودکار و متناسب با نوع سند به خروجی اضافه میشوند (۳ سطح: Brief/Moderate/Detailed + واژهنامه در Detailed)
- **🤖 LLM Rewriting (اختیاری)** — دکمه «LLM Settings» در صفحه ورودیها: Ollama (محلی، بدون کلید) / Gemini / HuggingFace. متنهای انتخابی کتابخانه توسط AI به پاراگرافهای حرفهای و خنثی بازنویسی میشوند؛ اگر LLM در دسترس نباشد، متن خام (خنثیشده) خودکار جایگزین میشود — هیچ قابلیتی کم نمیشود
- **📎 Reference System** — هر قالب به اسناد واقعی کتابخانه وصل است؛ خروجی Word شامل بخش «Reference Documents» با فهرست اسناد میدانی مرتبط میشود
- **🛢️ Professional Well Templates** — پریستهای چاه: خاورمیانه H₂S، شیرین، Jack-Up، HPHT، Deepwater، Shale افقی، ERD
- **🛢️ Professional Well Templates** — پریستهای چاه: خاورمیانه H₂S، شیرین، Jack-Up، HPHT، Deepwater، Shale افقی، ERD
- **🧬 Operational Template Library** — قالبهای فازبهمرحله با پارامترهای قابل تنظیم
- **💰 Cost & Pricing (CBS)** — دیتابیس **کاملاً جنرال** قیمت کالا/خدمات (۱۲ دسته، ۳۳۷ قلم) — **بدون هیچ اسم چاه، شرکت یا مخزن**؛ قیمتهای پیشفرض قابل ویرایش (دیریت دکل، سیمانکاری، بیتها، لولهها، خدمات، تکمیل، اسیدکاری، پرسنل و...)؛ اتصال خودکار به Time Breakdown (دیریت دکل × روزها)، محاسبه خودکار زیرجمع دستهها، contingency و هزینه بهازای متر، خروجی **AFE / Cost Breakdown Structure** بهصورت Word حرفهای. در ویزارد با دکمه «📋 Select Goods & Services…» میتوانید **انتخاب کنید کدام کالا/سرویس با چه تعداد و چه قیمتی** در خروجی بیاید — برنامه میپرسد، شما جواب میدهید.
- **⏱️ Time Breakdown** — ویرایشگر زمان فازها و NPT + **پروژه نمونه جنرال**: ۱۶۷ ردیف عملیات (حفاری + تکمیل + پرلوریشن + اسیدکاری، مجموع ۱۳۱.۸۲ روز / ۱۴۵.۰۰ روز با contingency) بدون هیچ نام چاه/شرکت — قابل بارگذاری با یک کلیک برای محاسبه هزینه دکل
- **✅ Validation Engine (۴ سطح)** — پیش از هر خروجی، طراحی با چهار سطح اعتبارسنجی میشود: Schema (نوع/محدوده/واحد) → Logical (تناقضهای ساختاری مثل کیسینگ عمیقتر از TD) → Engineering (سازگاری مهندسی مثل ECD>FG یا BOP<MASP) → Operational Readiness (معیار پذیرش، برنامه H2S و...)؛ یافتههای **CRITICAL خروجی را مسدود میکنند** (مگر با تأیید رسمی که در سند و Audit Log ثبت میشود) و سکشن «VALIDATION & COMPLIANCE» به سند اضافه میشود
- **🔗 Engineering Dependency Graph** — تغییر هر ورودی (وزن گل، سایز حفره، عمق کیسینگ، فشار سازند...) بهصورت مرکزی مشخص میکند کدام ماژولها (هیدرواستاتیک، ECD، MAASP، سیمان، زمان، هزینه، ریسک...) تحت تأثیر قرار میگیرند و این تأثیر در سند ثبت میشود
- **📏 سیستم واحدها (Dimension-Safe)** — تبدیل یکپارچه psi/bar، m/ft، ppg/pcf/sg با تشخیص بعد و ثابتهای استاندارد (۰.۰۵۲، ۲۴.۵، Barlow/API 5C3)
- **🧪 تست خودکار (۲۰۸ تست در ۴ سویت)** — اجرای همه: `python tests/run_all.py`؛ ۸۹ تست مرجع مهندسی با تلورانس پذیرش (Hydrostatic، MAASP، KMW، Annular Velocity، Casing Burst API، Well Cost، Anti-Collision و...) + ۴۷ تست حاکمیتی (بکاپ/رمزنگاری/Revision Snapshots/Register/Linking) + رگرسیون ۵۱/۵۱ قالب end-to-end (تولید Word واقعی + ۶ سکشن حاکمیتی + اسکن نشت نام) + ۲۱ تست UI آفلاین
- **🧭 Anti-Collision Engine** — Minimum Curvature + Separation Factor (OWSG) با اسکن نزدیکترین فاصله، EoU (MWD) و آفست سطح اسلات مجاور؛ در Deep Engineering سند + Register
- **🔩 Advanced Casing Checks** — buoyancy، بار محوری شناورشده، تنش/نیروی حرارتی (E·α·ΔT)، کاهش ظرفیت سایش/خوردگی (remaining-wall) و triaxial با هندسهٔ تنزلیافته + حرارتی (`engineering_casing.py`)
- **🧭 Decision Trees** — درخت تشخیصی Stuck Pipe (علائم rotate/circulate/move → دیفرانسیل/مکانیکی/Key Seat) + انتخاب ابزار ماهیگیری بر اساس نوع ماهی (`engineering_decisions.py`)
- **🌐 Enterprise REST API** — `python3 launcher.py --server` (یا `api_server.py`): ۱۷ اندپوینت با کلید API — تولید سند، validation، register، hydraulics، anti-collision، CRUD پروسیجر/لینک، مشکلات، CBS، چاهها، بکاپ، آمار؛ مستندات OpenAPI در `/docs`؛ تست: `python3 tests/test_api.py`
- **🌊 Standpipe Pressure Model (API RP 13D)** — SPP کامل (سطحی + داخل لوله + BHA + بیت + حلقه) + ECD + رژیم جریان با ثابتهای تحلیلی اثباتشده (`engineering_hydraulics.py`)
- **🚨 Well Control Kill Sheet** — KMW/ICP/FCP/strokes-to-bit/shoe + شاخهبندی سناریوی کیک (Driller's / W&W / Bullhead) (`engineering_wellcontrol.py`)
- **⛰️ Geomechanics** — پنجرهٔ گل امن با Kirsch + Mohr-Coulomb (breakout/fracture) + LOT/FIT (`engineering_geomechanics.py`)
- **📊 Statistical Reports** — منوی «Statistical Reports» + خروجی Excel چندصفحهای (پروسیجر/مشکلات/CBS/کاتالوگ/NPT) + effective-date دانش (`reporting.py`)
- **🏗️ Cementing** — حجم/کیسه/آب + UCA/WOC + SGS + ریسک مهاجرت گاز (`engineering_cementing.py`)
- **🔥 Special Wells** — HPHT (الاستومر/فشار محبوس/متالورژی) + Deepwater (riser margin/subsea BOP) + مدل سد دوتایی تکمیل (`engineering_special.py`)
- **📡 WITSML Export** — خروجی WITSML v1.4.1 + JSON (منو یا `/api/witsml`) (`witsml_export.py`)
- **⚡ Auto-Prefill** — ورودیهای ویزارد از پروفایل چاه با نگاشت مترادف واژگان (Deviated ← Directional J-Type و…)
- **🛡️ کیفیت محتوا و نشت صفر** — فیلتر sanitizer (حذف TOC/کدهای حاشیهنویسی/تکهها/ایمیل/تلفن)، لیست سیاه کامل کدهای چاه/میدان/مخزن (MB-013، GS 4-2، Asmari، Pabdeh…) با حفظ درجههای فولاد (S135)، scrub دیتابیس پروسیجرها، برچسب صادقانهٔ verbatim بدون LLM — سویت `tests/test_content_quality.py` (۷۲ تست)
- - **🪝 Torque & Drag (soft-string + کالیبراسیون)** — بار قلاب، تورک سطحی، کمانش Dawson-Paslay + **کالیبراسیون friction factor از دادهٔ چاههای مجاور** (`engineering_td.py`)
- **🛢️ Kick Fluid Classification** — تشخیص گاز/آب/روغن از اختلاف SICP−SIDPP + friction خط چوک دیپواتر (`engineering_wellcontrol.py`)
- **⚙️ Fine-Grained Document Composition** — کاربر در هر مرحله جزئی انتخاب میکند: حفرهها (با پروسیجر/چکلیست هر حفره)، پروسیجرهای خاص از ۱۶ دسته، نوع/تولزهای تکمیل، و اسناد دانش انتخابی از کاتالوگ — دکمهٔ «⚙️ Fine-Grained Composition» در ویزارد (`wizard_compose.py`)
- **📊 Data Usage Audit** — ممیزی کامل بودن دستهبندی دیتابیس و قابلدسترسبودن همهٔ دادهها از UI (`tests/data_usage_audit.py`)
- **🗃️ Unified Database** — ادغام همهٔ دیتابیسها در `unified.db` با entity-links و FK واقعی + گزارش یکپارچگی بینپایگاهی (`unified_db.py`، `/api/unified`)
- **🖥️ Native Installer** — `python installer.py` (نصب/چک/تعمیر: وابستگیها + دیتابیسها + لانچر) و `python installer.py --check`
- **🪝 T&D Stiff-String 3D** — مدل خمشی با سهنقطهتماس + DLS (همیشه ≥ soft-string؛ در قائم صفر) (`engineering_td.py`)
- **📅 Daily Drilling Report (Plan vs Actual)** — سند Morning-Report با جدول واریانس روزانه و پرچمهای KPI + منوی «Tools → Daily Drilling Report» (`daily_report.py`)
- **🕳️ Cross-Well Intelligence** — یادگیری بینچاهی: رتبهبندی چاههای ذخیرهشده بر اساس شباهت مهندسی، پیشنهاد ورودی از چاه آفست، سکشن مقایسه و گزارش دیتابیس چاهها + دکمههای «Load from Stored Well» و «Suggest from Similar Offset Well» در ویزارد (`well_intelligence.py`)
- **🗂️ Canonical Input Registry** — منبع واحد کلید/واحد/محدودهٔ مهندسی (۳۸ کمیت، ~۹۰ alias): همهٔ موتورها (Validation/Standards/Register/Consistency) مقدار را از یکجا میخوانند — `input_registry.py`
- **🔍 Cross-Document Consistency** — اسکن سند نهایی برای تناقضهای مهندسی (casing>TD، MW>FG، ECD>FG، BOP<MASP) + سکشن «CROSS-DOCUMENT CONSISTENCY» (`engineering_consistency.py`)
- **🎯 Engineering Range Validation** — محدودههای واقعبینانه در Schema (MW 6-22 ppg، BOP 2-20k psi و...) — مقدار غیرفیزیکی در لحظهٔ ورود پرچم میشود
- **📥 WITSML Import** — دریافت WITSML (چاه/مسیر) و ادغام در ورودیهای ویزارد (`witsml_import.py`، `/api/witsml/import`)
- **🪛 IADC Dull Grading** — تفسیر کد ۸کاراکتری IADC با ارزیابی وضعیت بیت و سکشن Word (`iadc_dull.py`، `/api/iadc-dull`)
- **📦 بستهبندی سازمانی** — `pyinstaller packaging/DrillingProgram.spec` + اسکریپتهای build ویندوز/لینوکس (توزیع تکپوشه با کتابخانهٔ دانش)
- **🧾 Template & Procedure Audit خودکار** — `python3 tests/template_audit.py`: همهٔ قالبها و پروسیجرها از نظر placeholder/InputSchema/required/unit اسکن و گزارش PASS/FAIL/WARN میدهند (`audit_report.md`)
- **🔍 Document Integrity QA (Batch X)** — placeholder یکپارچه ({{x}}/{x}) + Audit نهایی با بلاک خروجی، فیلد عددی خالی ≠ 0، alias کلیدهای ورودی (fracture_gradient/formation_pressure/depth ft)، جمعآوری ورودی Procedure DB با جایگذاری در steps + گزارش پارامترهای حلنشده، گارد Time Breakdown بینپروژهای، گیت CRITICAL headless، دیالوگ Override اصلاحشده — سویت `tests/test_integrity.py` (۲۳ تست)
- **✅ سامانهٔ اعتبارسنجی جامع خروجی** — به همهٔ ۵۱ قالب و ۱۲ قابلیت دادهٔ پیشفرض کامل داده، خروجی واقعی تولید و صحت فرمت/متن/ساختار آن را بررسی میکند (۷۲۱ تست: `tests/validate_outputs.py`)؛ نمونههای اعتبارسنجیشده در `sample_outputs/` با `python3 tests/validate_outputs.py --export` قابل تولید است
- **📈 Sensitivity Analysis (Tornado)** — رتبهبندی ورودیهای بحرانی (اثر ±Δ بر SPP/ECD/KMW/MAASP/هزینه) + سکشن «SENSITIVITY SCREENING» و «Control parameters» در سند (`engineering_sensitivity.py`)
- **🔤 OCR Ingest + 📄 PDF Export** — `python3 ocr_ingest.py <folder>` (اسناد اسکنشده ← کتابخانه + کاتالوگ با dedupe هش؛ نیازمند Tesseract) و `python3 pdf_export.py <file.docx>` (نیازمند LibreOffice) — با پیام نصب واضح در نبود ابزار + سکشن «TIME BREAKDOWN SUMMARY» در اسناد
- **🔗 Procedure ← Well/Risk** — لینک پروسیجر به چاه/سکشن/ریسک (wells.db + problems.db) + سکشن «LINKED PROCEDURES» در Well Report + نقش مسئول (Role) در هر گام
- **📊 Engineering Calculation Register** — در هر سند تولیدی، ضمیمهٔ «ENGINEERING CALCULATION REGISTER»: تکبهتک اعداد محاسبهشده با **فرمول + مقادیر ورودی + نتیجه + منبع استاندارد** (API/IADC/API 5C3...) — پاسخ به سؤال «این عدد از کدام معادله/استاندارد است؟»
- **🔬 Deep Engineering Verification** — سکشن تأیید عمیق در سند: ROP بورگین-یانگ با **کالیبراسیون از دادهٔ چاههای کناری** (دیالوگ + جدول پیشبینی)، هیدرولیک Herschel-Bulkley، بررسی triaxial (von Mises)، surge/swab با تراکمپذیری؛ ورودیهای «Engineering Basis» (MW/PP/FG/سایزها/WOB/RPM/...) در همهٔ قالبها فعال است
- **🕘 Revision Snapshots** — هر ذخیرهٔ پروژه یک snapshot کامل میسازد (تا ۵۰ نسخه)؛ File → Project Revisions برای بازگردانی هر نسخهٔ قبلی
- **🔒 بکاپ رمزنگاریشده (Encryption at Rest)** — بکاپ همهٔ دیتابیسها بهصورت .enc با Fernet + PBKDF2-SHA256 (از UI یا `python backup_cli.py create --password ...`)
- **🗄️ Canonical Well Model** — مدل یکپارچه Well → Revision → Section (تشکیلها، کیسینگ، گل، BHA...) با شناسه پایدار؛ همه ماژولها میتوانند به یک Well/Section متصل شوند (`wells.db`)
- **🔄 Database Migration Framework** — ارتقای نسخهبندیشده خودکار همه دیتابیسها (`python db_migrations.py`)؛ ستونهای جدید (status/owner/approved_by/effective_date...) بدون شکستن دادههای موجود
- **✅ Program Readiness Score** — نمره کاملبودن ۰-۱۰۰ قبل از تأیید با فهرست موارد بحرانی (فشار سازند، BOP، برنامه H2S، Kick Tolerance، LOT/FIT...)؛ سکشن «PROGRAM READINESS SCORE» در سند
- **💡 Lessons Learned + NPT + Plan vs Actual** — دیالوگ «📊 Operations» از منوی Tools: ثبت درسآموختهها (میدان/عملیات/علت/پیشگیری)، رویدادهای NPT (علت/زیرعلت/هزینه مستقیم و غیرمستقیم/اقدام اصلاحی و پیشگیرانه + خلاصه)، و گزارش روزانه با واریانس عمق/ROP در برابر برنامه
- **📋 Procedure Lifecycle** — چرخه عمر پروسیجرها (Draft → Technical Review → HSE Review → Client Review → Approved → Released → Superseded → Archived) با دکمههای Set Status / Approve در Procedure Manager + ثبت در Audit Log
- **🔐 RBAC** — نقشها (Read-Only/Engineer/Reviewer/Approver/Admin) با بررسی و ثبت دسترسیها (`rbac.py`)
- **📋 Document Compliance Engine** — کارت گزارش انطباق سند قبل از انتشار: کاملبودن سکشنهای الزامی (بر اساس نوع سند)، یافتههای CRITICAL حلنشده، وجود References/Validation/Readiness — سکشن «DOCUMENT COMPLIANCE REPORT» در انتهای هر سند
- **🎯 Risk Decision & Response Matrix** — هر ریسک به trigger/diagnostics/mitigation/escalation/recovery/acceptance-criteria مجهز است؛ بر اساس تحلیل ریسک خودکار، ماتریس تصمیم متناظر به سند اضافه میشود
- **🛰️ Offset Well Intelligence** — جستجوی چاههای مشابه (میدان/نوع/عمق) با درسآموختهها و NPT تاریخی آنها؛ سکشن «OFFSET WELL INTELLIGENCE» در سند
- **🔩 Equipment Compatibility** — بررسی سازگاری بیت/حفره، BHA/کیسینگ، موتور/حفره، لاینر/کیسینگ، BOP/فشار سطحی؛ یافتههای CRITICAL گزارش میشوند
- **🎲 Monte Carlo Schedule & Cost** — P10/P50/P90 زمان و هزینه با توزیع مثلثی (۲۰۰۰ شبیهسازی) — سکشن «SCHEDULE & COST UNCERTAINTY»
- **📏 Standards Compliance Matrix** — رجیستری قواعد استاندارد (API RP 53/10B-2/13B-1/13D، API TR 5C3، NORSOK D-010، API RP 49...) با Rule ID، نسخه استاندارد، قلمرو کاربرد، الزام، معیار پذیرش و ارزیابی خودکار PASS/FAIL/CHECK بر اساس ورودیها — سکشن «STANDARDS COMPLIANCE MATRIX» در سند
- **📝 Structured Step Model** — هر مرحله پروسیجر با Precondition/Action/Parameter/Acceptance/Hazard/Control/Equipment/Role/Record/Escalation + **Hold Point ⛔ / Witness Point 👁**؛ استخراج خودکار از متن خام
- **🎯 Deep Engineering Models** — ROP با **کالیبراسیون از داده چاههای حفرشده** (مدل Bourgoyne-Young)، هیدرولیک **Power Law + Herschel-Bulkley** (با yield stress)، **چک Triaxial (von Mises)** کیسینگ، Surge/Swab با ضریب تراکمپذیری
- **💰 AFE vs Actual** — بودجه/تعهد/واقعی/پیشبینی با درصد مصرف و هشدار تجاوز از بودجه
- **📦 Material & Inventory Readiness** — موجودی بحرانی (کیسینگ، باریت، سیمان...) با هشدار ⛔ برای اقلام کسری بحرانی
- **💾 Backup / Restore** — اسنپشات همه دیتابیسها + تنظیمات در `~/.drilling_program/backups/` با SQLite backup API و manifest؛ بازیابی از منوی Tools
- **🔐 Secrets Management** — کلید API دیگر در فایل متن ساده نمی‌ماند: ذخیره در OS keyring (Credential Manager/Keychain/Secret Service) با fallback فایل ۰۶۰۰
- **📘 Well Engineering Report** — گزارش جامع یکچاه با ۱۰ سکشن (Profile → Validation → Readiness → Standards → Dependency → Problems → Risk Decision → Compatibility → Monte Carlo → Compliance) با یک کلیک از منوی Tools (Word)
- **📋 AUDIT_COMPLIANCE.md** — گزارش انطباق تکبندبهبند با ممیزی فنی (هر بند ۱-۲۵ + ضمائم با وضعیت ✅/🟡/❌ و شواهد)
- **🧬 Entity-Based Generalization** — جایگزینی regex خام با تشخیص موجودیت (شرکت/چاه/میدان/مخزن) + حفاظت از اصطلاحات فنی (Brown زمینشناسی، Total واژه، MI مهندسی گل)
- **⚙️ Advanced Engineering** — Kick Tolerance، BOP Pressure Envelope، Surge/Swab، Hole Cleaning (Critical Annular Velocity/Transport Ratio)، MPD (CBHP + پنجره فشار)، بارهای Evacuation/Lost-Returns کیسینگ
- **📜 Audit Log** — ثبت append-only هر رویداد مهم (تولید سند، override یافتههای بحرانی) با زمان/کاربر/جزئیات در `~/.drilling_program/audit.log`
- **🤖 AI Safety Boundary** — Numeric Lock: اگر LLM اعداد مهندسی را در بازنویسی حذف کند، متن قطعی (خام) جایگزین میشود؛ خروجی AI برچسب provenance دارد و هرگز تصمیم مهندسی نمیگیرد
- **🧹 جنرالسازی خودکار** — هر متن ورودی (قالب، کتابخانه، قیمتها) هنگام خروجی از نام شرکت (لیست سیاه ~۶۰ نام)، نام چاه (AZNS-xxx، F-20، PAD-93، SI-09 و...) و نام مخزن (Fahliyan، Sarvak و...) پاک میشود؛ فقط نام اپراتور/پیمانکاری که **شما** وارد میکنید در سند میماند
- **📊 داشبورد Home** — دسترسی سریع، آمار کتابخانه، پروژههای اخیر

---

## 🚀 نصب و اجرا

```bash
# 1) نصب وابستگیها
pip install -r requirements.txt

# 2) اجرای نرمافزار
python launcher.py
```

### دستورات خط فرمان

```bash
python launcher.py            # اجرای رابط کاربری
python launcher.py --install  # نصب وابستگیها
python launcher.py --check    # بررسی وابستگیها
python bootstrap.py            # راه‌اندازی کامل دیتابیس‌ها (یک فرمان)
python launcher.py --sample   # تولید سند نمونه Word (تست)
python launcher.py --init     # آمادهسازی پوشهها و دیتابیس
```

---

## 📁 ساختار فایلها

```
Program/
├── launcher.py                     # نقطه ورود (GUI / CLI)
├── main.py                         # پنجره اصلی — ۱۴ برگه
├── integrations.py                 # داشبورد، تب ریسک، برنامههای مادر، ابزار مهندسی، پیشنمایش
├── wizard_engine.py                # موتور ویزارد تولید برنامه/پروسیجر + خروجی Word
├── wizard_library.py               # قالبهای برنامه (۱۰ قالب)
├── wizard_procedures.py            # قالبهای پروسیجر (۱۹ قالب)
├── drilling_risk_analyzer.py       # سیستم تحلیل ریسک (ادغامشده)
├── engineering_calculations.py     # موتور محاسبات مهندسی
├── word_generator.py               # تولید سند Word
├── procedures_db.py                # بانک پروسیجرها (SQLite)
├── seed_procedures_v2.py           # دادههای اولیه پروسیجرها
├── operational_templates.py        # قالبهای عملیاتی
├── presets_module.py               # پریستهای چاه
├── preset_professional.py          # پریستهای حرفهای
├── time_breakdown.py               # زمانبندی عملیات
├── advanced_modules.py             # Kill Sheet، Daily Report، Trip/Tally، Appendix
├── drilling_database.py            # دیتابیس پروژهها
├── cbs_db.py                       # دیتابیس قیمتها (Cost Breakdown Structure — CBS)
├── cbs_ui.py                       # تب «💰 Cost & Pricing» (قیمتهای قابل ویرایش + AFE)
├── seed_f20_timebreakdown.py       # بارگذاری Time Breakdown واقعی چاه AZNS F-20 (نمونه)
├── seed_azns_prices.py             # import جدول قیمت AZNS F-20 Rev#07 → CBS + Time Breakdown
├── programs/                       # اسناد مادر (Master Execution Documents)
│   ├── ESP_Completion_Workover_Master_Execution.md
│   ├── S19_Drilling_Program.md / AZNS-057 / AZNS-031 / SPH-03C
│   └── library/                    # ۲۱۴ سند واقعی (پروسیجرها و برنامهها)
│       ├── INDEX.md                # فهرست دستهبندیشده
│       └── 001_...txt … 214_...txt
├── wizard_references.py            # نگاشت قالبهای ویزارد به اسناد کتابخانه
├── PROGRAM_GAP_ANALYSIS.md         # تحلیل پروسیجرهای ناقص و فایلهای موردنیاز
├── requirements.txt
└── README.md
```

---

## 🗂️ دیتابیسها (بهصورت خودکار ساخته میشوند)

| دیتابیس | مسیر | محتوا |
|---|---|---|
| پروسیجرها | `~/.drilling_program/procedures.db` | پروسیجرها، مراحل، چکلیستها |
| پروژهها | `~/.drilling_program/projects.db` | پروژههای ذخیرهشده |
| زمانبندی | `~/.drilling_program/time_breakdown.db` | فازهای زمانی (+ پروژه نمونه F-20) |
| قیمتها (CBS) | `~/.drilling_program/cbs.db` | کاتالوگ قیمت کالا/خدمات — قابل ویرایش |

پوشههای `projects/`، `logs/`، `config/`، `temp/` کنار برنامه ساخته میشوند.

---

## 📌 نکته درباره نمایش Master Programs

سندهای مادر (مثل ESP Workover) را بهصورت Markdown در پوشه `programs/` بگذارید؛
بهصورت خودکار در برگه «Master Programs» نرمافزار نمایش داده میشوند.
جدولها، چکلیستها، فهرستها و تیترها بهصورت ساختاریافته رندر میشوند.

---

## 🔄 نقشه توسعه (بر اساس PROGRAM_GAP_ANALYSIS.md)

پروسیجرهای اجرایی ESP (اسپلایس، پکر، TRSV، SSD، RTTS، سیمان، Kill Sheet و…) پس از
دریافت فایلهای مرجع به بانک پروسیجرها اضافه خواهند شد — فهرست کامل در
[PROGRAM_GAP_ANALYSIS.md](PROGRAM_GAP_ANALYSIS.md).

## 🧪 اعتبارسنجی جامع خروجی (Output Validation)
```bash
python3 tests/validate_outputs.py     # ۷۲۱ تست — همهٔ قابلیتها با دادهٔ پیشفرض
python3 tests/run_all.py              # کل ۷ سویت (۱۱۸۴ تست)
```
