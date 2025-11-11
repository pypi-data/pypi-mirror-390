"""
Multi-region provider configuration.

Features:
- Region-based provider selection
- Latency-based routing
- Geographic data residency
- Comprehensive error handling
"""

from typing import Dict, Any, Optional, List
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class RegionConfig:
    """
    Multi-region configuration for providers.
    
    Features:
    - Region-based endpoint selection
    - Latency-based routing
    - Geographic compliance
    """
    
    # Provider region endpoints
    PROVIDER_REGIONS = {
        'openai': {
            'us-east': 'https://api.openai.com/v1',
            'eu-west': 'https://api.openai.com/v1',  # OpenAI doesn't have regional endpoints
            'asia-pacific': 'https://api.openai.com/v1'
        },
        'anthropic': {
            'us-east': 'https://api.anthropic.com',
            'eu-west': 'https://api.anthropic.com',
            'asia-pacific': 'https://api.anthropic.com'
        },
        'ultrasafe': {
            'us-east': 'https://us-east.us.inc/v1',
            'eu-west': 'https://eu-west.us.inc/v1',
            'asia-pacific': 'https://asia.us.inc/v1'
        }
    }
    
    @classmethod
    def get_endpoint(
        cls,
        provider_name: str,
        region: str = 'us-east',
        custom_endpoint: Optional[str] = None
    ) -> str:
        """
        Get provider endpoint for region.
        
        Args:
            provider_name: Provider name
            region: Target region
            custom_endpoint: Custom endpoint override
            
        Returns:
            Endpoint URL
        """
        try:
            if custom_endpoint:
                return custom_endpoint
            
            if provider_name not in cls.PROVIDER_REGIONS:
                logger.warning(f"Unknown provider: {provider_name}, using default")
                return f"https://api.{provider_name}.com/v1"
            
            regions = cls.PROVIDER_REGIONS[provider_name]
            
            if region not in regions:
                logger.warning(f"Unknown region: {region}, using us-east")
                region = 'us-east'
            
            endpoint = regions[region]
            logger.debug(f"Provider {provider_name} endpoint for {region}: {endpoint}")
            return endpoint
            
        except Exception as e:
            logger.error(f"Error getting endpoint: {e}", exc_info=True)
            return f"https://api.{provider_name}.com/v1"
    
    @classmethod
    def apply_region_config(cls, provider_config: Dict[str, Any], region: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply region configuration to provider config.
        
        Args:
            provider_config: Provider configuration
            region: Target region
            
        Returns:
            Updated configuration with regional endpoint
        """
        try:
            if not region:
                return provider_config
            
            provider_name = provider_config.get('name', '')
            custom_endpoint = provider_config.get('base_url')
            
            # Get regional endpoint
            endpoint = cls.get_endpoint(provider_name, region, custom_endpoint)
            
            # Update config
            updated_config = provider_config.copy()
            updated_config['base_url'] = endpoint
            updated_config['region'] = region
            
            logger.info(f"Applied region config: {provider_name} -> {region}")
            return updated_config
            
        except Exception as e:
            logger.error(f"Error applying region config: {e}", exc_info=True)
            return provider_config


class RegionSelector:
    """
    Intelligent region selection based on latency.
    
    Features:
    - Latency-based routing
    - Health checking
    - Automatic failover
    """
    
    def __init__(self):
        """Initialize region selector."""
        try:
            self.region_latencies: Dict[str, float] = {}
            self.region_health: Dict[str, bool] = {}
            logger.info("RegionSelector initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RegionSelector: {e}", exc_info=True)
            self.region_latencies = {}
            self.region_health = {}
    
    def record_latency(self, region: str, latency_ms: float):
        """Record latency for a region."""
        try:
            self.region_latencies[region] = latency_ms
            self.region_health[region] = True
            logger.debug(f"Region {region} latency: {latency_ms}ms")
        except Exception as e:
            logger.error(f"Error recording latency: {e}", exc_info=True)
    
    def record_failure(self, region: str):
        """Record failure for a region."""
        try:
            self.region_health[region] = False
            logger.warning(f"Region {region} marked as unhealthy")
        except Exception as e:
            logger.error(f"Error recording failure: {e}", exc_info=True)
    
    def get_best_region(self, available_regions: List[str]) -> str:
        """
        Get best region based on latency and health.
        
        Args:
            available_regions: List of available regions
            
        Returns:
            Best region name
        """
        try:
            # Filter healthy regions
            healthy_regions = [
                r for r in available_regions
                if self.region_health.get(r, True)  # Default to healthy
            ]
            
            if not healthy_regions:
                logger.warning("No healthy regions, using first available")
                return available_regions[0] if available_regions else 'us-east'
            
            # Select region with lowest latency
            best_region = min(
                healthy_regions,
                key=lambda r: self.region_latencies.get(r, float('inf'))
            )
            
            logger.info(f"Selected best region: {best_region}")
            return best_region
            
        except Exception as e:
            logger.error(f"Error getting best region: {e}", exc_info=True)
            return available_regions[0] if available_regions else 'us-east'