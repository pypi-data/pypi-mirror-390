"""
Command-line interface for vCon WTF.

This module provides the main CLI entry point for converting transcript formats
and managing WTF documents.
"""

import json
from pathlib import Path
from typing import Any, Optional, Union

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..core.validator import validate_wtf_document
from ..providers.assemblyai import AssemblyAIConverter
from ..providers.base import BaseProviderConverter
from ..providers.canary import CanaryConverter
from ..providers.deepgram import DeepgramConverter
from ..providers.parakeet import ParakeetConverter
from ..providers.rev_ai import RevAIConverter
from ..providers.whisper import WhisperConverter
from .cross_provider import cross_provider

console = Console()


def _get_converter(provider: str) -> Optional[Any]:
    """Get converter instance for the specified provider."""
    provider = provider.lower()

    if provider == "whisper":
        return WhisperConverter()
    elif provider == "deepgram":
        return DeepgramConverter()
    elif provider == "assemblyai":
        return AssemblyAIConverter()
    elif provider == "rev-ai":
        return RevAIConverter()
    elif provider == "canary":
        return CanaryConverter()
    elif provider == "parakeet":
        return ParakeetConverter()
    # TODO: Add other providers as they are implemented

    return None


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """
    vCon WTF - Convert transcript JSONs to/from IETF World Transcription Format.

    This tool provides conversion between various transcription provider formats
    and the standardized WTF format, with full vCon integration support.
    """
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--provider",
    "-p",
    required=True,
    help="Transcription provider (whisper, deepgram, assemblyai, etc.)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: input_file.wtf.json)",
)
@click.option("--validate/--no-validate", default=True, help="Validate output WTF document")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def to_wtf(
    input_file: str, provider: str, output: Optional[str], validate: bool, verbose: bool
) -> None:
    """Convert provider-specific transcript to WTF format."""
    if verbose:
        console.print(f"[blue]Converting {input_file} from {provider} to WTF format...[/blue]")

    try:
        # Load input data
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)

        # Get converter based on provider
        converter = _get_converter(provider)
        if not converter:
            console.print(f"[red]Error: Unsupported provider '{provider}'[/red]")
            console.print("Use 'vcon-wtf providers' to see supported providers")
            return

        # Convert to WTF
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            task = progress.add_task("Converting...", total=None)
            wtf_doc = converter.convert_to_wtf(input_data)
            progress.update(task, description="Conversion complete")

        # Validate if requested
        if validate:
            is_valid, errors = validate_wtf_document(wtf_doc)
            if not is_valid:
                console.print(f"[red]Validation failed:[/red]")
                for error in errors:
                    console.print(f"  - {error}")
                return

        # Determine output file
        if not output:
            input_path = Path(input_file)
            output = str(input_path.with_suffix(".wtf.json"))

        # Save output
        with open(output, "w", encoding="utf-8") as f:
            json.dump(wtf_doc.model_dump(), f, indent=2, ensure_ascii=False)

        console.print(f"[green]Successfully converted to WTF format: {output}[/green]")
        if verbose:
            console.print(f"[blue]Transcript: {wtf_doc.transcript.text[:100]}...[/blue]")
            console.print(f"[blue]Duration: {wtf_doc.transcript.duration}s[/blue]")
            console.print(f"[blue]Segments: {len(wtf_doc.segments)}[/blue]")
            console.print(f"[blue]Confidence: {wtf_doc.transcript.confidence:.2f}[/blue]")

    except FileNotFoundError:
        console.print(f"[red]Error: Input file '{input_file}' not found[/red]")
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON in input file: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error during conversion: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--provider",
    "-p",
    required=True,
    help="Target provider format (whisper, deepgram, assemblyai, etc.)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: input_file.{provider}.json)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def from_wtf(input_file: str, provider: str, output: Optional[str], verbose: bool) -> None:
    """Convert WTF format to provider-specific transcript."""
    if verbose:
        console.print(f"[blue]Converting {input_file} from WTF to {provider} format...[/blue]")

    try:
        # Load input data
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)

        # Validate input WTF document
        from ..core.models import WTFDocument

        wtf_doc = WTFDocument.model_validate(input_data)

        # Get converter based on provider
        converter = _get_converter(provider)
        if not converter:
            console.print(f"[red]Error: Unsupported provider '{provider}'[/red]")
            console.print("Use 'vcon-wtf providers' to see supported providers")
            return

        # Convert from WTF
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            task = progress.add_task("Converting...", total=None)
            provider_data = converter.convert_from_wtf(wtf_doc)
            progress.update(task, description="Conversion complete")

        # Determine output file
        if not output:
            input_path = Path(input_file)
            output = str(input_path.with_suffix(f".{provider}.json"))

        # Save output
        with open(output, "w", encoding="utf-8") as f:
            json.dump(provider_data, f, indent=2, ensure_ascii=False)

        console.print(f"[green]Successfully converted to {provider} format: {output}[/green]")
        if verbose:
            console.print(f"[blue]Provider: {provider}[/blue]")
            console.print(f"[blue]Output keys: {list(provider_data.keys())}[/blue]")

    except FileNotFoundError:
        console.print(f"[red]Error: Input file '{input_file}' not found[/red]")
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON in input file: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error during conversion: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def validate(input_file: str, verbose: bool) -> None:
    """Validate WTF document format."""
    if verbose:
        console.print(f"[blue]Validating WTF document: {input_file}[/blue]")

    # TODO: Implement validation logic
    console.print(f"[yellow]WTF validation not yet implemented[/yellow]")
    console.print(f"[yellow]Input file: {input_file}[/yellow]")


@main.command()
@click.option(
    "--input-dir",
    "-i",
    type=click.Path(exists=True, file_okay=False),
    required=True,
    help="Input directory",
)
@click.option("--output-dir", "-o", type=click.Path(), required=True, help="Output directory")
@click.option("--provider", "-p", help="Provider format (auto-detect if not specified)")
@click.option("--pattern", default="*.json", help="File pattern to match")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def batch(
    input_dir: str,
    output_dir: str,
    provider: Optional[str],
    pattern: str,
    verbose: bool,
) -> None:
    """Batch convert multiple transcript files."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if verbose:
        console.print(f"[blue]Batch converting files from {input_path} to {output_path}[/blue]")
        if provider:
            console.print(f"[blue]Provider: {provider}[/blue]")
        else:
            console.print(f"[blue]Provider: auto-detect[/blue]")
        console.print(f"[blue]Pattern: {pattern}[/blue]")

    # TODO: Implement batch conversion logic
    console.print(f"[yellow]Batch conversion not yet implemented[/yellow]")


@main.command()
def providers() -> None:
    """List supported transcription providers."""
    table = Table(title="Supported Transcription Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_column("Status", style="green")

    providers_data = [
        ("whisper", "OpenAI Whisper speech recognition", "Implemented"),
        ("deepgram", "Deepgram real-time speech-to-text API", "Implemented"),
        ("assemblyai", "AssemblyAI transcription service", "Implemented"),
        ("rev-ai", "Rev.ai transcription service", "Implemented"),
        ("canary", "NVIDIA Canary speech recognition via Hugging Face", "Implemented"),
        (
            "parakeet",
            "NVIDIA Parakeet speech recognition via Hugging Face",
            "Implemented",
        ),
        ("google-cloud", "Google Cloud Speech-to-Text", "Planned"),
        ("amazon-transcribe", "Amazon Transcribe service", "Planned"),
        ("azure-speech", "Azure Speech Services", "Planned"),
        ("speechmatics", "Speechmatics speech recognition", "Planned"),
    ]

    for provider, description, status in providers_data:
        table.add_row(provider, description, status)

    console.print(table)


# Add cross-provider commands to main CLI
main.add_command(cross_provider)


if __name__ == "__main__":
    main()
