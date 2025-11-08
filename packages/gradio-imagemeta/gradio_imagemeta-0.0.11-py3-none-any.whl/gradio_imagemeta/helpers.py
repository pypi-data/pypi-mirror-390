import ast
from dataclasses import fields, is_dataclass
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from PIL import Image, PngImagePlugin, ExifTags
import numpy as np
from gradio import image_utils

def infer_type(s: Any):
    """
    Infers and converts a string to the most likely data type.

    It attempts conversions in the following order:
    1. Python literal (list, dict, tuple, etc.) if the string looks like one.
    2. Integer
    3. Float
    4. Boolean (case-insensitive 'true' or 'false')
    If all conversions fail, it returns the original string.

    Args:
        s: The input value to be converted.

    Returns:
        The converted value or the original value.
    """
    if not isinstance(s, str):
        # If the input is not a string, return it as is.
        return s
    
    # 1. Try to evaluate as a Python literal (list, dict, etc.)
    s_stripped = s.strip()    
    if s_stripped.startswith(('[', '{')) and s_stripped.endswith((']', '}')):
        try:            
            return ast.literal_eval(s_stripped)
        except (ValueError, SyntaxError, MemoryError, TypeError):            
            pass
    
    # 2. Try to convert to an integer
    try:
        return int(s_stripped)
    except ValueError:
        pass

    # 3. Try to convert to a float
    try:
        return float(s_stripped)
    except ValueError:
        pass
    
    # 4. Check for a boolean value
    s_lower = s_stripped.lower()
    if s_lower == 'true':
        return True
    if s_lower == 'false':
        return False
        
    # 5. If nothing else worked, return the original string (sem os espaços extras)
    return s

def extract_metadata(image_data: str | Path | Image.Image | np.ndarray | None, only_custom_metadata: bool = True) -> Dict[str, Any]:
    """
    Extracts metadata from an image.

    Args:
        image_data: Image data as a filepath, Path, PIL Image, NumPy array, or None.
        only_custom_metadata: If True, excludes technical metadata (e.g., ImageWidth, ImageHeight). Defaults to True.

    Returns:
        Dictionary of extracted metadata. Returns empty dictionary if no metadata is available or extraction fails.
    """
    if not image_data:
        return {}

    try:
        # Convert image_data to PIL.Image
        if isinstance(image_data, (str, Path)):
            image = Image.open(image_data)
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            image = image_data
        elif hasattr(image_data, 'path'):  # For ImageMetaData
            image = Image.open(image_data.path)
        else:
            return {}

        decoded_meta = {}
        if image.format == "PNG":
            if not only_custom_metadata:
                decoded_meta["ImageWidth"] = image.width
                decoded_meta["ImageHeight"] = image.height
            metadata = image.info
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, bytes):
                        value = value.decode(errors='ignore')
                    decoded_meta[str(key)] = value
        else:
            exif_data = image.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        value = value.decode(errors='ignore')
                    decoded_meta[str(tag)] = value
            if not only_custom_metadata:
                decoded_meta["ImageWidth"] = image.width
                decoded_meta["ImageHeight"] = image.height

        return decoded_meta
    except Exception:
        return {}

def preprocess_image(image_data: str | Path | Image.Image | np.ndarray, type: str = "numpy") -> np.ndarray | Image.Image:
    """
    Processes an image to the specified format.

    Args:
        image_data: Image data as a filepath, Path, PIL Image, or NumPy array.
        type: Output format, either "numpy" (array with shape (height, width, 3)) or "pil" (PIL Image). Defaults to "numpy".

    Returns:
        Processed image as a NumPy array or PIL Image.

    Raises:
        ValueError: If image_data type or output type is unsupported.
    """
    if isinstance(image_data, (str, Path)):
        payload = image_data
    elif isinstance(image_data, Image.Image):
        payload = image_data
    elif isinstance(image_data, np.ndarray):
        payload = image_data
    elif hasattr(image_data, 'path'):  # For ImageMetaData
        payload = image_data.path
    else:
        raise ValueError(f"Unsupported image_data type: {type(image_data)}")

    if type == "numpy":
        return image_utils.preprocess_image(payload, type="numpy")
    elif type == "pil":
        return image_utils.preprocess_image(payload, type="pil")
    else:
        raise ValueError(f"Unsupported type: {type}")

def add_metadata(image_data: str | Path | Image.Image | np.ndarray, save_path: str, metadata: Dict[str, Any]) -> Image.Image | None:
    """
    Adds custom metadata to an image and saves it to the specified path.

    For PNG, it uses tEXt chunks.
    For JPEG and other EXIF-supporting formats, it serializes the metadata
    as a JSON string and stores it in the 'UserComment' EXIF tag.

    Args:
        image_data: Image data as a filepath, Path, PIL Image, or NumPy array.
        save_path: Filepath where the modified image will be saved.
        metadata: Dictionary of custom metadata to add to the image.

    Returns:
        The saved image as a PIL Image object, or None if saving failed.
    """
    USER_COMMENT_TAG_ID = 0x9286 
    
    if not save_path or not metadata:
        
        if isinstance(image_data, Image.Image):
             image_data.save(save_path)
             return image_data
        try:
             image = Image.open(image_data)
             image.save(save_path)
             return image
        except:
             return None

    
    try:
        if isinstance(image_data, (str, Path)):
            image = Image.open(image_data)
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            image = image_data.copy()
        elif hasattr(image_data, 'path'):  # For ImageMetaData
            image = Image.open(image_data.path)
        else:
            return None 
    except Exception as e:
        print(f"Error loading image data: {e}")
        return None
    
    if image.mode not in ['RGB', 'RGBA']:
        image = image.convert('RGB')

    _, ext = os.path.splitext(save_path)
    file_format = ext.replace('.', '').upper()

    if file_format == "PNG":
        png_info = PngImagePlugin.PngInfo()
        for key, value in metadata.items():
            png_info.add_text(str(key), str(value))
        
        image.save(save_path, "PNG", pnginfo=png_info, quality=100)
    
    elif file_format in ["JPEG", "JPG", "TIFF"]:
        try:            
            metadata_json_string = json.dumps(metadata)
            exif_data = image.info.get('exif')
            
            if exif_data:                
                exif = Image.Exif()
                exif.frombytes(exif_data)
            else:
                exif = Image.Exif()

            encoding_prefix = b'\x00\x00\x00\x00\x00\x00\x00\x00'
            comment_bytes = metadata_json_string.encode('utf-8')
            exif[USER_COMMENT_TAG_ID] = encoding_prefix + comment_bytes           

            image.save(save_path, exif=exif.tobytes())

        except Exception as e:
            print(f"Metadata is not supported for `{file_format}` format, saving without it.")
            image.save(save_path)
    
    else:
        print(f"Warning: Metadata not supported for format '{file_format}'. Saving image without metadata.")
        image.save(save_path)    
    
    try:
        saved_image = Image.open(save_path)
        return saved_image.convert("RGB")
    except Exception as e:
        print(f"Failed to reopen saved image at {save_path}. Error: {e}")
        return None

def build_path_to_metadata_key_map(cls: Type, prefix_list: List[str]) -> Dict[str, str]:
    """
    Builds a map from a dataclass field path (e.g., 'image_settings.model') to the
    expected key in the metadata dictionary (e.g., 'Image Settings - Model').
    """
    path_map = {}
    if not is_dataclass(cls):
        return {}

    for f in fields(cls):
        current_path = f.name
        
        if is_dataclass(f.type):
            parent_label = f.metadata.get("label", f.name.replace("_", " ").title())
            new_prefix_list = prefix_list + [parent_label]
            nested_map = build_path_to_metadata_key_map(f.type, new_prefix_list)
            for nested_path, metadata_key in nested_map.items():
                path_map[f"{current_path}.{nested_path}"] = metadata_key
        else:
            label = f.metadata.get("label", f.name.replace("_", " ").title())
            full_prefix = " - ".join(prefix_list)
            metadata_key = f"{full_prefix} - {label}" if full_prefix else label
            path_map[current_path] = metadata_key
            
    return path_map

def transfer_metadata(
    output_fields: List[Any], 
    metadata: Dict[str, Any],
    propertysheet_map: Optional[Dict[int, Dict[str, Any]]] = None,
    gradio_component_map: Optional[Dict[int, str]] = None,
    remove_prefix_from_keys: bool = False
) -> List[Any]:
    """
    Maps a flat metadata dictionary to a list of Gradio UI components, with
    flexible and powerful matching logic for all component types.

    This function is UI-agnostic. For PropertySheets, it uses the `propertysheet_map`
    to reconstruct nested dataclass instances. It intelligently builds the expected
    metadata keys by interpreting the `prefixes` list: strings found as keys in the
    `metadata` are replaced by their values, while other strings are used literally.

    For standard Gradio components, it uses a three-tiered priority system:
    1.  **Explicit Mapping (Highest Priority):** If `gradio_component_map` is provided,
        it uses the specified metadata key for a given component ID.
    2.  **Base Label Matching:** If `remove_prefix_from_keys=True` and no explicit map
        is found, it matches the component's `.label` against "base" (prefix-stripped)
        metadata keys.
    3.  **Exact Label Matching (Default):** Otherwise, it attempts an exact match
        between the component's `.label` and a metadata key.

    Args:
        output_fields (List[Any]): The list of Gradio components to be updated.
        metadata (Dict[str, Any]): The flat dictionary of metadata from an image.
        propertysheet_map (Optional[Dict[int, Dict[str, Any]]]): 
            A map from a PropertySheet's `id()` to its configuration dict, which
            should contain its `type` and a list of `prefixes`.
        gradio_component_map (Optional[Dict[int, str]]):
            An optional map from a standard component's `id()` to the exact
            metadata key that should populate it.
        remove_prefix_from_keys (bool): If True, enables fallback matching
            by stripping prefixes from metadata keys for standard components.

    Returns:
        List[Any]: A list of `gr.update` or `gr.skip()` objects.
    """
    if propertysheet_map is None: propertysheet_map = {}
    if gradio_component_map is None: gradio_component_map = {}
        
    output_values = [None] * len(output_fields)
    component_to_index = {id(comp): i for i, comp in enumerate(output_fields)}

    # Pre-process metadata to create a map of base labels if needed.
    base_label_map = {}
    if remove_prefix_from_keys:
        base_label_map = {key.rsplit(' - ', 1)[-1]: value for key, value in metadata.items()}
    
    for component in output_fields:
        comp_id = id(component)
        output_index = component_to_index.get(comp_id)
        if output_index is None:
            continue
            
        # --- Logic for PropertySheets ---
        if comp_id in propertysheet_map:
            sheet_info = propertysheet_map[comp_id]
            dc_type = sheet_info.get("type")
            prefix_definitions = sheet_info.get("prefixes", [])
        
            # Build the list of actual prefix strings by interpreting the definitions.
            prefix_values = []
            for p_def in prefix_definitions:
                # If the prefix definition is a key in the metadata, use its value.
                if p_def in metadata:
                    prefix_values.append(str(metadata[p_def]))
                # Otherwise, treat it as a literal string.
                else:
                    prefix_values.append(p_def)
            
            prefix_values = [p for p in prefix_values if p]

            if not dc_type or not is_dataclass(dc_type):
                continue
            
            # Build the map from the dataclass structure to the expected full metadata keys.
            path_to_key_map = build_path_to_metadata_key_map(dc_type, prefix_values)
            
            # Get the base instance to start populating.
            #instance_to_populate = getattr(component, '_dataclass_value', dc_type())
            #if not is_dataclass(instance_to_populate):
            instance_to_populate = dc_type()

            # Populate the instance by iterating through the path map.
            for path, metadata_key in path_to_key_map.items():
                if metadata_key in metadata:
                    value_from_meta = metadata[metadata_key]
                    
                    parts = path.split('.')
                    obj_to_set = instance_to_populate
                    try:
                        for part in parts[:-1]:
                            obj_to_set = getattr(obj_to_set, part)
                        
                        final_field_name = parts[-1]                        
                        converted_value = infer_type(value_from_meta)                           
                        setattr(obj_to_set, final_field_name, converted_value)
                    except (AttributeError, KeyError, ValueError, TypeError) as e:
                        print(f"Warning (transfer_metadata): Could not set value for path '{path}'. Error: {e}")
            
            output_values[output_index] = instance_to_populate
            
        # --- Unified Logic for Standard Gradio Components ---
        else:
            value_to_set = None
            
            # Priority 1: Check for an explicit mapping via gradio_component_map.
            if comp_id in gradio_component_map:
                metadata_key = gradio_component_map[comp_id]
                if metadata_key in metadata:
                    value_to_set = metadata[metadata_key]
            
            # If no explicit mapping was found, proceed to label-based matching.
            if value_to_set is None:
                label = getattr(component, 'label', None)
                if label:
                    # Priority 2: Check for a base label match if the flag is set.
                    if remove_prefix_from_keys and label in base_label_map:
                        value_to_set = base_label_map[label]
                    # Priority 3: Fallback to an exact label match.
                    else:                        
                        matching_key = next((key for key in metadata if label in key), None)
                        if matching_key:
                            value_to_set = metadata[matching_key]                                                    

            # If a value was found by any method, create the update object.
            if value_to_set is not None:
                output_values[output_index] = infer_type(value_to_set)
    
    return output_values