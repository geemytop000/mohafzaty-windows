نسخة Windows (ملف تثبيت .exe) — بتتبني على GitHub مجانًا
====================================================
الملف ده مشروع جاهز. مش محتاج تفتح كود. الخطوات:

1) افتح الموقع  github.com  واعمل حساب مجاني.
2) اضغط New repository واكتب أي اسم (مثلاً mohafzaty-windows) واضغط Create.
3) اضغط "uploading an existing file" وارفع كل محتويات فولدر windows-installer
   (بما فيها فولدر .github). لو فولدر .github مش بيظهر، ارفعه بالسحب والإفلات.
4) رابط البرنامج مضبوط بالفعل على موقعك الحالي:
   https://96524af6.mohafzaty-pro.pages.dev/app/
   مش محتاج تغيّر أي حاجة في main.js.
5) من تبويب Actions اضغط "Build Windows installer" ثم Run workflow.
6) بعد ما يخلص (حوالي 5 دقايق) افتح العملية ونزّل ملف mohafzaty-pro-windows-installer فيه ملف الـ .exe.

ملحوظات صريحة:
- الملف ده ماتجرّبش عندي (بيئتي مفيهاش Windows)، فاعتبره أول تجربة وقولي لو حصل أي خطأ.
- ملف التثبيت غير موقّع رقميًا، فـ Windows ممكن يظهر تحذير "Windows protected your PC".
  العميل يضغط More info ثم Run anyway. إزالة التحذير محتاجة شهادة توقيع مدفوعة.
- التثبيت من المتصفح (Edge أو Chrome > Install app) بيدّي نفس النتيجة من غير تحذيرات ومجانًا.
