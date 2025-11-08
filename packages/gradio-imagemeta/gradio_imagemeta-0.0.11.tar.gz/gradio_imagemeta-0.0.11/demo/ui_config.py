from dataclasses import dataclass, field


@dataclass
class ImageSettings:
    """Configuration for image metadata settings."""
    model: str = field(default="", metadata={"label": "Model"})
    f_number: str = field(default="", metadata={"label": "FNumber"})
    iso_speed_ratings: str = field(default="", metadata={"label": "ISOSpeedRatings"})
    s_churn: float = field(
        default=0.0,
        metadata={"component": "slider", "label": "Schurn", "minimum": 0.0, "maximum": 1.0, "step": 0.01},
    )

@dataclass
class PropertyConfig:
    """Root configuration for image properties, including nested image settings."""
    image_settings: ImageSettings = field(default_factory=ImageSettings,  metadata={"label": "Image Settings"})          
    description: str = field(default="", metadata={"label": "Description"})