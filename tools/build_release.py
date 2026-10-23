"""Build and verify the portable delivery using only Python's standard library.

Run from the project: python tools/build_release.py
No virtual environment, AWS configuration, credentials or Git metadata is bundled.
"""

import ast
import hashlib
from pathlib import Path
import re
import zipfile


def build():
    root = Path(__file__).resolve().parents[1]
    tree = ast.parse((root / 'app.py').read_text(encoding='utf-8'))
    version = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == 'VERSION' for target in node.targets)
    )
    root_files = [
        'app.py', 'requirements.txt', 'iniciar.ps1', '.gitignore', '.gitattributes', 'LICENSE',
        'README.md', 'README_EN.md', 'DEMO.md', 'DEMO_EN.md', 'AWS_SETUP.md',
        'ENTREGA.md', 'CIERRE.md', 'SUBMISSION_EN.md', 'FEEDBACK_EN.md', 'iam-policy.json',
    ]
    paths = [root / name for name in root_files]
    for folder in ('tests', 'tools', 'evidencias', 'demo'):
        paths.extend(path for path in (root / folder).rglob('*')
                     if path.is_file() and '__pycache__' not in path.parts
                     and path.suffix.lower() not in ('.pyc', '.pyo'))
    paths = sorted(set(paths), key=lambda path: path.relative_to(root).as_posix())
    secrets = [re.compile(p) for p in (
        r'(?:AKIA|ASIA)[A-Z0-9]{16}', r'gh[pousr]_[A-Za-z0-9]{24,}',
        r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    )]
    for path in paths:
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f'Invalid source path: {path.name}')
        if path.suffix in ('.py', '.md', '.json', '.txt', '.ps1', '.yml', '.yaml'):
            content = path.read_text(encoding='utf-8-sig')
            if any(pattern.search(content) for pattern in secrets):
                raise ValueError(f'Possible credential detected in {path.name}; package not created.')
    manifest = ''.join(
        f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root).as_posix()}\n'
        for path in paths
    )
    manifest_path = root / 'SHA256SUMS.txt'
    manifest_path.write_text(manifest, encoding='utf-8')
    output = root / 'entrega'
    output.mkdir(exist_ok=True)
    archive = output / f'Aetheris-AI-MVP-{version}.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in paths + [manifest_path]:
            bundle.write(path, arcname='Aetheris-AI/' + path.relative_to(root).as_posix())
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert len(bundle.namelist()) == len(paths) + 1
        for line in manifest.splitlines():
            expected, name = line.split('  ', 1)
            assert hashlib.sha256(bundle.read('Aetheris-AI/' + name)).hexdigest() == expected
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(archive.suffix + '.sha256').write_text(
        f'{digest}  {archive.name}\n', encoding='utf-8')
    print(f'Verified package: {archive.name}; files={len(paths)+1}; bytes={archive.stat().st_size}')
    print(f'SHA-256: {digest}')
    return archive


if __name__ == '__main__':
    build()
