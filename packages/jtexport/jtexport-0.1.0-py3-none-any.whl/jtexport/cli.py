from __future__ import annotations

import argparse
from pathlib import Path

from .exporter import ExportConfig, export_file, export_tree


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="jtexport",
        description="Export #export cells from Jupytext (py:percent) files into clean modules",
    )
    p.add_argument("paths", nargs="+", help="Files or directories to process")
    p.add_argument(
        "--outdir", default="exports", help="Output directory root (default: exports)"
    )
    p.add_argument(
        "--project-root",
        default=None,
        help="Project root for relative paths (auto-detect if omitted)",
    )
    p.add_argument(
        "--keep-magics",
        action="store_true",
        help="Keep IPython magics (%) and shell (!) lines",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without writing files",
    )
    p.add_argument(
        "--fail-on-empty",
        action="store_true",
        help="Error if a source has no #export cells",
    )
    return p.parse_args(argv)


def main(argv=None) -> int:
    ns = parse_args(argv)

    cfg = ExportConfig(
        outdir=Path(ns.outdir),
        project_root=Path(ns.project_root) if ns.project_root else None,
        keep_magics=ns.keep_magics,
        dry_run=ns.dry_run,
        fail_on_empty=ns.fail_on_empty,
    )

    exit_code = 0
    for p in ns.paths:
        path = Path(p)
        try:
            if path.is_dir():
                outputs = export_tree(path, cfg)
                for outp, text in outputs:
                    if ns.dry_run and text is not None:
                        print(f"--- {outp} ---\n{text}")
            else:
                outp, text = export_file(path, cfg)
                if ns.dry_run and text is not None:
                    print(f"--- {outp} ---\n{text}")
        except Exception as e:
            exit_code = 1
            print(f"jtexport: error processing {path}: {e}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
