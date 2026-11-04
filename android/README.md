# تطبيق محفظتي برو للأندرويد

هذا المشروع عبارة عن Trusted Web Activity (TWA) يفتح تطبيق الويب الرسمي داخل تجربة Android مستقلة، مع الحفاظ على تسجيل الدخول والبيانات والمزامنة الحالية. مصدر التطبيق هو:

- https://mohafzatypro.com/app/

## بيانات التطبيق

- اسم التطبيق: محفظتي برو
- Application ID: `com.mohafzatypro.app`
- الإصدار الأول: `1.0.0`
- أقل إصدار Android: API 23

## إعداد توقيع APK في GitHub Actions

أضف القيم التالية من إعدادات المستودع: Settings → Secrets and variables → Actions → New repository secret.

- `ANDROID_KEYSTORE_BASE64`: محتوى ملف keystore بعد تحويله إلى Base64.
- `ANDROID_STORE_PASSWORD`: كلمة مرور ملف keystore.
- `ANDROID_KEY_PASSWORD`: كلمة مرور المفتاح.
- `ANDROID_KEY_ALIAS`: اسم المفتاح.

لا ترفع ملف keystore أو كلمات المرور إلى GitHub أو إلى أي مجلد داخل المستودع.

## بناء APK

بعد إعداد الأسرار، شغّل workflow المسمى **Build Android APK** من تبويب Actions. عند نجاح البناء، ينشئ workflow إصدار GitHub يحتوي على:

`mohafzaty-pro-android.apk`

رابط التنزيل الثابت:

`https://github.com/geemytop000/mohafzaty-windows/releases/latest/download/mohafzaty-pro-android.apk`

## التحقق من النطاق

يجب أن يكون الملف التالي منشورًا على الموقع:

`https://mohafzatypro.com/.well-known/assetlinks.json`

ويجب أن يحتوي على بصمة شهادة التوقيع المستخدمة في بناء APK. تغيير مفتاح التوقيع مستقبلًا يتطلب تحديث هذا الملف، كما يمنع Android تثبيت تحديث موقّع بمفتاح مختلف فوق النسخة السابقة.

## إصدار تحديث

زد `versionCode` و`versionName` في `app/build.gradle`، ثم شغّل workflow مرة أخرى. احتفظ بنسخة احتياطية آمنة من ملف التوقيع وكلمات مروره.
