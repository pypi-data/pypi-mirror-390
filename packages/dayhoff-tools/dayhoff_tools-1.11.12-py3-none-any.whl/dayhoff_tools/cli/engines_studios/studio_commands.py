"""Studio CLI commands for engines_studios system."""

import os
from typing import Optional

import click

from .api_client import StudioManagerClient
from .progress import format_time_ago, wait_with_progress


@click.group()
def studio_cli():
    """Manage studios."""
    pass


# ============================================================================
# Lifecycle Management
# ============================================================================


@studio_cli.command("create")
@click.option("--size", "size_gb", type=int, default=100, help="Studio size in GB")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def create_studio(size_gb: int, env: str):
    """Create a new studio for the current user."""

    client = StudioManagerClient(environment=env)
    user = os.environ.get("USER") or os.environ.get("USERNAME", "unknown")

    try:
        # Check if user already has a studio
        existing = client.get_my_studio()
        if existing:
            click.echo(
                f"✗ You already have a studio: {existing['studio_id']}", err=True
            )
            click.echo(f"   Use 'dh studio delete' to remove it first")
            raise click.Abort()

        click.echo(f"Creating {size_gb}GB studio for {user}...")

        studio = client.create_studio(user=user, size_gb=size_gb)

        if "error" in studio:
            click.echo(f"✗ Error: {studio['error']}", err=True)
            raise click.Abort()

        studio_id = studio["studio_id"]
        click.echo(f"✓ Studio created: {studio_id}")
        click.echo(f"\nAttach to an engine with:")
        click.echo(f"  dh studio attach <engine-name>")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@studio_cli.command("delete")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def delete_studio(yes: bool, env: str):
    """Delete your studio (WARNING: This deletes all data!)."""

    client = StudioManagerClient(environment=env)

    try:
        # Get user's studio
        studio = client.get_my_studio()
        if not studio:
            click.echo("You don't have a studio")
            return

        studio_id = studio["studio_id"]

        # Must be detached first
        if studio["status"] == "in-use":
            click.echo("✗ Studio must be detached before deletion", err=True)
            click.echo("  Run: dh studio detach")
            raise click.Abort()

        # Confirm
        if not yes:
            click.echo(
                f"⚠ WARNING: This will permanently delete all data in {studio_id}"
            )
            if not click.confirm("Are you sure?"):
                click.echo("Cancelled")
                return

        # Delete
        result = client.delete_studio(studio_id)

        if "error" in result:
            click.echo(f"✗ Error: {result['error']}", err=True)
            raise click.Abort()

        click.echo(f"✓ Studio {studio_id} deleted")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Status and Information
# ============================================================================


@studio_cli.command("status")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def studio_status(env: str):
    """Show information about your studio."""

    client = StudioManagerClient(environment=env)

    try:
        studio = client.get_my_studio()
        if not studio:
            click.echo("You don't have a studio yet. Create one with:")
            click.echo("  dh studio create")
            return

        click.echo(f"Studio ID: {studio['studio_id']}")
        click.echo(f"User: {studio['user']}")
        click.echo(f"Size: {studio['size_gb']}GB")
        click.echo(f"Status: {studio['status']}")
        click.echo(f"Created: {format_time_ago(studio['creation_date'])}")

        if studio.get("attached_engine_id"):
            click.echo(f"Attached to: {studio['attached_engine_id']}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@studio_cli.command("list")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def list_studios(env: str):
    """List all studios."""

    client = StudioManagerClient(environment=env)

    try:
        result = client.list_studios()
        studios = result.get("studios", [])

        if not studios:
            click.echo("No studios found")
            return

        # Table header
        click.echo(f"{'User':<20} {'Studio ID':<25} {'Size':<10} {'Status':<15}")
        click.echo("-" * 75)

        # Table rows
        for studio in studios:
            user = studio.get("user", "unknown")[:19]
            studio_id = studio.get("studio_id", "unknown")
            size = f"{studio.get('size_gb', 0)}GB"
            status = studio.get("status", "unknown")

            click.echo(f"{user:<20} {studio_id:<25} {size:<10} {status:<15}")

        click.echo(f"\nTotal: {len(studios)} studio(s)")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Attachment
# ============================================================================


@studio_cli.command("attach")
@click.argument("engine_name_or_id")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def attach_studio(engine_name_or_id: str, env: str):
    """Attach your studio to an engine with progress tracking."""

    client = StudioManagerClient(environment=env)

    try:
        # Get user's studio
        studio = client.get_my_studio()
        if not studio:
            click.echo("✗ You don't have a studio yet. Create one with:", err=True)
            click.echo("  dh studio create")
            raise click.Abort()

        studio_id = studio["studio_id"]

        if studio["status"] != "available":
            click.echo(
                f"✗ Studio is not available (status: {studio['status']})", err=True
            )
            raise click.Abort()

        # Resolve engine name to ID
        engine = client.get_engine_by_name(engine_name_or_id)
        if not engine:
            engine = {"instance_id": engine_name_or_id, "name": engine_name_or_id}

        engine_id = engine["instance_id"]
        engine_name = engine.get("name", engine_id)

        click.echo(f"📎 Attaching studio to {engine_name}...")

        # Initiate attachment
        result = client.attach_studio(
            studio_id=studio_id, engine_id=engine_id, user=studio["user"]
        )

        if "error" in result:
            click.echo(f"✗ Error: {result['error']}", err=True)
            raise click.Abort()

        operation_id = result["operation_id"]

        # Poll for progress
        click.echo(f"\n⏳ Attachment in progress...\n")

        try:
            final_status = wait_with_progress(
                status_func=lambda: client.get_attachment_progress(operation_id),
                is_complete_func=lambda s: s.get("status") == "completed",
                label="Progress",
                timeout_seconds=180,
            )

            click.echo(f"\n✓ Studio attached successfully!")
            click.echo(f"\nYour files are now available at:")
            click.echo(f"  /studios/{studio['user']}/")
            click.echo(f"\nConnect with:")
            click.echo(f"  dh engine ssh {engine_name}")

        except Exception as e:
            # Get final status to show error details
            try:
                final_status = client.get_attachment_progress(operation_id)
                if final_status.get("error"):
                    click.echo(
                        f"\n✗ Attachment failed: {final_status['error']}", err=True
                    )

                    # Show which step failed
                    if final_status.get("steps"):
                        failed_step = next(
                            (
                                s
                                for s in reversed(final_status["steps"])
                                if s.get("status") == "failed"
                            ),
                            None,
                        )
                        if failed_step:
                            click.echo(f"Failed at step: {failed_step['name']}")
                            if failed_step.get("error"):
                                click.echo(f"Error: {failed_step['error']}")
            except:
                pass

            raise

    except Exception as e:
        if "Attachment failed" not in str(e):
            click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@studio_cli.command("detach")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def detach_studio(env: str):
    """Detach your studio from its engine."""

    client = StudioManagerClient(environment=env)

    try:
        # Get user's studio
        studio = client.get_my_studio()
        if not studio:
            click.echo("✗ You don't have a studio", err=True)
            raise click.Abort()

        if studio["status"] != "in-use":
            click.echo(
                f"✗ Studio is not attached (status: {studio['status']})", err=True
            )
            raise click.Abort()

        studio_id = studio["studio_id"]

        click.echo(f"Detaching studio {studio_id}...")

        result = client.detach_studio(studio_id)

        if "error" in result:
            click.echo(f"✗ Error: {result['error']}", err=True)
            raise click.Abort()

        click.echo(f"✓ Studio detached")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


# ============================================================================
# Maintenance
# ============================================================================


@studio_cli.command("resize")
@click.option("--size", "-s", required=True, type=int, help="New size in GB")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def resize_studio(size: int, env: str):
    """Resize your studio volume (requires detachment)."""

    client = StudioManagerClient(environment=env)

    try:
        # Get user's studio
        studio = client.get_my_studio()
        if not studio:
            click.echo("✗ You don't have a studio", err=True)
            raise click.Abort()

        studio_id = studio["studio_id"]

        # Must be detached
        if studio["status"] != "available":
            click.echo(
                f"✗ Studio must be detached first (status: {studio['status']})",
                err=True,
            )
            raise click.Abort()

        current_size = studio.get("size_gb", 0)
        
        if size <= current_size:
            click.echo(
                f"✗ New size ({size}GB) must be larger than current size ({current_size}GB)",
                err=True,
            )
            raise click.Abort()

        if not click.confirm(f"Resize studio from {current_size}GB to {size}GB?"):
            click.echo("Cancelled")
            return

        result = client.resize_studio(studio_id, size)

        if "error" in result:
            click.echo(f"✗ Error: {result['error']}", err=True)
            raise click.Abort()

        click.echo(f"✓ Studio resize initiated: {current_size}GB → {size}GB")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@studio_cli.command("reset")
@click.option("--env", default="dev", help="Environment (dev, sand, prod)")
def reset_studio(env: str):
    """Reset a stuck studio (admin operation)."""

    client = StudioManagerClient(environment=env)

    try:
        # Get user's studio
        studio = client.get_my_studio()
        if not studio:
            click.echo("✗ You don't have a studio", err=True)
            raise click.Abort()

        studio_id = studio["studio_id"]
        current_status = studio.get("status", "unknown")

        click.echo(f"Studio: {studio_id}")
        click.echo(f"Current Status: {current_status}")

        if current_status in ["available", "in-use"]:
            click.echo("Studio is not stuck (status is normal)")
            return

        if not click.confirm(f"Reset studio status to 'available'?"):
            click.echo("Cancelled")
            return

        result = client.reset_studio(studio_id)

        if "error" in result:
            click.echo(f"✗ Error: {result['error']}", err=True)
            raise click.Abort()

        click.echo(f"✓ Studio reset to 'available' status")
        click.echo(f"  Note: Manual cleanup may be required on engines")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()

