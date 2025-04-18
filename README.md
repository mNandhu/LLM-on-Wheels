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
    %% Define Node Styles
    classDef startEnd fill:#f9f,stroke:#333,stroke-width:2px;
    classDef process fill:#ccf,stroke:#333,stroke-width:1px;
    classDef decision fill:#fcf,stroke:#333,stroke-width:1px;
    classDef io fill:#9cf,stroke:#333,stroke-width:1px;
    classDef memory fill:#cfc,stroke:#333,stroke-width:1px;
    classDef action fill:#ffc,stroke:#333,stroke-width:1px;

    %% Nodes
    Start(User Speaks) --> UserInputNode
    class Start startEnd
    class EndTurnNode startEnd

    UserInputNode["\1. UserInputNode<br>• Whisper: Audio → Text<br>• Update History/State<br>• Get Pose"]:::io
    UserInputNode --> IntentDetectionNode

    IntentDetectionNode{"\2. IntentDetectionNode<br>• Detect Intent<br>• Extract Entities"}:::decision
    IntentDetectionNode -->|"• FIND_OBJECT<br>• DESCRIBE_AREA<br>• NAVIGATE_TO_NAME"| MemoryQueryNode
    IntentDetectionNode -->|"NAVIGATE_TO_COORDS"| PrepNavTargetCoords["Prepare Target<br>(From Entities)"]
    IntentDetectionNode -->|"DIRECT_ACTION:<br>• Rotate<br>• Stop<br>• Etc."| ActionExecutionNode
    IntentDetectionNode -->|"• CHITCHAT<br>• QUESTION<br>• UNKNOWN<br>• CONFIRM"| LLMResponseNode

    MemoryQueryNode["\3. MemoryQueryNode<br>Query State Memory"]:::memory
    MemoryQueryNode --> RouteMemResult{"\4. Route Decision<br>Query Results"}:::decision

    RouteMemResult -->|"• Object Found<br>• Needs Navigation"| PrepNavTargetMemory["Prepare Target<br>(From Memory)"]
    RouteMemResult -->|"• Info Found"| LLMResponseNode
    RouteMemResult -->|"• Ambiguous<br>• Needs Clarify"| LLMResponseNode
    RouteMemResult -->|"• Not Found"| LLMResponseNode

    PrepNavTargetCoords --> NavigationNode
    PrepNavTargetMemory --> NavigationNode

    NavigationNode["\5a. NavigationNode<br>• Send Nav2 Goal<br>• Monitor Status<br>• Visual Verify"]:::action
    ActionExecutionNode["\5b. ActionNode<br>• Execute Command<br>• Monitor Status"]:::action

    NavigationNode -->|"• SUCCEEDED<br>• FAILED<br>• CANCELED"| LLMResponseNode
    ActionExecutionNode -->|"• SUCCEEDED<br>• FAILED"| LLMResponseNode

    LLMResponseNode["\6. LLM Response<br>• Generate Text<br>• Use Context"]:::process
    LLMResponseNode --> FormatResponseNode

    FormatResponseNode["\7. Format Response<br>• Finalize Text<br>• Update History"]:::process
    FormatResponseNode --> TextToSpeechNode
    TextToSpeechNode["\8. TTS Node<br>ElevenLabs Speech"]:::io
    TextToSpeechNode --> EndTurnNode(End Turn / Wait)

    %% EndTurnNode -.-> Start
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