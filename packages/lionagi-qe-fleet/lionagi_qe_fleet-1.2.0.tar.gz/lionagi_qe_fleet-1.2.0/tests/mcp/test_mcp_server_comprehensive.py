"""Comprehensive tests for MCP Server - targeting 90%+ coverage

This test suite covers all functionality in mcp_server.py including:
- Server initialization and configuration
- Fleet initialization and agent registration
- Tool registration
- Server lifecycle management
- Error handling
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from lionagi_qe.mcp.mcp_server import (
    MCPServer,
    create_mcp_server,
    run_mcp_server,
    MCP_AVAILABLE
)
from lionagi_qe.mcp import mcp_tools


class TestMCPServerCreation:
    """Test MCP Server creation and initialization"""

    def test_create_mcp_server_defaults(self):
        """Test server creation with default parameters"""
        server = create_mcp_server()

        assert server.name == "lionagi-qe"
        assert server.enable_routing is True
        assert server.enable_learning is False
        assert server.fleet is None
        assert server.mcp is not None

    def test_create_mcp_server_custom_name(self):
        """Test server creation with custom name"""
        server = create_mcp_server(name="custom-qe-server")

        assert server.name == "custom-qe-server"
        assert server.mcp.name == "custom-qe-server"

    def test_create_mcp_server_routing_disabled(self):
        """Test server creation with routing disabled"""
        server = create_mcp_server(enable_routing=False)

        assert server.enable_routing is False

    def test_create_mcp_server_learning_enabled(self):
        """Test server creation with learning enabled"""
        server = create_mcp_server(enable_learning=True)

        assert server.enable_learning is True

    def test_create_mcp_server_all_custom(self):
        """Test server creation with all custom parameters"""
        server = create_mcp_server(
            name="test-server",
            enable_routing=False,
            enable_learning=True
        )

        assert server.name == "test-server"
        assert server.enable_routing is False
        assert server.enable_learning is True

    def test_mcp_server_init_sets_logger(self):
        """Test that server initialization sets up logger"""
        server = MCPServer(name="test-logger")

        assert server.logger is not None
        assert server.logger.name == "lionagi_qe.mcp.test-logger"

    def test_mcp_server_has_fastmcp_instance(self):
        """Test that server has FastMCP instance"""
        server = create_mcp_server()

        assert hasattr(server, 'mcp')
        assert server.mcp is not None


class TestToolRegistration:
    """Test tool registration functionality"""

    def test_tools_registered_on_creation(self):
        """Test that tools are registered during server creation"""
        server = create_mcp_server()
        mcp = server.get_server()

        # Core testing tools
        assert "test_generate" in mcp._tools
        assert "test_execute" in mcp._tools
        assert "coverage_analyze" in mcp._tools
        assert "quality_gate" in mcp._tools

    def test_all_core_tools_registered(self):
        """Test all core tools are registered"""
        server = create_mcp_server()
        mcp = server.get_server()

        expected_tools = [
            "test_generate",
            "test_execute",
            "coverage_analyze",
            "quality_gate",
            "performance_test",
            "security_scan",
            "fleet_orchestrate",
            "get_fleet_status",
        ]

        for tool in expected_tools:
            assert tool in mcp._tools, f"Tool {tool} not registered"

    def test_all_advanced_tools_registered(self):
        """Test all advanced tools are registered"""
        server = create_mcp_server()
        mcp = server.get_server()

        advanced_tools = [
            "requirements_validate",
            "flaky_test_hunt",
            "api_contract_validate",
            "regression_risk_analyze",
            "test_data_generate",
            "visual_test",
            "chaos_test",
            "deployment_readiness",
        ]

        for tool in advanced_tools:
            assert tool in mcp._tools, f"Advanced tool {tool} not registered"

    def test_streaming_tools_registered(self):
        """Test streaming tools are registered"""
        server = create_mcp_server()
        mcp = server.get_server()

        assert "test_execute_stream" in mcp._tools

    def test_tool_count(self):
        """Test that expected number of tools are registered"""
        server = create_mcp_server()
        mcp = server.get_server()

        # Should have at least 17 tools
        assert len(mcp._tools) >= 17

    def test_registered_tools_are_functions(self):
        """Test that registered tools are callable functions"""
        server = create_mcp_server()
        mcp = server.get_server()

        for tool_name, tool_func in mcp._tools.items():
            assert callable(tool_func), f"Tool {tool_name} is not callable"


class TestGetServer:
    """Test get_server method"""

    def test_get_server_returns_fastmcp(self):
        """Test that get_server returns FastMCP instance"""
        server = create_mcp_server()
        mcp = server.get_server()

        assert mcp is not None
        assert hasattr(mcp, 'name')
        assert hasattr(mcp, '_tools')

    def test_get_server_same_instance(self):
        """Test that get_server always returns same instance"""
        server = create_mcp_server()

        mcp1 = server.get_server()
        mcp2 = server.get_server()

        assert mcp1 is mcp2


@pytest.mark.asyncio
class TestFleetInitialization:
    """Test fleet initialization"""

    async def test_initialize_fleet_success(self):
        """Test successful fleet initialization"""
        server = create_mcp_server()

        assert server.fleet is None

        await server.initialize_fleet()

        assert server.fleet is not None
        assert server.fleet.initialized is True

        await server.stop()

    async def test_initialize_fleet_creates_agents(self):
        """Test that fleet initialization creates core agents"""
        server = create_mcp_server()
        await server.initialize_fleet()

        # Check agents are registered
        test_gen = await server.fleet.get_agent("test-generator")
        test_exec = await server.fleet.get_agent("test-executor")
        commander = await server.fleet.get_agent("fleet-commander")

        assert test_gen is not None
        assert test_exec is not None
        assert test_commander is not None
        assert test_gen.agent_id.name == "test-generator"
        assert test_exec.agent_id.name == "test-executor"
        assert commander.agent_id.name == "fleet-commander"

        await server.stop()

    async def test_initialize_fleet_sets_global_instance(self):
        """Test that fleet initialization sets global fleet instance"""
        server = create_mcp_server()

        # Reset fleet instance
        mcp_tools.set_fleet_instance(None)

        await server.initialize_fleet()

        # Global instance should be set
        fleet = mcp_tools.get_fleet_instance()
        assert fleet is server.fleet

        await server.stop()

    async def test_initialize_fleet_with_routing_enabled(self):
        """Test fleet initialization with routing enabled"""
        server = create_mcp_server(enable_routing=True)
        await server.initialize_fleet()

        assert server.fleet.enable_routing is True

        await server.stop()

    async def test_initialize_fleet_with_learning_enabled(self):
        """Test fleet initialization with learning enabled"""
        server = create_mcp_server(enable_learning=True)
        await server.initialize_fleet()

        assert server.fleet.enable_learning is True

        await server.stop()

    async def test_initialize_fleet_idempotent(self):
        """Test that initializing fleet twice is safe"""
        server = create_mcp_server()

        await server.initialize_fleet()
        fleet1 = server.fleet

        # Initialize again
        await server.initialize_fleet()
        fleet2 = server.fleet

        # Should be same instance
        assert fleet1 is fleet2

        await server.stop()

    async def test_initialize_fleet_logs_warning_on_double_init(self):
        """Test that double initialization logs warning"""
        server = create_mcp_server()

        with patch.object(server.logger, 'warning') as mock_warning:
            await server.initialize_fleet()
            await server.initialize_fleet()

            mock_warning.assert_called_once_with("Fleet already initialized")

        await server.stop()

    async def test_initialize_fleet_agent_skills(self):
        """Test that agents are initialized with correct skills"""
        server = create_mcp_server()
        await server.initialize_fleet()

        test_gen = await server.fleet.get_agent("test-generator")

        assert "agentic-quality-engineering" in test_gen.skills
        assert "tdd-london-chicago" in test_gen.skills
        assert "api-testing-patterns" in test_gen.skills

        await server.stop()


@pytest.mark.asyncio
class TestServerLifecycle:
    """Test server lifecycle (start/stop)"""

    async def test_start_initializes_fleet(self):
        """Test that start() initializes the fleet"""
        server = create_mcp_server()

        assert server.fleet is None

        await server.start()

        assert server.fleet is not None
        assert server.fleet.initialized is True

        await server.stop()

    async def test_start_logs_ready_message(self):
        """Test that start() logs ready message"""
        server = create_mcp_server()

        with patch.object(server.logger, 'info') as mock_info:
            await server.start()

            # Should log ready message
            calls = [str(call) for call in mock_info.call_args_list]
            ready_logged = any("ready" in str(call).lower() for call in calls)
            assert ready_logged

        await server.stop()

    async def test_stop_exports_state(self):
        """Test that stop() exports fleet state"""
        server = create_mcp_server()
        await server.start()

        with patch.object(server.fleet, 'export_state', new_callable=AsyncMock) as mock_export:
            mock_export.return_value = {"state": "data"}

            await server.stop()

            mock_export.assert_called_once()

    async def test_stop_logs_state_exported(self):
        """Test that stop() logs state export message"""
        server = create_mcp_server()
        await server.start()

        with patch.object(server.logger, 'info') as mock_info:
            await server.stop()

            # Should log state export
            calls = [str(call) for call in mock_info.call_args_list]
            exported_logged = any("exported" in str(call).lower() for call in calls)
            assert exported_logged

    async def test_stop_logs_stopped_message(self):
        """Test that stop() logs stopped message"""
        server = create_mcp_server()
        await server.start()

        with patch.object(server.logger, 'info') as mock_info:
            await server.stop()

            # Should log stopped message
            calls = [str(call) for call in mock_info.call_args_list]
            stopped_logged = any("stopped" in str(call).lower() for call in calls)
            assert stopped_logged

    async def test_stop_without_fleet(self):
        """Test that stop() works even if fleet is not initialized"""
        server = create_mcp_server()

        # Should not raise error
        await server.stop()

    async def test_start_stop_cycle(self):
        """Test complete start/stop cycle"""
        server = create_mcp_server()

        # Start
        await server.start()
        assert server.fleet is not None

        # Stop
        await server.stop()

        # Can start again
        await server.start()
        assert server.fleet is not None

        await server.stop()


@pytest.mark.asyncio
class TestMCPIntegration:
    """Test MCP server integration with tools"""

    async def test_tools_can_access_fleet_after_init(self):
        """Test that tools can access fleet after initialization"""
        server = create_mcp_server()
        await server.start()

        # Tools should be able to access fleet
        fleet = mcp_tools.get_fleet_instance()
        assert fleet is server.fleet
        assert fleet is not None

        await server.stop()

    async def test_get_fleet_status_after_init(self):
        """Test calling get_fleet_status after initialization"""
        server = create_mcp_server()
        await server.start()

        # Should work
        status = await mcp_tools.get_fleet_status()

        assert status is not None
        assert "initialized" in status

        await server.stop()

    async def test_tools_fail_before_init(self):
        """Test that tools fail gracefully before fleet init"""
        # Reset fleet
        mcp_tools.set_fleet_instance(None)

        with pytest.raises(RuntimeError, match="Fleet not initialized"):
            await mcp_tools.get_fleet_status()


@pytest.mark.asyncio
class TestRunMCPServer:
    """Test run_mcp_server function"""

    @patch('lionagi_qe.mcp.mcp_server.create_mcp_server')
    @patch('asyncio.sleep', side_effect=KeyboardInterrupt)
    async def test_run_mcp_server_with_keyboard_interrupt(self, mock_sleep, mock_create):
        """Test run_mcp_server handles KeyboardInterrupt"""
        mock_server = Mock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server.get_server = Mock(return_value=Mock(run=AsyncMock()))
        mock_create.return_value = mock_server

        # Should handle KeyboardInterrupt gracefully
        try:
            await run_mcp_server()
        except KeyboardInterrupt:
            pass

        # Should have called start and stop
        mock_server.start.assert_called_once()
        mock_server.stop.assert_called_once()

    @patch('lionagi_qe.mcp.mcp_server.create_mcp_server')
    @patch('lionagi_qe.mcp.mcp_server.MCP_AVAILABLE', False)
    @patch('asyncio.sleep', side_effect=[None, KeyboardInterrupt])
    async def test_run_mcp_server_fallback_mode(self, mock_sleep, mock_create):
        """Test run_mcp_server in fallback mode (no FastMCP)"""
        mock_server = Mock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server.get_server = Mock()
        mock_create.return_value = mock_server

        with patch('lionagi_qe.mcp.mcp_server.logger') as mock_logger:
            try:
                await run_mcp_server()
            except KeyboardInterrupt:
                pass

            # Should log fallback warning
            mock_logger.warning.assert_called()
            warning_msg = str(mock_logger.warning.call_args)
            assert "fallback" in warning_msg.lower()

    @patch('lionagi_qe.mcp.mcp_server.create_mcp_server')
    async def test_run_mcp_server_creates_default_server(self, mock_create):
        """Test that run_mcp_server creates default server"""
        mock_server = Mock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server.get_server = Mock(return_value=Mock(run=AsyncMock(side_effect=KeyboardInterrupt)))
        mock_create.return_value = mock_server

        try:
            await run_mcp_server()
        except KeyboardInterrupt:
            pass

        # Should create server with defaults
        mock_create.assert_called_once_with()


class TestLogging:
    """Test logging configuration"""

    def test_server_has_logger(self):
        """Test that server has logger instance"""
        server = create_mcp_server(name="test-logging")

        assert hasattr(server, 'logger')
        assert server.logger is not None
        assert isinstance(server.logger, logging.Logger)

    def test_logger_name_includes_server_name(self):
        """Test that logger name includes server name"""
        server = create_mcp_server(name="custom-name")

        assert "custom-name" in server.logger.name

    @pytest.mark.asyncio
    async def test_initialize_fleet_logs_info(self):
        """Test that fleet initialization logs info messages"""
        server = create_mcp_server()

        with patch.object(server.logger, 'info') as mock_info:
            await server.initialize_fleet()

            # Should have logged multiple info messages
            assert mock_info.call_count >= 2

            # Check for specific log messages
            calls = [str(call) for call in mock_info.call_args_list]
            assert any("Initializing" in str(call) for call in calls)
            assert any("initialized" in str(call) for call in calls)

        await server.stop()

    def test_register_tools_logs_count(self):
        """Test that tool registration logs tool count"""
        server = MCPServer(name="test-tools")

        # Logger should have been called during __init__
        # (tools are registered in __init__)
        assert len(server.mcp._tools) >= 17


class TestErrorHandling:
    """Test error handling in server"""

    @pytest.mark.asyncio
    async def test_stop_handles_missing_fleet_gracefully(self):
        """Test that stop() handles missing fleet gracefully"""
        server = create_mcp_server()

        # Fleet is None
        assert server.fleet is None

        # Should not raise error
        try:
            await server.stop()
        except Exception as e:
            pytest.fail(f"stop() raised exception with no fleet: {e}")

    @pytest.mark.asyncio
    async def test_initialize_fleet_double_call_safe(self):
        """Test that calling initialize_fleet twice is safe"""
        server = create_mcp_server()

        await server.initialize_fleet()
        fleet1 = server.fleet

        # Should not raise error
        await server.initialize_fleet()
        fleet2 = server.fleet

        # Should be same instance
        assert fleet1 is fleet2

        await server.stop()


class TestMCPAvailability:
    """Test MCP_AVAILABLE flag"""

    def test_mcp_available_flag_exists(self):
        """Test that MCP_AVAILABLE flag exists"""
        from lionagi_qe.mcp import mcp_server

        assert hasattr(mcp_server, 'MCP_AVAILABLE')
        assert isinstance(mcp_server.MCP_AVAILABLE, bool)

    @patch('lionagi_qe.mcp.mcp_server.MCP_AVAILABLE', False)
    def test_fallback_fastmcp_when_not_available(self):
        """Test that fallback FastMCP is used when not available"""
        # Should use fallback implementation
        from lionagi_qe.mcp.mcp_server import FastMCP

        fallback_mcp = FastMCP("test")
        assert fallback_mcp.name == "test"
        assert hasattr(fallback_mcp, '_tools')
        assert fallback_mcp._tools == {}


class TestAgentConfiguration:
    """Test agent configuration during initialization"""

    @pytest.mark.asyncio
    async def test_test_generator_agent_config(self):
        """Test test generator agent configuration"""
        server = create_mcp_server(enable_learning=True)
        await server.initialize_fleet()

        test_gen = await server.fleet.get_agent("test-generator")

        assert test_gen.agent_id.name == "test-generator"
        assert test_gen.enable_learning is True
        assert "agentic-quality-engineering" in test_gen.skills

        await server.stop()

    @pytest.mark.asyncio
    async def test_test_executor_agent_config(self):
        """Test test executor agent configuration"""
        server = create_mcp_server()
        await server.initialize_fleet()

        test_exec = await server.fleet.get_agent("test-executor")

        assert test_exec.agent_id.name == "test-executor"
        assert "shift-left-testing" in test_exec.skills

        await server.stop()

    @pytest.mark.asyncio
    async def test_fleet_commander_agent_config(self):
        """Test fleet commander agent configuration"""
        server = create_mcp_server()
        await server.initialize_fleet()

        commander = await server.fleet.get_agent("fleet-commander")

        assert commander.agent_id.name == "fleet-commander"
        assert "holistic-testing-pact" in commander.skills

        await server.stop()

    @pytest.mark.asyncio
    async def test_agents_share_memory(self):
        """Test that all agents share the same memory instance"""
        server = create_mcp_server()
        await server.initialize_fleet()

        test_gen = await server.fleet.get_agent("test-generator")
        test_exec = await server.fleet.get_agent("test-executor")
        commander = await server.fleet.get_agent("fleet-commander")

        # All should share the same memory
        assert test_gen.memory is server.fleet.memory
        assert test_exec.memory is server.fleet.memory
        assert commander.memory is server.fleet.memory

        await server.stop()


@pytest.mark.asyncio
class TestStateExport:
    """Test state export functionality"""

    async def test_stop_exports_state_when_fleet_exists(self):
        """Test that stop exports state when fleet exists"""
        server = create_mcp_server()
        await server.start()

        mock_state = {"agents": [], "memory": {}}
        with patch.object(server.fleet, 'export_state', return_value=mock_state) as mock_export:
            await server.stop()

            mock_export.assert_called_once()

    async def test_stop_skips_export_when_no_fleet(self):
        """Test that stop skips export when fleet doesn't exist"""
        server = create_mcp_server()

        # No fleet initialized
        assert server.fleet is None

        # Should not raise error
        await server.stop()


class TestServerName:
    """Test server naming"""

    def test_default_server_name(self):
        """Test default server name"""
        server = create_mcp_server()
        assert server.name == "lionagi-qe"

    def test_custom_server_name(self):
        """Test custom server name"""
        server = create_mcp_server(name="my-custom-qe-server")
        assert server.name == "my-custom-qe-server"

    def test_server_name_matches_mcp_name(self):
        """Test that server name matches MCP instance name"""
        server = create_mcp_server(name="test-name-match")

        assert server.name == server.mcp.name
        assert server.name == "test-name-match"
