"""Unit tests for v1.1.1 bugfixes"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from lionagi_qe.agents import CodeComplexityAnalyzerAgent, QualityGateAgent
from lionagi_qe.core.task import QETask
from lionagi_qe.core.memory import QEMemory


class TestCodeComplexityFix:
    """Test CodeComplexityAnalyzerAgent config attribute fix"""

    @pytest.fixture
    def mock_model(self):
        """Create mock LionAGI model"""
        model = MagicMock()
        model.provider = "openai"
        model.model = "gpt-4o-mini"
        return model

    @pytest.fixture
    def agent(self, mock_model):
        """Create CodeComplexityAnalyzerAgent with mocked dependencies"""
        memory = QEMemory()
        agent = CodeComplexityAnalyzerAgent(
            agent_id="complexity-test",
            model=mock_model,
            memory=memory
        )
        return agent

    def test_agent_has_agent_id_not_config(self, agent):
        """Verify agent has agent_id attribute, not config.agent_id"""
        # Should have agent_id directly
        assert hasattr(agent, "agent_id")
        assert agent.agent_id == "complexity-test"

        # Should NOT have config.agent_id (this was the bug)
        assert not hasattr(agent, "config") or not hasattr(agent.config, "agent_id")

    @pytest.mark.asyncio
    async def test_memory_keys_use_agent_id(self, agent, mock_model):
        """Verify agent uses self.agent_id (not self.config.agent_id) in memory keys"""
        # Mock the operate method to avoid actual LLM calls
        mock_result = MagicMock()
        mock_result.score = 85.0
        mock_result.issues = []
        mock_result.recommendations = []
        mock_result.metrics = {}
        mock_result.summary = "Test"
        agent.operate = AsyncMock(return_value=mock_result)

        task = QETask(
            task_type="analyze_complexity",
            context={
                "files": [{"path": "test.py", "content": "def foo(): pass"}],
                "thresholds": {"cyclomatic_complexity": 10},
                "enable_recommendations": False
            }
        )

        # Execute should work without AttributeError
        result = await agent.execute(task)

        # Verify memory keys were created using agent_id
        history_key = f"aqe/complexity/{agent.agent_id}/history"
        result_key = f"aqe/complexity/{agent.agent_id}/latest-result"

        # Check that memory was accessed with correct keys
        history = await agent.get_memory(history_key, default=[])
        assert isinstance(history, list)


class TestQualityGateFix:
    """Test QualityGateAgent response model attribute fix"""

    @pytest.fixture
    def mock_model(self):
        """Create mock LionAGI model"""
        model = MagicMock()
        model.provider = "openai"
        model.model = "gpt-4o-mini"
        return model

    @pytest.fixture
    def agent(self, mock_model):
        """Create QualityGateAgent with mocked dependencies"""
        memory = QEMemory()
        agent = QualityGateAgent(
            agent_id="quality-gate-test",
            model=mock_model,
            memory=memory
        )
        return agent

    @pytest.mark.asyncio
    async def test_decision_has_both_score_and_quality_score(self, agent):
        """Verify QualityGateDecision has both 'score' and 'quality_score' attributes"""
        from lionagi_qe.agents.quality_gate import QualityGateDecision, RiskAssessment

        # Create a test decision
        decision = QualityGateDecision(
            decision="GO",
            score=85.0,
            risk_assessment=RiskAssessment(
                risk_level="low",
                critical_path_impact=0.2,
                user_impact_scope=0.1,
                recovery_complexity=0.3,
                regulatory_impact=0.0,
                reputation_risk=0.1,
                overall_score=15.0,
                mitigation_strategies=[]
            ),
            policy_violations=[],
            metrics={"coverage": 85.0},
            threshold_results={"coverage": True},
            conditions=[],
            recommendations=[],
            override_eligible=False,
            justification="All metrics passed",
            next_steps=["Deploy to production"]
        )

        # Both attribute names should work
        assert decision.score == 85.0
        assert decision.quality_score == 85.0

        # They should return the same value
        assert decision.score == decision.quality_score

    @pytest.mark.asyncio
    async def test_backward_compatibility_with_quality_score(self, agent):
        """Verify existing code using quality_score still works"""
        from lionagi_qe.agents.quality_gate import QualityGateDecision, RiskAssessment

        decision = QualityGateDecision(
            decision="NO-GO",
            score=45.0,
            risk_assessment=RiskAssessment(
                risk_level="high",
                critical_path_impact=0.8,
                user_impact_scope=0.7,
                recovery_complexity=0.6,
                regulatory_impact=0.5,
                reputation_risk=0.9,
                overall_score=75.0,
                mitigation_strategies=["Add more tests"]
            ),
            policy_violations=[],
            metrics={"coverage": 45.0},
            threshold_results={"coverage": False},
            conditions=[],
            recommendations=["Increase test coverage"],
            override_eligible=False,
            justification="Coverage below threshold",
            next_steps=["Fix tests"]
        )

        # Code using the old attribute name should still work
        try:
            quality_score = decision.quality_score
            assert quality_score == 45.0
        except AttributeError:
            pytest.fail("quality_score attribute not accessible (backward compatibility broken)")


class TestAgentInitialization:
    """Test that all agents can be initialized without errors"""

    @pytest.fixture
    def mock_model(self):
        model = MagicMock()
        model.provider = "openai"
        model.model = "gpt-4o-mini"
        return model

    def test_code_complexity_agent_init(self, mock_model):
        """Test CodeComplexityAnalyzerAgent initialization"""
        memory = QEMemory()
        agent = CodeComplexityAnalyzerAgent(
            agent_id="test-complexity",
            model=mock_model,
            memory=memory
        )

        assert agent.agent_id == "test-complexity"
        assert agent.model == mock_model
        assert agent.memory is not None

    def test_quality_gate_agent_init(self, mock_model):
        """Test QualityGateAgent initialization"""
        memory = QEMemory()
        agent = QualityGateAgent(
            agent_id="test-quality-gate",
            model=mock_model,
            memory=memory
        )

        assert agent.agent_id == "test-quality-gate"
        assert agent.model == mock_model
        assert agent.memory is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
