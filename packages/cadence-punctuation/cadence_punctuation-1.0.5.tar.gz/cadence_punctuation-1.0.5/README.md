# Cadence

A multilingual punctuation restoration model based on Gemma-3-1b

## Features
- **Multilingual Support**: English + 22 Indic languages
- **Unimodel**: A single model for punctuations (doesn't require language identifier)
- **Encoder**: Bi-directional encoder (blazing fast)
- **AutoModel Compatible**: Easy integration with Hugging Face ecosystem
- **Efficient Processing**: Supports batch processing and sliding window for long texts
- **Script-Aware**: Handles multiple scripts with appropriate punctuation rules

## Installation
This package has features such as sliding-window decoding, (rule-based) capitalisation of English text and some (rule-based) corrections for the errors made by the model.

```bash
pip install cadence-punctuation
```

## Quick Start

### Using the python package (Recommended)

```python
from cadence import PunctuationModel

# Load model (local path)
model = PunctuationModel("path/to/download/weights")

# Punctuate single text
text = "hello world how are you today"
result = model.punctuate([text])
print(result[0])  # "Hello world, how are you today?"

# Punctuate multiple texts
texts = [
    "hello world how are you",
    "this is another test sentence",
    "यह एक हिंदी वाक्य है"  # Hindi example
]
results = model.punctuate(texts, batch_size=8)
for original, punctuated in zip(texts, results):
    print(f"Original: {original}")
    print(f"Punctuated: {punctuated}")
```

### Using AutoModel

```python
from transformers import AutoTokenizer, AutoModel
import torch

# Load model and tokenizer
model_name = "ai4bharat/Cadence"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name, trust_remote_code=True)

id2label = model.config.id2label

text = "यह एक वाक्य है इसका क्या मतलब है"
# text = "this is a test sentence what do you think"

# Tokenize input and prepare for model
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
input_ids = inputs['input_ids'][0] # Get input_ids for the first (and only) sentence

with torch.no_grad():
    outputs = model(**inputs)
    predictions_for_sentence = torch.argmax(outputs.logits, dim=-1)[0]


result_tokens_and_punctuation = []
all_token_strings = tokenizer.convert_ids_to_tokens(input_ids.tolist()) # Get all token strings

for i, token_id_value in enumerate(input_ids.tolist()):
    # Process only non-padding tokens based on the attention mask
    if inputs['attention_mask'][0][i] == 0:
        continue

    current_token_string = all_token_strings[i]

    is_special_token = token_id_value in tokenizer.all_special_ids
    
    if not is_special_token:
        result_tokens_and_punctuation.append(current_token_string)
    
    predicted_punctuation_id = predictions_for_sentence[i].item()
    punctuation_character = id2label[predicted_punctuation_id]

    if punctuation_character != "O" and not is_special_token:
        result_tokens_and_punctuation.append(punctuation_character)

punctuated_text = tokenizer.convert_tokens_to_string(result_tokens_and_punctuation)

print(f"Original Text: {text}")
print(f"Punctuated Text: {punctuated_text}")
```


## Officially Supported Languages
- English, Assamese, Bengali, Bodo, Dogri, Gujarati, Hindi, Kannada, Kashmiri, Konkani, Maithili, Malayalam, Manipuri, Marathi, Nepali, Odia, Punjabi, Sanskrit, Santali, Sindhi, Tamil, Telugu, Urdu

Tokenizer doesn't support Manipuri's Meitei script. The model can punctuate if the text is transliterated to Bengali's script.

One can try using this model for languages not listed above. Performance may vary.

## Supported Punctuation
The model can predict the following punctuation marks:
- Period (.)
- Comma (,)  
- Question mark (?)
- Exclamation mark (!)
- Semicolon (;)
- Colon (:)
- Hyphen (-)
- Quotes (" and ')
- Ellipse (...)
- Parentheses ()
- Hindi Danda (।)
- Urdu punctuation (۔، ؟)
- Arabic punctuation (٬ ،)
- Santali punctuation (᱾ ᱾।)
- Sanskrit punctuation (॥)
- And various combinations

## Configuration Options

### PunctuationModel Parameters

All the parameters are optional to pass.
- `model_path`: Path to a local directory where model weights will be downloaded to and cached, or from which pre-downloaded weights will be loaded. If None, weights downloaded to default HuggingFace cache location. 
- `gpu_id`: Specific GPU device ID to use (e.g., 0, 1). If None, the model will attempt to auto-detect and use an available GPU. This parameter is ignored if cpu is True. (default: None)
- `cpu`: If True, forces the model to run on the CPU, even if a GPU is available. (default: False)
- `max_length`: Maximum sequence length the model can process at once. If sliding_window is True, this value is used as the width of each sliding window. If sliding_window is False, texts longer than max_length will be truncated. (default: 300)
- `attn_implementation`: The attention implementation to use. (default: "eager")
- `sliding_window`: If True, enables sliding window mechanism to process texts longer than max_length. The text is split into overlapping chunks of max_length. If False, texts longer than max_length are truncated. (default: True)
- `verbose`: Enable verbose logging (default: False)
- `d_type`: Precision with which weights are loaded (default: bfloat16)
- `batch_size`: ((for punctuate() method)): Batch size to use (default: 8)

```python
# Custom configuration
model = PunctuationModel(
    model_path="path/to/download/weights",
    gpu_id=0,  # Use specific GPU
    max_length=512,  # length for trunation; also used as window size when sliding_window=True
    attn_implementation="flash_attention_2",
    sliding_window=True,  # Handle long texts
    verbose=False,  # Quiet mode
    d_type="bfloat16"
)

batch_size=32 
# Process long texts with sliding window
long_text = "Your very long text here..." * 100
short_text = "a short text"
result = model.punctuate([long_text, short_text],batch_size=batch_size)
```

## License
MIT License
