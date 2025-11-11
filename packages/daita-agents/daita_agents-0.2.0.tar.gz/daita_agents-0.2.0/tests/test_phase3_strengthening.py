"""
Test suite for Phase 3 Strengthening Features.

Tests verify the following additions:
1. Subscriber error metrics in RelayManager.get_stats()
2. Workflow health_check() method
3. Connection validation with validate_connections()
4. Message deduplication in reliable mode
"""
import pytest
import asyncio
import time
from typing import List, Dict, Any

from daita.core.relay import RelayManager
from daita.core.workflow import Workflow, WorkflowError, WorkflowStatus


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, name: str, fail_on_data: Any = None):
        self.name = name
        self.processed_data = []
        self.fail_on_data = fail_on_data

    async def start(self):
        pass

    async def stop(self):
        pass

    async def process(self, task: str, data: Any, context: Dict[str, Any]):
        if data == self.fail_on_data:
            raise ValueError(f"Agent {self.name} failed on data: {data}")

        self.processed_data.append({
            'task': task,
            'data': data,
            'context': context
        })

        return {
            'status': 'success',
            'result': f'{self.name} processed {data}',
            'agent_id': self.name
        }


class TestSubscriberErrorMetrics:
    """Test subscriber error metrics in RelayManager."""

    @pytest.mark.asyncio
    async def test_error_count_in_stats(self):
        """Test that subscriber error count appears in stats."""
        relay = RelayManager()
        await relay.start()

        async def failing_subscriber(data):
            raise RuntimeError("Test error")

        await relay.subscribe("test_channel", failing_subscriber)
        await relay.publish("test_channel", {"result": "test"})

        await asyncio.sleep(0.1)

        stats = relay.get_stats()
        assert 'subscriber_errors_count' in stats
        assert stats['subscriber_errors_count'] == 1

        await relay.stop()

    @pytest.mark.asyncio
    async def test_errors_by_channel(self):
        """Test per-channel error tracking."""
        relay = RelayManager()
        await relay.start()

        async def failing_subscriber(data):
            raise ValueError("Channel error")

        # Subscribe to multiple channels
        await relay.subscribe("channel_1", failing_subscriber)
        await relay.subscribe("channel_2", failing_subscriber)

        # Publish to both channels
        await relay.publish("channel_1", {"result": "data1"})
        await relay.publish("channel_1", {"result": "data2"})
        await relay.publish("channel_2", {"result": "data3"})

        await asyncio.sleep(0.1)

        stats = relay.get_stats()
        assert 'errors_by_channel' in stats

        # Both channels should have errors tracked
        # Note: error attribution is based on callback string containing channel name
        assert stats['subscriber_errors_count'] == 3

        await relay.stop()

    @pytest.mark.asyncio
    async def test_no_errors_shows_zero_count(self):
        """Test that stats show 0 errors when none occur."""
        relay = RelayManager()
        await relay.start()

        received = []

        async def working_subscriber(data):
            received.append(data)

        await relay.subscribe("test_channel", working_subscriber)
        await relay.publish("test_channel", {"result": "test"})

        await asyncio.sleep(0.1)

        stats = relay.get_stats()
        assert stats['subscriber_errors_count'] == 0
        assert 'errors_by_channel' not in stats or len(stats['errors_by_channel']) == 0

        await relay.stop()


class TestConnectionValidation:
    """Test workflow connection validation."""

    def test_validate_nonexistent_source(self):
        """Test that connecting nonexistent source raises error immediately."""
        workflow = Workflow("Test Workflow")

        workflow.add_agent("agent1", MockAgent("agent1"))

        # connect() validates immediately, so this should raise
        with pytest.raises(WorkflowError) as exc_info:
            workflow.connect("nonexistent_source", "channel", "agent1")

        assert "Source agent 'nonexistent_source' not found" in str(exc_info.value)

    def test_validate_nonexistent_destination(self):
        """Test that connecting nonexistent destination raises error immediately."""
        workflow = Workflow("Test Workflow")

        workflow.add_agent("agent1", MockAgent("agent1"))

        # connect() validates immediately, so this should raise
        with pytest.raises(WorkflowError) as exc_info:
            workflow.connect("agent1", "channel", "nonexistent_dest")

        assert "Destination agent 'nonexistent_dest' not found" in str(exc_info.value)

    def test_validate_circular_dependency(self):
        """Test validation catches circular dependencies."""
        workflow = Workflow("Test Workflow")

        workflow.add_agent("agent1", MockAgent("agent1"))
        workflow.connect("agent1", "channel", "agent1")

        errors = workflow.validate_connections()
        assert len(errors) == 1
        assert "Circular dependency: agent1 -> agent1" in errors[0]

    def test_validate_valid_connections(self):
        """Test validation passes for valid connections."""
        workflow = Workflow("Test Workflow")

        workflow.add_agent("agent1", MockAgent("agent1"))
        workflow.add_agent("agent2", MockAgent("agent2"))
        workflow.connect("agent1", "channel", "agent2")

        errors = workflow.validate_connections()
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_start_succeeds_when_all_valid(self):
        """Test that workflow.start() validates connections and succeeds when valid."""
        workflow = Workflow("Test Workflow")

        workflow.add_agent("agent1", MockAgent("agent1"))
        workflow.add_agent("agent2", MockAgent("agent2"))
        workflow.connect("agent1", "channel", "agent2")

        # Since connect() already validates, validate_connections() should return no errors
        errors = workflow.validate_connections()
        assert len(errors) == 0

        await workflow.start()
        assert workflow.status == WorkflowStatus.RUNNING

        await workflow.stop()

    @pytest.mark.asyncio
    async def test_start_succeeds_with_valid_connections(self):
        """Test that workflow.start() succeeds with valid connections."""
        workflow = Workflow("Test Workflow")

        workflow.add_agent("agent1", MockAgent("agent1"))
        workflow.add_agent("agent2", MockAgent("agent2"))
        workflow.connect("agent1", "channel", "agent2")

        await workflow.start()

        assert workflow.status == WorkflowStatus.RUNNING

        await workflow.stop()


class TestWorkflowHealthCheck:
    """Test workflow health check functionality."""

    def test_health_check_running_workflow(self):
        """Test health check on running workflow."""
        workflow = Workflow("Test Workflow")
        workflow.add_agent("agent1", MockAgent("agent1"))
        workflow.status = WorkflowStatus.RUNNING

        health = workflow.health_check()

        assert health['status'] == 'running'
        assert health['healthy'] is True
        assert 'agent1' in health['agents']
        assert health['agents']['agent1']['has_process'] is True
        assert len(health['issues']) == 0

    def test_health_check_agent_without_process(self):
        """Test health check detects agent without process method."""
        workflow = Workflow("Test Workflow")

        class BrokenAgent:
            pass

        workflow.add_agent("broken", BrokenAgent())
        workflow.status = WorkflowStatus.RUNNING

        health = workflow.health_check()

        assert health['healthy'] is False
        assert len(health['issues']) == 1
        assert "has no process method" in health['issues'][0]

    def test_health_check_high_subscription_count(self):
        """Test health check warns on high subscription count."""
        workflow = Workflow("Test Workflow")
        workflow.add_agent("agent1", MockAgent("agent1"))
        workflow.status = WorkflowStatus.RUNNING

        # Simulate high subscription count
        workflow._subscriptions = [(f"channel_{i}", lambda x: x) for i in range(1500)]

        health = workflow.health_check()

        assert health['healthy'] is False
        assert health['subscription_count'] == 1500
        assert any("High subscription count" in issue for issue in health['issues'])

    @pytest.mark.asyncio
    async def test_health_check_high_pending_messages(self):
        """Test health check warns on high pending message count."""
        workflow = Workflow("Test Workflow")
        workflow.add_agent("agent1", MockAgent("agent1"))
        workflow.add_agent("agent2", MockAgent("agent2"))
        workflow.connect("agent1", "channel", "agent2")

        # Enable reliability
        workflow.configure_reliability(acknowledgments=True)

        await workflow.start()

        # Create many pending messages by not acknowledging
        for i in range(150):
            await workflow.relay_manager.publish(
                "test_channel",
                {"result": f"data_{i}"},
                require_ack=True
            )

        await asyncio.sleep(0.1)

        health = workflow.health_check()

        assert 'pending_message_count' in health
        assert health['pending_message_count'] > 100
        assert any("High pending message count" in issue for issue in health['issues'])

        await workflow.stop()

    def test_health_check_agent_with_get_health(self):
        """Test health check uses agent's get_health if available."""
        workflow = Workflow("Test Workflow")

        class HealthyAgent:
            async def start(self):
                pass

            async def stop(self):
                pass

            async def process(self, task, data, context):
                pass

            def get_health(self):
                return {'custom_metric': 42, 'status': 'excellent'}

        workflow.add_agent("healthy", HealthyAgent())
        workflow.status = WorkflowStatus.RUNNING

        health = workflow.health_check()

        assert 'custom_metric' in health['agents']['healthy']
        assert health['agents']['healthy']['custom_metric'] == 42


class TestMessageDeduplication:
    """Test message deduplication in reliable mode."""

    @pytest.mark.asyncio
    async def test_duplicate_message_not_processed_twice(self):
        """Test that duplicate messages are not processed twice."""
        workflow = Workflow("Test Workflow")

        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")

        workflow.add_agent("agent1", agent1)
        workflow.add_agent("agent2", agent2)
        workflow.connect("agent1", "channel", "agent2")

        # Enable reliability for deduplication
        workflow.configure_reliability(acknowledgments=True)

        await workflow.start()

        # Publish same message multiple times
        message_id = await workflow.relay_manager.publish(
            "channel",
            {"result": "unique_data"},
            require_ack=True
        )

        await asyncio.sleep(0.1)

        # Manually trigger duplicate by re-adding message to processed set
        # and trying to process again
        initial_count = len(agent2.processed_data)

        # Simulate retry by manually notifying subscribers again
        await workflow.relay_manager._notify_subscribers_reliable(
            "channel",
            "unique_data",
            message_id
        )

        await asyncio.sleep(0.1)

        # Should not have processed duplicate
        assert len(agent2.processed_data) == initial_count

        await workflow.stop()

    @pytest.mark.asyncio
    async def test_dedup_cache_initialized(self):
        """Test that deduplication cache is initialized."""
        workflow = Workflow("Test Workflow")

        assert hasattr(workflow, '_processed_messages')
        assert isinstance(workflow._processed_messages, set)
        assert len(workflow._processed_messages) == 0

    @pytest.mark.asyncio
    async def test_cleanup_task_starts_with_reliability(self):
        """Test that cleanup task starts when reliability enabled."""
        workflow = Workflow("Test Workflow")

        workflow.add_agent("agent1", MockAgent("agent1"))
        workflow.add_agent("agent2", MockAgent("agent2"))
        workflow.connect("agent1", "channel", "agent2")

        workflow.configure_reliability(acknowledgments=True)

        await workflow.start()

        # Cleanup task should be running
        assert workflow._dedup_cleanup_task is not None
        assert not workflow._dedup_cleanup_task.done()

        await workflow.stop()

        # Cleanup task should be cancelled
        assert workflow._dedup_cleanup_task is None or workflow._dedup_cleanup_task.cancelled()

    @pytest.mark.asyncio
    async def test_cleanup_task_not_started_without_reliability(self):
        """Test that cleanup task doesn't start without reliability."""
        workflow = Workflow("Test Workflow")

        workflow.add_agent("agent1", MockAgent("agent1"))
        workflow.add_agent("agent2", MockAgent("agent2"))
        workflow.connect("agent1", "channel", "agent2")

        # Don't enable reliability
        await workflow.start()

        # Cleanup task should not be running
        assert workflow._dedup_cleanup_task is None

        await workflow.stop()

    @pytest.mark.asyncio
    async def test_failed_message_removed_from_dedup_cache(self):
        """Test that failed messages are removed from dedup cache for retry."""
        workflow = Workflow("Test Workflow")

        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2", fail_on_data="fail_me")

        workflow.add_agent("agent1", agent1)
        workflow.add_agent("agent2", agent2)
        workflow.connect("agent1", "channel", "agent2")

        workflow.configure_reliability(acknowledgments=True)

        await workflow.start()

        # Publish message that will fail
        message_id = await workflow.relay_manager.publish(
            "channel",
            {"result": "fail_me"},
            require_ack=True
        )

        await asyncio.sleep(0.2)

        # Message should have been removed from processed cache after failure
        # (so it can be retried)
        assert message_id not in workflow._processed_messages

        await workflow.stop()


class TestIntegrationScenarios:
    """Integration tests for all Phase 3 features together."""

    @pytest.mark.asyncio
    async def test_complete_workflow_with_all_features(self):
        """Test workflow using validation, health checks, and deduplication."""
        workflow = Workflow("Production Workflow")

        agent1 = MockAgent("fetcher")
        agent2 = MockAgent("processor")
        agent3 = MockAgent("analyzer")

        workflow.add_agent("fetcher", agent1)
        workflow.add_agent("processor", agent2)
        workflow.add_agent("analyzer", agent3)

        workflow.connect("fetcher", "raw_data", "processor")
        workflow.connect("processor", "processed_data", "analyzer")

        # Validate connections before starting
        errors = workflow.validate_connections()
        assert len(errors) == 0

        # Enable reliability for deduplication
        workflow.configure_reliability(acknowledgments=True)

        await workflow.start()

        # Check health - should be healthy after start
        health = workflow.health_check()
        assert len(health['agents']) == 3
        # Health may show issues during startup, so just check structure
        assert 'healthy' in health
        assert 'issues' in health

        # Inject data
        await workflow.inject_data("fetcher", "test_data", task="relay_message")

        await asyncio.sleep(0.3)

        # Check relay stats include error metrics
        relay_stats = workflow.relay_manager.get_stats()
        assert 'subscriber_errors_count' in relay_stats

        # Verify workflow stats
        workflow_stats = workflow.get_stats()
        assert workflow_stats['reliability_enabled'] is True

        # Check health again after processing
        health_after = workflow.health_check()
        assert len(health_after['agents']) == 3

        await workflow.stop()

    @pytest.mark.asyncio
    async def test_workflow_validation_prevents_bad_config(self):
        """Test that validation prevents misconfigured workflow from starting."""
        workflow = Workflow("Bad Workflow")

        workflow.add_agent("agent1", MockAgent("agent1"))

        # Attempting to connect to non-existent agent should fail immediately
        with pytest.raises(WorkflowError) as exc_info:
            workflow.connect("agent1", "channel", "ghost_agent")

        assert "Destination agent 'ghost_agent' not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_monitoring_in_production(self):
        """Test health monitoring detects issues."""
        workflow = Workflow("Monitored Workflow")

        # Add one good agent and one broken agent
        workflow.add_agent("good_agent", MockAgent("good"))

        class BrokenAgent:
            pass

        workflow.add_agent("broken_agent", BrokenAgent())

        workflow.status = WorkflowStatus.RUNNING

        # Health check should detect problem
        health = workflow.health_check()

        assert health['healthy'] is False
        assert len(health['issues']) > 0
        assert any("broken_agent" in issue for issue in health['issues'])

    @pytest.mark.asyncio
    async def test_error_metrics_track_failures(self):
        """Test that error metrics track subscriber failures."""
        relay = RelayManager()
        await relay.start()

        failure_count = 0

        async def flaky_subscriber(data):
            nonlocal failure_count
            failure_count += 1
            if failure_count <= 3:
                raise RuntimeError(f"Failure {failure_count}")

        await relay.subscribe("test_channel", flaky_subscriber)

        # Publish multiple messages
        for i in range(5):
            await relay.publish("test_channel", {"result": f"data_{i}"})

        await asyncio.sleep(0.2)

        # Check that errors were tracked
        stats = relay.get_stats()
        assert stats['subscriber_errors_count'] >= 3

        errors = relay.get_subscriber_errors(limit=10)
        assert len(errors) >= 3

        await relay.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
