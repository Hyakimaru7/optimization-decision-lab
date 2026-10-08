import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote
import yaml

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/optimization-modeling-experiments'
spec=importlib.util.spec_from_file_location('installer',ROOT/'tools/install_skill.py')
installer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def anchors(text):
    found=set()
    counts={}
    for heading in re.findall(r'^#{1,6}\s+(.+)$',text,re.M):
        heading=re.sub(r'<[^>]+>','',heading).strip().lower()
        slug=re.sub(r'[^\w\-\s]','',heading).replace(' ','-')
        count=counts.get(slug,0); counts[slug]=count+1
        found.add(slug if count==0 else f'{slug}-{count}')
    found.update(re.findall(r'<a\s+(?:id|name)="([^"]+)"',text))
    return found


class RepositoryTests(unittest.TestCase):
    def test_relative_links_and_fragments(self):
        for md in ROOT.rglob('*.md'):
            if any(part in ('results','.git','__pycache__') for part in md.relative_to(ROOT).parts): continue
            content=md.read_text(encoding='utf-8')
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',content):
                if link.startswith(('http://','https://','mailto:')): continue
                path,_,fragment=unquote(link).partition('#')
                target=(md.parent/path).resolve() if path else md
                self.assertTrue(target.exists(),(md.relative_to(ROOT),link))
                self.assertTrue(target.is_relative_to(ROOT),(md,link))
                if fragment and target.is_file():
                    self.assertIn(fragment,anchors(target.read_text(encoding='utf-8')),(md,link))

    def test_bilingual_pairs_and_metadata(self):
        for a,b in [('README.md','README.zh-CN.md'),('CONTRIBUTING.md','CONTRIBUTING.zh-CN.md'),('docs/EXAMPLES.md','docs/EXAMPLES.zh-CN.md')]:
            self.assertTrue((ROOT/a).is_file()); self.assertTrue((ROOT/b).is_file())
            self.assertIn(Path(b).name,(ROOT/a).read_text()); self.assertIn(Path(a).name,(ROOT/b).read_text())
        en=yaml.safe_load((SKILL/'SKILL.md').read_text().split('---',2)[1])
        zh=yaml.safe_load((SKILL/'SKILL.zh-CN.md').read_text().split('---',2)[1])
        self.assertEqual(en['name'],zh['name']); self.assertEqual(en['metadata'],zh['metadata'])
        self.assertEqual(en['name'],SKILL.name)
        for folder in ['references','assets']:
            for p in (SKILL/folder).glob('*.md'):
                q=SKILL/folder/'zh-CN'/p.name
                self.assertTrue(q.is_file(),p)
                self.assertIn(f'zh-CN/{p.name}',p.read_text()); self.assertIn(f'../{p.name}',q.read_text())

    def test_ci_has_test_and_demo_steps(self):
        config=yaml.safe_load((ROOT/'ci/tests.yml').read_text())
        self.assertEqual(config['permissions']['contents'],'read')
        runs=[step.get('run','') for step in config['jobs']['test']['steps']]
        self.assertTrue(any('unittest discover' in s for s in runs))
        self.assertTrue(any('examples/run_demo.py' in s for s in runs))

    def test_both_language_installations_are_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            for language in ('en','zh-CN'):
                target=installer.install(Path(tmp)/language,language)
                self.assertTrue((target/'scripts/evaluate_information.py').is_file())
                self.assertTrue((target/'references/zh-CN/decision-information.md').is_file())
                self.assertTrue((target/'assets/information-example.json').is_file())
                entry=(target/'SKILL.md').read_text()
                if language=='en':
                    self.assertEqual(entry,(SKILL/'SKILL.md').read_text())
                else:
                    self.assertIn('references/zh-CN/',entry)
                    self.assertIn('(SKILL.en.md)',entry)
                    self.assertEqual((target/'SKILL.en.md').read_bytes(),(SKILL/'SKILL.md').read_bytes())
                    self.assertEqual((target/'agents/openai.yaml').read_bytes(),(SKILL/'agents/openai.zh-CN.yaml').read_bytes())

    def test_existing_installation_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/SKILL.name; target.mkdir(); sentinel=target/'local-changes.txt';sentinel.write_text('preserve me')
            with self.assertRaises(ValueError): installer.install(tmp,'en')
            self.assertEqual(sentinel.read_text(),'preserve me')
            self.assertEqual(list(target.iterdir()),[sentinel])

    def test_demo_runs_from_another_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'artifacts'
            result=subprocess.run([sys.executable,str(ROOT/'examples/run_demo.py'),'--output',str(output)],cwd=tmp,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads((output/'production-comparison.json').read_text())
            self.assertEqual(report['solutions']['corrected_order']['best']['profit'],1040)
            self.assertEqual(report['solutions']['buffered_resources']['best']['profit'],990)
            info=json.loads((output/'information-report.json').read_text())
            self.assertEqual(info['selected_experiment'],'noisy_preproduction_test')


if __name__=='__main__': unittest.main(verbosity=2)
