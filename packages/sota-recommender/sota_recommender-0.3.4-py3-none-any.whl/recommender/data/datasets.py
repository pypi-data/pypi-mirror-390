"""
Built-in dataset loaders for popular recommendation datasets.
"""
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import urllib.request
import zipfile
import gzip
import shutil
import json


class DatasetLoader:
    """
    Base class for dataset loaders.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize loader.
        
        Args:
            cache_dir: Directory to cache downloaded datasets
        """
        if cache_dir is None:
            cache_dir = Path.home() / '.cache' / 'recommender_datasets'
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def download(self, url: str, filename: str) -> Path:
        """
        Download file if not cached.
        
        Args:
            url: URL to download from
            filename: Filename to save as
            
        Returns:
            Path to downloaded file
        """
        filepath = self.cache_dir / filename
        
        if filepath.exists():
            print(f"Using cached file: {filepath}")
            return filepath
        
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, filepath)
        print(f"Downloaded to {filepath}")
        
        return filepath
    
    def extract_zip(self, zip_path: Path, extract_to: Optional[Path] = None) -> Path:
        """
        Extract zip file.
        
        Args:
            zip_path: Path to zip file
            extract_to: Directory to extract to (default: same as zip)
            
        Returns:
            Path to extracted directory
        """
        if extract_to is None:
            extract_to = zip_path.parent
        
        print(f"Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        return extract_to
    
    def load(self) -> pd.DataFrame:
        """
        Load dataset.
        
        Returns:
            DataFrame with columns ['user_id', 'item_id', 'rating', 'timestamp']
        """
        raise NotImplementedError


class MovieLensLoader(DatasetLoader):
    """
    Loader for MovieLens datasets.
    
    Available sizes: '100k', '1m', '10m', '20m', '25m'
    """
    
    URLS = {
        '100k': 'https://files.grouplens.org/datasets/movielens/ml-100k.zip',
        '1m': 'https://files.grouplens.org/datasets/movielens/ml-1m.zip',
        '10m': 'https://files.grouplens.org/datasets/movielens/ml-10m.zip',
        '20m': 'https://files.grouplens.org/datasets/movielens/ml-20m.zip',
        '25m': 'https://files.grouplens.org/datasets/movielens/ml-25m.zip'
    }
    
    def __init__(self, size: str = '100k', cache_dir: Optional[str] = None):
        """
        Initialize MovieLens loader.
        
        Args:
            size: Dataset size ('100k', '1m', '10m', '20m', '25m')
            cache_dir: Cache directory
        """
        super().__init__(cache_dir)
        
        if size not in self.URLS:
            raise ValueError(f"Invalid size. Choose from: {list(self.URLS.keys())}")
        
        self.size = size
        self.url = self.URLS[size]
    
    def load(self) -> pd.DataFrame:
        """Load MovieLens dataset."""
        # Download
        zip_filename = f"ml-{self.size}.zip"
        zip_path = self.download(self.url, zip_filename)
        
        # Extract
        extract_dir = self.cache_dir / f"ml-{self.size}"
        if not extract_dir.exists():
            self.extract_zip(zip_path)
        
        # Load ratings
        if self.size == '100k':
            # 100k has different format
            ratings_file = extract_dir / 'ml-100k' / 'u.data'
            df = pd.read_csv(
                ratings_file,
                sep='\t',
                names=['user_id', 'item_id', 'rating', 'timestamp'],
                engine='python'
            )
        elif self.size == '1m':
            ratings_file = extract_dir / 'ml-1m' / 'ratings.dat'
            df = pd.read_csv(
                ratings_file,
                sep='::',
                names=['user_id', 'item_id', 'rating', 'timestamp'],
                engine='python'
            )
        else:
            # 10m, 20m, 25m use CSV format
            ratings_file = extract_dir / f'ml-{self.size}' / 'ratings.csv'
            df = pd.read_csv(ratings_file)
            
            # Rename columns to standard format
            df = df.rename(columns={
                'userId': 'user_id',
                'movieId': 'item_id'
            })
        
        print(f"Loaded MovieLens-{self.size}: {len(df)} ratings, "
              f"{df['user_id'].nunique()} users, {df['item_id'].nunique()} items")
        
        return df


class AmazonReviewsLoader(DatasetLoader):
    """
    Loader for Amazon product reviews dataset.
    
    Note: This is a simplified version. Full dataset requires more complex processing.
    """
    
    CATEGORIES = [
        'Books', 'Electronics', 'Movies_and_TV', 'CDs_and_Vinyl',
        'Clothing_Shoes_and_Jewelry', 'Home_and_Kitchen', 'Kindle_Store',
        'Sports_and_Outdoors', 'Cell_Phones_and_Accessories', 'Health_and_Personal_Care'
    ]
    
    BASE_URL = 'http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/'
    
    def __init__(self, category: str = 'Books', cache_dir: Optional[str] = None):
        """
        Initialize Amazon Reviews loader.
        
        Args:
            category: Product category
            cache_dir: Cache directory
        """
        super().__init__(cache_dir)
        
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category. Choose from: {self.CATEGORIES}")
        
        self.category = category
        self.url = f"{self.BASE_URL}reviews_{category}_5.json.gz"
    
    def load(self, max_reviews: Optional[int] = None) -> pd.DataFrame:
        """
        Load Amazon reviews dataset.
        
        Args:
            max_reviews: Maximum number of reviews to load (for memory efficiency)
            
        Returns:
            DataFrame with reviews
        """
        filename = f"reviews_{self.category}_5.json.gz"
        filepath = self.cache_dir / filename
        
        if not filepath.exists():
            print(f"Downloading {self.url}...")
            try:
                urllib.request.urlretrieve(self.url, filepath)
                print(f"Downloaded to {filepath}")
            except Exception as e:
                print(f"Error downloading: {e}")
                print("Returning empty DataFrame")
                return pd.DataFrame(columns=['user_id', 'item_id', 'rating', 'timestamp'])
        
        # Parse JSON
        reviews = []
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if max_reviews and i >= max_reviews:
                    break
                
                try:
                    review = json.loads(line)
                    reviews.append({
                        'user_id': review.get('reviewerID', ''),
                        'item_id': review.get('asin', ''),
                        'rating': float(review.get('overall', 0)),
                        'timestamp': int(review.get('unixReviewTime', 0))
                    })
                except:
                    continue
        
        df = pd.DataFrame(reviews)
        
        # Convert user/item IDs to integers
        df['user_id'] = pd.Categorical(df['user_id']).codes
        df['item_id'] = pd.Categorical(df['item_id']).codes
        
        print(f"Loaded Amazon-{self.category}: {len(df)} reviews, "
              f"{df['user_id'].nunique()} users, {df['item_id'].nunique()} items")
        
        return df


class LastFMLoader(DatasetLoader):
    """
    Loader for Last.fm dataset.
    """
    
    URL = 'http://ocelma.net/MusicRecommendationDataset/lastfm-1K.tar.gz'
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize Last.fm loader."""
        super().__init__(cache_dir)
    
    def load(self) -> pd.DataFrame:
        """Load Last.fm dataset."""
        # For now, return a placeholder
        # Full implementation would download and parse the dataset
        print("Last.fm loader not fully implemented yet")
        return pd.DataFrame(columns=['user_id', 'item_id', 'rating', 'timestamp'])


class BookCrossingLoader(DatasetLoader):
    """
    Loader for Book-Crossing dataset.
    """
    
    URL = 'http://www2.informatik.uni-freiburg.de/~cziegler/BX/BX-CSV-Dump.zip'
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize Book-Crossing loader."""
        super().__init__(cache_dir)
    
    def load(self) -> pd.DataFrame:
        """Load Book-Crossing dataset."""
        filename = 'BX-CSV-Dump.zip'
        zip_path = self.download(self.URL, filename)
        
        extract_dir = self.cache_dir / 'BX-CSV-Dump'
        if not extract_dir.exists():
            self.extract_zip(zip_path)
        
        # Load ratings
        ratings_file = extract_dir / 'BX-Book-Ratings.csv'
        
        try:
            df = pd.read_csv(
                ratings_file,
                sep=';',
                encoding='latin-1',
                on_bad_lines='skip'
            )
            
            df = df.rename(columns={
                'User-ID': 'user_id',
                'ISBN': 'item_id',
                'Book-Rating': 'rating'
            })
            
            # Add dummy timestamp
            df['timestamp'] = 0
            
            # Filter out zero ratings (implicit feedback)
            df = df[df['rating'] > 0]
            
            print(f"Loaded Book-Crossing: {len(df)} ratings, "
                  f"{df['user_id'].nunique()} users, {df['item_id'].nunique()} items")
            
            return df
        except Exception as e:
            print(f"Error loading Book-Crossing: {e}")
            return pd.DataFrame(columns=['user_id', 'item_id', 'rating', 'timestamp'])


# Convenience functions

def load_movielens(size: str = '100k', cache_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Load MovieLens dataset.
    
    Args:
        size: Dataset size ('100k', '1m', '10m', '20m', '25m')
        cache_dir: Cache directory
        
    Returns:
        DataFrame with ratings
    """
    loader = MovieLensLoader(size=size, cache_dir=cache_dir)
    return loader.load()


def load_amazon(category: str = 'Books', max_reviews: Optional[int] = None, 
                cache_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Load Amazon Reviews dataset.
    
    Args:
        category: Product category
        max_reviews: Maximum number of reviews to load
        cache_dir: Cache directory
        
    Returns:
        DataFrame with reviews
    """
    loader = AmazonReviewsLoader(category=category, cache_dir=cache_dir)
    return loader.load(max_reviews=max_reviews)


def load_book_crossing(cache_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Load Book-Crossing dataset.
    
    Args:
        cache_dir: Cache directory
        
    Returns:
        DataFrame with ratings
    """
    loader = BookCrossingLoader(cache_dir=cache_dir)
    return loader.load()


def create_synthetic_dataset(
    n_users: int = 1000,
    n_items: int = 500,
    n_interactions: int = 10000,
    rating_range: Tuple[int, int] = (1, 5),
    implicit: bool = False,
    seed: int = 42
) -> pd.DataFrame:
    """
    Create a synthetic dataset for testing.
    
    Args:
        n_users: Number of users
        n_items: Number of items
        n_interactions: Number of interactions
        rating_range: Range of ratings (min, max)
        implicit: Whether to generate implicit feedback
        seed: Random seed
        
    Returns:
        DataFrame with synthetic interactions
    """
    np.random.seed(seed)
    
    # Generate random interactions
    user_ids = np.random.randint(0, n_users, size=n_interactions)
    item_ids = np.random.randint(0, n_items, size=n_interactions)
    
    if implicit:
        ratings = np.ones(n_interactions)
    else:
        ratings = np.random.randint(rating_range[0], rating_range[1] + 1, size=n_interactions)
    
    timestamps = np.random.randint(1000000000, 1700000000, size=n_interactions)
    
    df = pd.DataFrame({
        'user_id': user_ids,
        'item_id': item_ids,
        'rating': ratings,
        'timestamp': timestamps
    })
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['user_id', 'item_id'], keep='first')
    
    print(f"Created synthetic dataset: {len(df)} interactions, "
          f"{df['user_id'].nunique()} users, {df['item_id'].nunique()} items")
    
    return df

