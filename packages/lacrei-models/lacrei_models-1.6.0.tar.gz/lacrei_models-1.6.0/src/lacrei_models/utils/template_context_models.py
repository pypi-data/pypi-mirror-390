import base64
import os

from django.conf import settings
from django.templatetags.static import static
from pydantic import BaseModel as PydanticBaseModel


def static_path_to_url(path):
    return static(path)


def get_static_email_url(static_path):
    """
    Gera URLs absolutas para emails, funcionando em qualquer ambiente.
    Para SVGs, usa data URI (incorporado no HTML).
    Para outros arquivos, tenta construir URL absoluta.
    """
    # Para SVGs, usar data URI (mais confiável em emails)
    if static_path.endswith(".svg"):
        return svg_to_data_uri(static_path)

    # Para outros arquivos, tentar construir URL absoluta
    static_url = static(static_path)

    # Se temos STATIC_EMAIL_PREFIX configurado, usar
    if hasattr(settings, "STATIC_EMAIL_PREFIX") and settings.STATIC_EMAIL_PREFIX:
        return f"{settings.STATIC_EMAIL_PREFIX.rstrip('/')}{static_url}"

    # Senão, retornar relativa (fallback)
    return static_url


def svg_to_data_uri(svg_path):
    """
    Converte SVG para data URI - funciona em qualquer ambiente.
    """
    try:
        # Remover 'images/' do início se estiver presente
        clean_path = (
            svg_path.replace("images/", "")
            if svg_path.startswith("images/")
            else svg_path
        )
        full_path = os.path.join(
            settings.BASE_DIR, "notification", "static", "images", clean_path
        )

        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                svg_content = f.read()

            # Encode em base64
            svg_bytes = svg_content.encode("utf-8")
            svg_b64 = base64.b64encode(svg_bytes).decode("ascii")
            return f"data:image/svg+xml;base64,{svg_b64}"
    except Exception:
        pass

    # Fallback para URL estática se der erro
    return static(svg_path)


class BaseTemplateContext(PydanticBaseModel):
    """
    Esse modelo Pydantic é usado como base para fornecer um valor que controla
    se o contexto está relacionado a um template que herda de `base_email.html`
    (o arquivo encontra-se dentro do app `notification`).

    O racional é que muitos dos templates herdam de `base_email.html` e
    o valor do contexto utilizado para renderizar os templates derivados é
    praticamente estático, dependendo somente das configurações de `settings` do
    ambiente em que o código está rodando.

    Logo esse mecanismo evita que os dados pertinentes à renderização de
    dados estáticos sejam armazenados no banco de dados sem necessidade.
    Porém, para a renderização do email, tais dados são necessários.

    O uso do campo é feito em `notification.services.NotificationService.send`
    """

    has_base_email_context: bool
    _template_prefix: str = ""

    @classmethod
    def convert_from_pickled_context(cls, pickled_context: dict) -> dict:
        assert cls._template_prefix

        kwargs_after_conversion = (
            cls._convert_from_pickled_content_to_this_model_args(pickled_context) or {}
        )
        validated_instance = cls(**kwargs_after_conversion)
        json_dict = validated_instance.model_dump(mode="json")
        json_dict.pop("has_base_email_context", False)

        return json_dict

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        cls, pickled_context: dict
    ) -> dict:  # pragma: no cover
        raise NotImplementedError()


class WithBaseEmailContext(BaseTemplateContext):
    has_base_email_context: bool = True


class WithoutBaseEmailContext(BaseTemplateContext):
    has_base_email_context: bool = False


def convert_pickled_context_to_json_context(template_prefix, pickled_context) -> dict:
    from utils import TEMPLATE_PREFIX_TO_PYDANTIC_MODEL

    pydantic_model = TEMPLATE_PREFIX_TO_PYDANTIC_MODEL.get(template_prefix, None)

    if pydantic_model is None:  # pragma: no cover
        return {}

    return pydantic_model.convert_from_pickled_context(pickled_context)
