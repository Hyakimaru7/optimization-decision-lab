#!/usr/bin/env python3
"""Install this skill into a chosen skills directory without replacing an existing skill."""
import argparse
from pathlib import Path
import shutil
import sys


def install(destination, language):
    if language not in ('en', 'zh-CN'):
        raise ValueError('language must be en or zh-CN')
    source=Path(__file__).resolve().parents[1]/'skills/optimization-modeling-experiments'
    parent=Path(destination).expanduser().resolve()
    target=parent/source.name
    if target.exists() or target.is_symlink():
        raise ValueError(f'Existing skill was not overwritten: {target}; choose a fresh destination or move the old installation yourself')
    parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    if language=='zh-CN':
        shutil.copy2(target/'SKILL.md',target/'SKILL.en.md')
        localized=(target/'SKILL.zh-CN.md').read_text(encoding='utf-8').replace('(SKILL.md)','(SKILL.en.md)')
        (target/'SKILL.md').write_text(localized,encoding='utf-8')
        (target/'SKILL.zh-CN.md').write_text(localized,encoding='utf-8')
        shutil.copy2(target/'agents/openai.zh-CN.yaml',target/'agents/openai.yaml')
    return target


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=('en','zh-CN'),default='en')
    parser.add_argument('--destination',type=Path,default=Path.home()/'.agents/skills',help='Parent skills directory; default: ~/.agents/skills')
    args=parser.parse_args()
    try:
        target=install(args.destination,args.language)
        print(f'Installed {args.language} skill at {target}')
        return 0
    except (OSError,ValueError) as error:
        print(str(error),file=sys.stderr)
        return 2


if __name__=='__main__': sys.exit(main())
