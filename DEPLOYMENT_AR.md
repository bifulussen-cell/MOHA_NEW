# نشر MOHA من هاتف Android

## قبل النشر
هذه حزمة إعداد أولي وليست شهادة أمان أو ضمان تشغيل الإنتاج.
لا ترفع أي ملف .env يحتوي على كلمات مرور أو مفاتيح.
لا تنشر الخدمة للعامة قبل اختبار التسجيل، الصلاحيات، الرفع، والدردشة البيطرية.

## 1. GitHub
ارفع محتويات هذا المجلد إلى فرع تجريبي أو مستودع خاص جديد.
احتفظ بالمشروع الأصلي MOHA دون تغيير حتى تنجح الاختبارات.

## 2. MongoDB Atlas
أنشئ قاعدة بيانات، ومستخدم قاعدة بيانات بكلمة مرور قوية، واضبط Network Access بشكل محدود قدر الإمكان.
انسخ رابط الاتصال في MONGO_URL داخل متغيرات Render السرية.

## 3. Render (الخادم)
أنشئ Blueprint من GitHub باستخدام render.yaml أو Web Service يدويًا:
Root Directory: backend
Build: pip install -r requirements.txt
Start: uvicorn server:app --host 0.0.0.0 --port $PORT
Health Check: /health
أضف متغيرات MONGO_URL و DB_NAME و SECRET_KEY و CORS_ORIGINS و EMERGENT_LLM_KEY (إذا كانت خدمة AI متاحة).
قد تفشل عملية البناء بسبب تبعيات قديمة؛ افحص سجل Render ولا تطلق الموقع قبل إصلاحها.

## 4. Cloudflare Pages (الواجهة)
اربط مستودع GitHub.
Root directory: frontend
Build command: npm install --legacy-peer-deps && npm run build
Build output directory: build
Environment variable at BUILD time:
REACT_APP_BACKEND_URL=https://YOUR-RENDER-SERVICE.onrender.com
أعد البناء بعد تغيير المتغير.
ضع عنوان Pages الفعلي في CORS_ORIGINS لدى Render.

## 5. الاختبار
افتح /health على الخادم. اختبر إنشاء حساب، تسجيل الدخول، الخصوصية، إعلانات السوق، الصور، والأذونات.
يجب إجراء تدقيق أمني وفحص اعتماديات قبل الإطلاق العام.
التشخيص البيطري بالذكاء الاصطناعي معلومات مساعدة وليس بديلاً للطبيب البيطري.
