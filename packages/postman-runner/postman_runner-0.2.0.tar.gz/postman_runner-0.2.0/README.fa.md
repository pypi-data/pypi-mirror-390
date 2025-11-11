# راهنمای استفاده از Postman Runner محلی

این پروژه یک ابزار خط فرمانی است که کالکشن‌های Postman را بدون نیاز به خود Postman اجرا می‌کند. با آن می‌توانید درخواست‌های واحد یا مجموعه‌ای را شبیه‌سازی و نتایج را همراه با آزمون‌های تعریف‌شده مشاهده کنید.

## پیش‌نیازها
- Python 3.10 یا جدیدتر
- نصب پکیج‌های موردنیاز با اجرای `pip install -r requirements.txt`

### راه‌اندازی محیط مجازی (اختیاری، ولی توصیه‌شده)
```bash
python3 -m venv .venv
source .venv/bin/activate  # در ویندوز: .venv\Scripts\activate
pip install -r requirements.txt
```

## ساختار کلی
- `postman_runner/cli.py`: نقطه ورود خط فرمان
- `postman_runner/collection_parser.py`: خواندن و نرمال‌سازی کالکشن‌ها
- `postman_runner/environment.py`: بارگذاری و اعمال متغیرهای محیطی Postman
- `postman_runner/executor.py`: اجرای درخواست HTTP با استفاده از `requests`
- `postman_runner/assertions.py`: پیاده‌سازی آزمون‌ها

## نحوه اجرای کالکشن
1. از داخل Postman کالکشن موردنظر را با فرمت Collection v2.1 به صورت JSON خروجی بگیرید.
2. فایل خروجی را به همراه فایل‌های Environment (در صورت نیاز) کنار هم قرار دهید.
3. دستور پایه برای اجرا:
   ```bash
   python3 -m postman_runner.cli --collection path/to/collection.json --request-name "Request Name"
   ```
   - نام درخواست باید دقیقاً مطابق مقدار `name` در کالکشن باشد (`postman_runner/collection_parser.py:14`).

### مشاهده لیست درخواست‌ها
```bash
python3 -m postman_runner.cli --collection path/to/collection.json --list
```
این دستور نام تمام درخواست‌های قابل اجرا را چاپ می‌کند (`postman_runner/cli.py:20`).

## اجرای تمام سرویس‌های موجود در کالکشن و ذخیره لاگ
- برای اجرای پشت سر هم تمام درخواست‌های موجود در یک کالکشن تنها کافی است از `--run-all` استفاده کنید:
  ```bash
  python3 -m postman_runner.cli --collection path/to/collection.json --run-all
  ```
- خروجی هر سرویس (متد، URL، وضعیت، هدرها، بدنه و نتیجه‌ی Assertion ها) پشت سر هم در ترمینال چاپ می‌شود و در انتها یک جمع‌بندی PASS/FAIL برای همه درخواست‌ها نمایش داده می‌شود (`postman_runner/cli.py:125`).
- اگر مسیر خاصی برای لاگ تعیین نکنید، کنار فایل کالکشن پوشه‌ای به نام `logs` ساخته می‌شود و گزارش کامل در فایلی مانند `<collection_name>_run.log` ذخیره خواهد شد (مثلاً `my_collection_run.log`).
- با `--log-file` می‌توانید موقعیت دیگری تعیین کنید؛ به عنوان مثال:
  ```bash
  python3 -m postman_runner.cli --collection path/to/collection.json --run-all --log-file reports/all.log
  ```
  این فایل شامل خروجی هر سرویس و خلاصه‌ی پایانی است (`postman_runner/cli.py:149`).
- امکان ترکیب متغیرهای Environment و Assertion های اضافه در این حالت نیز برقرار است؛ کافی است همانند اجرای تکی، سوییچ‌های `--environment` و `--assert-json` را اضافه کنید تا روی همه درخواست‌ها اعمال شوند.
- برای تست سریع، می‌توانید از نمونه‌ی `samples/httpbin_collection.json` استفاده کنید که دو سرویس GET ساده با Assertion تعریف‌شده دارد.

## استفاده از Environment ها
- برای مشخص‌کردن فایل Environment به صورت مستقیم:
  ```bash
  python3 -m postman_runner.cli --collection collection.json --request-name "Request" --environment environments/dev.postman_environment.json
  ```
- اگر مقدار `--environment` یک پوشه باشد، برنامه فایل‌های محیطی داخل آن را پیدا می‌کند و لیستی تعاملی نمایش می‌دهد (`postman_runner/cli.py:102`).
- بدون تعیین صریح Environment، برنامه پوشه‌ی کالکشن را بررسی می‌کند و در صورت یافتن چند فایل، از شما می‌پرسد کدام مورد استفاده شود.
- متغیرهای قالبی مانند `{{baseUrl}}`، `{{apiKey}}` و غیره در URL، هدرها، بادی و حتی assertion ها به طور خودکار جایگزین می‌شوند (`postman_runner/environment.py:38`).

> نکته: در حالت غیرتعاملی (مثلاً CI) اگر چند محیط یافت شود باید مسیر دقیق را با `--environment` مشخص کنید؛ در غیر این صورت اجرای برنامه متوقف می‌شود.

## اعمال Assertion های اضافه
می‌توانید فایل JSON دیگری برای آزمون‌های تکمیلی معرفی کنید:
```bash
python3 -m postman_runner.cli --collection collection.json --request-name "Request" --assert-json extra_assertions.json
```
این فایل هم تحت تأثیر متغیرهای Environment قرار می‌گیرد (`postman_runner/cli.py:52`).

## اجرای درخواست بدون کالکشن
در صورتی که بخواهید فقط یک درخواست ساده اجرا کنید:
```bash
python3 -m postman_runner.cli --inline '{
  "name": "Quick check",
  "method": "GET",
  "url": "{{baseUrl}}/status",
  "headers": {"Accept": "application/json"},
  "assertions": {"status_code": 200}
}' --environment environments/dev.postman_environment.json
```
یا می‌توانید تعریف درخواست را داخل فایل JSON ذخیره کرده و با `--inline-file path/to/request.json` اجرا کنید (`postman_runner/cli.py:35`).

## تنظیم Timeout
با `--timeout` مقدار پیش‌فرض ۳۰ ثانیه‌ای را تغییر دهید:
```bash
python3 -m postman_runner.cli --collection collection.json --request-name "Slow Request" --timeout 60
```

## خروجی برنامه
پس از اجرای درخواست:
- وضعیت (`Status`) و هدرها چاپ می‌شوند (`postman_runner/cli.py:67`).
- متن پاسخ دقیقاً نمایش داده می‌شود.
- اگر assertion تعریف شده باشد، نتیجه‌ی هر آزمون با PASS/FAIL گزارش می‌شود (`postman_runner/test_runner.py:6`).

## عیب‌یابی
- خطای «Request '...' not found» یعنی نام درخواست با کالکشن همخوانی ندارد یا ساختار کالکشن متفاوت است.
- اگر متغیری جایگزین نشد، از فعال بودن آن در فایل Environment مطمئن شوید؛ فقط مقادیر `enabled` پذیرفته می‌شوند (`postman_runner/environment.py:24`).
- برای درخواست‌های Form-Data نوع فایل، مسیر `src` باید روی سیستم در دسترس باشد (`postman_runner/executor.py:31`).

## توسعه بیشتر
- اضافه‌کردن پوشش تست واحد برای جایگزینی متغیرها
- پشتیبانی از به‌روزرسانی متغیرهای پس از اجرای درخواست (feature پیشنهادی)
- افزودن خروجی HTML یا گزارش خلاصه برای CI

با اجرای `python3 -m postman_runner.cli --help` می‌توانید تمام پارامترهای موجود را مشاهده کنید.
