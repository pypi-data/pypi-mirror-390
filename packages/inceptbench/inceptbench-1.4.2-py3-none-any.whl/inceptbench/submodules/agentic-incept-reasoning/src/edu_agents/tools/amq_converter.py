"""Stub for AMQConverter - not included in evaluator-only build."""


class AMQConverter:
    """Stub AMQConverter - raises error if used."""

    async def convert_to_amq(self, text: str) -> str:
        raise NotImplementedError(
            "AMQConverter is not available in this evaluator-only build. "
            "The full agentic-incept-reasoning package is required for AMQ conversion."
        )
