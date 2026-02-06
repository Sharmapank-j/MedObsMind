"""
DDMA (d²media Agent) - OpenAI-compatible Conversational AI Agent for dsquaremedicalmodel

This module provides a ChatGPT-like conversational interface for MedObsMind's dsquaremedicalmodel,
with OpenAI-compatible API, streaming support, function calling, and multi-turn conversations.

Similar to OpenAI's ChatGPT but specialized for medical use cases with Indian context.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, AsyncGenerator, Any
from enum import Enum

from .llm_service import LLMService
from .rag_service import RAGService
from .guardrails import Guardrails
from .conversation_service import ConversationService


class MessageRole(str, Enum):
    """Message roles in conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"  # Legacy


class ToolType(str, Enum):
    """Tool types for function calling"""
    FUNCTION = "function"


class FinishReason(str, Enum):
    """Reasons for completion finish"""
    STOP = "stop"
    LENGTH = "length"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"


class DDMAAgent:
    """
    d²media Agent (DDMA) - Conversational AI Agent for Medical Use Cases
    
    Features:
    - OpenAI-compatible API
    - Multi-turn conversations
    - Function/tool calling
    - Streaming responses
    - Medical domain expertise
    - Safety guardrails
    """
    
    def __init__(
        self,
        model: str = "dsquaremedicalmodel",
        system_prompt: Optional[str] = None
    ):
        """
        Initialize DDMA agent
        
        Args:
            model: Model name (dsquaremedicalmodel, dsquaremedicalmodel-multimodal)
            system_prompt: Custom system prompt (optional)
        """
        self.model = model
        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.guardrails = Guardrails()
        self.conversation_service = ConversationService()
        
        # Default medical system prompt
        self.default_system_prompt = """You are DDMA (d²media Agent), an AI medical assistant developed by d²media for MedObsMind.

Your capabilities:
- Provide evidence-based clinical guidance
- Support medical decision-making
- Explain medical concepts clearly
- Answer questions about patient care
- Use Indian medical guidelines (ICMR, AIIMS)
- Support both English and Hindi

Important guidelines:
- You are ASSISTIVE, not DIAGNOSTIC
- Always recommend clinician review for critical decisions
- Cite medical evidence when possible
- Acknowledge uncertainty when appropriate
- Prioritize patient safety above all
- Respect Indian medical context and practices

Your responses should be:
- Clear and concise
- Evidence-based
- Clinically relevant
- Culturally sensitive
- Safety-conscious"""
        
        self.system_prompt = system_prompt or self.default_system_prompt
        
        # Initialize available tools
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> List[Dict[str, Any]]:
        """
        Initialize available medical tools/functions
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_patient_vitals",
                    "description": "Get current vital signs for a patient including HR, BP, RR, SpO2, temperature",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {
                                "type": "string",
                                "description": "Patient identifier"
                            },
                            "time_range": {
                                "type": "string",
                                "enum": ["current", "24h", "48h", "7d"],
                                "description": "Time range for vital signs"
                            }
                        },
                        "required": ["patient_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_clinical_score",
                    "description": "Calculate clinical scores like NEWS2, qSOFA, SOFA, APACHE",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "score_type": {
                                "type": "string",
                                "enum": ["NEWS2", "qSOFA", "SOFA", "APACHE"],
                                "description": "Type of clinical score"
                            },
                            "vitals": {
                                "type": "object",
                                "description": "Patient vital signs"
                            }
                        },
                        "required": ["score_type", "vitals"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_guidelines",
                    "description": "Search Indian medical guidelines (ICMR, AIIMS) for specific conditions or treatments",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (condition, treatment, protocol)"
                            },
                            "source": {
                                "type": "string",
                                "enum": ["ICMR", "AIIMS", "all"],
                                "description": "Guideline source"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_drug_interaction",
                    "description": "Check for drug interactions and get dosing information from Indian formulary",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "drugs": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of drug names"
                            },
                            "patient_age": {
                                "type": "number",
                                "description": "Patient age for dosing"
                            },
                            "patient_weight": {
                                "type": "number",
                                "description": "Patient weight in kg"
                            }
                        },
                        "required": ["drugs"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_disease_info",
                    "description": "Get information about a disease including symptoms, diagnosis, treatment",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "disease": {
                                "type": "string",
                                "description": "Disease or condition name"
                            },
                            "aspect": {
                                "type": "string",
                                "enum": ["symptoms", "diagnosis", "treatment", "prognosis", "all"],
                                "description": "Specific aspect to focus on"
                            }
                        },
                        "required": ["disease"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_trend",
                    "description": "Analyze vital sign trends over time to detect deterioration or improvement",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {
                                "type": "string",
                                "description": "Patient identifier"
                            },
                            "parameter": {
                                "type": "string",
                                "enum": ["HR", "BP", "RR", "SpO2", "temperature", "all"],
                                "description": "Vital parameter to analyze"
                            },
                            "duration": {
                                "type": "string",
                                "enum": ["24h", "48h", "7d"],
                                "description": "Time period for trend analysis"
                            }
                        },
                        "required": ["patient_id"]
                    }
                }
            }
        ]
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 500,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate chat completion (OpenAI-compatible)
        
        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            tools: Available tools/functions
            tool_choice: "none", "auto", or specific function
            session_id: Session ID for conversation history
            
        Returns:
            Chat completion response (OpenAI format)
        """
        # Add system prompt if not present
        if not any(msg["role"] == "system" for msg in messages):
            messages.insert(0, {"role": "system", "content": self.system_prompt})
        
        # Format prompt for LLM
        prompt = self._format_messages(messages)
        
        # Check if tools are available and might be needed
        needs_tool = False
        if tools and tool_choice != "none":
            needs_tool = self._should_use_tool(messages, tools)
        
        # Generate response
        if needs_tool and tools:
            # Generate tool call
            response = await self._generate_tool_call(messages, tools)
        else:
            # Generate regular response
            response_text = await self.llm_service.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Apply guardrails
            safety_check = self.guardrails.check(response_text)
            
            if not safety_check["is_safe"]:
                response_text = safety_check["transformed_text"]
            
            response = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": self.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(prompt.split()) * 1.3,  # Approximate
                    "completion_tokens": len(response_text.split()) * 1.3,
                    "total_tokens": (len(prompt) + len(response_text)) * 1.3
                }
            }
        
        # Save to conversation history if session provided
        if session_id:
            await self.conversation_service.add_message(
                session_id=session_id,
                role="assistant",
                content=response["choices"][0]["message"]["content"]
            )
        
        return response
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 500,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate streaming chat completion
        
        Args:
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            session_id: Session ID for history
            
        Yields:
            Stream chunks (OpenAI format)
        """
        # Add system prompt
        if not any(msg["role"] == "system" for msg in messages):
            messages.insert(0, {"role": "system", "content": self.system_prompt})
        
        prompt = self._format_messages(messages)
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        
        # Simulate streaming (in production, use llama.cpp streaming)
        response_text = await self.llm_service.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Apply guardrails
        safety_check = self.guardrails.check(response_text)
        if not safety_check["is_safe"]:
            response_text = safety_check["transformed_text"]
        
        # Stream word by word
        words = response_text.split()
        full_response = ""
        
        for i, word in enumerate(words):
            chunk_content = word + " " if i < len(words) - 1 else word
            full_response += chunk_content
            
            chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": int(datetime.now().timestamp()),
                "model": self.model,
                "choices": [{
                    "index": 0,
                    "delta": {"content": chunk_content},
                    "finish_reason": None
                }]
            }
            yield chunk
            
            # Small delay for realistic streaming
            await asyncio.sleep(0.05)
        
        # Final chunk
        yield {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": int(datetime.now().timestamp()),
            "model": self.model,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }
        
        # Save to history
        if session_id:
            await self.conversation_service.add_message(
                session_id=session_id,
                role="assistant",
                content=full_response
            )
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages into prompt for LLM
        
        Args:
            messages: List of messages
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                prompt_parts.append(f"### System:\n{content}\n")
            elif role == "user":
                prompt_parts.append(f"### User:\n{content}\n")
            elif role == "assistant":
                prompt_parts.append(f"### Assistant:\n{content}\n")
            elif role == "tool":
                prompt_parts.append(f"### Tool Result:\n{content}\n")
        
        prompt_parts.append("### Assistant:\n")
        
        return "\n".join(prompt_parts)
    
    def _should_use_tool(self, messages: List[Dict], tools: List[Dict]) -> bool:
        """
        Determine if a tool should be called based on message content
        
        Args:
            messages: Conversation messages
            tools: Available tools
            
        Returns:
            True if tool should be called
        """
        last_user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg["content"].lower()
                break
        
        # Simple keyword matching (in production, use LLM to determine)
        tool_keywords = {
            "get_patient_vitals": ["vitals", "heart rate", "blood pressure", "spo2", "temperature"],
            "calculate_clinical_score": ["news2", "qsofa", "sofa", "score", "calculate"],
            "search_guidelines": ["guideline", "protocol", "icmr", "aiims", "recommendation"],
            "check_drug_interaction": ["drug", "medication", "interaction", "dosage"],
            "get_disease_info": ["what is", "tell me about", "disease", "condition", "diagnosis"],
            "analyze_trend": ["trend", "change", "over time", "progression", "deterioration"]
        }
        
        for tool_name, keywords in tool_keywords.items():
            if any(keyword in last_user_message for keyword in keywords):
                return True
        
        return False
    
    async def _generate_tool_call(
        self,
        messages: List[Dict],
        tools: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate a tool call response
        
        Args:
            messages: Conversation messages
            tools: Available tools
            
        Returns:
            Tool call response
        """
        # Simplified tool call generation
        # In production, use LLM to determine which tool and parameters
        
        last_user_message = messages[-1]["content"].lower()
        
        # Match tool based on keywords
        if "vitals" in last_user_message:
            tool_name = "get_patient_vitals"
            arguments = {"patient_id": "ICU-001", "time_range": "current"}
        elif "score" in last_user_message or "news2" in last_user_message:
            tool_name = "calculate_clinical_score"
            arguments = {"score_type": "NEWS2", "vitals": {}}
        elif "guideline" in last_user_message:
            tool_name = "search_guidelines"
            arguments = {"query": "sepsis management", "source": "all"}
        else:
            tool_name = "get_disease_info"
            arguments = {"disease": "sepsis", "aspect": "all"}
        
        tool_call_id = f"call_{uuid.uuid4().hex[:12]}"
        
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": self.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(arguments)
                        }
                    }]
                },
                "finish_reason": "tool_calls"
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool/function call
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        # In production, implement actual tool execution
        # For now, return mock data
        
        if tool_name == "get_patient_vitals":
            return {
                "patient_id": arguments.get("patient_id"),
                "timestamp": datetime.now().isoformat(),
                "vitals": {
                    "heart_rate": 115,
                    "blood_pressure": "95/60",
                    "respiratory_rate": 26,
                    "spo2": 92,
                    "temperature": 39.2,
                    "consciousness": "Alert"
                }
            }
        elif tool_name == "calculate_clinical_score":
            return {
                "score_type": arguments.get("score_type"),
                "score": 8,
                "risk_level": "High",
                "components": {
                    "heart_rate": 2,
                    "blood_pressure": 2,
                    "respiratory_rate": 2,
                    "temperature": 1,
                    "consciousness": 0
                }
            }
        elif tool_name == "search_guidelines":
            return {
                "query": arguments.get("query"),
                "results": [
                    {
                        "title": "ICMR Sepsis Management Guidelines 2023",
                        "summary": "Early recognition and treatment within 1 hour...",
                        "url": "https://icmr.nic.in/guidelines/sepsis"
                    }
                ]
            }
        else:
            return {"error": f"Tool {tool_name} not implemented"}
