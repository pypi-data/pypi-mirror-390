"""WikiMedia Multi-Language Analysis Tools for getout_of_text_3
============================================================

This module provides LangChain-compatible Tool classes for analyzing multi-language
WikiMedia datasets using computational forensic linguistics methodologies.

The tool is designed for cross-linguistic analysis of keyword usage patterns
across different languages and cultural contexts using OpenLLM-France WikiMedia datasets.

Key Features:
- Multi-language keyword analysis with language-specific keyword mapping
- Cross-linguistic semantic analysis and cultural context assessment
- Robust KWIC data parsing with multiple format support
- Forensic linguistics methodologies for comparative analysis
- Support for both single keyword and multi-language keyword dictionaries
- Enhanced error handling and debug capabilities

Usage:
    >>> from getout_of_text_3.agents.bedrock import WikimediaMultiLangAnalysisTool
    >>> tool = WikimediaMultiLangAnalysisTool(model=your_bedrock_model)
    >>> result = tool._run(
    ...     keyword_dict={"en": "bank", "fr": "banque", "es": "banco"},
    ...     results_json=your_kwic_data
    ... )
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, Union
import json
import re
from datetime import datetime

try:
    from langchain.tools import BaseTool
except ImportError as e:
    raise ImportError(
        "LangChain is required for WikiMedia analysis functionality. Install with: pip install langchain"
    ) from e

from pydantic import BaseModel, Field


class WikimediaAnalysisInput(BaseModel):
    """Input schema for WikiMedia multi-language forensic linguistics analysis."""
    
    keyword: Optional[str] = Field(
        default=None, 
        description="Single keyword for analysis (legacy mode)"
    )
    keyword_dict: Optional[Dict[str, str]] = Field(
        default=None,
        description="Dictionary mapping language codes to keywords (e.g., {'en': 'vehicle', 'fr': 'véhicule', 'es': 'vehículo'})"
    )
    results_json: Union[str, Dict[str, Any]] = Field(
        description="Pre-filtered WikiMedia KWIC JSON results from got3.search_keyword_corpus"
    )
    analysis_focus: Optional[str] = Field(
        default="forensic_linguistics", 
        description="Analysis approach: 'forensic_linguistics', 'semantic_variation', 'register_analysis', 'diachronic', 'comparative'"
    )
    max_contexts: Optional[int] = Field(
        default=None, description="DEPRECATED: No longer used. Tool processes all provided contexts."
    )
    return_json: bool = Field(
        default=False, description="If True, return structured JSON with reasoning and findings"
    )
    extraction_strategy: str = Field(
        default="all",
        description="Text extraction: 'first', 'all', or 'raw_json'"
    )
    debug: bool = Field(default=False, description="Enable debug metrics")


class WikimediaMultiLangAnalysisTool(BaseTool):
    """
    AI tool for computational forensic linguistics analysis of WikiMedia KWIC results.
    
    Enhanced for multi-lingual analysis - can accept either a single keyword or
    a dictionary mapping language codes to their respective keywords.
    
    Applies systematic data science, legal scholarship, and applied linguistics 
    methodologies to analyze keyword usage patterns across WikiMedia languages and genres.
    """
    name: str = "wikimedia_multilang_analysis"
    description: str = (
        "Performs computational forensic linguistics analysis on WikiMedia KWIC results "
        "with support for multi-lingual keyword analysis using data science and applied linguistics methodologies."
    )
    args_schema: Type[BaseModel] = WikimediaAnalysisInput
    model: Any = Field(exclude=True)

    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model

    def _run(
        self,
        keyword: Optional[str] = None,
        keyword_dict: Optional[Dict[str, str]] = None,
        results_json: Union[str, Dict[str, Any]] = None,
        analysis_focus: str = "forensic_linguistics",
        max_contexts: Optional[int] = None,
        return_json: bool = False,
        extraction_strategy: str = "all",
        debug: bool = False,
    ) -> Union[str, Dict[str, Any]]:
        try:
            return self._execute(keyword, keyword_dict, results_json, analysis_focus, max_contexts, return_json, extraction_strategy, debug)
        except Exception as e:
            error_str = str(e)
            return f"❌ Error during WikiMedia forensic analysis: {error_str}"

    async def _arun(
        self,
        keyword: Optional[str] = None,
        keyword_dict: Optional[Dict[str, str]] = None,
        results_json: Union[str, Dict[str, Any]] = None,
        analysis_focus: str = "forensic_linguistics",
        max_contexts: Optional[int] = None,
        return_json: bool = False,
        extraction_strategy: str = "all",
        debug: bool = False,
    ) -> Union[str, Dict[str, Any]]:
        return self._run(keyword, keyword_dict, results_json, analysis_focus, max_contexts, return_json, extraction_strategy, debug)

    def _execute(self, keyword, keyword_dict, results_json, analysis_focus, max_contexts, return_json, extraction_strategy, debug):
        # Validate input parameters
        if not keyword and not keyword_dict:
            raise ValueError("Either 'keyword' or 'keyword_dict' must be provided")
        
        # Parse and validate input - now handles both formats
        results_dict = self._parse_wikimedia_results(results_json)
        
        # Determine analysis mode and prepare keyword info
        if keyword_dict:
            # Multi-lingual mode
            analysis_keywords = keyword_dict
            analysis_type = "multilingual"
            primary_keyword = f"multilingual_analysis_{list(keyword_dict.values())[0]}"
        else:
            # Single keyword mode (legacy)
            analysis_keywords = {"unknown": keyword}
            analysis_type = "single"
            primary_keyword = keyword
        
        stats = self._compute_wikimedia_stats(results_dict, analysis_keywords, extraction_strategy)
        
        # Extract contexts and estimate token usage
        contexts = self._extract_contexts(results_dict, max_contexts, extraction_strategy)
        
        # Debug metrics
        if debug:
            print(f"✅ Reading WikiMedia results for {analysis_type} analysis")
            print(f"📝 Keywords: {analysis_keywords}")
            raw_chars = len(json.dumps(results_dict, default=str))
            extracted_chars = sum(len(c) for c in contexts)
            print(f"🧪 WikiMedia DEBUG: language_keys={len(results_dict)} raw_chars={raw_chars} extracted_chars={extracted_chars} total_contexts={len(contexts)}")
            
            # Debug: Show language distribution in ALL extracted contexts
            lang_context_counts = {}
            for context in contexts:
                if context.startswith('[') and ':' in context:
                    lang = context.split(':')[0][1:]  # Extract language from [lang:document_id]
                    lang_context_counts[lang] = lang_context_counts.get(lang, 0) + 1
            print(f"🎯 All extracted contexts by language: {lang_context_counts}")
            print(f"📊 Total contexts extracted: {len(contexts)}")
        
        # Build specialized prompt
        prompt = self._build_wikimedia_prompt(analysis_keywords, results_dict, stats, analysis_focus, max_contexts, return_json, extraction_strategy)
        
        # Invoke model
        response = self.model.invoke([{"role": "user", "content": prompt}])
        content = getattr(response, 'content', str(response))
        
        if return_json:
            return self._postprocess_wikimedia_json(content, stats, analysis_keywords)
        return content

    def _safe_str_conversion(self, obj):
        """Safely convert any object to string, handling nested structures."""
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, (list, tuple)):
            return " | ".join(str(item) for item in obj if item)
        elif isinstance(obj, dict):
            # For dict, join all values
            return " | ".join(str(v) for v in obj.values() if v)
        else:
            return str(obj)

    def _parse_wikimedia_results(self, results_json: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Parse WikiMedia results JSON - handles both formats: lang_id->kwic and lang->doc_id->kwic."""
        if isinstance(results_json, str):
            results_dict = json.loads(results_json)
        else:
            results_dict = results_json
        
        if not isinstance(results_dict, dict):
            raise ValueError("WikiMedia results must be a dict")
        
        # Check if we have the lang_id format (keys like "en_0", "fr_1")
        sample_keys = list(results_dict.keys())[:5]
        has_lang_id_format = any('_' in key and len(key.split('_')) == 2 for key in sample_keys)
        
        if has_lang_id_format:
            # Transform lang_id format to expected format
            transformed_dict = {}
            for lang_id, kwic_data in results_dict.items():
                if '_' not in lang_id:
                    continue
                    
                # Extract language code from lang_id (e.g., "en_0" -> "en")
                lang_code = lang_id.split('_')[0]
                
                # Initialize language dict if not exists
                if lang_code not in transformed_dict:
                    transformed_dict[lang_code] = {}
                
                # Handle KWIC data - it should be a dict like {'0': 'text content...', '1': 'more text...'}
                if isinstance(kwic_data, dict):
                    # Join all the KWIC entries for this document
                    kwic_texts = []
                    for kwic_key, kwic_value in kwic_data.items():
                        kwic_text = self._safe_str_conversion(kwic_value)
                        if kwic_text.strip():
                            kwic_texts.append(kwic_text)
                    
                    if kwic_texts:
                        # Join multiple KWIC contexts with separator
                        full_kwic_text = " ... ".join(kwic_texts)
                        transformed_dict[lang_code][lang_id] = full_kwic_text
                        
                elif isinstance(kwic_data, (list, tuple)):
                    # Handle list format
                    kwic_text = self._safe_str_conversion(kwic_data)
                    if kwic_text.strip():
                        transformed_dict[lang_code][lang_id] = kwic_text
                        
                else:
                    # Handle string or other formats
                    kwic_text = self._safe_str_conversion(kwic_data)
                    if kwic_text.strip():
                        transformed_dict[lang_code][lang_id] = kwic_text
            
            return transformed_dict
        else:
            # Already in expected format: lang -> doc_id -> kwic_text
            return results_dict

    def _extract_contexts(self, results_dict: Dict[str, Any], max_contexts: Optional[int], strategy: str) -> List[str]:
        """Extract ALL context strings from WikiMedia results - handles multilingual structure."""
        contexts = []
        
        # Handle WikiMedia JSON structure: {language: {document_id: kwic_text}}
        for lang_key, doc_dict in results_dict.items():
            if not isinstance(doc_dict, dict):
                continue
            
            # Extract ALL text content from document_id -> kwic_text mappings
            for doc_id, text_content in doc_dict.items():
                if isinstance(text_content, str) and text_content.strip():
                    # Format: [language:document_id] text_content
                    context_label = f"[{lang_key}:{doc_id}]"
                    contexts.append(f"{context_label} {text_content.strip()}")
                        
        return contexts

    def _compute_wikimedia_stats(self, results_dict: Dict[str, Any], analysis_keywords: Dict[str, str], strategy: str) -> Dict[str, Any]:
        """Compute statistics about WikiMedia results distribution - handles multilingual structure."""
        languages = set()
        lang_counts = {}
        total_contexts = 0
        
        for lang_key, doc_dict in results_dict.items():
            if isinstance(doc_dict, dict):
                languages.add(lang_key)
                
                # Count contexts (document entries)
                context_count = len(doc_dict)
                total_contexts += context_count
                lang_counts[lang_key] = context_count
        
        return {
            'keywords': analysis_keywords,
            'languages': sorted(list(languages)),
            'language_counts': lang_counts,
            'total_contexts': total_contexts,
            'extraction_strategy': strategy
        }

    def _build_wikimedia_prompt(self, analysis_keywords: Dict[str, str], results_dict: Dict[str, Any], stats: Dict[str, Any], 
                          analysis_focus: str, max_contexts: Optional[int], return_json: bool, 
                          extraction_strategy: str) -> str:
        """Build specialized prompt for multilingual WikiMedia forensic linguistics analysis."""
        
        contexts = self._extract_contexts(results_dict, max_contexts, extraction_strategy)
        
        # Build language summary from actual stats
        lang_summary = ", ".join([f"{lang}({stats['language_counts'][lang]})" for lang in stats['languages']])
        
        # Format keyword information for the prompt
        if len(analysis_keywords) > 1:
            keyword_info = "Multiple language-specific keywords: " + ", ".join([f"{lang}: '{keyword}'" for lang, keyword in analysis_keywords.items()])
            analysis_mode = "Cross-linguistic comparison"
        else:
            keyword_info = f"Single keyword: '{list(analysis_keywords.values())[0]}'"
            analysis_mode = "Single-language analysis"
        
        # Add explicit instruction about complete data inclusion
        contexts_section = f"""WikiMedia KWIC Contexts (ALL {len(contexts)} contexts from provided data):
---
IMPORTANT: ALL contexts from your provided WikiMedia data are included below: {lang_summary}
Each context is labeled [language:document_id] to show its source.
No sampling or filtering was performed - this is your complete dataset.
This is a multi-lingual dataset analyzing how concepts are expressed across different languages.
---
""" + "\n".join(contexts) + "\n---\n"
        
        focus_instructions = {
            "forensic_linguistics": """
            As a computational forensic linguist, perform systematic analysis to identify:
            1. **Cross-linguistic Semantic Range**: Document distinct senses/meanings across languages
            2. **Register Variation**: Compare usage patterns across languages and contexts
            3. **Collocational Profiles**: Identify language-specific collocates and their significance
            4. **Frequency Distributions**: Analyze language-specific frequency patterns
            5. **Cultural Semantic Differences**: Assess how meaning varies across linguistic communities
            6. **Forensic Implications**: Note patterns relevant to language identification, authorship, or cultural context
            """,
            "semantic_variation": """
            Focus on cross-linguistic semantic analysis:
            1. Identify polysemy patterns and meaning boundaries across languages
            2. Map semantic fields and conceptual domains by language
            3. Analyze metaphorical vs. literal usage across cultures
            4. Document semantic equivalence and divergence patterns
            """,
            "register_analysis": """
            Perform cross-linguistic register analysis:
            1. Compare formal vs. informal usage patterns across languages
            2. Identify language-specific conventions
            3. Analyze technical vs. general usage by language
            4. Map sociolinguistic variation patterns across cultures
            """,
            "comparative": """
            Perform cross-linguistic comparative analysis:
            1. Language-specific pattern comparison
            2. Usage frequency analysis across languages
            3. Contextual distribution mapping by language
            4. Identify language-specific semantic markers
            """
        }
        
        base_prompt = f"""
        You are a computational forensic linguistics AI agent analyzing multilingual WikiMedia data. 
        
        MULTILINGUAL ANALYSIS FRAMEWORK:
        You are analyzing a multilingual dataset with language-specific keywords. Apply equal attention to all languages represented, respecting linguistic diversity and cultural contexts.

        METHODOLOGICAL FRAMEWORK:
        Apply systematic data science, legal scholarship, and applied linguistics approaches for cross-linguistic analysis.

        CORPUS DATA SUMMARY:
        - Analysis Mode: {analysis_mode}
        - Keywords: {keyword_info}
        - Total Contexts Provided: {stats['total_contexts']:,} across {len(results_dict)} languages
        - Language Distribution: {lang_summary}
        - Contexts Analyzed: ALL {len(contexts)} contexts (complete dataset, no sampling)
        - Extraction Strategy: {extraction_strategy}
        
        ANALYSIS FOCUS: {analysis_focus}
        {focus_instructions.get(analysis_focus, focus_instructions['forensic_linguistics'])}

        SYSTEMATIC STEPS:
        1. **Data Overview**: Summarize distribution across ALL languages
        2. **Cross-linguistic Pattern Recognition**: Identify recurring and divergent patterns
        3. **Statistical Analysis**: Note frequency and distribution patterns across languages
        4. **Linguistic Analysis**: Analyze syntactic, semantic, and pragmatic features by language
        5. **Cultural Context Assessment**: Evaluate cultural and linguistic context variations
        6. **Interpretive Framework**: Provide systematic cross-linguistic interpretation guidelines

        CRITICAL CONSTRAINTS:
        - Use ALL the provided WikiMedia contexts (complete dataset as provided by user)
        - Apply rigorous linguistic methodology across all languages
        - Respect linguistic and cultural diversity in analysis
        - Avoid speculation beyond evidence
        - Maintain scientific objectivity across all language varieties

        {contexts_section}
        """
        
        if return_json:
            base_prompt += """
            Return ONLY valid JSON with this structure:
            {
              "keywords": object,
              "total_contexts": number,
              "language_distribution": object,
              "reasoning_content": [string, ...],
              "semantic_analysis": string,
              "cross_linguistic_patterns": string,
              "cultural_context_analysis": string,
              "forensic_implications": string,
              "summary": string,
              "limitations": string
            }
            """
        else:
            base_prompt += """
            Provide structured analysis with these sections:
            1. **Corpus Distribution Overview** (use the full language counts provided)
            2. **Cross-linguistic Semantic Analysis** 
            3. **Language-specific Patterns** (analyze patterns across ALL languages)
            4. **Cultural Context Analysis**
            5. **Collocational Analysis by Language**
            6. **Forensic Linguistics Assessment**
            7. **Cross-linguistic Interpretive Guidelines**
            8. **Methodological Limitations**
            """
        
        return base_prompt.strip()

    def _postprocess_wikimedia_json(self, content: str, stats: Dict[str, Any], analysis_keywords: Dict[str, str]) -> Dict[str, Any]:
        """Process and validate JSON response from model."""
        try:
            parsed = json.loads(content)
        except Exception:
            # Try to extract JSON from response
            match = re.search(r'{[\s\S]*}', content)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except Exception:
                    parsed = None
            else:
                parsed = None
        
        if not isinstance(parsed, dict):
            # Fallback structure
            parsed = {
                "keywords": analysis_keywords,
                "total_contexts": stats['total_contexts'],
                "language_distribution": stats['language_counts'],
                "reasoning_content": [
                    "Model did not return valid JSON; content auto-wrapped.",
                    "Analysis limited by response format issues."
                ],
                "semantic_analysis": content if isinstance(content, str) else str(content),
                "cross_linguistic_patterns": "Unable to extract due to format issues.",
                "cultural_context_analysis": "Unable to extract due to format issues.",
                "forensic_implications": "Analysis inconclusive due to response parsing failure.",
                "summary": "Response required manual wrapping - review raw content.",
                "limitations": "Auto-wrapped due to invalid JSON from model."
            }
        
        # Ensure required fields exist
        required_fields = {
            "reasoning_content": [],
            "semantic_analysis": "",
            "cross_linguistic_patterns": "",
            "cultural_context_analysis": "",
            "forensic_implications": "",
            "summary": "",
            "limitations": ""
        }
        
        for field, default in required_fields.items():
            if field not in parsed:
                parsed[field] = default
        
        return parsed


__all__ = [
    "WikimediaMultiLangAnalysisTool",
    "WikimediaAnalysisInput",
]
