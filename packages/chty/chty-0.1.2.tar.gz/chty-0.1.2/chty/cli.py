"""CLI interface for chty."""

from __future__ import annotations

from pathlib import Path

import typer
from typing_extensions import Annotated

from chty import __version__
from chty.codegen import generate_file
from chty.parser import parse_sql_file
from chty.schema import get_result_schema
from chty.validator import validate_file

app = typer.Typer(
    help="Type-safe ClickHouse query parameter and result codegen",
    no_args_is_help=True,
)


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo(f"chty version {__version__}")
        raise typer.Exit()


@app.callback()
def common_options(
    ctx: typer.Context,
    _version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            help="Show detailed output",
        ),
    ] = False,
):
    """Type-safe ClickHouse query parameter and result codegen."""
    ctx.obj = {"verbose": verbose}


@app.command()
def generate(
    ctx: typer.Context,
    paths: Annotated[
        list[Path],
        typer.Argument(
            help="SQL files or directories containing SQL files",
            exists=True,
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
            help="ClickHouse connection URL to generate result types (clickhouse://user:pass@host:port or https://user:pass@host:port for ClickHouse Cloud)",
        ),
    ] = None,
):
    """
    Generate typed Python code from SQL files with ClickHouse parameterized queries.

    Use --db-url to generate both parameter and result types.
    Without --db-url: Only parameter types are generated.

    Examples:
        # Process all SQL files in a directory
        chty generate queries/ -o generated/ --db-url clickhouse://admin:admin@localhost:8123

        # ClickHouse Cloud
        chty generate queries/ -o generated/ --db-url https://user:pass@abc123.clickhouse.cloud:8443

        # Process specific files
        chty generate queries/users.sql queries/events.sql -o generated/
    """
    verbose = ctx.obj["verbose"]

    # Expand directories to find .sql files
    sql_files = []
    for path in paths:
        if path.is_dir():
            sql_files.extend(sorted(path.glob("*.sql")))
        else:
            sql_files.append(path)

    if not sql_files:
        typer.echo("No SQL files found", err=True)
        raise typer.Exit(1)

    output.mkdir(parents=True, exist_ok=True)

    generated_files = []

    for sql_file in sql_files:
        try:
            if verbose:
                typer.echo(f"Processing {sql_file}...")

            query, parameters = parse_sql_file(sql_file)

            if verbose and parameters:
                param_names = ", ".join(p.name for p in parameters)
                typer.echo(f"  Parameters: {param_names}")

            result_schema = None
            if db_url:
                if verbose:
                    typer.echo("  Introspecting result schema from ClickHouse...")
                result_schema = get_result_schema(query, db_url)
                if verbose and result_schema:
                    result_cols = ", ".join(col_name for col_name, _ in result_schema)
                    typer.echo(f"  Result columns: {result_cols}")

            if not parameters and not result_schema:
                typer.echo(
                    f"⚠️  {sql_file}: No parameters or result schema",
                    err=True,
                )
                typer.echo("   Tip: Use --db-url to generate result types", err=True)
                continue

            output_file = generate_file(
                sql_file, output, query, parameters, result_schema
            )

            typer.echo(f"✓ {output_file}")

            generated_files.append(output_file)

        except Exception as e:
            typer.echo(f"✗ {sql_file}: {e}", err=True)
            raise typer.Exit(1)

    if generated_files:
        if db_url:
            typer.echo(f"\n✓ Generated {len(generated_files)} file(s) in {output}/")
        else:
            typer.echo(
                f"\n✓ Generated {len(generated_files)} file(s) (parameter types only) in {output}/"
            )
            typer.echo("💡 Tip: Use --db-url to also generate result types")
    else:
        typer.echo("\n⚠️  No files were generated", err=True)
        raise typer.Exit(1)


@app.command()
def validate(
    ctx: typer.Context,
    paths: Annotated[
        list[Path],
        typer.Argument(
            help="Generated Python files or directory containing generated files",
            exists=True,
        ),
    ],
    db_url: Annotated[
        str,
        typer.Option(
            "--db-url",
            help="ClickHouse connection URL (clickhouse://user:pass@host:port or https://user:pass@host:port for ClickHouse Cloud)",
        ),
    ],
):
    """
    Validate generated code against current ClickHouse schema.

    This checks for schema drift by comparing the generated TypedDict
    with the actual schema from ClickHouse.

    Examples:
        # Validate all files in a directory
        chty validate generated/ --db-url clickhouse://admin:admin@localhost:8123

        # ClickHouse Cloud
        chty validate generated/ --db-url https://user:pass@abc123.clickhouse.cloud:8443

        # Validate specific files
        chty validate generated/users.py generated/events.py --db-url clickhouse://localhost:8123
    """
    # Expand directories to find .py files
    generated_files = []
    for path in paths:
        if path.is_dir():
            generated_files.extend(sorted(path.glob("*.py")))
        else:
            generated_files.append(path)

    if not generated_files:
        typer.echo("No Python files found", err=True)
        raise typer.Exit(1)

    all_valid = True
    results = []

    for py_file in generated_files:
        is_valid, errors = validate_file(py_file, db_url)

        if is_valid:
            typer.echo(f"✓ {py_file}")
            results.append((py_file, True, []))
        else:
            typer.echo(f"✗ {py_file}:", err=True)
            for error in errors:
                typer.echo(f"  - {error}", err=True)
            results.append((py_file, False, errors))
            all_valid = False

    # Summary
    valid_count = sum(1 for _, valid, _ in results if valid)
    invalid_count = len(results) - valid_count

    if all_valid:
        typer.echo(f"\n✓ All {len(results)} file(s) are valid!")
        raise typer.Exit(0)
    else:
        typer.echo(
            f"\n✗ {invalid_count} file(s) failed validation, {valid_count} passed",
            err=True,
        )
        raise typer.Exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
