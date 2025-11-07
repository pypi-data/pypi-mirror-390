__version__ = '0.1.0'


import os
from yaml import safe_load
from ansible_runner import run_command


USER_HOME_DIR = os.path.expanduser('~')
ANSIBLE_DIR   = os.path.join(USER_HOME_DIR, '.ansible')


def ensure_galaxy_dependencies(galaxy_file_path):
    required_collections = []
    required_roles = []
    tmp_collections = []
    tmp_roles = []

    with open(galaxy_file_path, 'r') as stream:
        tmp_collections = safe_load(stream)['collections']
    with open(galaxy_file_path, 'r') as stream:
        tmp_roles       = safe_load(stream)['roles']

    for tmp_dict in tmp_collections:
        required_collections.append(tmp_dict['name'])
    for tmp_dict in tmp_roles:
        required_roles.append(tmp_dict['name'])

    installed_collections = run_command(
        executable_cmd='ansible-galaxy',
        cmdline_args=[
            'collection',
            'list',
            '--collections-path',
            ANSIBLE_DIR,
        ],
        quiet=True
    )[0]
    installed_roles = run_command(
        executable_cmd='ansible-galaxy',
        cmdline_args=[
            'role',
            'list',
            '--roles-path',
            ANSIBLE_DIR,
        ],
        quiet=True
    )[0]

    missing_collections = []
    for required in required_collections:
        if required not in installed_collections:
            missing_collections.append(required)
    if len(missing_collections) == 0:
        result = 0
    else:
        result = install_galaxy_dependencies(
            missing_collections,
            'collection'
        )

    if result != 0:
        return result

    missing_roles = []
    for required in required_roles:
        if required not in installed_roles:
            missing_roles.append(required)
    if len(missing_roles) == 0:
        return 0
    else:
        return install_galaxy_dependencies(
            missing_roles,
            'role'
        )


def install_galaxy_dependencies(dependencies, dependency_type):
    plural = f'{dependency_type}s'

    print(f'\nInstalling Ansible Galaxy {plural} into {ANSIBLE_DIR} ...')
    run_command(
        executable_cmd='ansible-galaxy',
        cmdline_args=[dependency_type, 'install'] + dependencies,
    )
    print('\n... {} installed.'.format(plural))
    return 0
