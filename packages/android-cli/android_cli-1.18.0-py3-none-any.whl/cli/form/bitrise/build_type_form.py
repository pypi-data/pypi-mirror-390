import questionary

from cli.utils.configs import BuildType, custom_style


def get_build_type_form():
    try:
        type_choices = [
            BuildType.TEST_DEPLOY_FEATURE.value,
            BuildType.TEST_DEPLOY_PLAYSTORE.value,
            BuildType.STAGING_FEATURE_BRANCH.value,
            BuildType.PROD_DEPLOY_FEATURE.value,
            BuildType.PROD_DEPLOY_PLAYSTORE.value,
        ]
        build_type = questionary.unsafe_prompt(
            {
                'type': 'select',
                'name': 'value',
                'message': 'Build Type?',
                'choices': type_choices,
                'style': custom_style
            }
        )
        return build_type['value']
    except KeyboardInterrupt:
        return -1
