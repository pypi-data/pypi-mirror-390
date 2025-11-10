"""
Punctuation model that uses the AutoModel compatible version
"""

import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from typing import List, Optional, Tuple, Any, Dict, Set
import functools
import re
import os
import sys

# Handle imports for both package and standalone usage
try:
    from .modeling_gemma3_punctuation import Gemma3ForTokenClassification
    from .utils import (
        punctuation_map, 
        id_to_punctuation, 
        ABBREVIATIONS_COMPLETE,
        SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP,
        get_token_script,
        post_process_cleaned_text,
        _final_spacing_cleanup
    )
except ImportError:
    raise ImportError("Please install the Cadence package using `pip install cadence-punctuation`")


class PunctuationModel:
    def __init__(self, model_path: Optional[str] = None,
                 gpu_id: Optional[int] = None,
                 cpu: bool = False,
                 max_length: int = 300,
                 attn_implementation: str = "eager",
                 sliding_window: bool = True,
                 verbose: bool = False,
                 d_type: str = "bfloat16"):
        
        self.model_name = "ai4bharat/Cadence"
        self.cache_dir = model_path
        self.cpu = cpu
        self.model_dtype_str = d_type
        self.classifier_dropout_prob = 0
        self.max_length = max_length
        self.attn_implementation = attn_implementation
        self.verbose = verbose
        self.sliding_window = sliding_window
        self.punctuation_map = punctuation_map
        self.id_to_punctuation = id_to_punctuation
        self.ABBREVIATIONS_COMPLETE = ABBREVIATIONS_COMPLETE
        self.SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP = SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP
        

        self._setup_device(gpu_id)
        self._load_model_and_tokenizer() # This will now print padding_side
        self._print_verbose("PunctuationModel initialized.")

    def _print_verbose(self, *args: Any, **kwargs: Any):
        if self.verbose:
            print(*args, **kwargs)

    def _setup_device(self, gpu_id: Optional[int]):
        self._print_verbose("Setting up device...")
        
        # Check CPU flag first - if True, force CPU usage
        if self.cpu:
            self.device = torch.device("cpu")
            self._print_verbose("CPU flag enabled. Using CPU device.")
            self.attn_implementation = "eager"
            self._print_verbose(f"Attention implementation set to: {self.attn_implementation}")
            if gpu_id is not None:
                self._print_verbose("Note: GPU ID specified but CPU flag is True. Using CPU.")
        elif gpu_id is not None and torch.cuda.is_available():
            try:
                self.device = torch.device(f"cuda:{int(gpu_id)}")
                torch.cuda.set_device(self.device)
                gpu_name = torch.cuda.get_device_name(torch.cuda.current_device())
                self._print_verbose(f"CUDA available. Using GPU ID: {torch.cuda.current_device()} ({gpu_name})")
            except Exception as e:
                print(f"Warning: Invalid GPU_ID '{gpu_id}' or CUDA error ({e}). Using default GPU 0 if available.")
                self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
                if self.device.type == 'cuda':
                    torch.cuda.set_device(self.device)
                    gpu_name = torch.cuda.get_device_name(torch.cuda.current_device())
                    self._print_verbose(f"Using default GPU: {torch.cuda.current_device()} ({gpu_name})")
                else:
                    self._print_verbose(f"CUDA not available. Using CPU.")
        elif torch.cuda.is_available(): # gpu_id is None, but CUDA is available
            self.device = torch.device("cuda:0") # Default to GPU 0
            torch.cuda.set_device(self.device)
            gpu_name = torch.cuda.get_device_name(torch.cuda.current_device())
            self._print_verbose(f"CUDA available. Using default GPU ID: 0 ({gpu_name})")
        else:
            self.device = torch.device("cpu")
            self._print_verbose(f"Using device: {self.device}")
            if gpu_id is not None: # User specified GPU but CUDA not found
                print("Warning: GPU ID specified, but CUDA not available. Using CPU.")

        self.model_dtype = torch.float32
        self.autocast_enabled = False
        if self.model_dtype_str == "bfloat16" and self.device.type == 'cuda' and torch.cuda.is_bf16_supported():
            self.model_dtype = torch.bfloat16; self.autocast_enabled = True
            self._print_verbose("Using bfloat16 with autocast.")
        elif self.model_dtype_str == "float16" and self.device.type == 'cuda':
            self.model_dtype = torch.float16; self.autocast_enabled = True
            self._print_verbose("Using float16 with autocast.")
        elif self.model_dtype_str != "float32":
            print(f"Warning: {self.model_dtype_str} requested but not supported on {self.device} or not 'float32'. Using float32.")
        self._print_verbose(f"Effective model dtype: {self.model_dtype} (Autocast enabled: {self.autocast_enabled})")


    def _load_model_and_tokenizer(self):
        self._print_verbose(f"Tokenizer path: {self.cache_dir}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.cache_dir)
            if self.tokenizer.pad_token is None:
                self._print_verbose("Tokenizer PAD token is None, setting to EOS token.")
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            
            self._print_verbose(f"Tokenizer initial padding_side: {self.tokenizer.padding_side}")
         

            self.pad_token_id = self.tokenizer.pad_token_id
            self.bos_token_id = self.tokenizer.bos_token_id
            self.eos_token_id = self.tokenizer.eos_token_id
            self._print_verbose(f"Tokenizer loaded. BOS: {self.bos_token_id}, EOS: {self.eos_token_id}, PAD: {self.pad_token_id}, Padding Side: {self.tokenizer.padding_side}")
            
            # Ensure all potential special token IDs are captured, even if some are None
            self.special_token_ids = set()
            if self.bos_token_id is not None: self.special_token_ids.add(self.bos_token_id)
            if self.eos_token_id is not None: self.special_token_ids.add(self.eos_token_id)
            if self.pad_token_id is not None: self.special_token_ids.add(self.pad_token_id)
            self._print_verbose(f"Registered special token IDs for skipping: {self.special_token_ids}")

        except Exception as e:
            print(f"FATAL: Error loading tokenizer: {e}"); raise

        try:

            self._print_verbose(f"Model path: {self.cache_dir}")
            model_args = {"torch_dtype": self.model_dtype}
            
            self.model = AutoModel.from_pretrained(
                self.model_name, 
                cache_dir=self.cache_dir,
                **model_args,
                trust_remote_code=True,
                attn_implementation=self.attn_implementation
            )
               
            self.model.to(self.device); self.model.eval()
            self._print_verbose("Model loading and setup finished.")
        except Exception as e:
            print(f"FATAL: Error loading model: {e}"); import traceback; traceback.print_exc(); raise


    def _reconstruct_single_text(self, input_token_ids_list: List[int], predicted_ids: List[int]) -> str:
        result_pieces: List[str] = []
        
        if len(input_token_ids_list) != len(predicted_ids):
            print(f"ERROR in _reconstruct_single_text: Input tokens ({len(input_token_ids_list)}) vs Predictions ({len(predicted_ids)}) mismatch.")
            return "Error: Token/Prediction Mismatch"

        ENG_STOP_STR = "."; DANDA_STR = "।"; URDU_STOP_STR = "۔"; QUESTION_MARK_STR = "?"
        STANDARD_COMMA_STR = ","; URDU_COMMA_STR = self.id_to_punctuation.get(self.punctuation_map.get("،", -1), "،")
        OTHER_ARABIC_COMMA_STR = self.id_to_punctuation.get(self.punctuation_map.get("٬", -1), "٬")
        QUOTE_STR = "\""; CLOSE_PAREN_STR = ")"
        OL_CHIKI_STOP_STR = "᱾"
        should_capitalize_next_latin_token = True

        for i in range(len(input_token_ids_list)):
            token_id = input_token_ids_list[i]
            
          
            if token_id in self.special_token_ids:
           
                continue 

            raw_token_output = self.tokenizer.convert_ids_to_tokens(token_id) # Returns a string for a single token ID
            decoded_token_str_original = self.tokenizer.convert_tokens_to_string([raw_token_output]) # Processes the single token string

            current_token_to_append = decoded_token_str_original
            if should_capitalize_next_latin_token:
                stripped_for_cap = current_token_to_append.lstrip()
                if stripped_for_cap:
                    word_part_for_script_check = "".join(filter(str.isalpha, stripped_for_cap.split(" ", 1)[0]))
                    if get_token_script(word_part_for_script_check) == "LATIN":
                        first_char_index = -1
                        for char_idx, char_val in enumerate(stripped_for_cap):
                            if char_val.isalpha(): first_char_index = char_idx; break
                        if first_char_index != -1:
                            leading_part = current_token_to_append[:-len(stripped_for_cap)]
                            cap_word_part = stripped_for_cap[:first_char_index] + \
                                            stripped_for_cap[first_char_index].upper() + \
                                            stripped_for_cap[first_char_index+1:]
                            current_token_to_append = leading_part + cap_word_part
                if current_token_to_append.strip(): # Only turn off if actual content was processed
                    should_capitalize_next_latin_token = False
            
            current_token_stripped_content = current_token_to_append.strip()
            if current_token_stripped_content == 'i': # Must be exactly 'i' (lowercase)
                    # Preserve leading/trailing spaces from current_token_to_append
                    s = current_token_to_append
                    lstripped_s = s.lstrip()
                    num_leading_spaces = len(s) - len(lstripped_s)
                    
                    rstripped_s = s.rstrip()
                    num_trailing_spaces = len(s) - len(rstripped_s)
                    
                    current_token_to_append = (" " * num_leading_spaces) + "I" + (" " * num_trailing_spaces)

            result_pieces.append(current_token_to_append)

            predicted_punct_id = predicted_ids[i]
            original_punct_str = self.id_to_punctuation.get(predicted_punct_id, "O")
            corrected_punct_str = original_punct_str
            
            word_for_script_and_abbr_check = decoded_token_str_original.strip()
            word_for_abbr_base = re.sub(r"[^a-zA-Z0-9]$", "", word_for_script_and_abbr_check)

            if original_punct_str != "O":
                token_script = get_token_script(word_for_script_and_abbr_check)
                base_char = None; is_quote_involved = False; quote_is_first = False
                is_paren_involved = False; paren_char = None
                potential_base = original_punct_str.replace('"', '').replace('(', '').replace(')', '')
                if potential_base in {ENG_STOP_STR, DANDA_STR, URDU_STOP_STR, QUESTION_MARK_STR, 
                                      STANDARD_COMMA_STR, URDU_COMMA_STR, OTHER_ARABIC_COMMA_STR, 
                                      "!", "..."}:
                    base_char = potential_base
                    if QUOTE_STR in original_punct_str: is_quote_involved = True; quote_is_first = original_punct_str.startswith(QUOTE_STR)
                    if CLOSE_PAREN_STR in original_punct_str and original_punct_str.startswith(CLOSE_PAREN_STR) : is_paren_involved = True; paren_char = CLOSE_PAREN_STR
                corrected_base_char = base_char
                if base_char:
                    if base_char in [DANDA_STR, URDU_STOP_STR, OL_CHIKI_STOP_STR] and token_script == "LATIN": corrected_base_char = ENG_STOP_STR
                    elif base_char in [URDU_STOP_STR, OL_CHIKI_STOP_STR] and token_script == "DEVANAGARI": corrected_base_char = DANDA_STR
                    elif base_char in [DANDA_STR, OL_CHIKI_STOP_STR] and token_script == "ARABIC": corrected_base_char = URDU_STOP_STR
                    elif base_char in [DANDA_STR, URDU_STOP_STR] and token_script == "OL_CHIKI": corrected_base_char = OL_CHIKI_STOP_STR
                    elif base_char in [URDU_COMMA_STR, OTHER_ARABIC_COMMA_STR] and token_script in ["LATIN", "DEVANAGARI"]: corrected_base_char = STANDARD_COMMA_STR
                    elif base_char == STANDARD_COMMA_STR and token_script == "ARABIC": corrected_base_char = URDU_COMMA_STR
                    if corrected_base_char != base_char and corrected_base_char is not None:
                        if is_quote_involved: corrected_punct_str = (QUOTE_STR + corrected_base_char) if quote_is_first else (corrected_base_char + QUOTE_STR)
                        elif is_paren_involved and paren_char: corrected_punct_str = paren_char + corrected_base_char
                        else: corrected_punct_str = corrected_base_char
            
            if corrected_punct_str in self.SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP:
                core_sentence_ender = self.SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP[corrected_punct_str]
                potential_abbr = (word_for_abbr_base + core_sentence_ender).lower()
                if potential_abbr not in self.ABBREVIATIONS_COMPLETE:
                    should_capitalize_next_latin_token = True
            
            if corrected_punct_str != "O":
                if result_pieces and result_pieces[-1].endswith(' '):
                    result_pieces[-1] = result_pieces[-1].rstrip()
                result_pieces.append(corrected_punct_str)
        
        return "".join(result_pieces)


    def _group_texts_by_length(self, texts_with_indices: List[Tuple[int, str]], batch_size: int) -> List[List[Tuple[int, str]]]:
        """Group texts by similar length to minimize padding."""
        # Calculate token lengths for all texts
        texts_with_lengths = []
        for idx, text in texts_with_indices:
            tokens = self.tokenizer.tokenize(text)
            texts_with_lengths.append((idx, text, len(tokens)))
        
        # Sort by token length
        texts_with_lengths.sort(key=lambda x: x[2])
        
        # Group into batches of similar length
        batches = []
        for i in range(0, len(texts_with_lengths), batch_size):
            batch = [(idx, text) for idx, text, _ in texts_with_lengths[i:i + batch_size]]
            batches.append(batch)
        
        return batches

    def _process_batch_with_indices(self, batch_with_indices: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
        """Process a batch of texts and return results with original indices."""
        batch_texts = [text for _, text in batch_with_indices]

        inputs = self.tokenizer(
                batch_texts,
                return_tensors="pt",
                padding="longest",
                truncation=True,
                max_length=self.max_length
            )
        input_ids_b = inputs["input_ids"].to(self.device)
        attention_mask_b = inputs["attention_mask"].to(self.device)

        with torch.no_grad(), \
                 torch.autocast(device_type=self.device.type, dtype=self.model_dtype, enabled=self.autocast_enabled):
                outputs = self.model(input_ids=input_ids_b, attention_mask=attention_mask_b)
                logits = outputs.logits
            
        predictions_b = torch.argmax(logits, dim=-1)

        batch_results = []
        for j, (original_idx, original_text) in enumerate(batch_with_indices):
                current_input_ids_padded = input_ids_b[j]
                current_attention_mask = attention_mask_b[j]
                current_predictions_padded = predictions_b[j]

                sequence_length = int(current_attention_mask.sum().item())

                if self.tokenizer.padding_side == 'left':
                    unpadded_input_token_ids = current_input_ids_padded[-sequence_length:].cpu().tolist()
                    unpadded_predicted_ids = current_predictions_padded[-sequence_length:].cpu().tolist()
                else:
                    if self.tokenizer.padding_side != 'right':
                        self._print_verbose(f"  WARNING - Unexpected padding_side '{self.tokenizer.padding_side}', assuming 'right'")
                        unpadded_input_token_ids = current_input_ids_padded[:sequence_length].cpu().tolist()
                        unpadded_predicted_ids = current_predictions_padded[:sequence_length].cpu().tolist()
                
                if not unpadded_input_token_ids:
                    self._print_verbose(f"  WARNING - No tokens after unpadding for text {original_idx}. Using original.")
                    batch_results.append((original_idx, original_text))
                    continue

                raw_reconstructed_text = self._reconstruct_single_text(unpadded_input_token_ids, unpadded_predicted_ids)
                processed_text_stage1 = post_process_cleaned_text(raw_reconstructed_text)
                final_text = _final_spacing_cleanup(processed_text_stage1)
                batch_results.append((original_idx, final_text))
        
        return batch_results

    def punctuate(self, texts: List[str], batch_size: int = 8) -> List[str]:
        self._print_verbose(f"Starting punctuation for {len(texts)} texts with batch_size {batch_size}, sliding_window={self.sliding_window}...")
        
        if not texts:
            return []
        
        # Initialize results array
        results = [''] * len(texts)
        
        if not self.sliding_window:
            # Mode 1: Truncate all texts and batch process with length grouping
            self._print_verbose("Mode: Batch processing all texts with truncation")
            texts_with_indices = [(i, text) for i, text in enumerate(texts)]
            grouped_batches = self._group_texts_by_length(texts_with_indices, batch_size)
            
            self._print_verbose(f"Grouped {len(texts)} texts into {len(grouped_batches)} length-based batches")
            
            for batch_num, batch_with_indices in enumerate(grouped_batches):
                self._print_verbose(f"Processing batch {batch_num + 1}/{len(grouped_batches)} ({len(batch_with_indices)} texts)")
                
                # Get token lengths for this batch for logging
                if self.verbose:
                    batch_lengths = [len(self.tokenizer.tokenize(text)) for _, text in batch_with_indices]
                    self._print_verbose(f"  Batch token lengths: {min(batch_lengths)}-{max(batch_lengths)} (avg: {sum(batch_lengths)//len(batch_lengths)})")
                
                batch_results = self._process_batch_with_indices(batch_with_indices)
                
                # Store results in correct positions
                for idx, result in batch_results:
                    results[idx] = result
        
        else:
            # Mode 2: Smart batching - separate short and long texts
            self._print_verbose("Mode: Smart batching with sliding window for long texts")
            
            short_texts_with_indices = []
            long_texts_with_indices = []
            
            # Separate texts by length
            for i, text in enumerate(texts):
                test_tokens = self.tokenizer.tokenize(text)
                if len(test_tokens) > self.max_length:
                    long_texts_with_indices.append((i, text))
                    self._print_verbose(f"  Text {i} marked for sliding window (length: {len(test_tokens)} tokens)")
                else:
                    short_texts_with_indices.append((i, text))
            
            self._print_verbose(f"Split into {len(short_texts_with_indices)} short texts and {len(long_texts_with_indices)} long texts")
            
            # Process short texts in length-grouped batches
            if short_texts_with_indices:
                self._print_verbose(f"Batch processing {len(short_texts_with_indices)} short texts")
                grouped_batches = self._group_texts_by_length(short_texts_with_indices, batch_size)
                
                for batch_num, batch_with_indices in enumerate(grouped_batches):
                    self._print_verbose(f"Processing short text batch {batch_num + 1}/{len(grouped_batches)} ({len(batch_with_indices)} texts)")
                    
                    # Get token lengths for this batch for logging
                    if self.verbose:
                        batch_lengths = [len(self.tokenizer.tokenize(text)) for _, text in batch_with_indices]
                        self._print_verbose(f"  Batch token lengths: {min(batch_lengths)}-{max(batch_lengths)} (avg: {sum(batch_lengths)//len(batch_lengths)})")
                    
                    batch_results = self._process_batch_with_indices(batch_with_indices)
                    
                    # Store results in correct positions
                    for idx, result in batch_results:
                        results[idx] = result
            
            # Process long texts individually with sliding window
            if long_texts_with_indices:
                self._print_verbose(f"Processing {len(long_texts_with_indices)} long texts with sliding window")
                for i, (original_idx, text) in enumerate(long_texts_with_indices):
                    self._print_verbose(f"Processing long text {i+1}/{len(long_texts_with_indices)} (original index {original_idx})")
                    try:
                        result = self._punctuate_sliding_window(text)
                        results[original_idx] = result
                    except Exception as e:
                        self._print_verbose(f"Error processing long text {original_idx}: {e}")
                        results[original_idx] = text  # Fallback to original
        
        self._print_verbose("Punctuation finished.")
        return results

    def _punctuate_sliding_window(self, text: str) -> str:
        """Process long text using sliding window with sentence-based context."""
        
        # Tokenize the full text
        full_input_ids = self.tokenizer.encode(text, add_special_tokens=True)
        
        self._print_verbose(f"    Full text length: {len(full_input_ids)} tokens")
        
        # Initialize tracking variables
        final_predictions = [0] * len(full_input_ids)  # Will be filled with actual predictions
        current_pos = 0  # Position in the full text we're currently processing
        context_start = 0  # Start of context in full_input_ids
        window_count = 0
        
        while current_pos < len(full_input_ids):
            window_count += 1
            
            # Determine context size
            context_size = current_pos - context_start
            max_context_size = min(int(0.3 * self.max_length), current_pos)
            
            if context_size > max_context_size:
                # Trim context to fit within limits
                context_start = current_pos - max_context_size
                context_size = max_context_size
            
            # Determine how many new tokens we can process
            available_space = self.max_length - context_size
            remaining_tokens = len(full_input_ids) - current_pos
            new_tokens_count = min(available_space, remaining_tokens)
            
            # Create window: context + new tokens
            window_start = context_start
            window_end = current_pos + new_tokens_count
            window_input_ids = full_input_ids[window_start:window_end]
            
            self._print_verbose(f"    Window {window_count}: pos {current_pos}-{current_pos + new_tokens_count}, " +
                               f"context {context_size}, new {new_tokens_count}, total {len(window_input_ids)}")
            
            # Run inference on this window
            window_predictions = self._run_inference_on_tokens(window_input_ids)
            
            # Extract predictions for the new tokens only
            context_offset = current_pos - window_start
            new_predictions = window_predictions[context_offset:]
            
            # Store predictions for new tokens
            for i, pred in enumerate(new_predictions):
                final_predictions[current_pos + i] = pred
            
            # Determine context for next iteration
            if current_pos + new_tokens_count >= len(full_input_ids):
                # We're done
                break
            
            # Find where to cut for next iteration's context
            next_context_start = self._find_next_context_start(
                final_predictions, current_pos, new_tokens_count
            )
            
            current_pos += new_tokens_count
            context_start = next_context_start
        
        self._print_verbose(f"    Completed sliding window processing with {window_count} windows")
        
        # Reconstruct the full text
        raw_reconstructed_text = self._reconstruct_single_text(full_input_ids, final_predictions)
        processed_text_stage1 = post_process_cleaned_text(raw_reconstructed_text)
        return _final_spacing_cleanup(processed_text_stage1)

    def _run_inference_on_tokens(self, input_ids: List[int]) -> List[int]:
        """Run inference on a list of token IDs and return predictions."""
        input_tensor = torch.tensor([input_ids], device=self.device)
        attention_mask = torch.ones_like(input_tensor)
        
        with torch.no_grad(), \
             torch.autocast(device_type=self.device.type, dtype=self.model_dtype, enabled=self.autocast_enabled):
            outputs = self.model(input_ids=input_tensor, attention_mask=attention_mask)
            logits = outputs.logits
        
        predictions = torch.argmax(logits, dim=-1)
        return predictions[0].cpu().tolist()

    def _find_next_context_start(self, predictions: List[int], current_pos: int, processed_count: int) -> int:
        """Find where to start context for next window (keep last 3 sentences)."""
        
        # Look for sentence boundaries in the newly processed predictions
        search_start = current_pos
        search_end = current_pos + processed_count
        
        sentence_boundaries = []
        for i in range(search_start, search_end):
            if self._is_sentence_end(predictions[i]):
                sentence_boundaries.append(i)
        
        self._print_verbose(f"      Found {len(sentence_boundaries)} sentence boundaries in current window")
        
        if len(sentence_boundaries) < 3:
            # Try commas as fallback
            comma_boundaries = []
            for i in range(search_start, search_end):
                if self._is_comma(predictions[i]):
                    comma_boundaries.append(i)
            
            self._print_verbose(f"      Found {len(comma_boundaries)} comma boundaries as fallback")
            
            # Combine sentence and comma boundaries, prioritizing sentences
            all_boundaries = sentence_boundaries + comma_boundaries
            all_boundaries.sort()
            
            if len(all_boundaries) >= 3:
                sentence_boundaries = all_boundaries
        
        if len(sentence_boundaries) >= 3:
            # Keep last 3 sentences: start after the 3rd-to-last boundary
            context_start = sentence_boundaries[-3] + 1
            self._print_verbose(f"      Using sentence-based context starting at position {context_start}")
        else:
            # Fallback: keep last 30% of processed tokens
            keep_count = max(1, int(0.3 * processed_count))
            context_start = search_end - keep_count
            self._print_verbose(f"      Using fallback 30% context starting at position {context_start}")
        
        # Ensure context doesn't exceed limits
        max_context = int(0.3 * self.max_length)
        min_context_start = search_end - max_context
        
        if context_start < min_context_start:
            # Try 50% limit
            max_context_extended = int(0.5 * self.max_length)
            min_context_start_extended = search_end - max_context_extended
            
            if context_start < min_context_start_extended:
                context_start = min_context_start_extended
                self._print_verbose(f"      Context limited to 50% cutoff at position {context_start}")
            else:
                context_start = min_context_start
                self._print_verbose(f"      Context limited to 30% cutoff at position {context_start}")
        
        return max(0, context_start)

    def _is_sentence_end(self, pred_id: int) -> bool:
        """Check if prediction ID corresponds to sentence-ending punctuation."""
        punct_str = self.id_to_punctuation.get(pred_id, "O")
        return punct_str in self.SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP

    def _is_comma(self, pred_id: int) -> bool:
        """Check if prediction ID corresponds to comma punctuation."""
        punct_str = self.id_to_punctuation.get(pred_id, "O")
        comma_punctuations = {",", "،", "٬"}
        return punct_str in comma_punctuations
