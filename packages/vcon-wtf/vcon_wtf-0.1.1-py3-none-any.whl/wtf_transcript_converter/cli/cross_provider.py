"""
Cross-provider testing CLI commands.

This module provides CLI commands for testing consistency, performance, and quality
across multiple transcription providers.
"""

import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


@click.group()
def cross_provider() -> None:
    """Cross-provider testing and comparison tools."""
    pass


@cross_provider.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output report file (default: cross_provider_report.json)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output with detailed reports")
def consistency(input_file: str, output: Optional[str], verbose: bool) -> None:
    """Test consistency across all providers using the same input data."""
    console.print(f"[blue]Testing consistency across providers with {input_file}...[/blue]")

    try:
        # Load input data
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)

        # Import the consistency tester
        from ..cross_provider import CrossProviderConsistencyTester

        tester = CrossProviderConsistencyTester()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            task = progress.add_task("Testing consistency...", total=None)
            results = tester.test_consistency_with_sample_data(input_data)
            progress.update(task, description="Analyzing results...")
            analysis = tester.analyze_consistency(results)
            progress.update(task, description="Generating report...")
            report = tester.generate_consistency_report(results)

        # Display results
        if verbose:
            console.print(Panel(report, title="Consistency Report", border_style="blue"))
        else:
            # Summary table
            table = Table(title="Consistency Summary")
            table.add_column("Provider", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Confidence", style="yellow")
            table.add_column("Words", style="magenta")
            table.add_column("Duration", style="blue")

            for result in results:
                status = "✅ Valid" if result.is_valid else "❌ Failed"
                confidence = f"{result.confidence_score:.3f}" if result.is_valid else "N/A"
                words = str(result.word_count) if result.is_valid else "N/A"
                duration = f"{result.duration:.2f}s" if result.is_valid else "N/A"

                table.add_row(result.provider, status, confidence, words, duration)

            console.print(table)

        # Save report if requested
        if output:
            report_data = {
                "analysis": analysis,
                "results": [
                    {
                        "provider": r.provider,
                        "success": r.is_valid,
                        "confidence": r.confidence_score,
                        "word_count": r.word_count,
                        "segment_count": r.segment_count,
                        "duration": r.duration,
                        "errors": r.validation_errors,
                    }
                    for r in results
                ],
                "report": report,
            }

            with open(output, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            console.print(f"[green]Report saved to {output}[/green]")

        # Overall status
        if analysis["status"] == "consistent":
            console.print("[green]✅ Providers are consistent![/green]")
        else:
            console.print("[yellow]⚠️  Providers show some inconsistencies[/yellow]")

    except Exception as e:
        console.print(f"[red]Error during consistency testing: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@cross_provider.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--iterations", "-i", default=3, help="Number of benchmark iterations")
@click.option("--output", "-o", type=click.Path(), help="Output report file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output with detailed reports")
def performance(input_file: str, iterations: int, output: Optional[str], verbose: bool) -> None:
    """Benchmark performance across all providers."""
    console.print(f"[blue]Benchmarking performance across providers with {input_file}...[/blue]")

    try:
        # Load input data
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)

        # Import the performance benchmark
        from ..cross_provider import PerformanceBenchmark

        benchmark = PerformanceBenchmark()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            task = progress.add_task("Benchmarking providers...", total=None)
            results = benchmark.benchmark_all_providers(input_data, iterations=iterations)
            progress.update(task, description="Analyzing performance...")
            analysis = benchmark.analyze_performance(results)
            progress.update(task, description="Generating report...")
            report = benchmark.generate_performance_report(results)

        # Display results
        if verbose:
            console.print(Panel(report, title="Performance Report", border_style="green"))
        else:
            # Summary table
            table = Table(title="Performance Summary")
            table.add_column("Provider", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Time (s)", style="yellow")
            table.add_column("Memory (MB)", style="magenta")
            table.add_column("Output (KB)", style="blue")

            for result in results:
                status = "✅ Success" if result.success else "❌ Failed"
                time_str = f"{result.conversion_time:.3f}" if result.success else "N/A"
                memory_str = f"{result.memory_usage_mb:.2f}" if result.success else "N/A"
                size_str = f"{result.wtf_doc_size_kb:.2f}" if result.success else "N/A"

                table.add_row(result.provider, status, time_str, memory_str, size_str)

            console.print(table)

        # Save report if requested
        if output:
            report_data = {
                "analysis": analysis,
                "results": [
                    {
                        "provider": r.provider,
                        "success": r.success,
                        "conversion_time": r.conversion_time,
                        "memory_usage_mb": r.memory_usage_mb,
                        "cpu_usage_percent": r.cpu_usage_percent,
                        "wtf_doc_size_kb": r.wtf_doc_size_kb,
                        "error": r.error_message,
                    }
                    for r in results
                ],
                "report": report,
            }

            with open(output, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            console.print(f"[green]Report saved to {output}[/green]")

        # Performance insights
        if analysis["status"] == "success":
            fastest = analysis["metrics"]["conversion_time"]["fastest"]
            fastest_time = analysis["metrics"]["conversion_time"]["fastest_time"]
            console.print(f"[green]🏆 Fastest provider: {fastest} ({fastest_time:.3f}s)[/green]")

    except Exception as e:
        console.print(f"[red]Error during performance benchmarking: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@cross_provider.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output report file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output with detailed reports")
def quality(input_file: str, output: Optional[str], verbose: bool) -> None:
    """Compare quality across all providers."""
    console.print(f"[blue]Comparing quality across providers with {input_file}...[/blue]")

    try:
        # Load input data
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)

        # Import the quality comparator
        from ..cross_provider import QualityComparator

        comparator = QualityComparator()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            task = progress.add_task("Analyzing quality...", total=None)
            results = comparator.compare_quality_across_providers(input_data)
            progress.update(task, description="Comparing results...")
            analysis = comparator.analyze_quality_comparison(results)
            progress.update(task, description="Generating report...")
            report = comparator.generate_quality_report(results)

        # Display results
        if verbose:
            console.print(Panel(report, title="Quality Report", border_style="yellow"))
        else:
            # Summary table
            table = Table(title="Quality Summary")
            table.add_column("Provider", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Confidence", style="yellow")
            table.add_column("Words", style="magenta")
            table.add_column("Low Conf", style="red")
            table.add_column("Punctuation", style="blue")

            for result in results:
                status = "✅ Success" if result.success else "❌ Failed"
                confidence = f"{result.overall_confidence:.3f}" if result.success else "N/A"
                words = str(result.word_count) if result.success else "N/A"
                low_conf = str(result.low_confidence_words) if result.success else "N/A"
                punctuation = f"{result.punctuation_accuracy:.3f}" if result.success else "N/A"

                table.add_row(result.provider, status, confidence, words, low_conf, punctuation)

            console.print(table)

        # Save report if requested
        if output:
            report_data = {
                "analysis": analysis,
                "results": [
                    {
                        "provider": r.provider,
                        "success": r.success,
                        "overall_confidence": r.overall_confidence,
                        "word_count": r.word_count,
                        "avg_word_confidence": r.avg_word_confidence,
                        "low_confidence_words": r.low_confidence_words,
                        "punctuation_accuracy": r.punctuation_accuracy,
                        "text_completeness": r.text_completeness,
                        "timing_accuracy": r.timing_accuracy,
                        "error": r.error_message,
                    }
                    for r in results
                ],
                "report": report,
            }

            with open(output, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            console.print(f"[green]Report saved to {output}[/green]")

        # Quality insights
        if analysis["status"] == "success":
            best_conf = analysis["best_performers"]["overall_confidence"]
            console.print(f"[green]🏆 Best confidence: {best_conf}[/green]")

    except Exception as e:
        console.print(f"[red]Error during quality comparison: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


@cross_provider.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory for reports")
@click.option("--iterations", "-i", default=3, help="Number of benchmark iterations")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def all(input_file: str, output_dir: Optional[str], iterations: int, verbose: bool) -> None:
    """Run all cross-provider tests (consistency, performance, quality)."""
    console.print(
        f"[blue]Running comprehensive cross-provider analysis with {input_file}...[/blue]"
    )

    # Create output directory if specified
    output_path: Optional[Path] = None
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

    # Run consistency test
    console.print("\n[cyan]1. Testing Consistency...[/cyan]")
    consistency_output = str(output_path / "consistency_report.json") if output_path else None
    try:
        consistency(input_file, consistency_output, verbose)
    except Exception as e:
        console.print(f"[red]Consistency test failed: {e}[/red]")

    # Run performance test
    console.print("\n[cyan]2. Benchmarking Performance...[/cyan]")
    performance_output = str(output_path / "performance_report.json") if output_path else None
    try:
        performance(input_file, iterations, performance_output, verbose)
    except Exception as e:
        console.print(f"[red]Performance test failed: {e}[/red]")

    # Run quality test
    console.print("\n[cyan]3. Comparing Quality...[/cyan]")
    quality_output = str(output_path / "quality_report.json") if output_path else None
    try:
        quality(input_file, quality_output, verbose)
    except Exception as e:
        console.print(f"[red]Quality test failed: {e}[/red]")

    console.print("\n[green]✅ Comprehensive cross-provider analysis complete![/green]")
    if output_dir:
        console.print(f"[blue]Reports saved to: {output_dir}[/blue]")


if __name__ == "__main__":
    cross_provider()
