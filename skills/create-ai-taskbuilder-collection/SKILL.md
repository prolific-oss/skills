---
name: create-task-builder-collection
description:
  Create an AI Task Builder collection from a template file, natural language document, or interactive prompts.
  Collections define structured task workflows that participants complete in studies.
allowed-tools: Bash, WebFetch, Read
argument-hint: [template-path or document-path or --generate]
version: 0.1.0
---

# Create AI Task Builder Collection

Create a Task Builder collection that defines a structured task workflow for participants to complete in Prolific studies.

## Prerequisites

This skill assumes the user has the following:

1. **Prolific CLI installed** - https://github.com/prolific-oss/cli
2. **PROLIFIC_TOKEN environment variable set** with a valid API token
3. **Claude Code enabled** to execute bash commands
4. **AI Task Builder Collections enabled** on your workspace (early-access feature - request via Prolific help center)

All prerequisites must be met, otherwise we should not proceed. If missing, please indicate the required prerequisites to
the user.

## Best Practices

- **Use Document Mode for non-technical users** - Describe your collection in a text file instead of answering questions
- **Be specific in documents** - Use clear patterns like "1-5 scale", "dropdown", "open text" to avoid ambiguity
- **Generate template files first** - Review and edit before creating the collection
- **Use interactive mode for full control** - Answer questions to build templates step-by-step
- **Always preview collections** - Use `prolific collection preview <id>` to see how participants will experience it
- **Expect multiple iterations** - Collections typically require 2-3 rounds of edit → update → preview
- **Preview before every publish** - Never publish without previewing first
- **Check the environment** by inspecting the `PROLIFIC_URL` environment variable (if not set, assumes production)
- **Save templates for reuse** - Templates can be modified and reused for similar collections

## Workflow Modes

This skill supports three workflows:

### 1. Document Mode (provide .txt, .md, or .docx file)

Parse a natural language document describing the collection, ask clarifying questions, and generate a template.

### 2. Interactive Mode (`--generate` flag or no arguments)

Ask the user questions and generate a template file locally for review and editing.

### 3. Create from Template Mode (provide .json or .yaml file)

Use an existing template file to create the collection.

## Documentation References

**IMPORTANT:** Always fetch the current API documentation at runtime to ensure compatibility with the latest API version.

**Primary documentation sources:**

- **Collections API**: https://docs.prolific.com/api-reference/ai-task-builder/collections
- **Instructions Reference**: https://docs.prolific.com/api-reference/ai-task-builder/instructions

Before generating templates or guiding users, use WebFetch to retrieve the current:

1. Collection structure and required fields
2. Supported instruction types and their properties
3. Content block types
4. Field requirements and validation rules

This ensures the skill always works with the latest API specification without requiring updates.

## Implementation Approach

### Document Mode

1. **Detect file type** by extension (.txt, .md, .docx vs .json, .yaml)
2. **Read the document** using Read tool (text files) or appropriate parser (Word docs)
3. **Fetch current API documentation** using WebFetch:
   - Collections API structure
   - Available instruction types and their required fields
   - Content block types
4. **Parse natural language** to extract:
   - Collection name and description
   - Task details (name, introduction, steps)
   - Page structure and titles
   - Field descriptions and their likely types
5. **Ask clarifying questions** for:
   - Ambiguous field types (e.g., "rating" could be multiple_choice or free_text_with_unit)
   - Missing required properties (e.g., options for multiple_choice fields)
   - Unclear ordering or grouping
   - Required vs optional fields
6. **Ask for output template path**
7. **Generate JSON template** based on parsed information and clarifications
8. **Save template** to specified file path
9. **Show next steps**: review, create collection, preview

### Interactive Mode

1. **Fetch current documentation** using WebFetch:
   - Collections API structure
   - Available instruction types and their required fields
   - Content block types
2. Ask user where to save the template file
3. Gather collection configuration through questions:
   - Collection name and description
   - Task details (name, introduction, steps)
   - Pages structure (title, order)
   - Page items (instructions and content blocks) - based on current API
4. Generate complete JSON template based on current API spec
5. Save template to specified file path
6. Show the user the file location
7. Explain they can review/edit it
8. Show command to create collection from template

### Create from Template Mode

1. Validate template file path argument exists
2. Check file is readable and valid JSON
3. Show template preview to user
4. Ask for confirmation
5. Execute: `prolific collection create -t <template-file>`
6. Parse output for collection ID
7. Report success with collection ID

## Required Information for Template Generation

When generating a template, you must gather from the user:

- **Output file path** (where to save the template, e.g., "my-collection.json")
- **Collection name** (required - collection title)
- **Collection description** (optional - summary of the collection)
- **Task details** (optional but recommended):
  - Task name (participant-facing task title)
  - Task introduction (overview or guidance text)
  - Task steps (array of sequential steps to follow)
- **Collection items (pages)** - one or more pages:
  - Page order (position sequence)
  - Page title (heading displayed to participants)
  - **Page items** - instructions and content blocks (types determined from API docs)

## Document Format Guidelines

When using Document Mode, the natural language document should describe the collection structure. The skill will parse this and ask clarifying questions.

### Supported Document Formats

- **Text files** (.txt, .md) - Plain text or Markdown
- **Word documents** (.docx) - Will be converted to text for parsing

### What to Include

1. **Collection overview** - Name and purpose
2. **Task details** - What participants will do
3. **Pages** - Logical sections/steps
4. **Fields per page** - Questions, inputs, or content to display

### Writing Style

Be clear and specific, but don't worry about exact technical terms. The skill will:

- Interpret common terms (e.g., "dropdown" → multiple_choice with answer_limit: 1)
- Ask for clarification when ambiguous
- Suggest appropriate field types based on context

### Example Document

```markdown
# Customer Feedback Collection

Collect feedback about our new mobile app feature.

## Overview

- Name: Mobile App Feedback Survey
- Purpose: Gather user opinions on the new checkout flow

## Task Instructions

Participants should:

1. Review the feature description
2. Provide ratings on key aspects
3. Share detailed feedback

## Page 1: Feature Overview

Show participants a description of the new feature with an image.

- Display: Feature description (text block)
- Display: Screenshot of the feature (image URL: https://example.com/feature.png)

## Page 2: Ratings

Ask participants to rate different aspects:

- Overall satisfaction (1-5 scale)
- Ease of use (1-5 scale)
- Visual design (1-5 scale)
- Would you recommend this to others? (Yes/No)

## Page 3: Detailed Feedback

Get more detailed responses:

- What did you like most? (open text, required)
- What could be improved? (open text, optional)
- How long have you used our app? (number with time unit: days/weeks/months/years)
- Upload a screenshot of any issues (file upload: images only)

## Page 4: Demographics

Optional demographic information:

- Age range (dropdown: 18-24, 25-34, 35-44, 45-54, 55+)
- How often do you use the app? (multiple choice: Daily, Weekly, Monthly, Rarely)
```

### Parsing Strategy

The skill will:

1. **Identify sections** (headings, paragraphs, lists)
2. **Extract collection metadata** (name, description from overview)
3. **Detect pages** (## Page N: Title or similar patterns)
4. **Recognize field patterns**:
   - "1-5 scale" → multiple_choice with 5 options
   - "Yes/No" → multiple_choice with 2 options
   - "open text" → free_text or textarea
   - "dropdown" → multiple_choice with answer_limit: 1
   - "file upload" → file_upload
   - "number with unit" → free_text_with_unit
   - "display/show" → rich_text or image content blocks
5. **Infer properties**:
   - "(required)" / "(optional)" → required: true/false
   - Lists of options → choices array for multiple_choice
   - Image URLs → image content block
6. **Ask clarifying questions**:
   - "Should 'Overall satisfaction (1-5 scale)' use numeric labels (1, 2, 3, 4, 5) or descriptive labels (Very Poor, Poor, Neutral, Good, Very Good)?"
   - "For 'open text' fields, do you want single-line (free_text) or multi-line (textarea)?"
   - "What helper text should we show for field X?"

### Tips for Best Results

- **Be explicit about field types** when you know what you want
- **Include example options** for multiple choice fields
- **Specify required vs optional** for each field
- **Provide URLs** for images or external content
- **Use clear section headings** to separate pages
- **Include helper text** or guidance for participants

## Command Sequence for Document Mode

```bash
#!/bin/bash
set -e  # Exit on error

# Mode 1: Document Mode
# Parse natural language document and generate template

DOCUMENT_FILE="$1"

# Validate document file exists
if [ ! -f "$DOCUMENT_FILE" ]; then
  echo "Error: Document file not found: $DOCUMENT_FILE"
  exit 1
fi

# Detect file type
EXT="${DOCUMENT_FILE##*.}"

# Read document content
if [[ "$EXT" == "txt" || "$EXT" == "md" ]]; then
  # Read text files directly
  DOCUMENT_CONTENT=$(cat "$DOCUMENT_FILE")
elif [ "$EXT" == "docx" ]; then
  # For Word documents, need to extract text
  # Options: use pandoc, python-docx, or similar
  # Example with pandoc:
  if command -v pandoc &> /dev/null; then
    DOCUMENT_CONTENT=$(pandoc -f docx -t plain "$DOCUMENT_FILE")
  else
    echo "Error: pandoc required for .docx files. Install: brew install pandoc"
    exit 1
  fi
else
  echo "Error: Unsupported document format. Use .txt, .md, or .docx"
  exit 1
fi

echo "Document loaded successfully!"
echo ""

# At this point, Claude should:
# 1. Fetch current API documentation using WebFetch
# 2. Parse the DOCUMENT_CONTENT to extract:
#    - Collection name and description
#    - Task details (name, introduction, steps)
#    - Pages and their structure
#    - Fields with their types and properties
# 3. Ask clarifying questions for ambiguous items
# 4. Generate JSON template based on parsed info + clarifications

# Example of what Claude would do after parsing:
OUTPUT_FILE="<user-provided-or-derived-from-doc-name>.json"

# Generate template using jq based on parsed information
jq -n \
  --arg name "Parsed Collection Name" \
  --arg desc "Parsed Collection Description" \
  '{
    "name": $name,
    "description": $desc,
    "task_details": {
      "task_name": "Parsed Task Name",
      "task_introduction": "Parsed Introduction",
      "task_steps": ["Parsed Step 1", "Parsed Step 2"]
    },
    "collection_items": [
      # Generated based on parsed pages and fields
    ]
  }' > "$OUTPUT_FILE"

echo ""
echo "=========================================="
echo "Template generated from document!"
echo "=========================================="
echo "Source: $DOCUMENT_FILE"
echo "Output: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "1. Review and edit the template file if needed"
echo "2. Create the collection:"
echo "   /create-task-builder-collection $OUTPUT_FILE"
echo ""
```

## Command Sequence for Interactive Mode

```bash
#!/bin/bash
set -e  # Exit on error

# Mode 2: Interactive Mode
# First, Claude should fetch the current API documentation to understand
# the supported instruction types and structure

# After fetching documentation, gather user inputs
OUTPUT_FILE="<user-provided-path>"
COLLECTION_NAME="<user-provided>"
COLLECTION_DESC="<user-provided>"
TASK_NAME="<user-provided>"
TASK_INTRO="<user-provided>"
# ... additional fields based on current API docs

# Generate the template JSON using jq for proper JSON formatting
# Structure should match the current API specification
jq -n \
  --arg name "$COLLECTION_NAME" \
  --arg desc "$COLLECTION_DESC" \
  --arg task_name "$TASK_NAME" \
  --arg task_intro "$TASK_INTRO" \
  '{
    "name": $name,
    "description": $desc,
    "task_details": {
      "task_name": $task_name,
      "task_introduction": $task_intro,
      "task_steps": [
        "Step 1: Read the content carefully",
        "Step 2: Complete all required fields",
        "Step 3: Submit your response"
      ]
    },
    "collection_items": [
      {
        "order": 1,
        "title": "Page 1 Title",
        "page_items": [
          # Items structure based on fetched API documentation
        ]
      }
    ]
  }' > "$OUTPUT_FILE"

echo ""
echo "=========================================="
echo "Template generated successfully!"
echo "=========================================="
echo "File saved to: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "1. Review and edit the template file if needed"
echo "2. Create the collection:"
echo "   /create-task-builder-collection $OUTPUT_FILE"
echo ""
```

## Command Sequence for Creating from Template

```bash
#!/bin/bash
set -e  # Exit on error

# Mode 3: Create from Template
TEMPLATE_FILE="$1"

# Validate template file
if [ -z "$TEMPLATE_FILE" ]; then
  echo "Error: Template file path is required"
  echo "Usage: /create-task-builder-collection <template-file>"
  exit 1
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "Error: Template file not found: $TEMPLATE_FILE"
  exit 1
fi

# Validate JSON syntax
if ! jq empty "$TEMPLATE_FILE" 2>/dev/null; then
  echo "Error: Invalid JSON in template file"
  exit 1
fi

# Show template preview
echo "Template file: $TEMPLATE_FILE"
echo ""
echo "Template preview:"
echo "----------------------------------------"
jq . "$TEMPLATE_FILE"
echo "----------------------------------------"
echo ""

# Ask for confirmation (user interaction point)
echo "Ready to create collection from this template?"
echo ""

# Create the collection
echo "Creating collection..."
COLLECTION_OUTPUT=$(prolific collection create -t "$TEMPLATE_FILE")
COLLECTION_ID=$(echo "$COLLECTION_OUTPUT" | jq -r '.id')

echo ""
echo "Collection created successfully!"
echo "Collection ID: $COLLECTION_ID"
echo ""
echo "Next steps:"
echo "1. Preview: prolific collection preview $COLLECTION_ID"
echo "2. Review: prolific collection get $COLLECTION_ID"
echo "3. Update if needed: prolific collection update $COLLECTION_ID -t $TEMPLATE_FILE"
echo "4. Publish when ready: /publish-task-builder-collection $COLLECTION_ID"
```

## Document Mode Generation Flow

When a user provides a natural language document, follow this approach:

### 1. Detect Mode

Check file extension:

- `.txt`, `.md` → Text document (Document Mode)
- `.docx` → Word document (Document Mode)
- `.json`, `.yaml` → Template file (Template Mode)

### 2. Read Document

Use Read tool for text files, pandoc or similar for Word documents.

### 3. Fetch Current API Documentation

Use WebFetch to retrieve current AI Task Builder specs (same as Interactive Mode).

### 4. Parse Document Content

Analyze the document to extract:

**Collection metadata:**

- Look for title/heading or "Name:" patterns
- Extract description from introductory paragraphs
- Identify purpose or overview sections

**Task details:**

- Find "Task", "Instructions", "Participants should" sections
- Extract task name, introduction, and numbered steps

**Pages:**

- Identify page markers: "## Page N:", "# Section:", headings
- Extract page titles and order

**Fields:**

- Recognize patterns:
  - "rate", "1-5 scale" → multiple_choice with numeric options
  - "Yes/No", "True/False" → multiple_choice with 2 options
  - "open text", "comments", "feedback" → free_text or textarea
  - "dropdown", "select from" → multiple_choice with answer_limit: 1
  - "choose all that apply" → multiple_choice with answer_limit: -1
  - "upload", "attach" → file_upload
  - "with unit", "measurement" → free_text_with_unit
  - "display", "show", "image" → rich_text or image content block
- Extract field labels from questions or prompts
- Identify required vs optional markers: "(required)", "(optional)", "must", "should"
- Extract option lists for multiple choice fields

### 5. Build Structured Representation

Create internal structure mapping document content to API schema.

### 6. Ask Clarifying Questions

For each ambiguous or incomplete item:

**Field type ambiguity:**

- "I found 'rate satisfaction (1-5)'. Should this use:
  1. Numeric labels (1, 2, 3, 4, 5)
  2. Descriptive labels (Very Poor, Poor, Neutral, Good, Very Good)?"

**Text field size:**

- "For 'What did you like?', do you want:
  1. Single-line text input (free_text)
  2. Multi-line text area (textarea - recommended for longer responses)?"

**Missing options:**

- "I found 'Age range (dropdown)' but no options listed. What options should be available?"

**Required fields:**

- "Should 'Email address' be required or optional?"

**Helper text:**

- "Would you like to add helper text for 'Upload screenshot'? (e.g., 'PNG or JPG, max 5MB')"

### 7. Ask for Output Path

"Where would you like to save the generated template?"

- Default: Same name as document but with .json extension

### 8. Generate Template

Use jq to build valid JSON template with all parsed and clarified information.

### 9. Report Success

Show:

- Source document path
- Generated template path
- Summary of what was created (N pages, M fields)
- Next steps (review, create collection)

## Interactive Template Generation Flow

When generating a template interactively, follow this approach:

### 1. Fetch Current API Documentation

**Action:** Use WebFetch to retrieve:

- https://docs.prolific.com/api-reference/ai-task-builder/collections
- https://docs.prolific.com/api-reference/ai-task-builder/instructions

Extract:

- Collection schema (required and optional fields)
- Supported instruction types with their properties
- Content block types
- Validation rules and constraints

### 2. File Location

**Question:** "Where would you like to save the collection template?"

- Default: `./collection-template.json` in current directory
- User can specify custom path

### 3. Basic Configuration

**Questions:**

- "What is the name for this collection?" (required per API docs)
- "What is the description for this collection?" (if optional per API docs)

### 4. Task Details

**Questions:**

- "What is the participant-facing task name?"
- "What are the instructions for participants?" (task introduction)
- "How many steps does this task have?"
- For each step: "What is step X?"

### 5. Collection Structure (Pages)

**Questions:**

- "How many pages will this collection have?"

For each page:

- "What is the title for page X?"
- "What is the order number for this page?"
- "How many items on this page?"

For each page item:

- "What type is item Y?" (present options from fetched API docs)
- "What is the order number for this item?"
- Ask type-specific questions based on the fetched instruction/content block requirements

### 6. Generate and Save

- Build complete JSON structure using jq
- Validate structure matches current API spec
- Save to specified file
- Show file location
- Provide next steps

## Important Notes

- **Always fetch documentation at runtime** - ensures compatibility with latest API
- **Document Mode is ideal for non-technical users** - describe your collection in plain language
- **Templates are saved locally** for review and editing before creation
- **Users can modify generated templates** - they're just JSON files (even after Document Mode generates them)
- **Templates can be reused** - save them for similar collections
- **Document Mode may require clarifications** - be prepared to answer questions about ambiguous content
- Collections are created in **DRAFT** state - they are NOT published automatically
- Collections must be **published as a study** before participants can access them
- Use `/publish-task-builder-collection <collection-id>` to create and publish a study
- **AI Task Builder Collections is an early-access feature** - must be enabled on your workspace

## After Template Generation

Report to the user:

1. **Template file location** (full path)
2. **Template preview** (show contents or summary)
3. **Next steps**:
   - Review and edit the template if needed
   - Create collection: `/create-task-builder-collection <template-file>`
   - Or manually: `prolific collection create -t <template-file>`
   - Reference current docs: https://docs.prolific.com/api-reference/ai-task-builder/collections

## After Collection Creation

Report to the user:

1. **Collection ID** (parse from CLI JSON output)
2. Confirm it's in **DRAFT** state
3. **Next steps** (collections often require several iterations):
   - **Preview the collection**: `prolific collection preview <collection-id>` - Opens a preview in your browser
   - Review collection details: `prolific collection get <collection-id>`
   - If changes needed:
     - Edit your template file
     - Update collection: `prolific collection update <collection-id> -t <template-file>`
     - Preview again to verify changes
   - When satisfied with the collection:
     - Publish as a study: `/publish-task-builder-collection <collection-id>`
     - Or manually: `prolific collection publish <collection-id> -t <study-template.json>`

**Important:** Always preview your collection before publishing to ensure it looks and functions as expected. Collections typically require 2-3 iterations to get right.

## Iterative Workflow: Preview and Update

Collections rarely work perfectly on the first attempt. Follow this iterative workflow:

### 1. Create Initial Collection

```bash
prolific collection create -t sentiment-collection.json
# Returns: Collection ID: a1b2c3d4-e5f6-4789-abcd-ef1234567890
```

### 2. Preview in Browser

```bash
prolific collection preview a1b2c3d4-e5f6-4789-abcd-ef1234567890
```

This opens a preview URL in your browser where you can see exactly how participants will experience the collection.

### 3. Review and Identify Issues

Common things to check:

- Question wording clarity
- Field order and flow
- Helper text effectiveness
- Instruction type appropriateness (e.g., should this be multiple_choice or free_text?)
- Missing or unnecessary fields

### 4. Edit Template File

Make changes to your local template file (e.g., `sentiment-collection.json`):

- Fix question wording
- Reorder fields by changing `order` values
- Add/remove fields
- Adjust field types or options

### 5. Update Collection

```bash
prolific collection update a1b2c3d4-e5f6-4789-abcd-ef1234567890 -t sentiment-collection.json
```

### 6. Preview Again

```bash
prolific collection preview a1b2c3d4-e5f6-4789-abcd-ef1234567890
```

Verify your changes look correct.

### 7. Repeat Until Satisfied

Continue the cycle of edit → update → preview until the collection is ready.

### 8. Publish as Study

Once satisfied:

```bash
/publish-task-builder-collection a1b2c3d4-e5f6-4789-abcd-ef1234567890
```

## Example Workflows

### Example 1: Document Mode

**User Request:**

> "I have a document describing a feedback collection. Can you create a collection from it?"
>
> File: `feedback-requirements.txt`

**Document Content:**

```text
# Customer Feedback Collection

We want to collect feedback on our new mobile checkout feature.

Collection Name: Mobile Checkout Feedback
Description: Gather user opinions on the new streamlined checkout process

## Task for Participants
Participants will:
1. Review the feature description
2. Rate key aspects
3. Provide detailed feedback

## Page 1: Feature Introduction
Show participants information about the feature:
- Display a text description of the new checkout flow
- Show an image: https://example.com/checkout-screenshot.png

## Page 2: Ratings
Ask participants to rate (1-5 scale, with 1=Very Poor, 5=Very Good):
- Overall ease of use
- Visual design quality
- Speed compared to old checkout

Also ask:
- Would you recommend this to others? (Yes/No)

## Page 3: Open Feedback
Get detailed responses:
- What did you like most? (open text, required, allow multiple lines)
- What could be improved? (open text, optional, multiple lines)
- How long have you used our app? (number with time unit: days, weeks, months, years)

## Page 4: Optional Info
- Age range (dropdown with options: 18-24, 25-34, 35-44, 45-54, 55+)
- How often do you shop with us? (choose one: Daily, Weekly, Monthly, Rarely)
```

**Execution:**

```bash
/create-task-builder-collection feedback-requirements.txt
```

**Claude's Response:**

```
Reading document: feedback-requirements.txt
Fetching current AI Task Builder API documentation...

Document parsed successfully! I found:
- Collection: Mobile Checkout Feedback
- 4 pages with 11 total items
- Mix of content blocks and input fields

I have a few clarifying questions:

1. For the text description on Page 1, what should the content say?
   [User provides the actual description text]

2. Page 2 has three 1-5 scale ratings. I'll create these as multiple_choice fields
   with options labeled: "1 - Very Poor", "2 - Poor", "3 - Neutral", "4 - Good", "5 - Very Good"
   Is that correct, or would you prefer just numbers (1, 2, 3, 4, 5)?
   [User: "The descriptive labels are perfect"]

3. For "What did you like most?" and "What could be improved?", you mentioned "multiple lines".
   Should these use 'textarea' type (multi-line text input)?
   [User: "Yes, textarea for both"]

4. Should I add helper text for any fields? For example, for the age range dropdown?
   [User: "No helper text needed for now"]

Generating template...

✓ Template generated successfully!
  File saved to: feedback-collection.json

Summary:
- 4 pages created
- 2 content blocks (rich_text, image)
- 9 input fields (multiple_choice, free_text, free_text_with_unit)
- All required fields marked appropriately

Next steps:
1. Review the template: cat feedback-collection.json
2. Edit if needed (it's just a JSON file)
3. Create collection: /create-task-builder-collection feedback-collection.json
4. Preview: prolific collection preview <collection-id>
```

### Example 2: Interactive Mode

**User Request:**

> "I want to create a Task Builder collection for sentiment analysis"

### Execution Steps

1. **Fetch API documentation**

   ```
   WebFetch: https://docs.prolific.com/api-reference/ai-task-builder/collections
   WebFetch: https://docs.prolific.com/api-reference/ai-task-builder/instructions
   ```

2. **Interactive questioning** (based on current API spec)
   - Gather collection name, description, task details
   - Build pages and page items structure
   - Validate against current API requirements

3. **Generate template** using jq with current structure

4. **Save and report**

   ```
   Template generated successfully!
   File saved to: sentiment-collection.json

   Next steps:
   1. Review and edit the template file if needed
   2. Create the collection:
      /create-task-builder-collection sentiment-collection.json
   ```

### Create from Template

> "Create a collection from sentiment-collection.json"

**Execution:**

```bash
#!/bin/bash
set -e

TEMPLATE_FILE="sentiment-collection.json"

if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "Error: Template file not found: $TEMPLATE_FILE"
  exit 1
fi

# Validate JSON
jq empty "$TEMPLATE_FILE" 2>/dev/null || {
  echo "Error: Invalid JSON in template file"
  exit 1
}

echo "Template file: $TEMPLATE_FILE"
echo ""
echo "Creating collection..."
prolific collection create -t "$TEMPLATE_FILE"

echo ""
echo "Collection created successfully!"
```

**Expected Output:**

```text
Template file: sentiment-collection.json

Creating collection...

Collection created successfully!
Collection ID: a1b2c3d4-e5f6-4789-abcd-ef1234567890
Status: DRAFT

Next steps:
- Preview the collection: prolific collection preview a1b2c3d4-e5f6-4789-abcd-ef1234567890
- Review details: prolific collection get a1b2c3d4-e5f6-4789-abcd-ef1234567890
- If changes needed: Edit template and run `prolific collection update a1b2c3d4-e5f6-4789-abcd-ef1234567890 -t <template-file>`
- When ready: /publish-task-builder-collection a1b2c3d4-e5f6-4789-abcd-ef1234567890

Tip: Collections typically require 2-3 iterations. Always preview before publishing!
```

## Troubleshooting

### "PROLIFIC_TOKEN not set"

- Set your API token: `export PROLIFIC_TOKEN=your_token_here`
- Or add it to your shell profile (~/.zshrc, ~/.bashrc)

### "AI Task Builder Collections not enabled"

- This is an early-access feature
- Request access via Prolific help center chat
- Must be enabled on your workspace before use

### "Template or document file not found"

- Verify the file path is correct
- Use absolute paths or ensure you're in the correct directory
- Check file permissions are readable
- For Document Mode: ensure file extension is .txt, .md, or .docx

### "pandoc not found" (for .docx files)

- Install pandoc: `brew install pandoc` (macOS) or `apt-get install pandoc` (Linux)
- Alternatively, convert .docx to .txt or .md manually
- Or use online tools to extract text from Word documents

### "Document parsing unclear"

- Be more specific in your document about field types
- Use clear patterns: "1-5 scale", "Yes/No", "open text", "dropdown"
- Include option lists for multiple choice fields
- Mark fields as "(required)" or "(optional)" explicitly
- Separate pages with clear headings (## Page 1:, ## Page 2:, etc.)

### "Generated template doesn't match my intent"

- This is normal for first attempts with Document Mode
- Review the generated template JSON file
- Edit it directly to fix any misinterpretations
- Consider being more explicit in your source document for next time
- You can always switch to Interactive Mode for more control

### "Invalid JSON"

- Validate your template syntax: `jq . < template.json`
- Check for:
  - Trailing commas (not allowed in JSON)
  - Missing quotes around strings
  - Unescaped special characters
  - Mismatched brackets/braces

### "CLI command not found"

- Ensure Prolific CLI is installed: `brew install prolific-oss/tap/prolific`
- Or use `which prolific` to find the correct path

### "Collection creation failed"

- Check PROLIFIC_TOKEN has correct permissions
- Verify all required fields are present in template
- Review CLI error message for specific issues
- Reference current API docs: https://docs.prolific.com/api-reference/ai-task-builder/collections

### "Invalid field or structure"

- API may have changed - fetch current documentation
- Verify template structure matches current API specification
- Check Prolific API docs for breaking changes
- Validate required fields are present

### "jq: command not found"

- Install jq for JSON manipulation: `brew install jq` (macOS) or `apt-get install jq` (Linux)
- jq is highly recommended for generating clean, valid JSON templates

### "Documentation fetch failed"

- Check internet connection
- Verify Prolific docs URLs are accessible
- Try accessing https://docs.prolific.com manually
- May need to reference cached documentation if offline

### "Preview command fails"

- Ensure collection was created successfully and you have the correct collection ID
- Check that you have permission to preview collections in this workspace
- Verify your browser is able to open URLs from the command line
- Try accessing the preview URL manually if provided in error message

### "Collection update fails"

- Ensure you're updating an existing collection (not trying to update a non-existent ID)
- Verify your template file has valid JSON syntax: `jq . < template.json`
- Check that all required fields are still present after your edits
- Collections in certain states may not be updateable - check status with `prolific collection get <id>`

### "Preview shows unexpected layout"

- This is normal during iteration - use preview to identify issues
- Edit your template file to adjust field order, types, or content
- Run `prolific collection update <id> -t <template-file>` to apply changes
- Preview again to verify
- Repeat until satisfied

## Key Advantages of Runtime Documentation Fetching

1. **Always current** - Works with latest API version without skill updates
2. **Self-healing** - Adapts to API changes automatically
3. **Single source of truth** - Prolific documentation is authoritative
4. **Reduced maintenance** - No need to update skill files when API changes
5. **Better user experience** - Users always work with correct, current specifications

## For Developers

When implementing this skill, the workflow should be:

1. **Start of generate mode**: Fetch API documentation
2. **Parse documentation**: Extract current field types, requirements, structure
3. **Generate questions**: Based on current API specification
4. **Build template**: Using current structure from documentation
5. **Validate**: Against current API spec before saving

This ensures the skill remains functional even as the Prolific API evolves, without requiring distribution of skill updates to all users.
