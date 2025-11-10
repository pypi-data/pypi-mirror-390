import logging
from collections.abc import AsyncGenerator
from a2a.utils import artifact
from a2a.utils.artifact import new_artifact
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContextBuilder
from a2a.server.context import ServerCallContext
from a2a.server.events import Event, QueueManager
from a2a.server.tasks import (
    PushNotificationConfigStore,
    PushNotificationSender,
    TaskStore,
)
from a2a.types import (
    Message,
    MessageSendParams,
    Task,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
)

from holos_sdk.utils import plan_to_message, try_convert_to_plan
from .plant_tracer import PlantTracer, no_op_tracer
from .types import Plan, Assignment, TaskArtifact

logger = logging.getLogger(__name__)


class HolosRequestHandler(DefaultRequestHandler):
    """
    Holos request handler that extends DefaultRequestHandler with tracing functionality.
    
    This handler adds tracing to:
    1. on_message_send - consumes incoming objects and traces results
    2. on_message_send_stream - consumes incoming objects, tries to convert to Plan, and traces all events
    """
    
    def __init__(
        self,
        agent_executor: AgentExecutor,
        task_store: TaskStore,
        queue_manager: QueueManager | None = None,
        push_config_store: PushNotificationConfigStore | None = None,
        push_sender: PushNotificationSender | None = None,
        request_context_builder: RequestContextBuilder | None = None,
        tracer: PlantTracer = no_op_tracer,
    ) -> None:
        """
        Initialize the Holos request handler.
        
        Args:
            agent_executor: The AgentExecutor instance to run agent logic
            task_store: The TaskStore instance to manage task persistence
            queue_manager: The QueueManager instance to manage event queues
            push_config_store: The PushNotificationConfigStore instance for managing push notification configurations
            push_sender: The PushNotificationSender instance for sending push notifications
            request_context_builder: The RequestContextBuilder instance used to build request contexts
            tracer: PlantTracer instance for submitting tracing data
        """
        super().__init__(
            agent_executor=agent_executor,
            task_store=task_store,
            queue_manager=queue_manager,
            push_config_store=push_config_store,
            push_sender=push_sender,
            request_context_builder=request_context_builder,
        )
        self._tracer = tracer

    def _ensure_tracer_in_context(self, context: ServerCallContext | None = None) -> ServerCallContext:
        """
        Ensure the tracer is available in the context.
        
        Creates a request-scoped copy of the tracer to prevent race conditions
        when handling multiple concurrent requests. Each request gets its own
        tracer instance with isolated state (consumed_objects, produced_objects).
        
        If context is provided, add the request-scoped tracer to its state.
        If context is None, create a new ServerCallContext with the request-scoped tracer.
        
        Args:
            context: The server call context (can be None)
            
        Returns:
            ServerCallContext with request-scoped tracer in state
        """
        # Create a request-scoped copy to prevent race conditions
        request_tracer = self._tracer.create_request_scoped_copy()
        
        if context is not None:
            context.state['tracer'] = request_tracer
            return context
        else:
            return ServerCallContext(state={'tracer': request_tracer})

    async def _trace_event(self, event: Event, tracer: PlantTracer) -> None:
        """
        Trace an event using the provided tracer.
        
        Args:
            event: The event to trace
            tracer: The request-scoped tracer to use for tracing
        """
        try:
            if isinstance(event, (Message, Task)):
                await tracer.submit_object_produced(event)
            elif isinstance(event, Assignment):
                await tracer.submit_object_produced_consumed(event)
            elif isinstance(event, TaskStatusUpdateEvent):
                await tracer.submit_object_updated(event)
            elif isinstance(event, TaskArtifactUpdateEvent):
                task = await self.task_store.get(event.task_id)
                if (event.last_chunk is None or event.last_chunk == True) and task.artifacts:
                    for artifact in task.artifacts:
                        if artifact.artifact_id == event.artifact.artifact_id:
                            task_artifact = TaskArtifact(
                                artifact=artifact,
                                context_id=event.context_id,
                                task_id=event.task_id,
                            )
                            await tracer.submit_object_produced(task_artifact)
                            break
            #No need to submit plan, the client will submit it
            # elif isinstance(event, Plan):
            #     tracer.submit_object_produced(event)
        
        except Exception as e:
            logger.error(f"Error in _trace_event: {e}", exc_info=True)
    
    async def on_message_send(
        self,
        params: MessageSendParams,
        context: ServerCallContext | None = None,
    ) -> Message | Task:
        """
        Handle message send with tracing.
        
        This follows the server-side pattern where we consume the incoming request
        object before processing (opposite of client-side which produces before sending).
        """
        context = self._ensure_tracer_in_context(context)
        request_tracer = context.state['tracer']
        await request_tracer.submit_object_consumed(params.message)
        
        result = await super().on_message_send(params, context)
        await self._trace_event(result, request_tracer)
        
        return result
    
    async def on_message_send_stream(
        self,
        params: MessageSendParams,
        context: ServerCallContext | None = None,
    ) -> AsyncGenerator[Event]:
        """
        Handle message send stream with tracing.
        
        This follows the server-side pattern:
        1. Consume the incoming request object (server-side receives)
        2. Try to convert to Plan and resubmit if successful (following client-side pattern)
        """

        context = self._ensure_tracer_in_context(context)
        request_tracer = context.state['tracer']
        await request_tracer.submit_object_consumed(params.message)
        plan = try_convert_to_plan(params.message)
        if plan:
            plans_to_submit = [plan]
            submitted_plans = set()
            while plans_to_submit:
                cur_plan = plans_to_submit.pop(0)
                if cur_plan.id in submitted_plans:
                    continue
                await request_tracer.submit_object_consumed(cur_plan)
                submitted_plans.add(cur_plan.id)
                plans_to_submit.extend(cur_plan.depend_plans)

        responsed_context_id = None
        responsed_task_id = None
        async for event in super().on_message_send_stream(params, context):
            await self._trace_event(event, request_tracer)

            if isinstance(event, Task):
                responsed_task_id = event.id
                responsed_context_id = event.context_id

            #just yielding a2a.types
            if isinstance(event, Event):
                yield event
            elif isinstance(event, Plan):
                plan_message = plan_to_message(event)
                task_artifact_update_event = TaskArtifactUpdateEvent(
                    artifact=new_artifact(plan_message.parts, name="plan_message"),
                    context_id=responsed_context_id,
                    task_id=responsed_task_id,
                )
                task_artifact = TaskArtifact(
                    artifact=task_artifact_update_event.artifact,
                    context_id=task_artifact_update_event.context_id,
                    task_id=task_artifact_update_event.task_id
                )
                await request_tracer.submit_object_produced(task_artifact)
                yield task_artifact_update_event
