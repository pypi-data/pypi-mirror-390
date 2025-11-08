import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

def analyze_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Girdi bulunamadı: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Bir dosya bekleniyordu, klasör verildi: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return {
        "file": str(path),
        "size_bytes": path.stat().st_size,
        "line_count": len(lines),
        "char_count": len(text),
        "created": datetime.fromtimestamp(path.stat().st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
    }

def run_pipeline(input_path: Path, output_path: Optional[Path], overwrite: bool) -> Path:
    result = analyze_file(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(input_path.suffix + ".report.json")
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Çıktı zaten var, --overwrite kullanın: {output_path}")
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path

def cmd_analyze(args: argparse.Namespace) -> int:
    try:
        result = analyze_file(args.input)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Dosya: {result['file']}")
            print(f"Boyut (B): {result['size_bytes']}")
            print(f"Satır: {result['line_count']}")
            print(f"Karakter: {result['char_count']}")
            print(f"Oluşturulma: {result['created']}")
            print(f"Güncellenme: {result['modified']}")
        return 0
    except Exception as e:
        print(f"Hata: {e}", file=sys.stderr)
        return 1

def cmd_run(args: argparse.Namespace) -> int:
    try:
        out = run_pipeline(args.input, args.output, args.overwrite)
        print(f"Kaydedildi: {out}")
        return 0
    except Exception as e:
        print(f"Hata: {e}", file=sys.stderr)
        return 1

def cmd_version(args: argparse.Namespace) -> int:
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            v = version("epi-clock")
        except PackageNotFoundError:
            v = "0.1.0"
    except Exception:
        v = "0.1.0"
    print(v)
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="epi-clock",
        description="Epi Clock Prototype CLI",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Ayrıntılı çıktı")

    sub = parser.add_subparsers(dest="command", required=True)

    p_an = sub.add_parser("analyze", help="Girdi dosyasını analiz et ve sonucu ekrana yaz")
    p_an.add_argument("input", type=Path, help="Analiz edilecek dosya yolu")
    p_an.add_argument("--json", action="store_true", help="Sonucu JSON formatında yazdır")
    p_an.set_defaults(func=cmd_analyze)

    p_run = sub.add_parser("run", help="Analizi çalıştır ve sonucu dosyaya kaydet")
    p_run.add_argument("input", type=Path, help="Girdi dosyası")
    p_run.add_argument("-o", "--output", type=Path, help="Çıktı dosyası (varsayılan: *.report.json)")
    p_run.add_argument("--overwrite", action="store_true", help="Var olan çıktının üzerine yaz")
    p_run.set_defaults(func=cmd_run)

    p_ver = sub.add_parser("version", help="Sürüm bilgisini göster")
    p_ver.set_defaults(func=cmd_version)

    return parser

def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "verbose", False):
        print(f"[{datetime.now().isoformat()}] Komut: {args.command}", file=sys.stderr)
    rc = args.func(args)
    sys.exit(rc)
