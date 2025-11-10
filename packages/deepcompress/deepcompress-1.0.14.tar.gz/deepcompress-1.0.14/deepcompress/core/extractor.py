"""
OCR extraction using DeepSeek-OCR integration.
"""

import asyncio
import hashlib
import time
from pathlib import Path
from typing import Any, Optional

from deepcompress.core.config import DeepCompressConfig
from deepcompress.exceptions import GPUError, OCRError
from deepcompress.models.document import Entity, ExtractedDocument, Page, Table


class OCRExtractor:
    """
    DeepSeek-OCR integration for vision-based document extraction.

    Uses a 3B parameter vision-language model with:
    - SAM-base vision encoder
    - CLIP-large global attention
    - MoE decoder (64 experts, 6 active)
    - 16× compression of vision tokens
    """

    def __init__(self, config: DeepCompressConfig) -> None:
        self.config = config
        self._model: Any = None
        self._tokenizer: Any = None
        self._device: str = config.ocr_device

    async def initialize(self) -> None:
        """
        Initialize the OCR model and tokenizer.

        Loads DeepSeek-OCR model onto GPU with bfloat16 precision.
        """
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
            import warnings
            
            # Suppress known warnings from DeepSeek-OCR model
            warnings.filterwarnings("ignore", message=".*model of type.*not supported for all configurations.*")
            warnings.filterwarnings("ignore", message=".*deepseek_vl_v2.*DeepseekOCR.*")
            warnings.filterwarnings("ignore", message=".*not initialized from the model checkpoint.*")
            warnings.filterwarnings("ignore", message=".*do_sample.*temperature.*")
            warnings.filterwarnings("ignore", message=".*attention mask.*pad token.*")
            warnings.filterwarnings("ignore", message=".*Flash Attention 2.0.*")
            
            # Apply compatibility patch for newer transformers versions
            self._apply_transformers_compatibility_patch()

            # DeepSeek-OCR uses AutoTokenizer, not AutoProcessor
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.config.ocr_model,
                revision=self.config.ocr_model_revision,
                trust_remote_code=True,
            )
            
            # Ensure pad_token is set to avoid warnings
            if self._tokenizer.pad_token is None:
                if self._tokenizer.eos_token is not None:
                    self._tokenizer.pad_token = self._tokenizer.eos_token
                else:
                    # Add a default pad token if none exists
                    self._tokenizer.add_special_tokens({'pad_token': '[PAD]'})

            # Determine device_map for optimal loading
            device_map = None
            if self._device.startswith("cuda"):
                # Load directly on specified GPU
                device_map = {"": self._device}
                
                # Set GPU memory fraction if configured
                if self.config.gpu_memory_fraction < 1.0:
                    device_idx = int(self._device.split(":")[-1]) if ":" in self._device else 0
                    torch.cuda.set_per_process_memory_fraction(
                        self.config.gpu_memory_fraction,
                        device=device_idx,
                    )
            
            # Base model kwargs
            model_kwargs = {
                "torch_dtype": torch.bfloat16 if self.config.use_bfloat16 else torch.float32,
                "trust_remote_code": True,
                "revision": self.config.ocr_model_revision,
                "low_cpu_mem_usage": True,  # Optimize memory usage during loading
            }
            
            # Add device_map if using CUDA
            if device_map is not None:
                model_kwargs["device_map"] = device_map

            # Attempt to use flash attention 2 if available and enabled
            if self.config.enable_flash_attention and self._device.startswith("cuda"):
                try:
                    self._model = AutoModel.from_pretrained(
                        self.config.ocr_model,
                        attn_implementation="flash_attention_2",
                        **model_kwargs,
                    )
                except (ImportError, ValueError, Exception) as e:
                    # Fall back to eager attention if flash attention not available
                    warnings.warn(f"Flash Attention 2 not available, falling back to eager: {e}")
                    model_kwargs.pop("attn_implementation", None)
                    self._model = AutoModel.from_pretrained(
                        self.config.ocr_model,
                        attn_implementation="eager",
                        **model_kwargs,
                    )
            else:
                # Use eager attention (standard)
                self._model = AutoModel.from_pretrained(
                    self.config.ocr_model,
                    attn_implementation="eager",
                    **model_kwargs,
                )

            # Move to device if not already there (for CPU fallback)
            if device_map is None and self._device != "cpu":
                self._model = self._model.to(self._device)

            self._model.eval()

        except ImportError as e:
            error_msg = str(e)
            if "flash_attn" in error_msg.lower():
                raise OCRError(
                    "Flash Attention library not installed. Install with: pip install flash-attn --no-build-isolation",
                    details={"error": error_msg},
                )
            raise OCRError(
                "Failed to import required libraries. Install with: pip install deepcompress[gpu]",
                details={"error": error_msg},
            )
        except Exception as e:
            raise GPUError(
                "Failed to initialize OCR model",
                details={"device": self._device, "error": str(e)},
            )

    async def extract(
        self,
        file_path: str,
        document_id: Optional[str] = None,
    ) -> ExtractedDocument:
        """
        Extract document content using DeepSeek-OCR.

        Args:
            file_path: Path to document (PDF or image)
            document_id: Optional document ID (generated if None)

        Returns:
            ExtractedDocument with extracted entities, tables, and text

        Raises:
            OCRError: If extraction fails
            GPUError: If GPU operations fail
        """
        if self._model is None:
            await self.initialize()

        start_time = time.time()

        try:
            images = await self._load_images(file_path)

            if document_id is None:
                document_id = self._generate_document_id(file_path)

            pages = []
            for page_num, image in enumerate(images, start=1):
                page = await self._extract_page(image, page_num)
                pages.append(page)

            processing_time_ms = (time.time() - start_time) * 1000

            return ExtractedDocument(
                document_id=document_id,
                page_count=len(pages),
                mode=self.config.ocr_mode,
                pages=pages,
                metadata={
                    "processing_time_ms": processing_time_ms,
                    "model": self.config.ocr_model,
                    "device": self._device,
                },
            )

        except Exception as e:
            raise OCRError(
                f"Failed to extract document: {file_path}",
                details={"error": str(e)},
            )

    async def _load_images(self, file_path: str) -> list[Any]:
        """
        Load images from PDF or image file.

        Args:
            file_path: Path to file

        Returns:
            List of PIL Images
        """
        from PIL import Image

        path = Path(file_path)

        if path.suffix.lower() == ".pdf":
            try:
                from pdf2image import convert_from_path

                loop = asyncio.get_event_loop()
                images = await loop.run_in_executor(
                    None,
                    lambda: convert_from_path(
                        str(path),
                        dpi=300,
                        fmt="png",
                    ),
                )
                return images
            except ImportError:
                raise OCRError(
                    "pdf2image not installed. Install with: pip install deepcompress[gpu]"
                )
        else:
            image = Image.open(path).convert("RGB")
            return [image]

    async def _extract_page(self, image: Any, page_number: int) -> Page:
        """
        Extract single page using DeepSeek-OCR.

        Args:
            image: PIL Image
            page_number: Page number (1-indexed)

        Returns:
            Page with extracted entities and tables
        """
        import torch
        import tempfile
        import os

        # DeepSeek-OCR expects images to be provided as file paths
        # We need to save the PIL image temporarily
        tmp_dir = tempfile.mkdtemp()
        tmp_image_path = os.path.join(tmp_dir, 'page.png')
        image.save(tmp_image_path, format='PNG')
        
        try:
            # Map OCR mode to base_size and image_size
            # small=640, base=1024, large=1280
            mode_config = {
                "small": {"base_size": 640, "image_size": 640},
                "base": {"base_size": 1024, "image_size": 640},
                "large": {"base_size": 1280, "image_size": 640},
            }
            config = mode_config.get(self.config.ocr_mode, mode_config["small"])
            
            # Use DeepSeek-OCR's custom infer method
            # Prompt format for structured extraction
            prompt = "<image>\nExtract all text, entities, tables, and structured information from this document image. Return the results in JSON format."
            
            # Create output directory for the model (required even with save_results=False)
            output_dir = os.path.join(tmp_dir, 'output')
            
            result = self._model.infer(
                self._tokenizer,
                prompt=prompt,
                image_file=tmp_image_path,
                output_path=output_dir,  # Required by the model
                base_size=config["base_size"],
                image_size=config["image_size"],
                crop_mode=True,
                save_results=False,
                test_compress=True,
            )
            
            # The result from infer() is typically a string with the extracted text
            # For document compression, we want the raw text output
            result_text = result if isinstance(result, str) else str(result)
            
        finally:
            # Clean up temporary directory and all its contents
            import shutil
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)

        entities, tables = self._parse_ocr_output(result_text)
        
        # Estimate tokens based on text length (rough approximation)
        estimated_tokens = len(result_text.split()) * 1.3  # ~1.3 tokens per word

        return Page(
            page_number=page_number,
            layout="multi_column",
            entities=entities,
            tables=tables,
            raw_text=result_text,
            metadata={"vision_tokens": int(estimated_tokens)},
        )

    def _parse_ocr_output(self, output: str) -> tuple[list[Entity], list[Table]]:
        """
        Parse DeepSeek-OCR JSON output into entities and tables.

        Args:
            output: JSON string from OCR model

        Returns:
            Tuple of (entities, tables)
        """
        import orjson

        try:
            data = orjson.loads(output)
        except Exception:
            data = {"entities": [], "tables": []}

        entities = []
        for ent_data in data.get("entities", []):
            entities.append(
                Entity(
                    type=ent_data.get("type", "unknown"),
                    text=ent_data.get("text", ""),
                    bbox=ent_data.get("bbox"),
                    confidence=ent_data.get("confidence", 1.0),
                )
            )

        tables = []
        for table_data in data.get("tables", []):
            tables.append(
                Table(
                    headers=table_data.get("headers", []),
                    rows=table_data.get("rows", []),
                    bbox=table_data.get("bbox"),
                    confidence=table_data.get("confidence", 1.0),
                )
            )

        return entities, tables

    def _generate_document_id(self, file_path: str) -> str:
        """
        Generate unique document ID from file path.

        Args:
            file_path: Path to file

        Returns:
            Document ID (hash of file path)
        """
        return hashlib.sha256(file_path.encode()).hexdigest()[:16]

    def _apply_transformers_compatibility_patch(self) -> None:
        """
        Apply compatibility patches for newer transformers versions.
        
        This fixes multiple compatibility issues:
        1. LlamaFlashAttention2 import error in older transformers
        2. DynamicCache.get_max_length() -> get_seq_length() API change
        3. LlamaAttention position_embeddings argument requirement in v4.46+
        """
        try:
            from transformers.models.llama import modeling_llama
            import inspect
            
            # Patch 1: Fix LlamaFlashAttention2 missing in newer transformers
            if not hasattr(modeling_llama, 'LlamaFlashAttention2'):
                if hasattr(modeling_llama, 'LlamaAttention'):
                    modeling_llama.LlamaFlashAttention2 = modeling_llama.LlamaAttention
                elif hasattr(modeling_llama, 'LlamaSdpaAttention'):
                    modeling_llama.LlamaFlashAttention2 = modeling_llama.LlamaSdpaAttention
                else:
                    class LlamaFlashAttention2Fallback:
                        """Fallback class for missing LlamaFlashAttention2"""
                        pass
                    modeling_llama.LlamaFlashAttention2 = LlamaFlashAttention2Fallback
            
            # Patch 3: Fix position_embeddings requirement in transformers >= 4.46
            # This wraps LlamaAttention classes to make position_embeddings optional
            for attention_class_name in ['LlamaAttention', 'LlamaFlashAttention2', 'LlamaSdpaAttention']:
                if hasattr(modeling_llama, attention_class_name):
                    original_class = getattr(modeling_llama, attention_class_name)
                    if not hasattr(original_class, '_deepcompress_patched'):
                        original_forward = original_class.forward
                        
                        # Check if position_embeddings is already in the signature
                        sig = inspect.signature(original_forward)
                        if 'position_embeddings' in sig.parameters:
                            # Wrap the forward method to make position_embeddings optional
                            def create_wrapped_forward(orig_forward):
                                def wrapped_forward(self, hidden_states, attention_mask=None,
                                                  position_ids=None, past_key_value=None,
                                                  output_attentions=False, use_cache=False,
                                                  cache_position=None, position_embeddings=None, **kwargs):
                                    # Generate rotary position embeddings if upstream code did not supply them.
                                    if position_embeddings is None:
                                        rotary_emb = getattr(self, 'rotary_emb', None)
                                        if rotary_emb is not None:
                                            cos = sin = None
                                            try:
                                                import inspect as _inspect  # Local import to avoid module-level dependency
                                                import torch
                                                import torch.nn.functional as F

                                                bsz, q_len, _ = hidden_states.size()
                                                config_tp = getattr(self.config, "pretraining_tp", 1)

                                                if config_tp > 1:
                                                    kv_slicing = (self.num_key_value_heads * self.head_dim) // config_tp
                                                    value_slices = self.v_proj.weight.split(kv_slicing, dim=0)
                                                    query_slices = self.q_proj.weight.split(
                                                        (self.num_heads * self.head_dim) // config_tp, dim=0
                                                    )
                                                    key_slices = self.k_proj.weight.split(kv_slicing, dim=0)
                                                    query_states = [
                                                        F.linear(hidden_states, query_slices[i])
                                                        for i in range(config_tp)
                                                    ]
                                                    query_states = torch.cat(query_states, dim=-1)
                                                    key_states = [
                                                        F.linear(hidden_states, key_slices[i])
                                                        for i in range(config_tp)
                                                    ]
                                                    key_states = torch.cat(key_states, dim=-1)
                                                    value_states = [
                                                        F.linear(hidden_states, value_slices[i])
                                                        for i in range(config_tp)
                                                    ]
                                                    value_states = torch.cat(value_states, dim=-1)
                                                else:
                                                    query_states = self.q_proj(hidden_states)
                                                    key_states = self.k_proj(hidden_states)
                                                    value_states = self.v_proj(hidden_states)

                                                query_states = query_states.view(
                                                    bsz, q_len, self.num_heads, self.head_dim
                                                ).transpose(1, 2)
                                                key_states = key_states.view(
                                                    bsz, q_len, self.num_key_value_heads, self.head_dim
                                                ).transpose(1, 2)
                                                value_states = value_states.view(
                                                    bsz, q_len, self.num_key_value_heads, self.head_dim
                                                ).transpose(1, 2)

                                                pos_ids = position_ids
                                                if pos_ids is None:
                                                    if cache_position is not None:
                                                        pos_ids = cache_position.view(1, -1).to(hidden_states.device)
                                                    else:
                                                        past_length = 0
                                                        if past_key_value is not None:
                                                            try:
                                                                if hasattr(past_key_value, "get_usable_length"):
                                                                    past_length = int(
                                                                        past_key_value.get_usable_length(q_len) or 0
                                                                    )
                                                                elif hasattr(past_key_value, "seen_tokens"):
                                                                    past_length = int(past_key_value.seen_tokens or 0)
                                                            except Exception:
                                                                past_length = 0
                                                        pos_ids = torch.arange(
                                                            past_length,
                                                            past_length + q_len,
                                                            dtype=torch.long,
                                                            device=hidden_states.device,
                                                        ).unsqueeze(0)

                                                rotary_callable = rotary_emb.forward if hasattr(rotary_emb, "forward") else rotary_emb
                                                rotary_sig = _inspect.signature(rotary_callable)
                                                if "cache_position" in rotary_sig.parameters:
                                                    cos, sin = rotary_emb(value_states, pos_ids, cache_position=cache_position)
                                                else:
                                                    cos, sin = rotary_emb(value_states, pos_ids)
                                            except Exception:
                                                cos = sin = None

                                            if cos is not None and sin is not None:
                                                position_embeddings = (cos, sin)

                                    return orig_forward(
                                        self,
                                        hidden_states,
                                        attention_mask=attention_mask,
                                        position_ids=position_ids,
                                        past_key_value=past_key_value,
                                        output_attentions=output_attentions,
                                        use_cache=use_cache,
                                        cache_position=cache_position,
                                        position_embeddings=position_embeddings,
                                        **kwargs,
                                    )
                                return wrapped_forward
                            
                            original_class.forward = create_wrapped_forward(original_forward)
                            original_class._deepcompress_patched = True
        except (ImportError, AttributeError) as e:
            # Log but don't fail - patches are optional
            import warnings
            warnings.warn(f"Could not apply all compatibility patches: {e}")
        
        # Patch 2: Fix DynamicCache API change (get_max_length -> get_seq_length)
        try:
            from transformers.cache_utils import DynamicCache
            
            # Check if get_max_length is missing but get_seq_length exists
            if not hasattr(DynamicCache, 'get_max_length') and hasattr(DynamicCache, 'get_seq_length'):
                # Add get_max_length as an alias to get_seq_length
                DynamicCache.get_max_length = DynamicCache.get_seq_length

            # Add seen_tokens compatibility shim for newer transformers
            if not hasattr(DynamicCache, 'seen_tokens'):
                def _get_seen_tokens(self):
                    """
                    Provide a unified accessor for the number of cached tokens.
                    """
                    try:
                        if hasattr(self, 'get_seq_length'):
                            return self.get_seq_length()
                        if hasattr(self, 'get_max_length'):
                            return self.get_max_length()
                    except Exception:
                        # Fall back to inspecting the key cache shape
                        pass

                    cache = getattr(self, "key_value_cache", None) or getattr(self, "key_cache", None)
                    if cache:
                        first = None
                        if isinstance(cache, dict):
                            first = next(iter(cache.values()), None)
                        elif isinstance(cache, (list, tuple)) and cache:
                            first = cache[0]
                        if isinstance(first, (list, tuple)) and first:
                            first = first[0]
                        if hasattr(first, "shape"):
                            return first.shape[-2]
                    return getattr(self, "_deepcompress_seen_tokens", 0)

                def _set_seen_tokens(self, value):
                    """
                    Map seen_tokens assignments to the new API when available.
                    """
                    if hasattr(self, 'set_seq_length'):
                        try:
                            self.set_seq_length(value)
                            return
                        except Exception:
                            pass
                    if hasattr(self, '_set_seen_tokens'):
                        try:
                            self._set_seen_tokens(value)
                            return
                        except Exception:
                            pass
                    self._deepcompress_seen_tokens = value

                DynamicCache.seen_tokens = property(_get_seen_tokens, _set_seen_tokens)

            # Add get_usable_length shim (renamed in newer transformers)
            if not hasattr(DynamicCache, 'get_usable_length'):
                def _get_usable_length(self, seq_length=None):
                    """
                    Return usable token length expected by older DeepSeek builds.
                    """
                    try:
                        if hasattr(self, 'get_seq_length'):
                            return self.get_seq_length()
                        if hasattr(self, 'get_max_length'):
                            return self.get_max_length()
                    except Exception:
                        pass

                    length = None
                    if hasattr(self, 'seen_tokens'):
                        try:
                            length = self.seen_tokens
                        except Exception:
                            length = None

                    if length is None:
                        cache = getattr(self, "key_value_cache", None) or getattr(self, "key_cache", None)
                        if cache:
                            first = None
                            if isinstance(cache, dict):
                                first = next(iter(cache.values()), None)
                            elif isinstance(cache, (list, tuple)) and cache:
                                first = cache[0]
                            if isinstance(first, (list, tuple)) and first:
                                first = first[0]
                            if hasattr(first, "shape"):
                                length = first.shape[-2]

                    if length is None:
                        length = getattr(self, "_deepcompress_seen_tokens", 0)

                    if seq_length is not None:
                        return min(length, seq_length)
                    return length

                DynamicCache.get_usable_length = _get_usable_length
        except (ImportError, AttributeError):
            pass

    async def extract_batch(
        self,
        file_paths: list[str],
    ) -> list[ExtractedDocument]:
        """
        Extract multiple documents in batch.

        Args:
            file_paths: List of file paths

        Returns:
            List of ExtractedDocuments
        """
        tasks = [self.extract(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        documents = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise OCRError(
                    f"Batch extraction failed for {file_paths[i]}",
                    details={"error": str(result)},
                )
            documents.append(result)

        return documents

