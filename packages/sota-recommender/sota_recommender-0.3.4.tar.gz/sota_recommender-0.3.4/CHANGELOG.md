# Changelog

All notable changes to this project will be documented in this file.

## [0.3.4] - 2025-11-06

Добавлен fallback для DataLoader: если PyTorch недоступен, DataLoader определяется как Any, чтобы имя всегда существовало.
Использованы строковые аннотации: все type hints с DataLoader теперь используют строки ('DataLoader' вместо DataLoader), чтобы Python не разрешал это имя во время выполнения.

## [0.3.3] - 2025-11-06

Что было исправлено:
Добавлен импорт TYPE_CHECKING из модуля typing
Добавлен условный импорт DataLoader для type checking (строка 10-11)
Сохранён импорт для runtime в блоке try/except (строка 16)
Теперь DataLoader доступен:
Для type checking (даже если PyTorch не установлен)
Для runtime (когда PyTorch установлен)

## [0.3.1] - 2025-11-04

Фикс версии релиза для pypi

## [0.2.0] - 2025-01-01

### 🎉 Major Release - Complete Rewrite

This release represents a complete rewrite and expansion of the library from a simple SVD implementation to a comprehensive SOTA recommender systems framework.

### Added

#### Core Infrastructure
- **Base Architecture**: Abstract base classes for all recommenders (`BaseRecommender`, `ImplicitRecommender`, `ExplicitRecommender`)
- **InteractionDataset**: Unified dataset class with train/test splitting (random, temporal, leave-one-out)
- **Trainer**: PyTorch trainer with early stopping, checkpointing, and callbacks
- **Registry Pattern**: Easy model registration and discovery

#### Models - Simple but Effective
- **EASE**: Embarrassingly Shallow Autoencoders with closed-form solution
- **SLIM**: Sparse Linear Methods with L1/L2 regularization

#### Models - Matrix Factorization
- **SVD**: Refactored and improved Truncated SVD
- **SVD++**: SVD with implicit feedback and biases
- **ALS**: Alternating Least Squares for implicit feedback

#### Models - Deep Learning
- **NCF**: Neural Collaborative Filtering (GMF + MLP) with PyTorch

#### Evaluation Framework
- **15+ Metrics**: Precision@K, Recall@K, NDCG@K, MAP@K, MRR, Hit Rate, RMSE, MAE, Coverage, Diversity, Novelty
- **Evaluator**: Comprehensive evaluation with pretty printing
- **Cross-validation**: K-fold cross-validation support

#### Data Processing
- **Dataset Loaders**: MovieLens (100k-25m), Amazon Reviews, Book-Crossing, Synthetic
- **Preprocessing**: Filtering, normalization, binarization, temporal splits, sequence creation
- **Negative Sampling**: 5 strategies (Uniform, Popularity, In-batch, Hard, Mixed)

#### Production Features
- **Model Persistence**: Save/load functionality for all models
- **GPU Support**: CUDA support for deep learning models
- **Sparse Operations**: Efficient sparse matrix handling
- **Batch Processing**: Efficient batch inference

#### Documentation
- **Comprehensive README**: 9 detailed usage examples, API reference, benchmarks
- **Examples**: Quick start guide with model comparisons
- **Tests**: Comprehensive test suite with 10+ test cases
- **Implementation Summary**: Detailed documentation of all features

### Changed
- **API**: Complete redesign with unified interface across all models
- **Structure**: Modular architecture with clear separation of concerns
- **Performance**: Significant optimization with sparse matrices and vectorization
- **Dependencies**: Updated to modern versions (numpy>=1.20, pandas>=1.3, etc.)

### Deprecated
- Old `CollaborativeRecommender` class (replaced by new architecture)

### Removed
- Legacy `recommender.py` file

### Fixed
- Various edge cases in predictions
- Memory efficiency for large datasets
- Consistent handling of unseen users/items

## [0.1.0] - 2024-XX-XX

### Initial Release
- Basic SVD-based collaborative filtering
- Simple fit/predict interface
- MovieLens example

---

## Version Format

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

## Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

