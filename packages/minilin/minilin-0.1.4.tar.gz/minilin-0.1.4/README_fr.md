# MiniLin Framework

**Apprenez plus avec moins** - Un framework d'apprentissage profond universel pour les scénarios à faibles ressources

[English](README.md) | [中文](README_cn.md) | [Русский](README_ru.md) | [Français](README_fr.md) | [العربية](README_ar.md)

[![Version Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/alltobebetter/minilin)

## 🚀 Qu'est-ce que MiniLin?

MiniLin est un framework d'apprentissage profond conçu pour les **scénarios à faibles ressources** où les données sont rares et les ressources de calcul limitées. Il fournit un flux de travail automatisé de bout en bout pour les tâches de texte, d'image et d'audio, avec une optimisation intégrée pour le déploiement sur des appareils périphériques.

### Caractéristiques principales

- 🎯 **Solution en 3 lignes**: Pipeline ML complet des données au déploiement
- 🤖 **Sélection automatique de stratégie**: Choisit automatiquement la stratégie d'entraînement optimale
- 📦 **Modèles légers**: Modèles efficaces pré-intégrés
- 🔧 **Compression de modèles**: Quantification, élagage et distillation de connaissances intégrés
- 📱 **Déploiement périphérique**: Export vers ONNX, TFLite, TensorRT
- 🌐 **Multi-modal**: Support pour texte, images et audio
- 🎓 **Apprentissage few-shot**: LoRA, Adapter et Prompt Tuning
- 🔄 **Augmentation de données**: Rétro-traduction, Mixup, CutMix
- 🚀 **Déploiement API**: Serveur FastAPI REST API

## 📦 Installation

### Installation de base
```bash
pip install minilin
```

### Avec dépendances optionnelles
```bash
# Pour les tâches de vision
pip install minilin[vision]

# Pour les tâches audio
pip install minilin[audio]

# Pour les fonctionnalités d'optimisation (LoRA, Adapter)
pip install minilin[optimization]

# Pour le déploiement (FastAPI)
pip install minilin[deployment]

# Tout installer
pip install minilin[all]
```

## 🎯 Démarrage rapide

### Utilisation de base (3 lignes!)
```python
from minilin import AutoPipeline

pipeline = AutoPipeline(task="text_classification", data_path="./data")
pipeline.train()
pipeline.deploy(output_path="./model.onnx")
```

### Utilisation avancée
```python
from minilin import AutoPipeline

pipeline = AutoPipeline(
    task="text_classification",
    data_path="./data",
    target_device="mobile",      # Appareil cible: mobile, edge, cloud
    max_samples=500,             # Échantillons d'entraînement maximum
    compression_level="high"     # Niveau de compression: low, medium, high
)

# Analyser les données
analysis = pipeline.analyze_data()
print(f"Stratégie recommandée: {analysis['recommended_strategy']}")

# Entraînement
pipeline.train(epochs=10, batch_size=16, learning_rate=2e-5)

# Évaluation
metrics = pipeline.evaluate()
print(f"Précision: {metrics['accuracy']:.4f}")

# Déploiement avec quantification
pipeline.deploy(output_path="./model_mobile.onnx", quantization="int8")
```

## 🎓 Fonctionnalités avancées

### Apprentissage few-shot avec LoRA
```python
from minilin.models import apply_few_shot_method

# Appliquer LoRA pour un fine-tuning efficace
model = apply_few_shot_method(model, method="lora", r=8, alpha=16)

# Entraînement avec seulement 50 exemples!
pipeline.train(max_samples=50, epochs=20)
```

### Distillation de connaissances
```python
from minilin.optimization import KnowledgeDistiller

# Distiller les connaissances d'un grand modèle vers un petit modèle
distiller = KnowledgeDistiller(
    teacher_model=large_model,
    student_model=small_model,
    temperature=3.0,
    alpha=0.5
)

metrics = distiller.distill(train_loader, val_loader, epochs=5)
```

### Apprentissage multi-modal
```python
from minilin.models import create_multimodal_model

# Créer un modèle multi-modal
model = create_multimodal_model(
    text_model_name="distilbert-base-uncased",
    image_model_name="mobilenetv3_small_100",
    num_classes=10,
    fusion_method="attention"
)
```

## 📊 Tâches supportées

### Tâches textuelles
- ✅ Classification de texte
- ✅ Reconnaissance d'entités nommées (NER)
- ✅ Analyse de sentiment

### Tâches de vision
- ✅ Classification d'images
- 🔄 Détection d'objets (bientôt)

### Tâches audio
- ✅ Classification audio
- 🔄 Reconnaissance vocale (bientôt)

### Tâches multi-modales
- ✅ Texte + Image
- ✅ Texte + Audio
- ✅ Texte + Image + Audio

## 🔥 Performance

- **Vitesse d'entraînement**: 2-3x plus rapide que l'entraînement standard
- **Taille du modèle**: Compressé à 10-20% de la taille originale
- **Vitesse d'inférence**: Temps réel sur appareils périphériques (>30 FPS)
- **Perte de précision**: <2% après compression

## 📚 Exemples

Consultez le répertoire [examples](examples/) pour plus d'exemples:

- [Classification de texte](examples/text_classification.py)
- [Classification d'images](examples/image_classification.py)
- [Classification audio](examples/audio_classification.py)
- [Apprentissage multi-modal](examples/multimodal_example.py)
- [Fonctionnalités avancées](examples/advanced_features.py)

## 🤝 Contribution

Nous accueillons les contributions! Veuillez consulter [CONTRIBUTING.md](CONTRIBUTING.md) pour plus de détails.

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📧 Contact

- **GitHub**: https://github.com/alltobebetter/minilin
- **Email**: me@supage.eu.org

---

**Fait avec ❤️ par l'équipe MiniLin**
