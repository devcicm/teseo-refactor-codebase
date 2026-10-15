import json
import tempfile
import unittest
from pathlib import Path
from sys import path
path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import version_audit


class VersionContractTest(unittest.TestCase):
    def test_self_consistency(self):
        self.assertEqual([],version_audit.audit_self())
    def test_metadata_is_prerelease_not_stable(self):
        v=json.loads((version_audit.ROOT/'VERSION.json').read_text())
        self.assertTrue(version_audit.SEMVER.fullmatch(v['release_version']))
        self.assertEqual(v['release_channel'],'release_candidate')
        self.assertIn('-',v['release_version'])
        self.assertNotEqual(v['release_version'],v['protocol_version'])
    def test_canonical_catalog_immutable(self):
        v=json.loads((version_audit.ROOT/'VERSION.json').read_text())
        self.assertEqual(v['criteria']['count'],77)
        self.assertEqual(len(set(version_audit.ID.findall((version_audit.ROOT/v['criteria']['file']).read_text())) - {'N-01'}),77)
    def test_detects_changed_declared_version(self):
        with tempfile.TemporaryDirectory() as td:
            import shutil
            d=Path(td)
            for name in ['SKILL.md','README.md','VERSION.json','CAPABILITIES.json','crear_skill_refactor_v2.5.py']:
                shutil.copy2(version_audit.ROOT/name,d/name)
            for directory in ['references','scripts','tests']:
                shutil.copytree(version_audit.ROOT/directory,d/directory)
            (d/'README.md').write_text('# Teseo — refactor v0.0.0\n')
            self.assertIn('VERSION_MISMATCH_README.md',version_audit.audit_self(d))
    def test_static_project_inventory(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/'package.json').write_text('{"version":"1.2.3","engines":{"node":">=20"}}')
            x=version_audit.inventory_project(root)
            self.assertEqual(x['items'][0]['declared_version'],'1.2.3')
            self.assertEqual(x['items'][0]['effective_runtime'],'UNVERIFIED')
    def test_inventory_ignores_symlink(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as ext:
            root=Path(td);target=Path(ext)/'package.json';target.write_text('{"version":"99.0.0"}')
            (root/'package.json').symlink_to(target)
            self.assertFalse(version_audit.inventory_project(root)['items'])
    def test_semver_rejects_incomplete_version(self):
        self.assertIsNone(version_audit.SEMVER.fullmatch('2.5'))
        self.assertIsNotNone(version_audit.SEMVER.fullmatch('2.5.0-rc.1'))

if __name__=='__main__':unittest.main()
