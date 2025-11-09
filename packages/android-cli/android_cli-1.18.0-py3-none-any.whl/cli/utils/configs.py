from enum import Enum

from prompt_toolkit.styles import Style


class BuildType(Enum):
    TEST_DEPLOY_FEATURE = "TEST_DEPLOY_FEATURE"
    TEST_DEPLOY_PLAYSTORE = "TEST_DEPLOY_PLAYSTORE"
    STAGING_FEATURE_BRANCH = "STAGING_FEATURE_BRANCH"
    PROD_DEPLOY_FEATURE = "PROD_DEPLOY_FEATURE"
    PROD_DEPLOY_PLAYSTORE = "PROD_DEPLOY_PLAYSTORE"

    @staticmethod
    def from_string(s):
        for build_type in BuildType:
            if build_type.value == s:
                return build_type
        raise ValueError(f"BuildType '{s}' unknown.")


custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),  # Color y estilo para el símbolo de la pregunta
    ('question', 'bold'),  # Estilo para la pregunta
    ('selected', 'fg:#cc5454 bold'),  # Color para la opción seleccionada
    ('pointer', 'fg:#673ab7 bold'),  # Color y estilo para el puntero
    ('highlighted', 'fg:#2ecc71 bold'),  # Color y estilo para la opción destacada
    # ('answer', 'fg:#f44336 bold'),  # Color y estilo para la respuesta
    ('text', ''),  # Estilo para el texto normal
])
