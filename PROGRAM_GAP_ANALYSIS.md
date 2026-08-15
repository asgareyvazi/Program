# 📋 تحلیل کامل نرمافزار — پروگرمها و پروسیجرهای موجود، ناقص و موردنیاز

**تاریخ:** 2026-08-08
**پروژه:** Drilling Program & Procedure Generator (نسخه یکپارچهشده)
**مخزن:** `asgareyvazi/Program`

> این فایل پاسخ مستقیم به درخواست: «بگو چه پروسیجری یا پروگرمی ناقص است یا چه پروسیجر و پروگرمی میتوانم برایت بفرستم» — بههمراه فهرست دقیق فایلهایی که باید ارسال شوند تا نرمافزار کامل شود.

---

## ۰۰) کتابخانه برنامههای واقعی — ۴ برنامه کامل از کاربر اضافه شد

| # | برنامه | چاه | مشخصات | حجم (پس از تمیزکاری) |
|---|---|---|---|---|
| 1 | `programs/S19_Drilling_Program.md` | S19 (S19 A / S19-B) | افقی — مخزن Sarvak Zone 4 — دکل NIDC Fath 28 — NIOC/PEDEC — ۲۸۱ صفحه | ۲.۶ MB |
| 2 | `programs/AZNS-057_Drilling_Program.md` | AZNS-057 (S331) | Highly Deviated — South Azadegan — Abadan Plain — ۹۳۰۹۲۲ | ۰.۶۵ MB |
| 3 | `programs/AZNS-031_Drilling_Program.md` | AZNS-031 | افقی — Sarvak Oil Producer — Dashte Azadegan — CNPCI-PEDEC / GWDC | ۰.۸۹ MB |
| 4 | `programs/SPH-03C_Drilling_Program.md` | SPH-03C | عمودی — تولیدی — Sepehr-Jufair — مخزن Lower Fahliyan — Rig 27 Fath | ۱.۶ MB |

- هر ۴ برنامه داخل **Master Programs** نرمافزار هستند (رندر سریع + جستجو در متن).
- این برنامهها مرجع ساخت **قالب پیشرفته Wizard** (بخش ۰.۱) شدند.

## ۰.۱) حالت جدید: تولیدکننده عمومی برنامه/پروسیجر (Wizard) — نسخه ۳.۲

> «یک برنامه حفاری میخوام» → کاربر **نوع سند** را انتخاب میکند → **سکشنهای موردنظر را تیک میزند** → ورودیها را پر میکند → **فونت/صفحهبندی/جلد/TOC** را تنظیم میکند → سند Word کامل و قابل ویرایش تحویل میگیرد.

### جریان کامل (طبق تأیید کاربر)

| مرحله | چه اتفاقی میافتد |
|---|---|
| ۱. نوع سند | لیست دوستانه (برنامه/پروسیجر) — قالبها برای کاربر نمایش داده نمیشوند |
| ۲. انتخاب سکشنها | چکباکس برای هر بخش سند (مثلاً ۱۷ بخش برنامه حفاری) — سکشنهای انتخابنشده حذف میشوند |
| ۳. ورودیها | فرم پویا گروهبندیشده + دکمه 🌐 Web Research برای معرفی میدان/سازند |
| ۴. تنظیمات خروجی | فونت، اندازه فونت، صفحه A4/Letter، عمودی/افقی، حاشیهها، جلد، فهرست مطالب (فیلد Word)، سرصفحه/پاصفحه |
| ۵. تولید | سند .docx قابل ویرایش — فیلدهای خالی بهصورت `[To Be Filled]` |

### اصول پیادهسازیشده

1. **کتابخانه = منبع ایده، نه کپی** — ۲۱۹ سند واقعی فقط برای ساختار/دانش/چکلیست استفاده میشوند.
2. **حذف اسم شرکتها + درج اسم کاربر** — تابع `neutralize_text(متن, operator_name, contractor_name)`: نامهای NISOC/PECO/OEOC/CNPCI/GWDC/SLB/Halliburton/... (لیست سیاه گسترده ~۵۰ مورد) حذف و بهجای آنها **نام اپراتور/پیمانکار واردشده توسط کاربر** جایگزین میشود (در بدنه، صفحه جلد، دانش و ریسک). الگوریتم امن با placeholder موقت: اگر اسم کاربر خودش شامل توکن ممنوعه باشد (مثل «PEDEC Oil Co») خراب نمیشود؛ توکنهای مشترک اولویت اپراتور دارند.
3. **انتخاب سکشن** — `extract_sections` / `render_selected` هر قالب را به سکشنهای `##` تقسیم میکند.
4. **کنترل چیدمان Word** — فونت/اندازه/صفحه/حاشیه/جلد/TOC/سرصفحه-پاصفحه در `md_to_docx`.
5. **جستجوی اینترنت** — `wizard_web.py`: ویکیپدیا REST + DuckDuckGo Instant Answer، بدون API key؛ پیشنهاد جستجو برای هر نوع سند؛ خروجی با ذکر منبع درج میشود.
6. **جای خالی** — همه فیلدهای خالی `[To Be Filled]` میمانند.
7. **📋 ROPE Field Checklists** — متن کامل R.O.P.E. Manual (Rig Operations Performance Execution — ۵۵+ چکلیست عملیاتی و تجهیزاتی) در `programs/library/ROPE_Manual.txt` ذخیره و در `wizard_rope.py` بهصورت ساختاریافته پارس شده؛ بر اساس نوع سند، چکلیستهای مرتبط (BHA/Bit/Casing/Cementing/Plug/Tripping/Well Control/Stuck Pipe/CT/Slickline/HPHT/Fishing/H2S/BOP و...) با سطح Brief/Moderate/Detailed به خروجی اضافه میشوند (واژهنامه در Detailed). نام شرکتها (Schlumberger/IPM/Dowell/Varco/Vetco/TIW/...) از همه خروجیها حذف و با نام اپراتور/پیمانکار کاربر جایگزین میشود.
8. **🤖 LLM Rewriting** — دکمه «LLM Settings»: Ollama (محلی) / Gemini / HuggingFace. متنهای منتخب کتابخانه توسط AI بازنویسی میشوند؛ fallback خودکار به متن خام خنثیشده وقتی LLM در دسترس نیست.
8. **🧠 Field Knowledge Enrichment (ML)** — سکشن مستر از رابط کاربری حذف شد؛ کتابخانه ۲۱۹ سندی **فقط داخلی** است. موتور بازیابی `wizard_knowledge.py` با **TF-IDF (ML کلاسیک، بدون وابستگی)** و در صورت نصب `sentence-transformers` با **Embedding معنایی**، مرتبطترین چکلیستها/مراحل/پروسیجرهای واقعی را برای هر نوع سند انتخاب میکند و (پس از حذف نام شرکتها) بهصورت سکشن «FIELD KNOWLEDGE ENRICHMENT» در خروجی درج میکند. سطح غنیسازی: Brief / Moderate / Detailed.
8. **🔍 Risk Review یکپارچه (پاسخ به سؤال کاربر: «آیا ریسک آنالایزر با برنامه مچ هست؟»)** — قبل از تولید نهایی، ویزارد توالی عملیات را از سکشنهای انتخابشده + ورودیها میسازد (`wizard_risk.build_sequence_from_document`)، با موتور ریسک تحلیل میکند (`AnalysisEngine` — همان پایگاه دانش تب Risk Analyzer)، خطرات Critical/High و NPT مورد انتظار را به کاربر نشان میدهد، **سؤالهای تأیید میپرسد** (مثلاً «آیا H2S monitoring در برنامه است؟») و پاسخها را بههمراه جدول ریسکها، اقدامات Contingency و چکلیست بهترینروشها بهعنوان سکشن **«RISK ASSESSMENT & CONTINGENCY PLAN»** داخل سند Word نهایی درج میکند.

### قالبهای برنامه (۱۴ عدد)

| قالب | نوع | ورودیها | منبع |
|---|---|---|---|
| **Advanced Drilling Program** | برنامه | **۹۳** | ⭐ NIOC/بینالمللی (بر اساس S19/AZNS) |
| Drilling Program (New Well) | برنامه | ۳۸ | استاندارد |
| HPHT Drilling Program | برنامه | ۳۱ | دریای شمال / Shell-NORSOK |
| Deepwater Drilling Program | برنامه | ۳۷ | خلیج مکزیک / API RP 96 |
| Horizontal Shale / ERD Program | برنامه | ۳۶ | شیل آمریکای شمالی |
| Workover Program (General) | برنامه | ۳۵ | عمومی |
| ESP Workover Program (سند AZNS) | برنامه | ۱۰ + جایگزینی خودکار توکنها | سند کاربر |
| Well Abandonment (P&A) | برنامه | ۲۵ | NORSOK D-010 |
| Well Kill Operation | برنامه | ۲۲ | API RP 59 |
| Cementing Job | برنامه | ۵۲ | API RP 10B |
| Well Testing / DST | برنامه | ۲۹ | استاندارد |
| Fishing Operation | برنامه | ۳۴ | IADC |
| Stimulation (Acid/Frac) | برنامه | ۳۵ | استاندارد |
| Coiled Tubing Operation | برنامه | ۲۵ | API 5C7 |
| Tripping (POOH/RIH) | پروسیجر | ۱۹ |
| Running Casing | پروسیجر | ۲۲ |
| BOP Pressure Test | پروسیجر | ۲۰ |
| Kick Circulation (Driller's Method) | پروسیجر | ۱۴ |
| Stuck Pipe / Jarring | پروسیجر | ۲۶ |
| Slickline (Plug/SSD) | پروسیجر | ۲۰ |
| ESP Running | پروسیجر | ۲۱ |
| Packer Setting | پروسیجر | ۱۶ |
| Perforation (Wireline/TCP) | پروسیجر | ۱۷ |
| DST | پروسیجر | ۲۷ |
| Wellhead Installation | پروسیجر | ۱۲ |
| Lost Circulation Treatment | پروسیجر | ۲۷ |
| Rig Move & Rig-Up | پروسیجر | ۱۰ |
| H2S Emergency Response | پروسیجر | ۱۵ |
| Tubing Pressure Test | پروسیجر | ۱۳ |
| BHA Make-Up | پروسیجر | ۱۲ |

**پاسخ به سؤال «میتونی ادامه بدی یا فایل میخایی؟»:**
- ✅ **پایه کامل است** — این ۳۰ قالب (۱۴ برنامه + ۱۶ پروسیجر) از دانش جهانی صنعت (API، ISO، NORSOK، IADC، Shell DEP، Aramco SAES) + ۴ برنامه واقعی کاربر ساخته شده و همین الان کار میکند.
- 📬 **فایلها فقط برای شخصیسازی لازم هستند** — اگر سند رسمی شرکتت (مثل AZNS-093) یا پروسیجر vendor را بفرستی، همان را بهعنوان قالب/مرجع اضافه میکنم تا خروجی دقیقاً با رویههای شرکتت منطبق شود.
- 🔁 هر قالب جدیدی که بفرستی، با همان ساختار (ورودی → سند Word) داخل ویزارد قرار میگیرد.

---

## ۱) خلاصه وضعیت نرمافزار بعد از یکپارچهسازی

| بخش | وضعیت | توضیح |
|---|---|---|
| **ویزارد تولید برنامه/پروسیجر** | ✅ جدید | ۱۰ برنامه + ۱۶ پروسیجر با ورودیهای هوشمند و خروجی Word |
| **پنجره اصلی (main.py)** | ✅ کامل | ۱۴ تب: داشبورد، دادهها، ریسک، مهندسی، برنامههای مادر |
| **تولید سند Word (word_generator.py)** | ✅ فعال | تولید سند کامل Drilling Program با جدولها و فرمت حرفهای |
| **بانک پروسیجرها (procedures_db.py + seed_procedures_v2.py)** | ✅ فعال | ۵۳ پروسیجر گامبهگام + چکلیست + خروجی Word |
| **قالبهای عملیاتی (operational_templates.py)** | ✅ فعال | کتابخانه قالب فازبهمرحله با پارامترهای قابل تنظیم |
| **قالبهای چاه (presets_module.py / preset_professional.py)** | ✅ فعال | ۸+ پریست حرفهای (خاورمیانه H2S، دریای شمال HPHT، خلیج مکزیک و…) |
| **تحلیل ریسک حفاری (drilling_risk_analyzer.py)** | ✅ **ادغام شد** | داخل نرمافزار بهصورت تب کامل — بدون کم شدن هیچ قابلیتی (پایگاه ریسک، برنامههای Contingency، چکلیست موارد فراموششده، پشتیبان AI) |
| **محاسبات مهندسی (engineering_calculations.py)** | ✅ **وصل شد** | رابط کاربری جدید: تبدیل واحد، هیدرولیک، صحتسنجی Casing، سیمان، کنترل چاه، Torque & Drag |
| **زمانبندی (time_breakdown.py)** | ✅ فعال | ویرایشگر زمان فازها با دیتابیس |
| **ماژولهای پیشرفته (advanced_modules.py)** | ✅ فعال | Kill Sheet، Daily Report، Trip/Tally Sheet، Cost Estimator، Appendixها |
| **دیتابیس پروژه (drilling_database.py)** | ✅ فعال | ذخیره/بازیابی پروژهها |
| **برنامههای مادر (Master Programs)** | ✅ **اضافه شد** | سند کامل ESP Completion Workover داخل نرمافزار (برگه Master Programs) |
| **داشبورد (Home)** | ✅ **اضافه شد** | دسترسی سریع به همه ابزارها + آمار کتابخانه + پروژههای اخیر |

---

## ۲) اشکالات نرمافزار که در این نسخه برطرف شد

| # | اشکال | محل | وضعیت |
|---|---|---|---|
| 1 | `DataFormatter.force` وجود نداشت → خطا در تولید سند | word_generator.py | ✅ اضافه شد |
| 2 | `ReportFormat` در مسیر جایگزین تعریف نشده بود → خطا در Generate | main.py | ✅ اصلاح شد |
| 3 | آیتمهای تکراری و بیاستفاده در منوی Templates | main.py | ✅ پاکسازی شد |
| 4 | `_quick_load_preset` با روش ناپایدار `__new__` کار میکرد | main.py | ✅ بازنویسی شد |
| 5 | `New Project` تبها را خالی نمیکرد | main.py | ✅ بازنویسی شد (Reset کامل همه تبها) |
| 6 | `Preview` فقط پیام نمایش میداد | main.py | ✅ پیشنمایش واقعی سند اضافه شد |
| 7 | تحلیلگر ریسک فقط بهصورت جدا اجرا میشد | — | ✅ داخل نرمافزار ادغام شد |
| 8 | موتور محاسبات مهندسی رابط کاربری نداشت | — | ✅ برگه Engineering Tools اضافه شد |
| 9 | سند ESP شما در جایی نگهداری نمیشد | — | ✅ فایل `programs/ESP_Completion_Workover_Master_Execution.md` + نمایشگر داخل نرمافزار |

---

## ۳) پروسیجرها/پروگرمهای **کامل** در نرمافزار (نیازی به ارسال مجدد نیست)

این موارد بهصورت ساختاریافته در بانک پروسیجرها یا قالبها موجودند:

1. **Drilling Program Generator** — تولید کامل برنامه حفاری (شرکت/چاه، سازندها، Casing، گل، BHA، سیمان، جهتی، BOP، دکل، زمان)
2. **Procedure Manager** — ۵۳ پروسیجر گامبهگام شامل: حفاری سکشنها، لولهگذاری، سیمانکاری، کنترل چاه، Core، DST، آزادسازی رشته (jarring)، Fish، و…
3. **قالبهای عملیاتی** — فازهای RIH/POOH، گیرکردن لوله، هرزروی، هرزروی شدید، کنترل چاه، H2S…
4. **پریستهای چاه** — خاورمیانه H2S، شیرین، Jack-Up، HPHT، Deepwater، Shale افقی، ERD، زمینگرمایی
5. **ابزارهای مهندسی** — هیدرولیک، صحتسنجی Casing، سیمان، MAASP/Kick Tolerance، تبدیل واحد
6. **تحلیل ریسک** — ۲۵۴۱+ مورد ریسک و ۱۰۰+ مورد «فراموششده» در پایگاه داده + برنامههای Contingency

---

## ۴) پروسیجرها/پروگرمهای **ناقص یا گمشده** — مخصوص پروژه ESP (AZNS-XXX)

> مبنای این تحلیل: سند «ESP Completion Workover – Master Execution Document» که ارسال کردی + استانداردهای صنعت.
> سند شما یک **Master Document (چارچوب کلی)** است؛ برای اجرای واقعی، پروسیجرهای اجرایی زیر باید به نرمافزار اضافه شوند:

### ۴.۱ — پروسیجرهای اجرایی که در سند فقط **ارجاع** شدهاند و متن کاملشان موجود نیست

| # | پروسیجر ناقص | کجا ارجاع شده | برای تکمیل چه چیزی لازم است |
|---|---|---|---|
| P-01 | **AZNS-093 Workover Program Rev-04** (برنامه کامل کار روی چاه) | بخش ۱.۴ | کل برنامه کار چاه AZNS-093 |
| P-02 | **CK-17 ESP Cable Splice Report** (گزارش اسپلایس کابل) | بخش ۱.۴ | متن کامل گزارش + Acceptance Criteria |
| P-03 | **ESP Assembly & Running Procedure** (مونتاژ و ران کردن پمپ) | بخش ۶.۱ #۹ | پروسیجر کامل vendor (پمپ/موتور/پروتکتور/گاز سپریتور/شیرود) |
| P-04 | **ESP Cable Splice Procedure کامل** | بخش ۹ | پروسیجر گامبهگام اسپلایس با ابعاد، ابزارها، تست IR/اهم |
| P-05 | **Packer Setting / Release Procedure** | بخش ۶.۱ #۶ | پروسیجر کامل نشستن/آزادسازی پکر ۹-۵/۸" با AGV |
| P-06 | **TRSV Function Test Procedure** | بخش ۶.۱ #۷ | تست عملکرد TRSV (باز/بسته، Control Line، نشتی) |
| P-07 | **SSD Shifting Procedure** | بخش ۶.۱ #۸ | روش جابجایی SSD با Slickline + مشخصات Profile |
| P-08 | **Wellhead Installation Manual (THS/THA/XMT)** | بخش ۶.۱ #۱۱-۱۲ | دفترچه نصب، گشتاور بولتها، P-seal، تست |
| P-09 | **Corrosion Logging Procedure** | بخش ۶.۱ #۱۴ | پروسیجر لاگ خوردگی (ابزار، سرعت، کالیبراسیون) |
| P-10 | **Tubular Inspection Specification** | بخش ۶.۱ #۱۵ | مشخصات بازرسی لولهها (دریفت، ضخامت، نخها) |
| P-11 | **DME Emulsion Mixing Procedure (جزئیات)** | بخش ۵.۷ | فرمول دقیق: نسبت آب/گازوئیل، مقدار افزودنی، همزدن |
| P-12 | **RTTS Setting & Retrieval Procedure** | بخش ۵.۳ | پروسیجر کامل RTTS برای تعویض THS |
| P-13 | **BOP Test Matrix (جدول کامل تست)** | بخش ۳.۲ | فشارها و ترتیب تست هر جزء BOP |
| P-14 | **Kill Sheet (برگه مهار چاه)** | بخش ۲ | برگه کامل kill با DME emulsion (فشار، حجم، چگالی) |
| P-15 | **Cementing Procedure (پلاگ سیمان داخل لاینر ۷")** | بخش ۵.۲ | حجم، چگالی، WOC، تست خشک |

### ۴.۲ — اقلامی که در سند ذکر شدهاند اما **جزئیات/فایل ندارند**

| # | قلم | وضعیت |
|---|---|---|
| I-01 | نقشه نهایی Completion Diagram (پیوست A) | خالی است — باید ارسال شود |
| I-02 | Tubing Tally نهایی (پیوست B) | خالی است |
| I-03 | نقشه Wellhead GA (پیوست C) | خالی است |
| I-04 | گشتاورهای OEM همه نخها (بخش ۶.۱ #۱۳) | فقط ۵ ردیف در ضمیمه D — جدول کامل لازم است |
| I-05 | حلقههای Ring Gasket (پیوست E) | ردیف THA-to-THS «[Confirm]» مانده |
| I-06 | مشخصات VSD/ترانسفورماتور/کابل ۳۳kV | در سند [model] است |
| I-07 | مشخصات کامل ESP (موتور HP، پمپ، سنسور) | در سند [model] است |
| I-08 | دادههای چاه (فشار، دما، عمقها، RTE) | همه [To Be Confirmed] هستند |
| I-09 | **CCCP طراحی/نقشه** | فقط تعداد (±۱۳۰/±۱۱۰) ذکر شده |
| I-10 | **ESP Startup Procedure (VSD ramp-up)** | فقط «شروع با ۳۰Hz» — پروسیجر کامل لازم است |
| I-11 | **H2S Contingency Plan** (چاه H2S است!) | فقط اشاره شده — طرح کامل HSE/H2S لازم است |
| I-12 | **Lessons Learned کاملتر** | ۱۷ مورد موجود — گزارش کامل چاههای قبلی مفید است |

---

## ۵) فایلهایی که باید برایم ارسال کنی (اولویتبندی شده)

> فرمت پیشنهادی: **Word (.docx)** یا **PDF** برای اسناد، و **Excel (.xlsx)** برای جدولها/تالیها. اگر فایل نرمافزاری (Python) داری، همان را بفرست.

### اولویت ۱ — بحرانی (بدون آنها، پروژه ESP قابل اجرا نیست)

| # | فایل | دلیل |
|---|---|---|
| 1 | **AZNS-093 Workover Program Rev-04** | برنامه مرجع اصلی کار چاه — کل مراحل روی آن سوار است |
| 2 | **CK-17 ESP Cable Splice Report** | اسپلایس مهمترین نقطه شکست ESP است |
| 3 | **ESP Vendor Manuals** (assembly, running, splice, packer, AGV, penetrators) | همه پروسیجرهای اجرایی ESP از اینجا میآید |
| 4 | **Wellhead Vendor Manuals** (THS/THA/XMT، penetrator rod، P-seal، تست) | تعویض THS بدون آن ممکن نیست |
| 5 | **TRSV / SSD Vendor Procedures** | تست و عملکرد این دو ابزار حیاتی است |

### اولویت ۲ — مهم (برای تکمیل بخشهای فنی سند)

| # | فایل |
|---|---|
| 6 | Corrosion Logging Procedure (شرکت لاگگیری) |
| 7 | Tubular Inspection Specification (QC/TPI) |
| 8 | DME Emulsion Mixing Procedure (شرکت شیمیایی) |
| 9 | RTTS / Cementing Service Procedures |
| 10 | جدول گشتاور کامل نخها (OEM) + نقشههای Completion/Tally/Wellhead |
| 11 | دادههای چاه AZNS-XXX (DDR/EOWR نهایی، فشارها، دماها، عمقها) |
| 12 | گزارشهای روزانه و Lessons Learned چاههای قبلی (اگر موجود است) |

### اولویت ۳ — اختیاری (برای غنیتر شدن نرمافزار)

| # | فایل |
|---|---|
| 13 | نمونه Kill Sheet پر شده از عملیات قبلی |
| 14 | قالب Daily Report / فرمهای تست الکتریکی و فشار |
| 15 | هر پروسیجر/برنامه دیگری که داری (حفاری، تکمیلی، تعمیری) — **به هر شکلی بفرست؛ من ساختاریافته داخل نرمافزار میگذارم** |

---

## ۶) نقشه راه — بعد از دریافت فایلها چه میکنم

1. **دریافت و ساختاردهی:** هر فایل را به بخشهای گامبهگام (Steps)، چکلیست (Checklist)، پارامترهای ورودی و تستها تقسیم میکنم.
2. **ورود به بانک پروسیجرها:** پروسیجرها وارد `procedures_db` میشوند تا از طریق Procedure Manager قابل جستجو، ویرایش و خروجی Word باشند.
3. **تکمیل سند مادر ESP:** جای [To Be Confirmed] / [model] ها با دادههای واقعی پر میشود و نسخه نهایی در `programs/` بهروزرسانی میشود.
4. **قالب ESP Workover:** یک پریست «ESP Workover» کامل میسازم تا با یک کلیک، برنامه ESP برای هر چاه جدید ساخته شود.
5. **گزارش:** بعد از هر مرحله، تغییرات را گزارش میدهم.

---

## ۷) ساختار جدید فایلهای نرمافزار

```
Program/
├── launcher.py                     # نقطه ورود (GUI / --sample / --check / --install)
├── main.py                         # پنجره اصلی + ۱۴ برگه + منوها
├── integrations.py                 # ⭐ جدید: داشبورد، تب ریسک، تب برنامههای مادر، ابزار مهندسی، پیشنمایش
├── wizard_engine.py                # ⭐ موتور ویزارد: ورودیها ← سند Word
├── wizard_library.py               # ⭐ ۱۰ قالب برنامه (Drilling/Workover/ESP/P&A/Kill/…)
├── wizard_procedures.py            # ⭐ ۱۶ قالب پروسیجر (Tripping/BOP/Kick/ESP/…)
├── drilling_risk_analyzer.py       # ⭐ تحلیلگر ریسک (ادغامشده در نرمافزار)
├── engineering_calculations.py     # موتور محاسبات مهندسی (حالا با رابط کاربری)
├── word_generator.py               # تولید سند Word
├── procedures_db.py                # بانک پروسیجرها
├── seed_procedures_v2.py           # دادههای اولیه پروسیجرها
├── operational_templates.py        # قالبهای عملیاتی
├── presets_module.py               # پریستهای چاه
├── preset_professional.py          # پریستهای حرفهای
├── time_breakdown.py               # زمانبندی
├── advanced_modules.py             # Kill Sheet، گزارش روزانه، ضمائم و…
├── drilling_database.py            # دیتابیس پروژهها
├── programs/                       # ⭐ اسناد مادر (Master Execution Documents)
│   └── ESP_Completion_Workover_Master_Execution.md
├── PROGRAM_GAP_ANALYSIS.md         # ⭐ همین فایل
├── requirements.txt                # وابستگیها
└── README.md                       # راهنمای نصب و استفاده
```

---

## ۸) جمعبندی

- ✅ نرمافزار **بازطراحی و یکپارچه شد** بدون کم شدن هیچ قابلیتی — همه ماژولهای قبلی سر جایشان هستند و کار میکنند.
- ✅ **drilling_risk_analyzer** کامل داخل نرمافزار قرار گرفت (برگه «Risk Analyzer»).
- ✅ سند **ESP Completion Workover** شما بهصورت کامل داخل نرمافزار بارگذاری شد (برگه «Master Programs»).
- ⏳ **۱۳ پروسیجر اجرایی + ۱۲ قلم اطلاعاتی** برای تکمیل پروژه ESP لازم است (بخشهای ۴ و ۵).
- 📬 **فایلهای اولویت ۱ را هرچه زودتر بفرست** — بقیه را هم به مرور.
