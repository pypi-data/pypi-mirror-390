from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, HttpUrl  # <-- Importe o Field

from lacrei_models.utils.template_context_models import static_path_to_url


class BaseEmailContext(PydanticBaseModel):
    icon_png_url: HttpUrl | str = Field(
        default_factory=lambda: static_path_to_url("images/icon.png")
    )
    Ilustration_e_mail_svg_url: HttpUrl | str = Field(
        default_factory=lambda: static_path_to_url("images/Ilustration-e-mail.svg")
    )
    facebook_svg_url: HttpUrl | str = Field(
        default_factory=lambda: static_path_to_url("images/facebook.svg")
    )
    instagram_svg_url: HttpUrl | str = Field(
        default_factory=lambda: static_path_to_url("images/instagram.svg")
    )
    linkedin_svg_url: HttpUrl | str = Field(
        default_factory=lambda: static_path_to_url("images/linkedin.svg")
    )
    e_mail_svg_url: HttpUrl | str = Field(
        default_factory=lambda: static_path_to_url("images/e-mail.svg")
    )


def get_base_email_context() -> dict:
    """Retorna o dicionário de contexto base do e-mail."""
    return BaseEmailContext().model_dump(mode="json")
