import os
import subprocess
from cli.entities.setting import Settings
from cli.utils.singleton import singleton
import questionary


@singleton
class App:
    version: str = "1.18.1"

    def init(self):
        os.system('printf "\033c"')
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"Press [enter] to start GIT-CLI {self.version}")

        # await Aws().check_session()
        Settings().init()
        self.init_install()

    @staticmethod
    def close():
        os.system('printf "\033c"')
        os.system('cls' if os.name == 'nt' else 'clear')
        exit()

    def init_install(self):
        lokalise_api_token = Settings().config['lokalise']['api_token']
        lokalise_project_id = Settings().config['lokalise']['project_id']
        bitrise_test_token = Settings().config['bitrise']['test']['build_trigger_token']
        bitrise_staging_token = Settings().config['bitrise']['staging']['build_trigger_token']
        bitrise_prod_token = Settings().config['bitrise']['prod']['build_trigger_token']

        try:
            subprocess.run(['git', 'config', '--global', '--unset-all', 'core.editor'], check=True, stdout=True,
                           stderr=True)
        except:
            pass

        try:
            subprocess.run(['git', 'config', '--global', 'core.editor', 'none'], check=True,
                           stdout=True, stderr=True)
        except subprocess.CalledProcessError as e:
            print(e)
            print("Hubo un error al establecer el editor en Git.")

        if lokalise_api_token == '' or lokalise_api_token is None or lokalise_api_token == 'api_token':
            try:
                input_lokalise_api_token = questionary.unsafe_prompt([
                    {
                        'type': 'input',
                        'name': 'api_token',
                        'message': f'Lokalise api token: '
                    }])

                Settings().config['lokalise']['api_token'] = input_lokalise_api_token['api_token']
                Settings().save()

            except KeyboardInterrupt:
                self.close()

        if lokalise_project_id == '' or lokalise_project_id is None or lokalise_project_id == 'project_id':
            try:
                input_lokalise_project_id = questionary.unsafe_prompt([
                    {
                        'type': 'input',
                        'name': 'project_id',
                        'message': f'Lokalise project id: '
                    }])

                Settings().config['lokalise']['project_id'] = input_lokalise_project_id['project_id']
                Settings().save()

            except KeyboardInterrupt:
                self.close()

        if bitrise_test_token == '' or bitrise_test_token is None:
            try:
                input_bitrise_test_token = questionary.unsafe_prompt([
                    {
                        'type': 'input',
                        'name': 'token',
                        'message': f'[TEST] Bitrise token: '
                    }])

                input_bitrise_test_id = questionary.unsafe_prompt([
                    {
                        'type': 'input',
                        'name': 'id',
                        'message': f'[TEST] Bitrise project id: '
                    }])

                Settings().config['bitrise']['test']['build_trigger_token'] = input_bitrise_test_token['token']
                Settings().config['bitrise']['test']['curl_url_id'] = input_bitrise_test_id['id']
                Settings().save()

            except KeyboardInterrupt:
                self.close()

        if bitrise_staging_token == '' or bitrise_staging_token is None:
            try:
                input_bitrise_staging_token = questionary.unsafe_prompt([
                    {
                        'type': 'input',
                        'name': 'token',
                        'message': f'[STAGING] Bitrise token: '
                    }])

                input_bitrise_test_id = questionary.unsafe_prompt([
                    {
                        'type': 'input',
                        'name': 'id',
                        'message': f'[STAGING] Bitrise project id: '
                    }])

                Settings().config['bitrise']['staging']['build_trigger_token'] = input_bitrise_staging_token['token']
                Settings().config['bitrise']['staging']['curl_url_id'] = input_bitrise_test_id['id']
                Settings().save()

            except KeyboardInterrupt:
                self.close()

        if bitrise_prod_token == '' or bitrise_prod_token is None:
            try:
                input_bitrise_prod_token = questionary.unsafe_prompt([
                    {
                        'type': 'input',
                        'name': 'token',
                        'message': f'[PROD] Bitrise token: '
                    }])

                input_bitrise_prod_id = questionary.unsafe_prompt([
                    {
                        'type': 'input',
                        'name': 'id',
                        'message': f'[PROD] Bitrise project id: '
                    }])

                Settings().config['bitrise']['prod']['build_trigger_token'] = input_bitrise_prod_token['token']
                Settings().config['bitrise']['prod']['curl_url_id'] = input_bitrise_prod_id['id']
                Settings().save()

            except KeyboardInterrupt:
                self.close()
