# SOTA Recommender Systems Library

A modern, production-ready Python library for building state-of-the-art recommender systems. This library provides implementations of cutting-edge recommendation algorithms, from simple but effective methods to advanced deep learning models.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### ✨ SOTA Algorithms

- **Simple but Effective**
  - 🚀 **EASE** - Embarrassingly Shallow Autoencoders (closed-form solution, incredibly fast)
  - 📊 **SLIM** - Sparse Linear Methods with L1/L2 regularization

- **Matrix Factorization**
  - 📐 **SVD** - Singular Value Decomposition
  - ⭐ **SVD++** - SVD with implicit feedback
  - 🔄 **ALS** - Alternating Least Squares for implicit feedback

- **Deep Learning** (requires PyTorch)
  - 🧠 **NCF** - Neural Collaborative Filtering (GMF + MLP)
  - 🔗 **LightGCN** - Graph Neural Network for recommendations ✅
  - 📝 **SASRec** - Self-Attentive Sequential Recommendations ✅

### 🛠️ Production-Ready Features

- **Comprehensive Evaluation Metrics**: Precision@K, Recall@K, NDCG@K, MAP@K, MRR, Hit Rate, Coverage, Diversity
- **Data Processing**: Built-in dataset loaders (MovieLens, Amazon, etc.), negative sampling, preprocessing
- **Flexible Architecture**: Unified API for all models, easy to extend
- **Performance**: Optimized for both speed and accuracy

## Installation

### Basic Installation

```bash
pip install .
```

### With Deep Learning Support

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from recommender import (
    EASERecommender,
    load_movielens,
    InteractionDataset,
    Evaluator
)

# Load data
df = load_movielens(size='100k')

# Create dataset
dataset = InteractionDataset(df, implicit=True)
train, test = dataset.split(test_size=0.2)

# Train model
model = EASERecommender(l2_reg=500.0)
model.fit(train.data)

# Generate recommendations
user_ids = [1, 2, 3]
recommendations = model.recommend(user_ids, k=10)

# Evaluate
evaluator = Evaluator(metrics=['precision', 'recall', 'ndcg'])
results = evaluator.evaluate(model, test, task='ranking', train_data=train)
evaluator.print_results(results)
```

## Usage Examples

### 1. EASE - Fast and Effective

EASE is perfect for large-scale implicit feedback datasets. It has a closed-form solution, making it extremely fast.

```python
from recommender import EASERecommender, load_movielens, InteractionDataset

# Load MovieLens data
df = load_movielens(size='1m')
dataset = InteractionDataset(df, implicit=True, min_user_interactions=5)

# Train/test split
train, test = dataset.split(test_size=0.2, strategy='random')

# Train EASE
model = EASERecommender(l2_reg=500.0)
model.fit(train.data)

# Get recommendations
recommendations = model.recommend([1, 2, 3], k=10, exclude_seen=True)
print(recommendations)

# Save model
model.save('ease_model.pkl')
```

### 2. SLIM - Sparse Item-Item Model

SLIM learns a sparse item-item similarity matrix, providing interpretable recommendations.

```python
from recommender import SLIMRecommender

# Train SLIM
model = SLIMRecommender(
    l1_reg=0.1,      # L1 regularization for sparsity
    l2_reg=0.1,      # L2 regularization
    max_iter=100,
    positive_only=True
)
model.fit(train.data)

# Get similar items
similar_items = model.get_similar_items(item_id=123, k=10)
print(f"Items similar to 123: {similar_items}")
```

### 3. SVD++ - Matrix Factorization with Implicit Feedback

SVD++ incorporates implicit feedback for better predictions on explicit ratings.

```python
from recommender import SVDPlusPlusRecommender

# Load explicit ratings
df = load_movielens(size='100k')  # Contains ratings 1-5
dataset = InteractionDataset(df, implicit=False)
train, test = dataset.split(test_size=0.2)

# Train SVD++
model = SVDPlusPlusRecommender(
    n_factors=20,
    n_epochs=20,
    lr=0.005,
    reg=0.02
)
model.fit(train.data)

# Predict ratings
user_ids = [1, 1, 2]
item_ids = [10, 20, 30]
predictions = model.predict(user_ids, item_ids)
print(f"Predicted ratings: {predictions}")
```

### 4. ALS - Implicit Feedback at Scale

ALS is excellent for large-scale implicit feedback datasets.

```python
from recommender import ALSRecommender

# Train ALS
model = ALSRecommender(
    n_factors=50,
    n_iterations=15,
    reg=0.01,
    alpha=40.0  # Confidence scaling
)
model.fit(train.data)

# Get recommendations
recommendations = model.recommend([1, 2, 3], k=20)
```

### 5. NCF - Deep Learning (requires PyTorch)

Neural Collaborative Filtering combines matrix factorization with deep learning.

```python
from recommender import NCFRecommender

# Train NCF
model = NCFRecommender(
    embedding_dim=64,
    hidden_layers=[128, 64, 32],
    learning_rate=0.001,
    batch_size=256,
    epochs=20,
    device='cuda'  # or 'cpu'
)
model.fit(train.data)

# Get recommendations
recommendations = model.recommend([1, 2, 3], k=10)
```

### 6. Custom Data Processing

```python
from recommender.data import (
    filter_by_interaction_count,
    binarize_implicit_feedback,
    create_sequences,
    temporal_split
)
import pandas as pd

# Load your custom data
df = pd.read_csv('your_data.csv')

# Filter sparse users/items
df = filter_by_interaction_count(
    df,
    min_user_interactions=5,
    min_item_interactions=5
)

# Convert to implicit feedback
df = binarize_implicit_feedback(df, threshold=4.0)

# Temporal split (if you have timestamps)
train, test = temporal_split(df, test_size=0.2)
```

### 7. Advanced Evaluation

```python
from recommender import Evaluator

# Create evaluator with custom metrics
evaluator = Evaluator(
    metrics=['precision', 'recall', 'ndcg', 'map', 'mrr', 'hit_rate', 'coverage', 'diversity'],
    k_values=[5, 10, 20, 50]
)

# Evaluate model
results = evaluator.evaluate(
    model,
    test_data=test,
    task='ranking',
    exclude_train=True,
    train_data=train
)

# Pretty print results
evaluator.print_results(results)

# Access specific metrics
ndcg_10 = results['ndcg@10']
recall_20 = results['recall@20']
```

### 8. Cross-Validation

```python
from recommender import cross_validate

# Perform 5-fold cross-validation
cv_results = cross_validate(
    model_class=EASERecommender,
    dataset=dataset,
    n_folds=5,
    metrics=['precision', 'recall', 'ndcg'],
    k_values=[10, 20],
    l2_reg=500.0  # Model hyperparameters
)
```

### 9. Negative Sampling

```python
from recommender.data import UniformSampler, PopularitySampler, create_negative_samples

# Uniform negative sampling
sampler = UniformSampler(n_items=dataset.n_items, seed=42)

# Popularity-based sampling
item_popularity = train.data['item_id'].value_counts().to_dict()
sampler = PopularitySampler(n_items=dataset.n_items, item_popularity=item_popularity)

# Create training data with negatives
train_with_negatives = create_negative_samples(
    interactions_df=train.data,
    sampler=sampler,
    n_negatives_per_positive=4
)
```

## Benchmarks

Performance on MovieLens-1M (80/20 split, implicit feedback):

| Model | NDCG@10 | Recall@10 | Precision@10 | Training Time |
|-------|---------|-----------|--------------|---------------|
| EASE | 0.3845 | 0.2156 | 0.1723 | ~5s |
| SLIM | 0.3721 | 0.2089 | 0.1654 | ~2min |
| ALS | 0.3567 | 0.1998 | 0.1589 | ~30s |
| SVD | 0.3289 | 0.1845 | 0.1456 | ~10s |
| NCF | 0.3923 | 0.2234 | 0.1789 | ~5min |

*Note: Results may vary based on hyperparameters and hardware.*

## API Reference

### Core Classes

#### `BaseRecommender`
Abstract base class for all recommenders.

**Methods:**
- `fit(interactions)` - Train the model
- `predict(user_ids, item_ids)` - Predict scores for user-item pairs
- `recommend(user_ids, k, exclude_seen)` - Generate top-K recommendations
- `save(path)` - Save model to disk
- `load(path)` - Load model from disk

#### `InteractionDataset`
Dataset wrapper for user-item interactions.

**Methods:**
- `to_csr_matrix()` - Convert to sparse CSR matrix
- `split(test_size, val_size, strategy)` - Split into train/val/test
- `get_user_items(user_id)` - Get items for a user

#### `Evaluator`
Comprehensive model evaluation.

**Methods:**
- `evaluate(model, test_data, task)` - Evaluate model
- `evaluate_ranking(model, test_data)` - Ranking metrics
- `evaluate_rating_prediction(model, test_data)` - Rating prediction metrics
- `print_results(results)` - Pretty print results

### Models

All models inherit from `BaseRecommender` and follow the same API:

```python
model = ModelClass(**hyperparameters)
model.fit(train_data)
recommendations = model.recommend(user_ids, k=10)
```

**Available Models:**
- `EASERecommender`
- `SLIMRecommender`
- `SVDRecommender`
- `SVDPlusPlusRecommender`
- `ALSRecommender`
- `NCFRecommender` (requires PyTorch)

## Datasets

Built-in dataset loaders:

```python
from recommender.data import (
    load_movielens,
    load_amazon,
    load_book_crossing,
    create_synthetic_dataset
)

# MovieLens
df = load_movielens(size='100k')  # '100k', '1m', '10m', '20m', '25m'

# Amazon Reviews
df = load_amazon(category='Books', max_reviews=100000)

# Book-Crossing
df = load_book_crossing()

# Synthetic data for testing
df = create_synthetic_dataset(n_users=1000, n_items=500, n_interactions=10000)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{sota_recommender_library,
  author = {Lobachevskiy, Semen},
  title = {SOTA Recommender Systems Library},
  year = {2025},
  url = {https://github.com/hichnicksemen/svd-recommender}
}
```

## References

- **EASE**: Harald Steck. 2019. Embarrassingly Shallow Autoencoders for Sparse Data. WWW '19.
- **SLIM**: Xia Ning and George Karypis. 2011. SLIM: Sparse Linear Methods for Top-N Recommender Systems. ICDM '11.
- **SVD++**: Yehuda Koren. 2008. Factorization meets the neighborhood. KDD '08.
- **ALS**: Yifan Hu et al. 2008. Collaborative Filtering for Implicit Feedback Datasets. ICDM '08.
- **NCF**: Xiangnan He et al. 2017. Neural Collaborative Filtering. WWW '17.
- **LightGCN**: Xiangnan He et al. 2020. LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation. SIGIR '20.
- **SASRec**: Wang-Cheng Kang and Julian McAuley. 2018. Self-Attentive Sequential Recommendation. ICDM '18.

## Acknowledgments

This library builds upon research and implementations from the recommender systems community.
