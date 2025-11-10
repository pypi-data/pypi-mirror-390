from functools import lru_cache
from pathlib import Path
from typing import List
import tomlkit
from polylith_cli.polylith import configuration, repo, toml
poetry_pyproject_template = '[tool.poetry]\nname = "{name}"\nversion = "0.1.0"\n{description}\n{authors}\nlicense = ""\n\npackages = []\n\n[tool.poetry.dependencies]\npython = "{python_version}"\n\n[build-system]\nrequires = ["poetry-core>=1.0.0"]\nbuild-backend = "poetry.core.masonry.api"\n'
poetry_pep621_pyproject_template = '[tool.poetry]\npackages = []\n\n[project]\nname = "{name}"\nversion = "0.1.0"\n{description}\n{authors}\n\nrequires-python = "{python_version}"\n\ndependencies = []\n\n[build-system]\nrequires = ["poetry-core>=1.0.0"]\nbuild-backend = "poetry.core.masonry.api"\n'
hatch_pyproject_template = '[build-system]\nrequires = ["hatchling", "hatch-polylith-bricks"]\nbuild-backend = "hatchling.build"\n\n[project]\nname = "{name}"\nversion = "0.1.0"\n{description}\n{authors}\n\nrequires-python = "{python_version}"\n\ndependencies = []\n\n[tool.hatch.build.targets.wheel]\npackages = ["{namespace}"]\n\n[tool.hatch.build.hooks.polylith-bricks]\n\n[tool.polylith.bricks]\n'
pdm_pyproject_template = '[build-system]\nrequires = ["pdm-backend", "pdm-polylith-bricks"]\nbuild-backend = "pdm.backend"\n\n[project]\nname = "{name}"\nversion = "0.1.0"\n{description}\n{authors}\n\nrequires-python = "{python_version}"\n\ndependencies = []\n\n[tool.polylith.bricks]\n'

def get_project_name(toml_data) -> str:
    if repo.is_pep_621_ready(toml_data):
        return toml_data['project']['name']
    return toml_data['tool']['poetry']['name']

def get_project_name_from_toml(data: dict) -> str:
    try:
        return get_project_name(data['toml'])
    except KeyError as e:
        path = data['path']
        raise KeyError(f'Error in {path}') from e

@lru_cache
def get_toml(path: Path) -> tomlkit.TOMLDocument:
    return toml.read_toml_document(path)

def get_project_files(root: Path) -> dict:
    projects = sorted(root.glob(f'projects/*/{repo.default_toml}'))
    development = Path(root / repo.default_toml)
    proj = {'projects': projects}
    dev = {'development': [development]}
    return {**proj, **dev}

def toml_data(path: Path, project_type: str) -> dict:
    return {'toml': get_toml(path), 'path': path.parent, 'type': project_type}

def get_toml_files(root: Path) -> List[dict]:
    project_files = get_project_files(root)
    proj = [toml_data(p, 'project') for p in project_files['projects']]
    dev = [toml_data(d, 'development') for d in project_files['development']]
    return proj + dev

def get_packages_for_projects(root: Path) -> List[dict]:
    toml_files = get_toml_files(root)
    namespace = configuration.get_namespace_from_config(root)
    return [{'name': get_project_name_from_toml(d), 'packages': toml.get_project_package_includes(namespace, d['toml']), 'path': d['path'], 'type': d['type'], 'deps': toml.get_project_dependencies(d['toml']), 'exclude': toml.collect_configured_exclude_patterns(d['toml'])} for d in toml_files]

def _get_poetry_template(pyproject: dict) -> str:
    if repo.is_pep_621_ready(pyproject):
        return poetry_pep621_pyproject_template
    return poetry_pyproject_template

def guess_project_template(pyproject: dict) -> str:
    if repo.is_poetry(pyproject):
        template = _get_poetry_template(pyproject)
    elif repo.is_hatch(pyproject):
        template = hatch_pyproject_template
    elif repo.is_pdm(pyproject):
        template = pdm_pyproject_template
    else:
        raise ValueError('Failed to guess the type of Project')
    return template

def get_project_template(root: Path) -> str:
    root_pyproject = get_toml(root / repo.default_toml)
    return guess_project_template(root_pyproject)