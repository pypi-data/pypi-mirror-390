"""Bedrock AI Agent Tools for getout_of_text_3
==========================================

This package provides specialized LangChain-compatible tools for AWS Bedrock
that extend getout_of_text_3's analytical capabilities with advanced AI agents.

Available Tools:
- WikimediaMultiLangAnalysisTool: Multi-language forensic linguistics analysis
"""

from .wikimedia_multilang import WikimediaMultiLangAnalysisTool, WikimediaAnalysisInput

__all__ = [
    "WikimediaMultiLangAnalysisTool",
    "WikimediaAnalysisInput",
]