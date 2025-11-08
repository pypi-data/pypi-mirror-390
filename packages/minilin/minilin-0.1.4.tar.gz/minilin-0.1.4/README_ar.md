# إطار عمل MiniLin

**تعلم المزيد بموارد أقل** - إطار عمل شامل للتعلم العميق في السيناريوهات محدودة الموارد

[English](README.md) | [中文](README_cn.md) | [Русский](README_ru.md) | [Français](README_fr.md) | [العربية](README_ar.md)

[![إصدار Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![الترخيص](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![الإصدار](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/alltobebetter/minilin)

## 🚀 ما هو MiniLin؟

MiniLin هو إطار عمل للتعلم العميق مصمم **للسيناريوهات محدودة الموارد** حيث تكون البيانات نادرة والموارد الحاسوبية محدودة. يوفر سير عمل آلي شامل من البيانات إلى النشر لمهام النصوص والصور والصوت، مع تحسين مدمج للنشر على الأجهزة الطرفية.

### الميزات الرئيسية

- 🎯 **حل في 3 أسطر**: خط أنابيب ML كامل من البيانات إلى النشر
- 🤖 **اختيار تلقائي للاستراتيجية**: يختار تلقائياً استراتيجية التدريب المثلى
- 📦 **نماذج خفيفة**: نماذج فعالة مدمجة مسبقاً
- 🔧 **ضغط النماذج**: التكميم والتقليم وتقطير المعرفة مدمجة
- 📱 **النشر الطرفي**: التصدير إلى ONNX و TFLite و TensorRT
- 🌐 **متعدد الوسائط**: دعم النصوص والصور والصوت
- 🎓 **التعلم بأمثلة قليلة**: LoRA و Adapter و Prompt Tuning
- 🔄 **تعزيز البيانات**: الترجمة العكسية و Mixup و CutMix
- 🚀 **نشر API**: خادم FastAPI REST API

## 📦 التثبيت

### التثبيت الأساسي
```bash
pip install minilin
```

### مع التبعيات الاختيارية
```bash
# لمهام الرؤية
pip install minilin[vision]

# لمهام الصوت
pip install minilin[audio]

# لميزات التحسين (LoRA، Adapter)
pip install minilin[optimization]

# للنشر (FastAPI)
pip install minilin[deployment]

# تثبيت كل شيء
pip install minilin[all]
```

## 🎯 البدء السريع

### الاستخدام الأساسي (3 أسطر!)
```python
from minilin import AutoPipeline

pipeline = AutoPipeline(task="text_classification", data_path="./data")
pipeline.train()
pipeline.deploy(output_path="./model.onnx")
```

### الاستخدام المتقدم
```python
from minilin import AutoPipeline

pipeline = AutoPipeline(
    task="text_classification",
    data_path="./data",
    target_device="mobile",      # الجهاز المستهدف: mobile، edge، cloud
    max_samples=500,             # الحد الأقصى لعينات التدريب
    compression_level="high"     # مستوى الضغط: low، medium، high
)

# تحليل البيانات
analysis = pipeline.analyze_data()
print(f"الاستراتيجية الموصى بها: {analysis['recommended_strategy']}")

# التدريب
pipeline.train(epochs=10, batch_size=16, learning_rate=2e-5)

# التقييم
metrics = pipeline.evaluate()
print(f"الدقة: {metrics['accuracy']:.4f}")

# النشر مع التكميم
pipeline.deploy(output_path="./model_mobile.onnx", quantization="int8")
```

## 🎓 الميزات المتقدمة

### التعلم بأمثلة قليلة مع LoRA
```python
from minilin.models import apply_few_shot_method

# تطبيق LoRA للضبط الدقيق الفعال
model = apply_few_shot_method(model, method="lora", r=8, alpha=16)

# التدريب بـ 50 مثالاً فقط!
pipeline.train(max_samples=50, epochs=20)
```

### تقطير المعرفة
```python
from minilin.optimization import KnowledgeDistiller

# تقطير المعرفة من نموذج كبير إلى نموذج صغير
distiller = KnowledgeDistiller(
    teacher_model=large_model,
    student_model=small_model,
    temperature=3.0,
    alpha=0.5
)

metrics = distiller.distill(train_loader, val_loader, epochs=5)
```

### التعلم متعدد الوسائط
```python
from minilin.models import create_multimodal_model

# إنشاء نموذج متعدد الوسائط
model = create_multimodal_model(
    text_model_name="distilbert-base-uncased",
    image_model_name="mobilenetv3_small_100",
    num_classes=10,
    fusion_method="attention"
)
```

## 📊 المهام المدعومة

### مهام النصوص
- ✅ تصنيف النصوص
- ✅ التعرف على الكيانات المسماة (NER)
- ✅ تحليل المشاعر

### مهام الرؤية
- ✅ تصنيف الصور
- 🔄 كشف الأشياء (قريباً)

### مهام الصوت
- ✅ تصنيف الصوت
- 🔄 التعرف على الكلام (قريباً)

### المهام متعددة الوسائط
- ✅ نص + صورة
- ✅ نص + صوت
- ✅ نص + صورة + صوت

## 🔥 الأداء

- **سرعة التدريب**: أسرع 2-3 مرات من التدريب القياسي
- **حجم النموذج**: مضغوط إلى 10-20% من الحجم الأصلي
- **سرعة الاستدلال**: وقت حقيقي على الأجهزة الطرفية (>30 FPS)
- **فقدان الدقة**: <2% بعد الضغط

## 📚 أمثلة

راجع دليل [examples](examples/) لمزيد من الأمثلة:

- [تصنيف النصوص](examples/text_classification.py)
- [تصنيف الصور](examples/image_classification.py)
- [تصنيف الصوت](examples/audio_classification.py)
- [التعلم متعدد الوسائط](examples/multimodal_example.py)
- [الميزات المتقدمة](examples/advanced_features.py)

## 🤝 المساهمة

نرحب بالمساهمات! يرجى الاطلاع على [CONTRIBUTING.md](CONTRIBUTING.md) للتفاصيل.

## 📄 الترخيص

هذا المشروع مرخص بموجب ترخيص MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 📧 الاتصال

- **GitHub**: https://github.com/minilin-ai/minilin
- **التوثيق**: https://minilin.readthedocs.io
- **البريد الإلكتروني**: contact@minilin.ai

---

**صُنع بـ ❤️ بواسطة فريق MiniLin**
