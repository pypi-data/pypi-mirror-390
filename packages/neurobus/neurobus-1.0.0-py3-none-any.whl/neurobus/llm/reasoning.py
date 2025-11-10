"""
Reasoning engine for event analysis using LLMs.

Provides intelligent event processing, analysis, and decision support.
"""

import json
import logging
from typing import Any

from neurobus.core.event import Event
from neurobus.llm.connector import LLMConnector

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    LLM-powered reasoning engine for events.

    Analyzes events, extracts insights, and provides intelligent
    recommendations using LLM capabilities.

    Features:
    - Event analysis and classification
    - Insight extraction
    - Pattern detection
    - Decision support
    - Chain-of-thought reasoning
    - Context-aware responses

    Example:
        >>> engine = ReasoningEngine(connector)
        >>> await engine.initialize()
        >>>
        >>> # Analyze event
        >>> analysis = await engine.analyze_event(event)
        >>> print(analysis["classification"])
        >>>
        >>> # Extract insights
        >>> insights = await engine.extract_insights([event1, event2, event3])
    """

    def __init__(
        self,
        connector: LLMConnector,
        enable_chain_of_thought: bool = True,
    ) -> None:
        """
        Initialize reasoning engine.

        Args:
            connector: LLM connector instance
            enable_chain_of_thought: Enable step-by-step reasoning
        """
        self.connector = connector
        self.enable_chain_of_thought = enable_chain_of_thought

        # Statistics
        self._stats = {
            "analyses": 0,
            "insights_extracted": 0,
            "decisions_made": 0,
        }

        logger.info(f"ReasoningEngine initialized " f"(provider={connector.__class__.__name__})")

    async def initialize(self) -> None:
        """Initialize engine."""
        logger.info("ReasoningEngine ready")

    async def analyze_event(
        self,
        event: Event,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze a single event.

        Args:
            event: Event to analyze
            context: Optional additional context

        Returns:
            Analysis results including:
            - classification: Event classification
            - sentiment: Sentiment analysis
            - priority: Suggested priority
            - insights: Key insights
            - recommendations: Action recommendations
        """
        self._stats["analyses"] += 1

        # Build analysis prompt
        prompt = self._build_analysis_prompt(event, context)

        # Get LLM response
        response = await self.connector.generate(
            prompt=prompt,
            system_prompt=self._get_system_prompt("event_analysis"),
        )

        # Parse response
        try:
            analysis = self._parse_analysis(response.content)
            analysis["tokens_used"] = response.tokens_used
            return analysis

        except Exception as e:
            logger.error(f"Error parsing analysis: {e}", exc_info=True)
            return {
                "error": str(e),
                "raw_response": response.content,
                "tokens_used": response.tokens_used,
            }

    async def extract_insights(
        self,
        events: list[Event],
        time_window: str | None = None,
    ) -> dict[str, Any]:
        """
        Extract insights from multiple events.

        Args:
            events: List of events to analyze
            time_window: Optional time window description

        Returns:
            Insights including:
            - patterns: Detected patterns
            - anomalies: Anomalous events
            - trends: Observed trends
            - summary: Overall summary
        """
        self._stats["insights_extracted"] += 1

        # Build insights prompt
        prompt = self._build_insights_prompt(events, time_window)

        # Get LLM response
        response = await self.connector.generate(
            prompt=prompt,
            system_prompt=self._get_system_prompt("insight_extraction"),
        )

        # Parse response
        try:
            insights = self._parse_insights(response.content)
            insights["tokens_used"] = response.tokens_used
            insights["events_analyzed"] = len(events)
            return insights

        except Exception as e:
            logger.error(f"Error parsing insights: {e}", exc_info=True)
            return {
                "error": str(e),
                "raw_response": response.content,
                "tokens_used": response.tokens_used,
            }

    async def make_decision(
        self,
        event: Event,
        options: list[str],
        criteria: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make decision about event handling.

        Args:
            event: Event to decide on
            options: Available options
            criteria: Decision criteria

        Returns:
            Decision including:
            - chosen_option: Selected option
            - confidence: Confidence score (0-1)
            - reasoning: Decision reasoning
            - alternatives: Alternative options
        """
        self._stats["decisions_made"] += 1

        # Build decision prompt
        prompt = self._build_decision_prompt(event, options, criteria)

        # Get LLM response
        response = await self.connector.generate(
            prompt=prompt,
            system_prompt=self._get_system_prompt("decision_making"),
        )

        # Parse response
        try:
            decision = self._parse_decision(response.content)
            decision["tokens_used"] = response.tokens_used
            return decision

        except Exception as e:
            logger.error(f"Error parsing decision: {e}", exc_info=True)
            return {
                "error": str(e),
                "raw_response": response.content,
                "tokens_used": response.tokens_used,
            }

    async def reason_about_events(
        self,
        events: list[Event],
        question: str,
    ) -> dict[str, Any]:
        """
        Reason about events with chain-of-thought.

        Args:
            events: Events to reason about
            question: Question to answer

        Returns:
            Reasoning result including:
            - answer: Final answer
            - reasoning_steps: Chain-of-thought steps
            - confidence: Confidence score
        """
        # Build reasoning prompt
        prompt = self._build_reasoning_prompt(events, question)

        # Get LLM response with CoT
        if self.enable_chain_of_thought:
            system_prompt = self._get_system_prompt("chain_of_thought")
        else:
            system_prompt = self._get_system_prompt("direct_answer")

        response = await self.connector.generate(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        # Parse reasoning
        try:
            reasoning = self._parse_reasoning(response.content)
            reasoning["tokens_used"] = response.tokens_used
            return reasoning

        except Exception as e:
            logger.error(f"Error parsing reasoning: {e}", exc_info=True)
            return {
                "error": str(e),
                "raw_response": response.content,
                "tokens_used": response.tokens_used,
            }

    def _build_analysis_prompt(
        self,
        event: Event,
        context: dict[str, Any] | None,
    ) -> str:
        """Build prompt for event analysis."""
        lines = [
            "Analyze the following event:",
            "",
            f"Topic: {event.topic}",
            f"Timestamp: {event.timestamp}",
            f"Data: {json.dumps(event.data, indent=2)}",
        ]

        if event.context:
            lines.append(f"Context: {json.dumps(event.context, indent=2)}")

        if context:
            lines.append(f"Additional Context: {json.dumps(context, indent=2)}")

        lines.extend(
            [
                "",
                "Provide analysis in JSON format:",
                "{",
                '  "classification": "event type/category",',
                '  "sentiment": "positive/neutral/negative",',
                '  "priority": "high/medium/low",',
                '  "insights": ["insight1", "insight2"],',
                '  "recommendations": ["action1", "action2"]',
                "}",
            ]
        )

        return "\n".join(lines)

    def _build_insights_prompt(
        self,
        events: list[Event],
        time_window: str | None,
    ) -> str:
        """Build prompt for insight extraction."""
        lines = [
            f"Extract insights from {len(events)} events:",
        ]

        if time_window:
            lines.append(f"Time Window: {time_window}")

        lines.append("")

        # Add event summaries
        for i, event in enumerate(events[:10], 1):  # Limit to first 10
            lines.append(f"{i}. {event.topic} - {json.dumps(event.data)}")

        if len(events) > 10:
            lines.append(f"... and {len(events) - 10} more events")

        lines.extend(
            [
                "",
                "Provide insights in JSON format:",
                "{",
                '  "patterns": ["pattern1", "pattern2"],',
                '  "anomalies": ["anomaly1"],',
                '  "trends": ["trend1", "trend2"],',
                '  "summary": "overall summary"',
                "}",
            ]
        )

        return "\n".join(lines)

    def _build_decision_prompt(
        self,
        event: Event,
        options: list[str],
        criteria: dict[str, Any] | None,
    ) -> str:
        """Build prompt for decision making."""
        lines = [
            "Make a decision about this event:",
            "",
            f"Event: {event.topic}",
            f"Data: {json.dumps(event.data, indent=2)}",
            "",
            f"Available Options: {', '.join(options)}",
        ]

        if criteria:
            lines.append(f"Decision Criteria: {json.dumps(criteria, indent=2)}")

        lines.extend(
            [
                "",
                "Provide decision in JSON format:",
                "{",
                '  "chosen_option": "selected option",',
                '  "confidence": 0.85,',
                '  "reasoning": "explanation",',
                '  "alternatives": ["alt1", "alt2"]',
                "}",
            ]
        )

        return "\n".join(lines)

    def _build_reasoning_prompt(
        self,
        events: list[Event],
        question: str,
    ) -> str:
        """Build prompt for reasoning."""
        lines = [
            f"Question: {question}",
            "",
            "Events:",
        ]

        for i, event in enumerate(events, 1):
            lines.append(f"{i}. {event.topic} - {json.dumps(event.data)}")

        if self.enable_chain_of_thought:
            lines.extend(
                [
                    "",
                    "Think step by step and provide:",
                    "1. Your reasoning steps",
                    "2. The final answer",
                    "3. Confidence level (0-1)",
                ]
            )

        return "\n".join(lines)

    def _get_system_prompt(self, mode: str) -> str:
        """Get system prompt for different modes."""
        prompts = {
            "event_analysis": (
                "You are an expert event analyst. Analyze events carefully, "
                "classify them accurately, and provide actionable insights. "
                "Always respond in valid JSON format."
            ),
            "insight_extraction": (
                "You are a data analyst specializing in pattern detection. "
                "Identify trends, anomalies, and patterns in event data. "
                "Always respond in valid JSON format."
            ),
            "decision_making": (
                "You are a decision support system. Evaluate options carefully, "
                "consider all factors, and provide well-reasoned recommendations. "
                "Always respond in valid JSON format."
            ),
            "chain_of_thought": (
                "You are a logical reasoning system. Think step by step, "
                "show your work, and arrive at well-supported conclusions."
            ),
            "direct_answer": ("You are a concise assistant. Provide direct, accurate answers."),
        }

        return prompts.get(mode, "You are a helpful assistant.")

    def _parse_analysis(self, content: str) -> dict[str, Any]:
        """Parse analysis response."""
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())

        except json.JSONDecodeError:
            # Fallback: return as raw text
            return {"raw_analysis": content}

    def _parse_insights(self, content: str) -> dict[str, Any]:
        """Parse insights response."""
        return self._parse_analysis(content)  # Same parsing logic

    def _parse_decision(self, content: str) -> dict[str, Any]:
        """Parse decision response."""
        return self._parse_analysis(content)  # Same parsing logic

    def _parse_reasoning(self, content: str) -> dict[str, Any]:
        """Parse reasoning response."""
        # For chain-of-thought, keep full text
        result = self._parse_analysis(content)
        if "raw_analysis" in result:
            result["reasoning"] = result.pop("raw_analysis")
        return result

    def get_stats(self) -> dict[str, Any]:
        """Get engine statistics."""
        return {
            "analyses": self._stats["analyses"],
            "insights_extracted": self._stats["insights_extracted"],
            "decisions_made": self._stats["decisions_made"],
            "connector_stats": self.connector.get_stats(),
        }

    async def close(self) -> None:
        """Close engine."""
        logger.info("ReasoningEngine closed")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ReasoningEngine("
            f"connector={self.connector.__class__.__name__}, "
            f"cot={self.enable_chain_of_thought})"
        )
