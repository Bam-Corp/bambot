# bam/prometheus.py
import prometheus_client
import click

def setup_prometheus():
    """Set up Prometheus metrics for the Bam CLI application"""
    prometheus_client.start_http_server(8000)
    click.echo(click.style("Prometheus metrics server started on port 8000", fg="green"))

    container_count = prometheus_client.Gauge("bam_container_count", "Number of Bam containers")
    container_count.set(len(docker.from_env().containers.list()))