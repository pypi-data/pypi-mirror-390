"""
FastAPI service for serving recommender models.

Provides REST API endpoints for:
- Health check
- Generate recommendations
- Predict scores
- Model info
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import pickle

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


if FASTAPI_AVAILABLE:
    # Request/Response models
    class RecommendRequest(BaseModel):
        """Request for recommendations."""
        user_ids: List[int] = Field(..., description="List of user IDs")
        k: int = Field(10, description="Number of recommendations per user", ge=1, le=100)
        exclude_seen: bool = Field(True, description="Exclude already seen items")
    
    class RecommendResponse(BaseModel):
        """Response with recommendations."""
        recommendations: Dict[int, List[Dict[str, Any]]] = Field(
            ..., description="Map of user_id to list of {item_id, score}"
        )
    
    class PredictRequest(BaseModel):
        """Request for predictions."""
        user_ids: List[int] = Field(..., description="List of user IDs")
        item_ids: List[int] = Field(..., description="List of item IDs")
    
    class PredictResponse(BaseModel):
        """Response with predictions."""
        predictions: List[float] = Field(..., description="Predicted scores")
    
    class ModelInfo(BaseModel):
        """Model information."""
        model_type: str
        n_users: int
        n_items: int
        version: str
        is_fitted: bool
    
    class HealthResponse(BaseModel):
        """Health check response."""
        status: str
        model_loaded: bool


    class RecommenderService:
        """
        Recommender model serving service.
        
        Provides REST API for inference.
        """
        
        def __init__(
            self,
            model_path: Optional[str] = None,
            host: str = "0.0.0.0",
            port: int = 8000,
            enable_cors: bool = True
        ):
            """
            Initialize service.
            
            Args:
                model_path: Path to saved model
                host: Host to bind to
                port: Port to bind to
                enable_cors: Enable CORS middleware
            """
            if not FASTAPI_AVAILABLE:
                raise ImportError(
                    "FastAPI is required for serving. "
                    "Install with: pip install fastapi uvicorn"
                )
            
            self.model = None
            self.model_path = model_path
            self.host = host
            self.port = port
            
            # Create FastAPI app
            self.app = FastAPI(
                title="Recommender Service",
                description="REST API for recommender models",
                version="1.0.0"
            )
            
            # Enable CORS if requested
            if enable_cors:
                self.app.add_middleware(
                    CORSMiddleware,
                    allow_origins=["*"],
                    allow_credentials=True,
                    allow_methods=["*"],
                    allow_headers=["*"],
                )
            
            # Setup routes
            self._setup_routes()
            
            # Load model if path provided
            if model_path:
                self.load_model(model_path)
        
        def _setup_routes(self):
            """Setup API routes."""
            
            @self.app.get("/", response_model=HealthResponse)
            async def root():
                """Root endpoint."""
                return {
                    "status": "running",
                    "model_loaded": self.model is not None
                }
            
            @self.app.get("/health", response_model=HealthResponse)
            async def health():
                """Health check endpoint."""
                return {
                    "status": "healthy",
                    "model_loaded": self.model is not None
                }
            
            @self.app.get("/model/info", response_model=ModelInfo)
            async def model_info():
                """Get model information."""
                if self.model is None:
                    raise HTTPException(status_code=503, detail="Model not loaded")
                
                return {
                    "model_type": self.model.__class__.__name__,
                    "n_users": self.model.n_users,
                    "n_items": self.model.n_items,
                    "version": getattr(self.model, 'version', '0.2.0'),
                    "is_fitted": self.model.is_fitted
                }
            
            @self.app.post("/recommend", response_model=RecommendResponse)
            async def recommend(request: RecommendRequest):
                """
                Generate recommendations for users.
                
                Example:
                ```json
                {
                    "user_ids": [1, 2, 3],
                    "k": 10,
                    "exclude_seen": true
                }
                ```
                """
                if self.model is None:
                    raise HTTPException(status_code=503, detail="Model not loaded")
                
                try:
                    import numpy as np
                    
                    # Get recommendations
                    user_ids = np.array(request.user_ids)
                    recs = self.model.recommend(
                        user_ids,
                        k=request.k,
                        exclude_seen=request.exclude_seen
                    )
                    
                    # Format response
                    formatted_recs = {}
                    for user_id, items in recs.items():
                        formatted_recs[int(user_id)] = [
                            {"item_id": int(item_id), "score": float(score)}
                            for item_id, score in items
                        ]
                    
                    return {"recommendations": formatted_recs}
                
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            
            @self.app.post("/predict", response_model=PredictResponse)
            async def predict(request: PredictRequest):
                """
                Predict scores for user-item pairs.
                
                Example:
                ```json
                {
                    "user_ids": [1, 1, 2],
                    "item_ids": [10, 20, 30]
                }
                ```
                """
                if self.model is None:
                    raise HTTPException(status_code=503, detail="Model not loaded")
                
                if len(request.user_ids) != len(request.item_ids):
                    raise HTTPException(
                        status_code=400,
                        detail="user_ids and item_ids must have same length"
                    )
                
                try:
                    import numpy as np
                    
                    # Get predictions
                    user_ids = np.array(request.user_ids)
                    item_ids = np.array(request.item_ids)
                    predictions = self.model.predict(user_ids, item_ids)
                    
                    return {"predictions": predictions.tolist()}
                
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            
            @self.app.post("/model/load")
            async def load_model_endpoint(
                path: str,
                background_tasks: BackgroundTasks
            ):
                """
                Load a model from disk.
                
                Example:
                ```json
                {
                    "path": "/path/to/model.pkl"
                }
                ```
                """
                # Load in background to not block
                background_tasks.add_task(self.load_model, path)
                return {"message": f"Loading model from {path}"}
        
        def load_model(self, path: str):
            """
            Load model from disk.
            
            Args:
                path: Path to model file
            """
            print(f"Loading model from {path}...")
            
            try:
                with open(path, 'rb') as f:
                    self.model = pickle.load(f)
                
                print(f"Model loaded: {self.model.__class__.__name__}")
                print(f"  Users: {self.model.n_users}")
                print(f"  Items: {self.model.n_items}")
                
            except Exception as e:
                print(f"Error loading model: {e}")
                raise
        
        def run(self):
            """Start the service."""
            print(f"Starting Recommender Service on {self.host}:{self.port}")
            uvicorn.run(self.app, host=self.host, port=self.port)
        
        def run_async(self):
            """Run service with auto-reload (for development)."""
            print(f"Starting Recommender Service (dev mode) on {self.host}:{self.port}")
            uvicorn.run(
                "recommender.serving.api:app",
                host=self.host,
                port=self.port,
                reload=True
            )


    # Convenience function
    def create_service(
        model_path: Optional[str] = None,
        host: str = "0.0.0.0",
        port: int = 8000
    ) -> RecommenderService:
        """
        Create a recommender service.
        
        Args:
            model_path: Path to saved model
            host: Host to bind to
            port: Port to bind to
            
        Returns:
            Configured service
        
        Example:
        ```python
        from recommender.serving import create_service
        
        service = create_service(model_path='model.pkl', port=8000)
        service.run()
        ```
        """
        return RecommenderService(model_path=model_path, host=host, port=port)


else:
    # Dummy implementations if FastAPI not available
    def create_service(*args, **kwargs):
        raise ImportError(
            "FastAPI is required for serving. "
            "Install with: pip install fastapi uvicorn"
        )
    
    class RecommenderService:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "FastAPI is required for serving. "
                "Install with: pip install fastapi uvicorn"
            )

