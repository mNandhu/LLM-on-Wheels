# Autonomous Mobile Robot - Assistance Mode

This project implements the "Assistance Mode" for a modular autonomous mobile robot using the LangGraph framework. This mode enables user interaction (voice), context-aware task handling, and robot action orchestration based on previously gathered environmental knowledge.

## Overview

The robot operates in two modes:

*   **Exploration Mode:** Generates a map and structured state memory of the environment.
*   **Assistance Mode:** (This project) Processes user voice commands to perform tasks like object finding, navigation, and answering questions.

## Core Components

*   **LangGraph Flow:** Defines the state and transitions for processing user commands.
*   **Nodes:** Individual functions or methods that perform specific tasks within the LangGraph flow (e.g., speech-to-text, intent detection, memory query, navigation).
*   **External Interfaces:** Integrations with external services and robot hardware (e.g., Whisper, ElevenLabs, ROS 2 Nav2, robot controllers).

## LangGraph Flow Diagram

```mermaid
graph TD
    classDef startEnd fill:#f9f,stroke:#333,stroke-width:2px;
    classDef process fill:#ccf,stroke:#333,stroke-width:1px;
    classDef decision fill:#fcf,stroke:#333,stroke-width:1px;
    classDef io fill:#9cf,stroke:#333,stroke-width:1px;
    classDef memory fill:#cfc,stroke:#333,stroke-width:1px;
    classDef action fill:#ffc,stroke:#333,stroke-width:1px;

    Start(User Speaks) --> UserInputNode;
    class Start startEnd;

    UserInputNode["1. UserInputNode<br>(Whisper: Audio -> Text,<br>Update History, Get Pose)"]:::io;
    UserInputNode --> IntentDetectionNode;

    IntentDetectionNode{"2. IntentDetectionNode<br>(Detect Intent & Entities)"}:::decision;
    IntentDetectionNode -- "Intent: FIND_OBJECT /<br> DESCRIBE_AREA /<br> NAVIGATE_TO_NAME" --> MemoryQueryNode;
    IntentDetectionNode -- "Intent: NAVIGATE_TO_COORDS" --> PrepNavTargetCoords["Prepare Navigation Target<br>(From Entities)"] ;
    IntentDetectionNode -- "Intent: DIRECT_ACTION<br>(Rotate, Stop, etc.)" --> ActionExecutionNode;
    IntentDetectionNode -- "Intent: CHITCHAT /<br> QUESTION_ANSWERING /<br> UNKNOWN / CONFIRMATION" --> LLMResponseNode;

    MemoryQueryNode["3. MemoryQueryNode<br>(Query Structured State Memory)"]:::memory;
    MemoryQueryNode --> RouteMemResult{"4. RouteBasedOnMemoryResult<br>(Check Query Results)"}:::decision;

    RouteMemResult -- "Object/Location Found<br>& Navigation Needed" --> PrepNavTargetMemory["Prepare Navigation Target<br>(From Memory Result)"];
    RouteMemResult -- "Info Found<br>(for Description/Answer)" --> LLMResponseNode;
    RouteMemResult -- "Ambiguous /<br>Needs Clarification" --> LLMResponseNode;
    RouteMemResult -- "Not Found" --> LLMResponseNode;

    PrepNavTargetCoords --> NavigationNode;
    PrepNavTargetMemory --> NavigationNode;

    NavigationNode["5a. NavigationNode<br>(Send Goal to Nav2,<br>Monitor Status,<br>Optional Visual Verify)"]:::action;
    ActionExecutionNode["5b. ActionExecutionNode<br>(Execute Non-Nav Action,<br>Monitor Status)"]:::action;

    NavigationNode -- "Status: SUCCEEDED / FAILED / CANCELED" --> LLMResponseNode;
    ActionExecutionNode -- "Status: SUCCEEDED / FAILED" --> LLMResponseNode;

    LLMResponseNode["6. LLMResponseNode<br>(Generate Response Text<br>using Context, History, Status)"]:::process;
    LLMResponseNode --> FormatResponseNode;

    FormatResponseNode["7. FormatResponseNode<br>(Finalize Text,<br>Update History)"]:::process;
    FormatResponseNode --> TextToSpeechNode;
    TextToSpeechNode["8. TextToSpeechNode<br>(ElevenLabs: Text -> Speech)"]:::io;

    TextToSpeechNode --> EndTurnNode(End Turn / Wait);
    class EndTurnNode startEnd;
```

## Implementation Details

Refer to the `implementation.prompt.md` file for detailed implementation requirements, including:

*   LangGraph state definition
*   Node implementations
*   Graph construction
*   External interface specifications
*   Error handling

## Getting Started

1.  Clone the repository.
2.  Install dependencies.
3.  Configure external API keys (Whisper, ElevenLabs, LLM).
4.  Set up ROS 2 Nav2.
5.  Run the Assistance Mode LangGraph flow.

## Contributing

Contributions are welcome! Please submit pull requests with clear descriptions of the changes.