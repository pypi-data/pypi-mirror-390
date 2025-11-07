"""
QuickInsights Web API Module

FastAPI-based REST API for QuickInsights library.
Provides HTTP endpoints for data analysis, visualization, and ML operations.
"""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import json
import asyncio
from datetime import datetime

# Custom JSON encoder for NumPy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

def convert_numpy_types(obj):
    """Convert NumPy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
    from fastapi.responses import JSONResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    from fastapi.openapi.docs import get_swagger_ui_html
    from fastapi.openapi.utils import get_openapi
except ImportError:
    # Fallback for when FastAPI is not installed
    FastAPI = None
    HTTPException = None
    UploadFile = None
    File = None
    Form = None
    BackgroundTasks = None
    JSONResponse = None
    FileResponse = None
    CORSMiddleware = None
    BaseModel = None
    Field = None
    get_swagger_ui_html = None
    get_openapi = None

from .core import analyze, analyze_numeric, analyze_categorical
from .error_handling import QuickInsightsError, DataValidationError
from .plugin_system import get_plugin_manager, execute_plugins_by_type, PluginType
from .memory_manager_v2 import MemoryProfiler
from .async_core import AsyncTaskManager


# Pydantic Models for API
class AnalysisRequest(BaseModel):
    """Request model for data analysis"""
    data: List[Dict[str, Any]] = Field(..., description="Data to analyze as list of dictionaries")
    show_plots: bool = Field(True, description="Whether to generate plots")
    save_plots: bool = Field(False, description="Whether to save plots to files")
    output_dir: str = Field("./quickinsights_output", description="Output directory for plots")
    
    class Config:
        schema_extra = {
            "example": {
                "data": [
                    {"name": "Alice", "age": 25, "salary": 50000},
                    {"name": "Bob", "age": 30, "salary": 60000},
                    {"name": "Charlie", "age": 35, "salary": 70000}
                ],
                "show_plots": True,
                "save_plots": False,
                "output_dir": "./output"
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for data analysis"""
    success: bool = Field(..., description="Whether the analysis was successful")
    data: Dict[str, Any] = Field(..., description="Analysis results")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Analysis timestamp")
    processing_time: float = Field(..., description="Processing time in seconds")


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type")
    timestamp: datetime = Field(..., description="Error timestamp")


class PluginInfo(BaseModel):
    """Plugin information model"""
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    plugin_type: str = Field(..., description="Plugin type")
    enabled: bool = Field(..., description="Whether plugin is enabled")
    priority: int = Field(..., description="Plugin priority")


class MemoryInfo(BaseModel):
    """Memory usage information model"""
    current_memory_mb: float = Field(..., description="Current memory usage in MB")
    peak_memory_mb: float = Field(..., description="Peak memory usage in MB")
    memory_percent: float = Field(..., description="Memory usage percentage")
    available_memory_mb: float = Field(..., description="Available memory in MB")


# Global variables
app = None
memory_profiler = None
async_manager = None


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    global app, memory_profiler, async_manager
    
    if FastAPI is None:
        raise ImportError("FastAPI is not installed. Install with: pip install quickinsights[web]")
    
    app = FastAPI(
        title="QuickInsights API",
        description="REST API for QuickInsights data analysis library",
        version="0.3.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize components
    memory_profiler = MemoryProfiler()
    async_manager = AsyncTaskManager()
    
    # Register routes
    register_routes()
    
    return app


def register_routes():
    """Register API routes"""
    
    @app.get("/", response_model=Dict[str, str])
    async def root():
        """Root endpoint with API information"""
        return {
            "message": "QuickInsights API",
            "version": "0.3.0",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    @app.get("/health", response_model=Dict[str, Any])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "memory_usage": get_memory_info()
        }
    
    @app.post("/analyze", response_model=AnalysisResponse)
    async def analyze_data(request: AnalysisRequest):
        """Analyze data using QuickInsights"""
        try:
            start_time = datetime.now()
            
            # Convert data to DataFrame
            df = pd.DataFrame(request.data)
            
            # Perform analysis
            result = analyze(
                df=df,
                show_plots=request.show_plots,
                save_plots=request.save_plots,
                output_dir=request.output_dir
            )
            
            # Convert NumPy types to Python native types
            result = convert_numpy_types(result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResponse(
                success=True,
                data=result,
                message="Analysis completed successfully",
                timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Analysis failed: {str(e)}"
            )
    
    @app.post("/analyze/numeric", response_model=AnalysisResponse)
    async def analyze_numeric_data(request: AnalysisRequest):
        """Analyze numeric columns only"""
        try:
            start_time = datetime.now()
            
            df = pd.DataFrame(request.data)
            result = analyze_numeric(
                df=df,
                show_plots=request.show_plots,
                save_plots=request.save_plots,
                output_dir=request.output_dir
            )
            
            # Convert NumPy types to Python native types
            result = convert_numpy_types(result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResponse(
                success=True,
                data=result,
                message="Numeric analysis completed successfully",
                timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Numeric analysis failed: {str(e)}"
            )
    
    @app.post("/analyze/categorical", response_model=AnalysisResponse)
    async def analyze_categorical_data(request: AnalysisRequest):
        """Analyze categorical columns only"""
        try:
            start_time = datetime.now()
            
            df = pd.DataFrame(request.data)
            result = analyze_categorical(
                df=df,
                show_plots=request.show_plots,
                save_plots=request.save_plots,
                output_dir=request.output_dir
            )
            
            # Convert NumPy types to Python native types
            result = convert_numpy_types(result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResponse(
                success=True,
                data=result,
                message="Categorical analysis completed successfully",
                timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Categorical analysis failed: {str(e)}"
            )
    
    @app.post("/upload/csv", response_model=AnalysisResponse)
    async def upload_csv(
        file: UploadFile = File(...),
        show_plots: bool = Form(True),
        save_plots: bool = Form(False),
        output_dir: str = Form("./quickinsights_output")
    ):
        """Upload and analyze CSV file"""
        try:
            start_time = datetime.now()
            
            # Read CSV file
            import io
            contents = await file.read()
            df = pd.read_csv(io.BytesIO(contents))
            
            # Perform analysis
            result = analyze(
                df=df,
                show_plots=show_plots,
                save_plots=save_plots,
                output_dir=output_dir
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResponse(
                success=True,
                data=result,
                message=f"CSV analysis completed successfully for {file.filename}",
                timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"CSV analysis failed: {str(e)}"
            )
    
    @app.get("/plugins", response_model=List[PluginInfo])
    async def list_plugins():
        """List all available plugins"""
        try:
            manager = get_plugin_manager()
            plugins = []
            
            for plugin in manager.list_plugins():
                info = plugin.get_info()
                plugins.append(PluginInfo(
                    name=info.name,
                    version=info.version,
                    plugin_type=info.plugin_type.value,
                    enabled=info.enabled,
                    priority=info.priority.value
                ))
            
            return plugins
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list plugins: {str(e)}"
            )
    
    @app.post("/plugins/execute/{plugin_type}")
    async def execute_plugins(
        plugin_type: str,
        request: AnalysisRequest
    ):
        """Execute plugins of specific type"""
        try:
            df = pd.DataFrame(request.data)
            
            # Convert string to PluginType enum
            try:
                pt = PluginType(plugin_type.upper())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid plugin type: {plugin_type}"
                )
            
            results = execute_plugins_by_type(pt, df)
            
            return {
                "success": True,
                "plugin_type": plugin_type,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Plugin execution failed: {str(e)}"
            )
    
    @app.get("/memory", response_model=MemoryInfo)
    async def get_memory_status():
        """Get current memory usage information"""
        try:
            return get_memory_info()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get memory info: {str(e)}"
            )
    
    @app.post("/memory/cleanup")
    async def cleanup_memory():
        """Trigger memory cleanup"""
        try:
            if memory_profiler and hasattr(memory_profiler, 'cleanup_memory'):
                memory_profiler.cleanup_memory()
            else:
                # Fallback: trigger garbage collection
                import gc
                gc.collect()
            
            return {
                "success": True,
                "message": "Memory cleanup completed",
                "timestamp": datetime.now()
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Memory cleanup failed: {str(e)}"
            )
    
    @app.get("/async/tasks")
    async def list_async_tasks():
        """List all async tasks"""
        try:
            if async_manager:
                return {
                    "pending_tasks": len(async_manager.task_queue),
                    "running_tasks": len(async_manager.running_tasks),
                    "completed_tasks": len(async_manager.completed_tasks)
                }
            else:
                return {"message": "Async manager not available"}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list async tasks: {str(e)}"
            )


def get_memory_info() -> MemoryInfo:
    """Get current memory usage information"""
    if memory_profiler:
        try:
            # Get current memory snapshot
            if hasattr(memory_profiler, 'get_current_snapshot'):
                snapshot = memory_profiler.get_current_snapshot()
                current_memory_mb = snapshot.memory_rss / 1024 / 1024
                memory_percent = snapshot.memory_percent
                available_memory_mb = snapshot.available_memory / 1024 / 1024
            else:
                # Fallback to basic memory info
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()
                current_memory_mb = memory_info.rss / 1024 / 1024
                memory_percent = process.memory_percent()
                available_memory_mb = psutil.virtual_memory().available / 1024 / 1024
            
            peak_memory_mb = memory_profiler.performance_metrics.get("peak_memory", 0) / 1024 / 1024
            
            return MemoryInfo(
                current_memory_mb=current_memory_mb,
                peak_memory_mb=peak_memory_mb,
                memory_percent=memory_percent,
                available_memory_mb=available_memory_mb
            )
        except Exception:
            # Fallback to basic memory info
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return MemoryInfo(
                current_memory_mb=memory_info.rss / 1024 / 1024,
                peak_memory_mb=0,
                memory_percent=process.memory_percent(),
                available_memory_mb=psutil.virtual_memory().available / 1024 / 1024
            )
    else:
        return MemoryInfo(
            current_memory_mb=0,
            peak_memory_mb=0,
            memory_percent=0,
            available_memory_mb=0
        )


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server"""
    import uvicorn
    
    if app is None:
        create_app()
    
    uvicorn.run(
        "quickinsights.web_api:app",
        host=host,
        port=port,
        reload=reload
    )


# Flask fallback for compatibility
def create_flask_app():
    """Create Flask application as fallback"""
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        
        flask_app = Flask(__name__)
        CORS(flask_app)
        
        @flask_app.route("/", methods=["GET"])
        def flask_root():
            return jsonify({
                "message": "QuickInsights API (Flask)",
                "version": "0.3.0",
                "note": "Consider using FastAPI for better performance"
            })
        
        @flask_app.route("/analyze", methods=["POST"])
        def flask_analyze():
            try:
                data = request.get_json()
                df = pd.DataFrame(data.get("data", []))
                
                result = analyze(
                    df=df,
                    show_plots=data.get("show_plots", True),
                    save_plots=data.get("save_plots", False),
                    output_dir=data.get("output_dir", "./quickinsights_output")
                )
                
                return jsonify({
                    "success": True,
                    "data": result,
                    "message": "Analysis completed successfully"
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 400
        
        return flask_app
        
    except ImportError:
        raise ImportError("Flask is not installed. Install with: pip install quickinsights[web]")


if __name__ == "__main__":
    # Create and run the FastAPI app
    app = create_app()
    run_server()
