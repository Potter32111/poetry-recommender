from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Helper for safe inclusion
def safe_include(module_name, router_name="router", **kwargs):
    try:
        import importlib
        module = importlib.import_module(f"app.api.{module_name}")
        rt = getattr(module, router_name)
        router.include_router(rt, **kwargs)
        logger.info(f"Successfully included router: {module_name}")
    except Exception as e:
        logger.error(f"Failed to include router {module_name}: {e}")

# Standard routers (each sub-router defines its own prefix)
safe_include("poems", tags=["poems"])
safe_include("users", tags=["users"])
safe_include("memorization", tags=["memorization"])
safe_include("recommendations", tags=["recommendations"])
