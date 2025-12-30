from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.models import models
from app.models.schemas import (
    BSKMaster, ServiceMaster, DEOMaster, Provision
)
from app.models.database import engine, get_db
from typing import List
import os
from dotenv import load_dotenv
import logging
import pandas as pd
import sys
import gc

# Add project root to path for ai_service imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Create database tables (no-op for existing NeonDB)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BSK Training Optimization API",
    description="API for AI-Assisted Training Optimization System",
    version="1.0.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in allowed_origins else allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Starting BSK Training Optimization API...")
    
    # Force garbage collection to free memory
    gc.collect()
    
    # Check if we're on Render
    is_render = os.getenv("RENDER") == "true"
    logger.info(f"Environment: {'Render' if is_render else 'Local'}")
    
    # Initialize embeddings (always rebuild on Render due to ephemeral storage)
    try:
        from ai_service.service_recommendation import initialize_embeddings_from_db
        logger.info("Initializing service embeddings from database...")
        
        # Force rebuild on Render, check for updates locally
        force_rebuild = is_render
        success = initialize_embeddings_from_db(
            force_rebuild=force_rebuild, 
            include_inactive=False
        )
        
        if success:
            logger.info("✅ Service embeddings initialized successfully")
        else:
            logger.warning("⚠️  Embeddings initialization returned False")
    except Exception as e:
        logger.error(f"❌ Failed to initialize embeddings: {e}")
        logger.warning("⚠️  Continuing without pre-computed embeddings")
        logger.warning("Recommendations will compute embeddings on-demand (slower)")
    
    logger.info("✅ Application startup complete")

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to BSK Training Optimization API",
        "status": "online",
        "version": "1.0.0",
        "environment": "render" if os.getenv("RENDER") == "true" else "local"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for Render"""
    from ai_service.service_recommendation import get_embedding_stats
    
    try:
        stats = get_embedding_stats()
        return {
            "status": "healthy",
            "environment": "render" if os.getenv("RENDER") == "true" else "local",
            "embeddings_loaded": stats.get('total_services', 0) > 0,
            "total_services": stats.get('total_services', 0)
        }
    except:
        return {
            "status": "healthy",
            "environment": "render" if os.getenv("RENDER") == "true" else "local",
            "embeddings_loaded": False
        }

# BSK Master endpoints
@app.get("/bsk/", response_model=List[BSKMaster])
def get_bsk_list(skip: int = 0, limit: int = Query(None), db: Session = Depends(get_db)):
    logger.info(f"Fetching BSK list with skip={skip}, limit={limit}")
    query = db.query(models.BSKMaster).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    bsk_list = query.all()
    logger.info(f"Found {len(bsk_list)} BSK records")
    return bsk_list

@app.get("/bsk/{bsk_code}", response_model=BSKMaster)
def get_bsk(bsk_code: str, db: Session = Depends(get_db)):
    logger.info(f"Fetching BSK with code: {bsk_code}")
    bsk = db.query(models.BSKMaster).filter(models.BSKMaster.bsk_code == bsk_code).first()
    if bsk is None:
        logger.warning(f"BSK not found with code: {bsk_code}")
        raise HTTPException(status_code=404, detail="BSK not found")
    return bsk

# Service Master endpoints
@app.get("/services/", response_model=List[ServiceMaster])
def get_services(skip: int = 0, limit: int = Query(None), db: Session = Depends(get_db)):
    logger.info(f"Fetching services with skip={skip}, limit={limit}")
    query = db.query(models.ServiceMaster).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    services = query.all()
    logger.info(f"Found {len(services)} service records")
    return services

@app.get("/services/{service_id}", response_model=ServiceMaster)
def get_service(service_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching service with ID: {service_id}")
    service = db.query(models.ServiceMaster).filter(models.ServiceMaster.service_id == service_id).first()
    if service is None:
        logger.warning(f"Service not found with ID: {service_id}")
        raise HTTPException(status_code=404, detail="Service not found")
    return service

# DEO Master endpoints
@app.get("/deo/", response_model=List[DEOMaster])
def get_deo_list(skip: int = 0, limit: int = Query(None), db: Session = Depends(get_db)):
    logger.info(f"Fetching DEO list with skip={skip}, limit={limit}")
    query = db.query(models.DEOMaster).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    deo_list = query.all()
    logger.info(f"Found {len(deo_list)} DEO records")
    return deo_list

@app.get("/deo/{agent_id}", response_model=DEOMaster)
def get_deo(agent_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching DEO with agent ID: {agent_id}")
    deo = db.query(models.DEOMaster).filter(models.DEOMaster.agent_id == agent_id).first()
    if deo is None:
        logger.warning(f"DEO not found with agent ID: {agent_id}")
        raise HTTPException(status_code=404, detail="DEO not found")
    return deo

# Provision endpoints
@app.get("/provisions/", response_model=List[Provision])
def get_provisions(skip: int = 0, limit: int = Query(None), db: Session = Depends(get_db)):
    logger.info(f"Fetching provisions with skip={skip}, limit={limit}")
    query = db.query(models.Provision).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    provisions = query.all()
    logger.info(f"Found {len(provisions)} provision records")
    return provisions

@app.get("/provisions/{customer_id}", response_model=Provision)
def get_provision(customer_id: str, db: Session = Depends(get_db)):
    logger.info(f"Fetching provision with customer_id: {customer_id}")
    provision = db.query(models.Provision).filter(models.Provision.customer_id == customer_id).first()
    if provision is None:
        logger.warning(f"Provision not found with customer_id: {customer_id}")
        raise HTTPException(status_code=404, detail="Provision not found")
    return provision

@app.get("/underperforming_bsks/")
def get_underperforming_bsks(
    num_bsks: int = 50,
    sort_order: str = 'asc',
    db: Session = Depends(get_db)
):
    try:
        from ai_service.bsk_analytics import find_underperforming_bsks
        
        # Fetch all BSKs, provisions, DEOs, and services
        bsks = db.query(models.BSKMaster).all()
        provisions = db.query(models.Provision).all()
        deos = db.query(models.DEOMaster).all()
        services = db.query(models.ServiceMaster).all()
        
        # Convert to DataFrame
        bsks_df = pd.DataFrame([b.__dict__ for b in bsks])
        provisions_df = pd.DataFrame([p.__dict__ for p in provisions])
        deos_df = pd.DataFrame([d.__dict__ for d in deos])
        services_df = pd.DataFrame([s.__dict__ for s in services])
        
        # Remove SQLAlchemy _sa_instance_state
        for df in [bsks_df, provisions_df, deos_df, services_df]:
            if '_sa_instance_state' in df.columns:
                df.drop('_sa_instance_state', axis=1, inplace=True)
        
        # Compute underperforming BSKs
        result_df = find_underperforming_bsks(bsks_df, provisions_df, deos_df, services_df)
        
        # Sort by score and return requested number
        ascending = sort_order == 'asc'
        result_df = result_df.sort_values(by="score", ascending=ascending).head(num_bsks)
        
        # Return as JSON
        return result_df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"Error in get_underperforming_bsks: {e}")
        raise HTTPException(status_code=500, detail=str(e))