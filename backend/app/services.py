import requests
from typing import List, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class AIWallpaperService:
    """Service for generating wallpapers using AI models"""
    
    @staticmethod
    async def generate_with_replicate(prompt: str, model: str = "flux", width: int = 1920, height: int = 1080) -> str:
        """Generate wallpaper using Replicate API"""
        if not settings.REPLICATE_API_KEY:
            raise ValueError("Replicate API key not configured")
        
        import replicate
        
        try:
            # Replicate models: flux, stable-diffusion-3, etc.
            model_url = f"black-forest-labs/{model}"
            
            output = replicate.run(
                model_url,
                input={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_outputs": 1,
                    "num_inference_steps": 50,
                }
            )
            
            if output and len(output) > 0:
                return output[0]  # Return first generated image URL
            
            raise Exception("No output from Replicate")
            
        except Exception as e:
            logger.error(f"Replicate generation failed: {str(e)}")
            raise
    
    @staticmethod
    async def generate_with_vertex_ai(prompt: str, width: int = 1920, height: int = 1080) -> str:
        """Generate wallpaper using Google Vertex AI"""
        if not settings.GOOGLE_VERTEX_AI_API_KEY:
            raise ValueError("Google Vertex AI key not configured")
        
        try:
            from google.cloud import aiplatform
            
            # Initialize Vertex AI
            aiplatform.init(project=settings.FIREBASE_PROJECT_ID)
            
            # Use Imagen model
            model = aiplatform.gapic.PredictionServiceClient()
            
            # Create request
            endpoint = model.endpoint_path(
                project=settings.FIREBASE_PROJECT_ID,
                location="us-central1",
                endpoint="imagen"
            )
            
            # This is a simplified example - actual implementation would depend on
            # the specific Vertex AI Imagen API
            
            raise NotImplementedError("Full Vertex AI integration pending")
            
        except Exception as e:
            logger.error(f"Vertex AI generation failed: {str(e)}")
            raise
    
    @staticmethod
    async def generate_wallpaper(prompt: str, model: str = "flux", width: int = 1920, height: int = 1080) -> str:
        """Generate wallpaper using specified AI model"""
        
        if model == "flux":
            return await AIWallpaperService.generate_with_replicate(prompt, "flux", width, height)
        elif model == "stable_diffusion":
            return await AIWallpaperService.generate_with_replicate(prompt, "stable-diffusion-3", width, height)
        elif model == "vertex_ai":
            return await AIWallpaperService.generate_with_vertex_ai(prompt, width, height)
        else:
            raise ValueError(f"Unknown model: {model}")

class DeviceSyncService:
    """Service for syncing wallpapers to devices"""
    
    @staticmethod
    def get_active_events_for_device(db, org_id: str, device_id: str) -> List:
        """Get all active events for a device's organization"""
        from app.models import Event
        from datetime import datetime
        
        now = datetime.utcnow()
        active_events = db.query(Event).filter(
            Event.org_id == org_id,
            Event.is_active == True,
            Event.start_date <= now,
            Event.end_date >= now
        ).all()
        
        return active_events
    
    @staticmethod
    def update_device_sync_status(db, device_id: str, status: str, error_message: Optional[str] = None):
        """Update device's last sync time and status"""
        from app.models import Device, DeviceSyncLog
        from datetime import datetime
        
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if device:
            device.last_sync = datetime.utcnow()
            device.status = "online" if status == "success" else "offline"
            
            # Log the sync
            sync_log = DeviceSyncLog(
                device_id=device_id,
                org_id=device.org_id,
                status=status,
                error_message=error_message
            )
            db.add(sync_log)
            db.commit()
    
    @staticmethod
    def prepare_sync_response(active_events: List, rotation_interval: int = 60) -> dict:
        """Prepare device sync response"""
        from datetime import datetime
        
        active_event_dicts = [
            {
                "event_id": event.event_id,
                "title": event.title,
                "wallpaper_urls": event.wallpaper_urls,
                "rotation_interval": event.rotation_interval
            }
            for event in active_events
        ]
        
        return {
            "active_events": active_event_dicts,
            "next_sync_time": rotation_interval * 60,  # Convert to seconds
            "timestamp": datetime.utcnow()
        }
