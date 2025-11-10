"""
PlantTracer - A wrapper class for tracing functionality

This module provides a PlantTracer class that simplifies tracing operations
by allowing configuration of default values during initialization.
"""

import uuid
import asyncio
import aiohttp
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Literal, Union, List, Set
from a2a.types import Message, Task, AgentCard, Artifact
from .types import Plan, Assignment


class PlantTracer:
    """
    A wrapper class for plant tracing functionality.
    
    This class allows you to configure default values for tracing operations,
    reducing the need to specify common parameters in each tracing call.
    """
    
    def __init__(self,
                 base_url: str,
                 creator_id: Optional[str] = None,
                 creator_name: Optional[str] = None,
                 agent_card: Optional[AgentCard] = None,
                 auto_link_from_objects: bool = True,
                 ):
        """
        Args:
            base_url: API base URL for tracing operations, if base_url is None, all submits will ignore.
            creator_id: Client id or agent url
            agent_card: Optional agent card (will use agent_card.url as agent_id if provided)
            auto_link_from_objects: Whether to automatically link from_objects to the object, if true will store consumed objects in memory and use them as from_objects for future tracing
        """
        self._version = "0.0.2"
        self.creator_id = creator_id
        self.creator_name = creator_name
        self.api_base_url = base_url
        self.auto_link_from_objects = auto_link_from_objects
        self.consumed_objects: Set[str] = set()
        self.produced_objects: Set[str] = set()
        if agent_card and not self.creator_id:
            self.creator_id = agent_card.url
        if agent_card and not self.creator_name:
            self.creator_name = agent_card.name
        
        if self.api_base_url is None:
            self.creator_id = 'no op'
            self.auto_link_from_objects = False

        if not self.creator_id:
            self.creator_id = str(uuid.uuid4())
            # raise ValueError("creator_id or agent_card should be provided at least one")


    def _convert_to_dict(self, obj: Any) -> Dict[str, Any]:
        """
        Convert an object to a dictionary, handling both A2A objects and regular dicts.
        
        Args:
            obj: Object to convert (A2A object or dict)
        
        Returns:
            Dictionary representation of the object
        """
        if hasattr(obj, 'model_dump'):
            return obj.model_dump(exclude_none=True)
        elif isinstance(obj, dict):
            return obj
        else:
            return obj


    async def send_tracing_data(self, tracing_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_base_url:
            return {
                "code": -100,
                "message": "base_url is not provided, all submits will ignore"
            }

        url = f"{self.api_base_url}/holos/plant/traces"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=tracing_data) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            return {
                "code": -100,
                "message": f"Failed to send tracing data: {str(e)}, url: {url}"
            }


    async def submit_object_tracing_data(
        self,
        object: Union[Message, Plan, Assignment, Task, Artifact, Dict[str, Any]],
        event_type: Literal['produced', 'consumed', 'produced_consumed', 'updated', 'patched'],
        from_objects: Optional[List[str]] = None,
        timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Args:
            object: The object to trace
            event_type: Type of event that occurred with the object
            from_objects: List of object's id that this object was based on or derived from
            timestamp: Timestamp of the tracing event in float seconds
        """
        tracing_data = {
            "creator_id": self.creator_id,
            "creator_name": self.creator_name,
            "object": self._convert_to_dict(object),
            "event_type": event_type,
            "from_objects": from_objects,
            "timestamp": timestamp or datetime.now(timezone.utc).timestamp(),
        }
        return await self.send_tracing_data(tracing_data)

    def _get_object_id(self, object: Union[Message, Plan, Assignment, Task, Artifact, Dict[str, Any]]) -> str:
        object_dict = self._convert_to_dict(object)
        object_class_name = object.__class__.__name__.lower()
        if 'id' in object_dict:
            id = object_dict['id']
        else:
            #try 'kind'_id, get kind first
            if 'kind' in object_dict:
                kind = object_dict['kind']
            else:
                kind = object_class_name

            if f"{kind}Id" in object_dict:
                id = object_dict[f"{kind}Id"]
            elif "task" in object_class_name and "event" in object_class_name and "taskId" in object_dict:
                id = object_dict["taskId"]
            elif "task" in object_class_name and "event" in object_class_name and "task_id" in object_dict:
                id = object_dict["task_id"]
            else:
                raise ValueError(f"Missing id in object: {object_dict}, kind: {kind}")
        return id
    
    # Basic tracing functions
    async def submit_object_produced(self, new_object, from_objects: Optional[List[str]] = None):
        if self.auto_link_from_objects:
            self.produced_objects.add(self._get_object_id(new_object))
            if from_objects is None:
                from_objects = list(self.consumed_objects)

        return await self.submit_object_tracing_data(new_object, 'produced', from_objects)


    async def submit_object_consumed(self, object, from_objects: Optional[List[str]] = None):
        if self.auto_link_from_objects:
            if len(self.produced_objects) > 0:
                self.consumed_objects.clear()
                self.produced_objects.clear()
            self.consumed_objects.add(self._get_object_id(object))

        return await self.submit_object_tracing_data(object, 'consumed', from_objects)


    async def submit_object_produced_consumed(self, new_object, from_objects: Optional[List[str]] = None):
        if self.auto_link_from_objects:
            self.produced_objects.add(self._get_object_id(new_object))
            if from_objects is None:
                from_objects = list(self.consumed_objects)

        return await self.submit_object_tracing_data(new_object, 'produced_consumed', from_objects)
    

    async def submit_object_updated(self, object, mode='PUT', from_objects: Optional[List[str]] = None):
        if mode == 'PUT':
            return await self.submit_object_tracing_data(object, 'updated', from_objects)
        elif mode == 'PATCH':
            return await self.submit_object_tracing_data(object, 'patched', from_objects)
        else:
            raise ValueError(f"Invalid mode: {mode}, should be PUT or PATCH")

    def create_request_scoped_copy(self) -> 'PlantTracer':
        """
        Create a request-scoped copy of this tracer with isolated state.
        
        This method creates a new PlantTracer instance that shares the same
        configuration (base_url, creator_id, etc.) but has its own isolated
        consumed_objects and produced_objects sets. This prevents race conditions
        when handling multiple concurrent requests.
        
        Returns:
            A new PlantTracer instance with isolated state
        """
        tracer = PlantTracer(
            base_url=self.api_base_url,
            creator_id=self.creator_id,
            creator_name=self.creator_name,
            agent_card=None,  # Don't pass agent_card as we already have creator_id/name
            auto_link_from_objects=self.auto_link_from_objects,
        )
        return tracer


# Create a no-op tracer instance for use as a default
no_op_tracer = PlantTracer(base_url=None)
