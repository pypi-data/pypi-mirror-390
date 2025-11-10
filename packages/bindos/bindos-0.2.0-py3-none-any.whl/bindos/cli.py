import csv
import argparse
from .core import curvature_score, stabilize
from .pro_engine import stabilize_pro


def load_column(path: str, col_index: int, max_rows: int | None) -> list[float]:
    values: list[float] = []
    with open(path, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        print("Header:", header)
        for i, row in enumerate(reader):
            if max_rows is not None and max_rows > 0 and i >= max_rows:
                break
            try:
                values.append(float(row[col_index]))
            except (ValueError, IndexError):
                continue
    return values


def write_stabilized_csv(
    input_path: str,
    output_path: str,
    col_index: int,
    stabilized: list[float],
) -> None:
    with open(input_path, "r", newline="") as f_in, open(
        output_path, "w", newline=""
    ) as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        header = next(reader, None)
        if header is None:
            return
        if 0 <= col_index < len(header):
            base_name = header[col_index]
        else:
            base_name = f"col_{col_index}"
        new_header = list(header)
        new_header.append(f"{base_name}_stabilized")
        writer.writerow(new_header)
        for i, row in enumerate(reader):
            new_row = list(row)
            if i < len(stabilized):
                new_row.append(stabilized[i])
            else:
                new_row.append("")
            writer.writerow(new_row)


def main() -> None:
    parser = argparse.ArgumentParser(prog="bindos-run")
    parser.add_argument("path", type=str)
    parser.add_argument("--column-index", type=int, default=1)
    parser.add_argument("--max-rows", type=int, default=100)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--alpha", type=float, default=0.4)
    parser.add_argument("--mode", type=str, default="core")
    parser.add_argument("--output", type=str, default="")
    args = parser.parse_args()

    series = load_column(args.path, args.column_index, args.max_rows)
    print("Loaded points:", len(series))
    if len(series) < 3:
        print("Not enough points for curvature")
        return

    if args.mode == "core":
        res = stabilize(series, steps=args.steps, alpha=args.alpha)
    elif args.mode == "pro":
        res = stabilize_pro(series, steps=args.steps, kappa=args.alpha)
    else:
        raise ValueError("mode must be 'core' or 'pro'")

    print("Initial curvature:", res["curvature_initial"])
    print("Stabilized curvature:", res["curvature_stabilized"])
    print("First 5 initial:", res["initial"][:5])
    print("First 5 stabilized:", res["stabilized"][:5])

    if args.output:
        write_stabilized_csv(
            args.path,
            args.output,
            args.column_index,
            res["stabilized"],
        )
        print("Wrote stabilized CSV to:", args.output)

