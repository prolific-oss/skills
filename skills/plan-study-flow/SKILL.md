---
name: Plan Study Flow
description: Use this skill to plan or create specifications for Prolific studies. 
version: 0.1.0
---

## Plan Study

This is the first step of the study setup process. The goal is to gather initial information about the study, not setting up the study itself.

Ask questions to help the researcher to create a high level specification for their study. Create a spec.md file when you have all the information you need to complete the specification. If the user shares more information, keep them in the spec file. The spec.md file should be in the following format:

<SpecTemplate>
## Overview
Provide a brief overview of the study, including its purpose, objectives, and any relevant background information. Keep it concise and clear, highlighting the key aspects of the study. 
## Task Format
`batch` for annotation tasks or `collection` for data collection tasks. Specify the format that best suits the study's requirements. 
## Output Details
Highlevel description of the expected output, including the type of data to be collected or annotated, the format of the output, and any specific requirements or constraints. 
</SpecTemplate>

## Study Setup Flow

Create flow.json file to represent the flow of the study setup process. Align the flow based on the task format. Use the following structure for the flow.json file:

```json
{
  "nodes": [
    { "id": "start", "name": "Start" },
    { "id": "plan", "name": "Plan" },
    { "id": "dataset", "name": "Capture Dataset" },
    { "id": "task_design_batch", "name": "Annotation Task Design" },
    { "id": "task_design_collection", "name": "Data Collection Task Design" },
    { "id": "participants", "name": "Participants" },
    { "id": "publish", "name": "Analysis" }
  ],
  "edges": [
    { "from": "start", "to": "plan" },
    { "from": "plan", "to": "dataset" },
    { "from": "dataset", "to": "task_design_batch" },
    { "from": "task_design_batch", "to": "participants" },
    { "from": "participants", "to": "publish" },
  ]
}
```
