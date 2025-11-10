# ModelHub Prompt Management Guide

This guide provides comprehensive documentation on managing prompts with the ModelHub SDK using MLflow's Prompt Registry.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Creating and Registering Prompts](#creating-and-registering-prompts)
4. [Prompt Versioning](#prompt-versioning)
5. [Aliases](#aliases)
6. [Loading and Using Prompts](#loading-and-using-prompts)
7. [Prompt Evaluation](#prompt-evaluation)
8. [Integration with Model Tracking](#integration-with-model-tracking)
9. [Best Practices](#best-practices)
10. [Examples](#examples)

## Introduction

Prompt engineering is a critical aspect of developing effective Generative AI (GenAI) applications. The ModelHub SDK leverages MLflow's Prompt Registry to provide a comprehensive solution for managing, versioning, and evaluating prompts.

### Key Benefits

- **Version Control**: Track the evolution of prompts with commit-based versioning
- **Centralized Management**: Store and organize prompts in a central registry
- **Deployment Flexibility**: Use aliases to manage prompt versions in different environments
- **Integration**: Connect prompts with models and experiments for end-to-end lifecycle management
- **Evaluation**: Assess prompt performance with built-in metrics and evaluation tools

## Getting Started

### Installation

To use prompt management features, install the ModelHub SDK with MLflow integration:

```bash
pip install "autonomize-model-sdk[mlflow]"
```

### Initializing the Client

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import MLflowClient

# Initialize credential
credential = ModelhubCredential(
    modelhub_url="https://api-modelhub.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize MLflow client
client = MLflowClient(credential=credential)
```

## Creating and Registering Prompts

### Basic Registration

The `register_prompt` method creates a new prompt or a new version of an existing prompt:

```python
template = """Summarize content you are provided with in {{ num_sentences }} sentences.
Sentences: {{ sentences }}"""

prompt = client.mlflow.register_prompt(
    name="summarization-prompt",
    template=template,
    commit_message="Initial commit",
    version_metadata={"author": "author@example.com"},
    tags={"task": "summarization", "language": "en"}
)

print(f"Created prompt '{prompt.name}' (version {prompt.version})")
```

### Template Variables

Variables in prompt templates are enclosed in double curly braces `{{ variable_name }}`. These can be replaced with actual values when using the prompt.

### Metadata and Tags

- **Version Metadata**: Additional information about a specific version (author, review status, etc.)
- **Tags**: Labels that apply to all versions of a prompt (task type, language, etc.)

```python
prompt = client.mlflow.register_prompt(
    name="classification-prompt",
    template="Classify the following text into one of the following categories: {{ categories }}.\nText: {{ text }}",
    commit_message="Classification prompt for general use",
    version_metadata={
        "author": "data_science_team@example.com",
        "reviewed_by": "senior_prompt_engineer@example.com",
        "review_date": "2025-03-15"
    },
    tags={
        "task": "classification",
        "language": "en",
        "domain": "general"
    }
)
```

## Prompt Versioning

### Creating a New Version

To create a new version of an existing prompt, use the same name but with an updated template:

```python
new_template = """You are an expert summarizer. Condense the following content into exactly {{ num_sentences }}
clear and informative sentences that capture the key points.

Sentences: {{ sentences }}

Your summary should:
- Contain exactly {{ num_sentences }} sentences
- Include only the most important information
- Be written in a neutral, objective tone
"""

updated_prompt = client.mlflow.register_prompt(
    name="summarization-prompt",  # Use existing prompt name
    template=new_template,
    commit_message="Improved prompt with more specific instructions",
    version_metadata={"author": "author@example.com"}
)

print(f"Created new version: {updated_prompt.version}")
```

### Comparing Versions

In the MLflow UI, you can compare different versions of a prompt to see what has changed:

1. Navigate to the prompt details page
2. Click on the "Compare" tab
3. Select the versions you want to compare

This shows a side-by-side diff of the templates, highlighting additions, deletions, and changes.

## Aliases

Aliases are named references to specific prompt versions, enabling you to maintain stable references in your code while updating the actual versions used.

### Creating an Alias

```python
# Set a production alias for version 2
client.mlflow.set_prompt_alias(
    "summarization-prompt",
    alias="production",
    version=2
)

# Set a development alias for the latest version
client.mlflow.set_prompt_alias(
    "summarization-prompt",
    alias="development",
    version=3
)
```

### Common Alias Patterns

- **Environment-based**: `development`, `staging`, `production`
- **Maturity-based**: `experimental`, `approved`, `deprecated`
- **Purpose-based**: `internal`, `customer-facing`, `compliance`

### Using Aliases for Deployment Pipelines

Aliases enable robust deployment workflows:

1. Develop and test new prompt versions with the `development` alias
2. Promote to `staging` for broader testing
3. Deploy to production by updating the `production` alias
4. Easily roll back by pointing the `production` alias to a previous version

## Loading and Using Prompts

### Loading by Version or Alias

```python
# Load by version number
prompt_v1 = client.mlflow.load_prompt("prompts:/summarization-prompt/1")

# Load by alias
prod_prompt = client.mlflow.load_prompt("prompts:/summarization-prompt@production")
dev_prompt = client.mlflow.load_prompt("prompts:/summarization-prompt@development")

# Latest version (if no version or alias specified)
latest_prompt = client.mlflow.load_prompt("prompts:/summarization-prompt")
```

### Formatting Prompts with Variables

```python
# Format the prompt with variable values
formatted_prompt = prompt.format(
    num_sentences=3,
    sentences="Artificial intelligence has transformed how businesses operate in the 21st century. Companies are leveraging AI for everything from customer service to supply chain optimization. The technology enables automation of routine tasks, freeing human workers for more creative endeavors. However, concerns about job displacement and ethical implications remain significant."
)

print(formatted_prompt)
```

### Using with AutoRAG

AutoRAG provides a standardized interface for calling different LLM providers. This is the recommended approach for all LLM interactions:

```python
import os
from autorag.language_models import OpenAILanguageModel, AnthropicLanguageModel

# Initialize OpenAI LLM through AutoRAG
openai_llm = OpenAILanguageModel(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Send formatted prompt to OpenAI
response = openai_llm.generate(
    message=[{"role": "user", "content": formatted_prompt}],
    model="gpt-4o-mini",
    temperature=0.1
)

print(response.content)

# Initialize Anthropic LLM through AutoRAG
anthropic_llm = AnthropicLanguageModel(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

# Send formatted prompt to Anthropic
response = anthropic_llm.generate(
    message=[{"role": "user", "content": formatted_prompt}],
    model="claude-3-opus-20240229",
    temperature=0.1,
    max_tokens=1000
)

print(response.content)
```

#### Async Usage

AutoRAG also supports asynchronous calls:

```python
# Async version with OpenAI
response = await openai_llm.agenerate(
    message=[{"role": "user", "content": formatted_prompt}],
    model="gpt-4o-mini",
    temperature=0.1
)

print(response.content)
```

#### LangChain Integration with AutoRAG

You can integrate LangChain with AutoRAG for a more consistent approach:

```python
import os
from langchain_core.prompts import ChatPromptTemplate
from autorag.language_models import OpenAILanguageModel
from langchain_core.language_models import FunctionCallModel

# Load registered prompt
prompt = client.mlflow.load_prompt("prompts:/summarization-prompt@production")

# Convert to LangChain format (single curly braces)
langchain_prompt = ChatPromptTemplate.from_messages([
    ("system", prompt.to_single_brace_format()),
    ("placeholder", "{messages}")
])

# Initialize AutoRAG LLM
autorag_llm = OpenAILanguageModel(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Create a LangChain wrapper around AutoRAG's LLM
class AutoRAGLangChainWrapper(FunctionCallModel):
    def __init__(self, autorag_llm, model_name):
        self.llm = autorag_llm
        self.model_name = model_name

    def invoke(self, input, config=None):
        if isinstance(input, list):
            messages = input
        else:
            messages = [{"role": "user", "content": input}]

        response = self.llm.generate(
            message=messages,
            model=self.model_name,
            temperature=0.1
        )

        return response.content

# Create LangChain components
llm = AutoRAGLangChainWrapper(autorag_llm, "gpt-3.5-turbo")
chain = langchain_prompt | llm

# Invoke chain
response = chain.invoke({
    "num_sentences": 2,
    "sentences": "This is the text to summarize.",
    "messages": ""  # Required by the placeholder
})

print(response)
```

## Prompt Evaluation

### Preparing Evaluation Data

```python
import pandas as pd

eval_data = pd.DataFrame({
    "inputs": [
        "Artificial intelligence has transformed how businesses operate...",
        "Climate change continues to affect ecosystems worldwide..."
    ],
    "targets": [
        "AI has revolutionized business operations...",
        "Climate change is causing accelerating environmental damage..."
    ]
})
```

### Creating a Prediction Function

```python
import openai

def predict(data):
    predictions = []
    prompt = client.mlflow.load_prompt("prompts:/summarization-prompt@production")

    for _, row in data.iterrows():
        formatted_prompt = prompt.format(sentences=row["inputs"], num_sentences=1)
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.1
        )
        predictions.append(completion.choices[0].message.content)

    return predictions
```

### Running the Evaluation

```python
with client.start_run(run_name="prompt-evaluation"):
    # Log parameters
    client.mlflow.log_param("model", "gpt-4o-mini")
    client.mlflow.log_param("temperature", 0.1)
    client.mlflow.log_param("prompt_version", 2)

    # Run evaluation
    results = client.mlflow.evaluate(
        model=predict,
        data=eval_data,
        targets="targets",
        extra_metrics=[
            client.mlflow.metrics.latency(),
            client.mlflow.metrics.genai.answer_similarity(model="openai:/gpt-4"),
            client.mlflow.metrics.genai.toxicity()
        ]
    )
```

### Comparing Different Prompt Versions

```python
# Define prediction functions for different prompt versions
def predict_v1(data):
    # Use version 1
    prompt = client.mlflow.load_prompt("prompts:/summarization-prompt/1")
    # ... rest of prediction logic

def predict_v2(data):
    # Use version 2
    prompt = client.mlflow.load_prompt("prompts:/summarization-prompt/2")
    # ... rest of prediction logic

# Evaluate version 1
with client.start_run(run_name="prompt-v1-evaluation"):
    client.mlflow.log_param("prompt_version", 1)
    results_v1 = client.mlflow.evaluate(
        model=predict_v1,
        data=eval_data,
        targets="targets",
        extra_metrics=[client.mlflow.metrics.genai.answer_similarity()]
    )

# Evaluate version 2
with client.start_run(run_name="prompt-v2-evaluation"):
    client.mlflow.log_param("prompt_version", 2)
    results_v2 = client.mlflow.evaluate(
        model=predict_v2,
        data=eval_data,
        targets="targets",
        extra_metrics=[client.mlflow.metrics.genai.answer_similarity()]
    )
```

## Integration with Model Tracking

### Logging Models with Associated Prompts

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Load registered prompt
prompt = client.mlflow.load_prompt("prompts:/summarization-prompt@production")

# Create LangChain components
langchain_prompt = ChatPromptTemplate.from_messages([
    ("system", prompt.to_single_brace_format()),
    ("placeholder", "{messages}")
])
llm = ChatOpenAI(model="gpt-3.5-turbo")
chain = langchain_prompt | llm

# Log the model with the associated prompt
with client.start_run(run_name="summarizer-model"):
    client.mlflow.langchain.log_model(
        chain,
        artifact_path="model",
        prompts=["prompts:/summarization-prompt@production"]
    )
```

### Automatic Prompt Logging with Models-from-Code

Create a Python script file that loads and uses prompts:

```python
# summarizer.py
import mlflow
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def create_chain():
    # Load prompt from registry
    prompt = mlflow.load_prompt("prompts:/summarization-prompt@production")

    # Create LangChain components
    langchain_prompt = ChatPromptTemplate.from_messages([
        ("system", prompt.to_single_brace_format()),
        ("user", "{text}")
    ])

    llm = ChatOpenAI(model="gpt-3.5-turbo")
    chain = langchain_prompt | llm

    return chain

mlflow.models.set_model(create_chain())
```

Then log the model from this script:

```python
with client.start_run():
    model_info = client.mlflow.langchain.log_model(
        lc_model="./summarizer.py",
        artifact_path="summarizer"
    )
```

MLflow will automatically detect and log the prompt used in the model.

## Best Practices

### Prompt Structure

1. **Clear Instructions**: Begin with precise instructions about the task
2. **Context Setting**: Establish the role, perspective, or constraints
3. **Variable Placement**: Position variables logically in the template
4. **Output Formatting**: Provide explicit formatting instructions when needed
5. **Input Verification**: Include instructions for validating or handling problematic inputs

### Version Management

1. **Descriptive Commit Messages**: Write clear, descriptive commit messages for each version
2. **Semantic Versioning**: Consider using semantic versioning principles for aliases
3. **Regular Cleanup**: Archive or delete unused or deprecated prompts
4. **Version Metadata**: Include relevant metadata with each version (author, purpose, etc.)

### Alias Strategy

1. **Environment Alignment**: Create aliases that match your deployment environments
2. **Gradual Rollout**: Use aliases to manage gradual rollouts of new prompt versions
3. **Experiments**: Use temporary aliases for A/B testing different prompts
4. **Documentation**: Document the purpose and current version of each alias

### Evaluation

1. **Representative Data**: Use diverse, representative data for evaluations
2. **Multiple Metrics**: Evaluate prompts using multiple relevant metrics
3. **Regular Re-evaluation**: Periodically re-evaluate prompt performance
4. **Baseline Comparisons**: Always compare against baseline or previous versions

## Examples

### Chatbot with Context Retention

```python
# Register a system prompt
chat_system_prompt = client.mlflow.register_prompt(
    name="chat-system-prompt",
    template="You are a helpful AI assistant that answers questions clearly and concisely. You are knowledgeable about {{ domain }} topics.",
    commit_message="Basic system prompt for chat assistant"
)

# Register a user instruction prompt
chat_instruction_prompt = client.mlflow.register_prompt(
    name="chat-instruction-prompt",
    template="Please answer the following question about {{ domain }}:\n\nQuestion: {{ question }}",
    commit_message="User instruction prompt for questions"
)

# Using the prompts with conversation history
def chat_with_history(domain, question, history=None):
    if history is None:
        history = []

    # Load prompts
    system_prompt = client.mlflow.load_prompt("prompts:/chat-system-prompt/1")
    instruction_prompt = client.mlflow.load_prompt("prompts:/chat-instruction-prompt/1")

    # Format prompts
    formatted_system = system_prompt.format(domain=domain)
    formatted_instruction = instruction_prompt.format(domain=domain, question=question)

    # Prepare messages
    messages = [
        {"role": "system", "content": formatted_system}
    ]

    # Add conversation history
    for msg in history:
        messages.append(msg)

    # Add current question
    messages.append({"role": "user", "content": formatted_instruction})

    # Get response
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    # Return response and updated history
    assistant_response = response.choices[0].message.content
    history.append({"role": "user", "content": formatted_instruction})
    history.append({"role": "assistant", "content": assistant_response})

    return assistant_response, history
```

### Multi-stage Prompt Pipeline

```python
# Register prompts for different stages
extraction_prompt = client.mlflow.register_prompt(
    name="data-extraction-prompt",
    template="""Extract the following information from the text:
- Name
- Email
- Phone number
- Main skills (up to 3)

Text: {{ document }}

Format the output as a JSON object with the fields: name, email, phone, skills (array)."""
)

summarization_prompt = client.mlflow.register_prompt(
    name="resume-summary-prompt",
    template="""Create a concise 2-sentence summary of the candidate's qualifications and experience.
Use the following extracted information:
{{ extracted_data }}"""
)

recommendation_prompt = client.mlflow.register_prompt(
    name="job-recommendation-prompt",
    template="""Based on the candidate's profile below, recommend {{ num_recommendations }} suitable job positions.
For each position, include the job title and a brief explanation of why they would be a good fit.

Candidate profile:
{{ candidate_summary }}

The recommendations should be in the following format:
1. [Job Title] - [Brief explanation]
2. [Job Title] - [Brief explanation]
...etc."""
)

# Pipeline function
def resume_processing_pipeline(document_text):
    # Stage 1: Extract data
    extraction_template = client.mlflow.load_prompt("prompts:/data-extraction-prompt/1")
    extraction_result = call_llm(extraction_template.format(document=document_text))

    # Stage 2: Summarize
    summary_template = client.mlflow.load_prompt("prompts:/resume-summary-prompt/1")
    summary_result = call_llm(summary_template.format(extracted_data=extraction_result))

    # Stage 3: Recommend jobs
    recommendation_template = client.mlflow.load_prompt("prompts:/job-recommendation-prompt/1")
    recommendations = call_llm(recommendation_template.format(
        candidate_summary=summary_result,
        num_recommendations=3
    ))

    return {
        "extracted_data": extraction_result,
        "summary": summary_result,
        "recommendations": recommendations
    }

def call_llm(prompt_text):
    # Placeholder for actual LLM call
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.1
    )
    return response.choices[0].message.content
```

### A/B Testing Prompts

```python
import random

# Register two different versions for A/B testing
prompt_a = client.mlflow.register_prompt(
    name="product-description-prompt",
    template="Write a concise, informative product description for {{ product_name }}. Include key features and benefits.",
    commit_message="Basic product description prompt (Version A)"
)

prompt_b = client.mlflow.register_prompt(
    name="product-description-prompt",
    template="""Write an engaging, persuasive product description for {{ product_name }}.

1. Start with a compelling hook
2. Highlight the 3 most important features
3. Emphasize the unique benefits
4. End with a clear call to action

Keep the description under 100 words.""",
    commit_message="Detailed, structured product description prompt (Version B)"
)

# Set aliases for A/B testing
client.mlflow.set_prompt_alias("product-description-prompt", alias="version_a", version=1)
client.mlflow.set_prompt_alias("product-description-prompt", alias="version_b", version=2)

# A/B testing function
def ab_test_product_descriptions(product_data, test_id):
    results = []

    for product in product_data:
        # Randomly select A or B variant (but consistently based on test_id)
        variant_seed = hash(f"{test_id}:{product['id']}")
        random.seed(variant_seed)
        variant = "version_a" if random.random() < 0.5 else "version_b"

        # Load the selected prompt variant
        prompt = client.mlflow.load_prompt(f"prompts:/product-description-prompt@{variant}")

        # Format and use the prompt
        formatted_prompt = prompt.format(product_name=product["name"])

        # Call LLM
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.7
        )

        description = response.choices[0].message.content

        # Log the result
        with client.start_run(run_name=f"product-description-{product['id']}"):
            client.mlflow.log_param("product_id", product["id"])
            client.mlflow.log_param("product_name", product["name"])
            client.mlflow.log_param("prompt_variant", variant)
            client.mlflow.log_param("prompt_version", 1 if variant == "version_a" else 2)
            client.mlflow.log_text(description, "description.txt")

        results.append({
            "product_id": product["id"],
            "product_name": product["name"],
            "variant": variant,
            "description": description
        })

    return results
```
