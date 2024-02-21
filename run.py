import json
import re

import clients
import models
import handlers


def get_env0_environment_variables(
    file_path,
):
    with open(file_path, 'r') as file:
        env0_environment_variables = json.load(file)
        
    return env0_environment_variables

def get_secret_variables_by_prefix(
    variables,
    prefix,
    aws_region,
):
    secrets = {}
    print('Calling Secrets Manager')
    secrets_manager_client = clients.aws_secrets_manager_client.AwsSecretsManagerApiClient(
        region=aws_region,
    )
    print(' Secrets Manager inited')
    print(f'variables: {variables}')
    
    prefix_handler = handlers.prefix_handler.PrefixHandler(prefix)
    for key, value in variables.items():
        if prefix_handler.is_prefixed(value):
            print(
                f'Found secret matching prefix "{prefix}" - {key}:{value}',
            )
            secret_key = prefix_handler.extract_secret_key(
                prefix_embedded_value=value,
            )
            secret_value = secrets_manager_client.get_secret_value_by_key(secret_key)
            secrets[secret_key] = secret_value
            
    return secrets
    
def dump_secrets_into_environment_variables(
    file_path,
    secrets_data,
    env0_environment_variables
):
    print('##########dumping into env0_env')
    
    print(f'ENV VARIABLES {env0_environment_variables}')
    
    print(f'secrets_data {secrets_data}')
    with open(file_path, 'w+') as file:
        for key, value in secrets_data.items():
            file.write(f'{key}: {value}')
            
            
        #     env0_environment_variables[key] = value
        # json.dump(env0_environment_variables, file)
        # dump into env0_env only retrieved secrets


if __name__ == '__main__':
    env0_variables = models.env0_settings.Env0Settings()
    # import pydantic
    # class Env0Variables(pydantic.BaseModel):
    #     env0_env_path:  str = 'env0.env-vars.json'
        
    # env0_variables = Env0Variables()
    
    print(f'########### env0_variables {env0_variables} ############')
    
    print(f'########### env0_variables.env0_env_path {env0_variables.env0_env_path} ############')
    
    print(f'########### env0_variables.env0_env_path_json_file {env0_variables.env0_env_path_json_file} ############')
    
    
    print(f'########### getting env0_environment_variables ############')
    env0_environment_variables = get_env0_environment_variables(
        file_path=env0_variables.env0_env_path_json_file,
    )
    print(f'########### env0_environment_variables {env0_environment_variables}############')
    
    print(f'########### getting retrieved_secrets ############')
    retrieved_secrets = get_secret_variables_by_prefix(
        variables=env0_environment_variables,
        prefix='kosta_ssm',
        aws_region='us-east-1',
    )
    print(f'########### retrieved_secrets {retrieved_secrets} ############')
    
    dump_secrets_into_environment_variables(
        file_path=env0_variables.env0_env_path,
        secrets_data=retrieved_secrets,
        env0_environment_variables=env0_environment_variables,
    )
