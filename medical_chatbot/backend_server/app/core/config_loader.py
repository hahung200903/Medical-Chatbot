import yaml

with open('system_prompts.yaml', 'r', encoding='utf-8') as file:
    system_prompt = yaml.safe_load(file)

with open('config.yaml', 'r', encoding='utf-8') as file:
    system_config = yaml.safe_load(file)

__all__ = ['system_prompt', 'system_config']



