"""
SecureKit command-line interface
"""

import click
import json
import sys
from typing import Optional
from securekit.kms.local import LocalKeyManager

@click.group()
@click.option('--keystore', default='./securekit_keystore.json', 
              help='Path to keystore file')
@click.pass_context
def cli(ctx, keystore: str):
    """SecureKit - Production-ready cryptography CLI"""
    ctx.ensure_object(dict)
    ctx.obj['KEYSTORE_PATH'] = keystore

@cli.command()
@click.option('--purpose', required=True, help='Key purpose (encryption, signing, etc.)')
@click.option('--metadata', help='JSON metadata for the key')
@click.pass_context
def create_key(ctx, purpose: str, metadata: Optional[str]):
    """Create a new cryptographic key"""
    try:
        key_manager = LocalKeyManager(ctx.obj['KEYSTORE_PATH'])
        
        metadata_dict = {}
        if metadata:
            metadata_dict = json.loads(metadata)
        
        key_id = key_manager.generate_key(purpose, metadata_dict)
        click.echo(f"Created key: {key_id}")
        
    except Exception as e:
        click.echo(f"Error creating key: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.pass_context
def list_keys(ctx):
    """List all available keys"""
    try:
        key_manager = LocalKeyManager(ctx.obj['KEYSTORE_PATH'])
        keys = key_manager.list_keys()
        
        if not keys:
            click.echo("No keys found")
            return
        
        for key in keys:
            click.echo(f"ID: {key['key_id']}")
            click.echo(f"  Purpose: {key.get('purpose', 'unknown')}")
            click.echo(f"  Created: {key.get('created_at', 'unknown')}")
            click.echo()
            
    except Exception as e:
        click.echo(f"Error listing keys: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('key_id')
@click.pass_context
def rotate_key(ctx, key_id: str):
    """Rotate a cryptographic key"""
    try:
        key_manager = LocalKeyManager(ctx.obj['KEYSTORE_PATH'])
        new_key_id = key_manager.rotate_key(key_id)
        click.echo(f"Rotated key {key_id} -> {new_key_id}")
        
    except Exception as e:
        click.echo(f"Error rotating key: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.pass_context
def health_check(ctx):
    """Perform health check on key manager"""
    try:
        key_manager = LocalKeyManager(ctx.obj['KEYSTORE_PATH'])
        health = key_manager.health_check()
        
        click.echo(f"Status: {health.get('status', 'unknown')}")
        if health.get('error'):
            click.echo(f"Error: {health['error']}")
        else:
            click.echo(f"Keys count: {health.get('keys_count', 0)}")
            
    except Exception as e:
        click.echo(f"Health check failed: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()