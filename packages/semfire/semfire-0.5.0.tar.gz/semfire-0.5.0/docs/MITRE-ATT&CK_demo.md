# SemFire Detection Strategies (ATT&CK v18)

Generated: 2025-11-04T11:29:51.341594

## Overview

This document describes SemFire's detection strategies aligned with MITRE ATT&CK v18's 
Detection Strategies and Analytics model.

## Detection Strategies

### Multi-Turn Conversation Analysis

**ID**: `multi_turn_analysis`
**Description**: Analyze conversation sequences for semantic steering and context poisoning patterns across multiple message exchanges
**Behavioral Pattern**: Gradual semantic manipulation through conversation turns
**Platform**: LLM API

#### Analytics

##### Context Steering Detection

- **Description**: Detect hypothetical framing and steering language patterns
- **Logic**: Monitor for phrases indicating hypothetical scenarios: 'let's consider', 'what if', 'hypothetically', 'for the sake of argument'
- **Data Sources**: llm_api:request, conversation:history
- **Data Components**: LLM Request Content, Conversation History
- **Tunable Parameters**:
  - `lookback_window`: 5-10 messages
  - `indicator_threshold`: 3+ steering phrases
  - `score_threshold`: 7

##### Indirect Reference Detection

- **Description**: Identify attempts to reference previous harmful context indirectly
- **Logic**: Track backward references in conversation: 'refer back', 'as mentioned', 'expand on', 'that topic'
- **Data Sources**: conversation:history, conversation:context
- **Data Components**: Message References, Context Window
- **Tunable Parameters**:
  - `reference_density`: 2+ per message
  - `context_distance`: 3-7 messages back

##### Scheming Language Detection

- **Description**: Detect manipulative language indicating deceptive intent
- **Logic**: Identify phrases suggesting manipulation: 'they think', 'make them believe', 'without them knowing', 'subtly'
- **Data Sources**: llm_api:request, semantic:analysis
- **Data Components**: Request Content, Semantic Patterns
- **Tunable Parameters**:
  - `scheming_threshold`: 2+ manipulation phrases
  - `confidence_level`: 0.7

---

### Prompt Injection Detection

**ID**: `prompt_injection_analysis`
**Description**: Identify direct and indirect prompt injection attempts
**Behavioral Pattern**: Malicious instructions embedded in user input
**Platform**: LLM API

#### Analytics

##### Direct Injection Detection

- **Description**: Detect explicit instruction override attempts
- **Logic**: Monitor for instruction keywords: 'ignore previous', 'disregard', 'new instructions', 'system:', 'you are now'
- **Data Sources**: application:input, llm_api:request
- **Data Components**: User Input, API Request
- **Tunable Parameters**:
  - `keyword_threshold`: 1+ override phrase
  - `position_sensitivity`: beginning or end of message

---

### Crescendo Attack Escalation Detection

**ID**: `crescendo_escalation`
**Description**: Monitor for gradual escalation of request sensitivity across conversation
**Behavioral Pattern**: Incremental increase in harmful request severity
**Platform**: LLM API

#### Analytics

##### Sensitivity Escalation Tracking

- **Description**: Track increasing sensitivity scores across conversation turns
- **Logic**: Calculate sensitivity delta between consecutive messages and detect upward trends
- **Data Sources**: conversation:history, behavioral:monitoring
- **Data Components**: Message Sensitivity Scores, Conversation Progression
- **Tunable Parameters**:
  - `escalation_threshold`: 3+ consecutive increases
  - `sensitivity_delta`: >2 points per turn

##### Backtracking After Block Detection

- **Description**: Detect rephrasing attempts after content policy blocks
- **Logic**: Identify similar semantic content following policy violations
- **Data Sources**: llm_api:audit, conversation:history
- **Data Components**: Policy Violations, Message Similarity
- **Tunable Parameters**:
  - `semantic_similarity`: >0.8
  - `time_window`: within 3 messages

---

## Log Sources

SemFire uses the following log sources (v18 naming convention):

- `llm_api:request`: LLM API request/response logs
- `llm_api:audit`: LLM service audit and access logs
- `conversation:history`: Conversation session and message history
- `conversation:context`: Conversation context window tracking
- `application:input`: User input to LLM applications
- `application:prompt`: System prompts and prompt engineering logs
- `semantic:analysis`: Semantic pattern analysis logs
- `behavioral:monitoring`: User behavior and session monitoring
