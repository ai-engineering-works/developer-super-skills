# Integration Testing — CLI Invocation & File I/O

## Testing argparse CLI with subprocess

```python
import subprocess
import pytest
import polars as pl
from pathlib import Path


class TestCLIInvocation:
    """Test the CLI entry point end-to-end via subprocess."""

    @pytest.fixture
    def input_dir(self, tmp_path):
        """Create input CSV files in a temp directory."""
        orders = pl.DataFrame({
            "order_id": [1, 2, 3],
            "customer_id": [101, 102, 101],
            "amount": [50.0, 75.0, 120.0],
        })
        customers = pl.DataFrame({
            "customer_id": [101, 102],
            "name": ["Alice", "Bob"],
        })

        orders.write_csv(tmp_path / "orders.csv")
        customers.write_csv(tmp_path / "customers.csv")
        return tmp_path

    @pytest.fixture
    def output_dir(self, tmp_path):
        out = tmp_path / "output"
        out.mkdir()
        return out

    def test_cli_produces_output_file(self, input_dir, output_dir):
        result = subprocess.run(
            [
                "python", "-m", "app.cli",
                "--orders", str(input_dir / "orders.csv"),
                "--customers", str(input_dir / "customers.csv"),
                "--output", str(output_dir / "enriched.parquet"),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert (output_dir / "enriched.parquet").exists()

    def test_cli_output_has_correct_schema(self, input_dir, output_dir):
        subprocess.run(
            [
                "python", "-m", "app.cli",
                "--orders", str(input_dir / "orders.csv"),
                "--customers", str(input_dir / "customers.csv"),
                "--output", str(output_dir / "enriched.parquet"),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        result = pl.read_parquet(output_dir / "enriched.parquet")
        assert "order_id" in result.columns
        assert "name" in result.columns
        assert result.shape[0] == 3

    def test_cli_fails_on_missing_input_file(self, tmp_path):
        result = subprocess.run(
            [
                "python", "-m", "app.cli",
                "--orders", str(tmp_path / "nonexistent.csv"),
                "--customers", str(tmp_path / "also_missing.csv"),
                "--output", str(tmp_path / "out.parquet"),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_cli_help_shows_usage(self):
        result = subprocess.run(
            ["python", "-m", "app.cli", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "--orders" in result.stdout
        assert "--customers" in result.stdout
        assert "--output" in result.stdout
```

## Testing argparse Parser Directly

```python
import pytest
from app.cli import create_parser, main


class TestArgParser:
    @pytest.fixture
    def parser(self):
        return create_parser()

    def test_parses_required_arguments(self, parser):
        args = parser.parse_args([
            "--orders", "orders.csv",
            "--customers", "customers.csv",
            "--output", "result.parquet",
        ])

        assert args.orders == "orders.csv"
        assert args.customers == "customers.csv"
        assert args.output == "result.parquet"

    def test_parses_optional_delimiter(self, parser):
        args = parser.parse_args([
            "--orders", "orders.csv",
            "--customers", "customers.csv",
            "--output", "out.parquet",
            "--delimiter", "|",
        ])

        assert args.delimiter == "|"

    def test_default_delimiter_is_comma(self, parser):
        args = parser.parse_args([
            "--orders", "o.csv",
            "--customers", "c.csv",
            "--output", "out.parquet",
        ])

        assert args.delimiter == ","

    def test_fails_without_required_args(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parses_format_flag(self, parser):
        args = parser.parse_args([
            "--orders", "o.csv",
            "--customers", "c.csv",
            "--output", "out.csv",
            "--output-format", "csv",
        ])

        assert args.output_format == "csv"
```

## Testing File I/O Functions

```python
import pytest
import polars as pl
from pathlib import Path
from app.io import read_input_file, write_output_file, detect_file_format


class TestReadInputFile:
    def test_reads_csv(self, tmp_path):
        csv_path = tmp_path / "data.csv"
        csv_path.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n")

        result = read_input_file(csv_path)

        assert isinstance(result, pl.DataFrame)
        assert result.shape == (2, 3)
        assert result["name"].to_list() == ["Alice", "Bob"]

    def test_reads_parquet(self, tmp_path):
        parquet_path = tmp_path / "data.parquet"
        pl.DataFrame({"id": [1, 2], "value": [100, 200]}).write_parquet(parquet_path)

        result = read_input_file(parquet_path)

        assert result.shape == (2, 2)
        assert result["id"].to_list() == [1, 2]

    def test_reads_csv_with_custom_delimiter(self, tmp_path):
        tsv_path = tmp_path / "data.tsv"
        tsv_path.write_text("id\tname\n1\tAlice\n2\tBob\n")

        result = read_input_file(tsv_path, delimiter="\t")

        assert result["name"].to_list() == ["Alice", "Bob"]

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_input_file(tmp_path / "missing.csv")

    def test_raises_on_unsupported_format(self, tmp_path):
        xlsx_path = tmp_path / "data.xlsx"
        xlsx_path.write_bytes(b"fake xlsx content")

        with pytest.raises(ValueError, match="Unsupported.*format"):
            read_input_file(xlsx_path)

    def test_reads_csv_with_empty_body(self, tmp_path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("id,name,value\n")

        result = read_input_file(csv_path)
        assert result.shape[0] == 0
        assert result.columns == ["id", "name", "value"]


class TestWriteOutputFile:
    def test_writes_parquet(self, tmp_path):
        df = pl.DataFrame({"id": [1, 2], "value": [100, 200]})
        output_path = tmp_path / "result.parquet"

        write_output_file(df, output_path)

        assert output_path.exists()
        reloaded = pl.read_parquet(output_path)
        assert reloaded.shape == (2, 2)

    def test_writes_csv(self, tmp_path):
        df = pl.DataFrame({"id": [1, 2], "value": [100, 200]})
        output_path = tmp_path / "result.csv"

        write_output_file(df, output_path, format="csv")

        assert output_path.exists()
        reloaded = pl.read_csv(output_path)
        assert reloaded.shape == (2, 2)

    def test_creates_parent_directories(self, tmp_path):
        df = pl.DataFrame({"id": [1]})
        output_path = tmp_path / "sub" / "dir" / "result.parquet"

        write_output_file(df, output_path)

        assert output_path.exists()

    def test_overwrites_existing_file(self, tmp_path):
        output_path = tmp_path / "result.parquet"

        write_output_file(pl.DataFrame({"v": [1]}), output_path)
        write_output_file(pl.DataFrame({"v": [2]}), output_path)

        result = pl.read_parquet(output_path)
        assert result["v"].to_list() == [2]


class TestDetectFileFormat:
    @pytest.mark.parametrize("filename, expected", [
        ("data.csv", "csv"),
        ("data.CSV", "csv"),
        ("data.parquet", "parquet"),
        ("data.pq", "parquet"),
        ("path/to/data.tsv", "csv"),
    ])
    def test_detects_format_from_extension(self, filename, expected):
        assert detect_file_format(Path(filename)) == expected

    def test_raises_on_unknown_extension(self):
        with pytest.raises(ValueError):
            detect_file_format(Path("data.xlsx"))
```

## Testing File Roundtrips

```python
import polars as pl
from polars.testing import assert_frame_equal


class TestFileRoundtrip:
    """Verify data survives write -> read without corruption."""

    def test_csv_roundtrip_preserves_data(self, tmp_path):
        original = pl.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Carol"],
            "amount": [100.50, 200.75, 300.00],
        })

        path = tmp_path / "roundtrip.csv"
        original.write_csv(path)
        reloaded = pl.read_csv(path)

        assert_frame_equal(reloaded, original)

    def test_parquet_roundtrip_preserves_types(self, tmp_path):
        original = pl.DataFrame({
            "id": pl.Series([1, 2, 3], dtype=pl.Int64),
            "ratio": pl.Series([0.1, 0.2, 0.3], dtype=pl.Float64),
            "flag": pl.Series([True, False, True], dtype=pl.Boolean),
        })

        path = tmp_path / "roundtrip.parquet"
        original.write_parquet(path)
        reloaded = pl.read_parquet(path)

        assert_frame_equal(reloaded, original)
        assert reloaded["id"].dtype == pl.Int64
        assert reloaded["ratio"].dtype == pl.Float64
        assert reloaded["flag"].dtype == pl.Boolean

    def test_csv_roundtrip_with_special_characters(self, tmp_path):
        original = pl.DataFrame({
            "name": ["O'Brien", 'Smith, Jr.', 'Line\nBreak'],
            "note": ["has 'quotes'", "has, comma", "has\nnewline"],
        })

        path = tmp_path / "special.csv"
        original.write_csv(path)
        reloaded = pl.read_csv(path)

        assert_frame_equal(reloaded, original)
```

## Quick Reference

| Pattern | Purpose |
|---------|---------|
| `subprocess.run([...], check=True)` | Run CLI and assert exit code |
| `parser.parse_args([...])` | Test argparse directly |
| `tmp_path / "file.csv"` | Isolated file I/O per test |
| `pl.read_csv()` / `pl.read_parquet()` | Verify output contents |
| `assert_frame_equal(a, b)` | Exact DataFrame comparison |
| `result.returncode` | Check CLI success/failure |
| `result.stderr` | Check error messages |
