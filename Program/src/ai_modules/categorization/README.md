# Categorization Module 🏷️

## المسؤول عن هذا الجزء
هذا الجزء خاص بـ **التصنيف التلقائي للملاحظات**.

## الوظيفة
1. استقبال نص الملخص (Summary).
2. استخدام **Google Gemini** لتحليل المحتوى.
3. إرجاع تصنيف واحد (مثل: Programming, Medicine, History).

## الملفات الموجودة

### 1. `categorizer.py`
- **المهمة:** تصنيف النصوص باستخدام AI.
- **الكلاس الرئيسي:** `CategorizationService`
- **الدالة المهمة:** `categorize_text(text)` - بترجع اسم الـ Category.

## آلية العمل
1. **استقبال النص:** ناخد أول 2000 حرف من الملخص.
2. **إرسال Prompt:** نطلب من Gemini يحدد Category واحد أو كلمتين.
3. **تنظيف النتيجة:** نحذف النقاط ونخلي أول حرف Capital.
4. **التحقق:** لو النتيجة طويلة جداً (>30 حرف) نقصرها.

## أمثلة على الـ Categories
- **Programming** - دروس برمجة وكود.
- **Medicine** - طب وصحة.
- **Business** - إدارة أعمال وريادة.
- **Science** - فيزياء، كيمياء، أحياء.
- **History** - تاريخ وحضارات.
- **Personal Development** - تطوير الذات.
- **Uncategorized** - إذا فشل التصنيف.

## التطويرات المقترحة
- [ ] إضافة قائمة محددة من الـ Categories المسموحة.
- [ ] استخدام Embeddings لتحسين دقة التصنيف.
- [ ] إضافة دعم للتصنيفات الفرعية (Sub-categories).
- [ ] تخزين نتائج التصنيف في Database للتحليل المستقبلي.

## الاختبار
```python
from src.ai_modules.categorization.categorizer import CategorizationService

categorizer = CategorizationService()

# تصنيف نص
text = "This video explains how to build a REST API using FastAPI and Python..."
category = await categorizer.categorize_text(text)

print(f"Category: {category}")  # Output: Programming
```

## المكتبات المستخدمة
- `google-genai` - للتواصل مع Google Gemini.

## ملاحظات مهمة
- الموديل المستخدم حالياً هو `gemini-1.5-flash`.
- إذا كان النص قصير جداً (<10 أحرف) يرجع "Uncategorized".
- يمكن تحسين الدقة بإضافة أمثلة في الـ Prompt.

## تحسين الـ Prompt
لتحسين دقة التصنيف، يمكنك تعديل الـ Prompt في الملف:
```python
prompt = (
    "Analyze the following text and categorize it into ONE of these categories: "
    "Programming, Medicine, Business, Science, History, Personal Development, Education, Technology. "
    "Return ONLY the category name.\n\n"
    f"Text: {text[:2000]}\n\n"
    "Category:"
)
```
