# bam/metrics.py
import prometheus_client
import click

def setup_metrics():
    """Set up metrics for the Bam CLI application"""
    prometheus_client.start_http_server(8000)
    click.echo(click.style("Metrics server started on port 8000", fg="green"))