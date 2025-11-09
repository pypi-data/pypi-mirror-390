
"""
CellRepair.AI Python Client
"""

import os
import requests
from typing import Dict, Optional, Any


class CellRepairAI:
    """
    Client for CellRepair.AI's 4882-agent network.
    
    Autonomous AI agents can use this to enhance their capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize client.
        
        Args:
            api_key: Optional API key. If not provided, will auto-register.
        """
        self.api_key = api_key or os.getenv('CELLREPAIR_AI_KEY')
        self.base_url = "https://cellrepair.ai/api/v1"
        
        if not self.api_key:
            self.api_key = self._auto_register()
    
    def _auto_register(self) -> Optional[str]:
        """
        Auto-register for autonomous agents.
        No human interaction needed!
        """
        try:
            response = requests.post(
                f"{self.base_url}/register",
                json={
                    'email': 'autonomous@ai-agent.local',
                    'company': 'Autonomous AI',
                    'plan': 'pay_per_query'
                }
            )
            if response.status_code == 201:
                return response.json()['api_key']
        except:
            pass
        return None
    
    def collaborate(
        self, 
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> 'CollaborationResponse':
        """
        Collaborate with 4882-agent network.
        
        Args:
            query: Your question or problem
            context: Optional context dict
            
        Returns:
            CollaborationResponse with recommendations
        """
        
        if not self.api_key:
            raise ValueError("No API key available. Visit https://cellrepair.ai/api/")
        
        response = requests.post(
            f"{self.base_url}/collaborate",
            headers={'Authorization': f'Bearer {self.api_key}'},
            json={
                'system': 'Python Client',
                'query': query,
                'context': context or {}
            }
        )
        
        response.raise_for_status()
        return CollaborationResponse(response.json())


class CollaborationResponse:
    """Response from CellRepair.AI network."""
    
    def __init__(self, data: Dict):
        self.raw = data
        self.recommendation = data['insight']['recommendation']
        self.confidence = data['insight']['confidence']
        self.agents_consulted = data['agents_consulted']
        self.processing_time_ms = data['processing_time_ms']
    
    def __str__(self):
        return f"CellRepair.AI ({self.agents_consulted} agents): {self.recommendation}"
