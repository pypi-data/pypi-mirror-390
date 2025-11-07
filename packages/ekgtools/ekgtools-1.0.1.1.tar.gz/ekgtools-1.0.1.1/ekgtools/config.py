DEFAULT_CONFIG = {
    'sig_arr_length': 5000,
    'bandpass_lower': 0.5,
    'bandpass_higher': 100,
    'median_filter_size': 5,
    'default_8_leads': ["I", "II", "V1", "V2", "V3", "V4", "V5", "V6"],
    'standard_12_leads': ["I", "II", "III", "V1", "V2", "V3", "V4", "V5", "V6", "aVR", "aVL", "aVF"]
}


def resolve_config(user_config: dict | None = None, overrides: dict | None = None) -> dict:
    """Merge defaults with optional user-provided config and overrides."""
    merged = DEFAULT_CONFIG.copy()
    if user_config:
        merged.update(user_config)
    if overrides:
        merged.update({k: v for k, v in overrides.items() if v is not None})
    return merged


config = resolve_config()
