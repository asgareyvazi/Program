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
- **🧪 Reference Test Suite** — تستهای مرجع مهندسی با تلورانس پذیرش (Hydrostatic، MAASP، KMW، Annular Velocity، Casing Burst API، Well Cost) — اجرا: `python tests/test_engineering_reference.py` (۲۱ تست)
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
