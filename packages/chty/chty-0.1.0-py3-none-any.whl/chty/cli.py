"""CLI interface for chty."""

from __future__ import annotations

from pathlib import Path

import typer
from typing_extensions import Annotated

from chty.codegen import generate_file
from chty.parser import parse_sql_file
from chty.schema import get_result_schema
from chty.validator import validate_file

app = typer.Typer(
    help="Type-safe ClickHouse query parameter and result codegen",
    no_args_is_help=True,
)


@app.command()
def generate(
    sql_files: Annotated[
        list[Path],
        typer.Argument(
            help="SQL files to process (supports glob patterns)",
            exists=True,
            dir_okay=False,
        ),
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Output directory for generated Python files",
        ),
    ] = Path("generated"),
    db_url: Annotated[
        str | None,
        typer.Option(
            "--db-url",
            help="[RECOMMENDED] ClickHouse connection URL for full type safety (e.g., clickhouse://user:pass@host:port)",
        ),
    ] = None,
):
    """
    Generate typed Python code from SQL files with ClickHouse parameterized queries.

    Recommended: Use --db-url for full type safety (parameters + results).
    Without --db-url: Only generates parameter types.

    Examples:
        # Full type safety (recommended)
        chty generate queries/*.sql -o generated/ --db-url clickhouse://admin:admin@localhost:8123

        # Parameter types only (fallback when no DB access)
        chty generate queries/*.sql -o generated/
    """
    if not sql_files:
        typer.echo("No SQL files provided", err=True)
        raise typer.Exit(1)

    output.mkdir(parents=True, exist_ok=True)

    generated_files = []

    for sql_file in sql_files:
        try:
            typer.echo(f"Processing {sql_file}...")

            query, parameters = parse_sql_file(sql_file)

            if not parameters:
                typer.echo(f"  ⚠️  No parameters found in {sql_file}", err=True)
                continue

            result_schema = None
            if db_url:
                typer.echo("  → Introspecting result schema from ClickHouse...")
                result_schema = get_result_schema(query, db_url)
                result_cols = ", ".join(col_name for col_name, _ in result_schema)
                typer.echo(
                    f"  → Found {len(result_schema)} result columns: {result_cols}"
                )

            output_file = generate_file(
                sql_file, output, query, parameters, result_schema
            )

            param_names = ", ".join(p.name for p in parameters)
            result_info = (
                f", results: {len(result_schema)} cols" if result_schema else ""
            )
            typer.echo(
                f"  ✓ Generated {output_file} (params: {param_names}{result_info})"
            )

            generated_files.append(output_file)

        except Exception as e:
            typer.echo(f"  ✗ Error processing {sql_file}: {e}", err=True)
            raise typer.Exit(1)

    if generated_files:
        if db_url:
            typer.echo(
                f"\n✓ Generated {len(generated_files)} file(s) with full type safety in {output}/"
            )
        else:
            typer.echo(
                f"\n✓ Generated {len(generated_files)} file(s) with parameter types in {output}/"
            )
            typer.echo(
                "💡 Tip: Add --db-url for result type safety and validation support"
            )
    else:
        typer.echo("\n⚠️  No files were generated", err=True)
        raise typer.Exit(1)


@app.command()
def validate(
    generated_files: Annotated[
        list[Path],
        typer.Argument(
            help="Generated Python files to validate",
            exists=True,
            dir_okay=False,
        ),
    ],
    db_url: Annotated[
        str,
        typer.Option(
            "--db-url",
            help="ClickHouse connection URL (e.g., clickhouse://user:pass@host:port)",
        ),
    ],
):
    """
    Validate generated code against current ClickHouse schema.

    This checks for schema drift by comparing the generated TypedDict
    with the actual schema from ClickHouse.

    Example:
        chty validate generated/*.py --db-url clickhouse://admin:admin@localhost:8123
    """
    if not generated_files:
        typer.echo("No files provided", err=True)
        raise typer.Exit(1)

    typer.echo(f"Validating {len(generated_files)} file(s) against ClickHouse...\n")

    all_valid = True
    results = []

    for py_file in generated_files:
        typer.echo(f"Checking {py_file}...")
        is_valid, errors = validate_file(py_file, db_url)

        if is_valid:
            typer.echo("  ✓ Valid\n")
            results.append((py_file, True, []))
        else:
            typer.echo("  ✗ Validation failed:", err=True)
            for error in errors:
                typer.echo(f"    - {error}", err=True)
            typer.echo("")
            results.append((py_file, False, errors))
            all_valid = False

    # Summary
    valid_count = sum(1 for _, valid, _ in results if valid)
    invalid_count = len(results) - valid_count

    if all_valid:
        typer.echo(f"✓ All {len(results)} file(s) are valid!")
        raise typer.Exit(0)
    else:
        typer.echo(
            f"✗ {invalid_count} file(s) failed validation, {valid_count} passed",
            err=True,
        )
        raise typer.Exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
