import sys
import click

from tai_sql import pm
from collections import defaultdict

@click.group()
def roles():
    """Utilidades para gestionar roles y permisos"""
    pass

@click.command()
def show():
    """Muestra los roles y permisos definidos en el sistema"""
    roles = pm.roles.list()
    if not roles:
        click.echo(click.style("⚠️  No hay roles definidos en el sistema.", fg='yellow', bold=True))
        sys.exit(0)
    
    click.echo()
    click.echo(click.style("🔐 ROLES DEFINIDOS EN EL SISTEMA", fg='blue', bold=True))
    click.echo(click.style("=" * 40, fg='blue'))
    
    for i, role in enumerate(roles, 1):
        click.echo()
        click.echo(click.style(f"📋 ROLE #{i}", fg='cyan', bold=True))
        click.echo(click.style("─" * 20, fg='cyan'))
        click.echo(f"   {click.style('Nombre:', fg='green', bold=True)} {click.style(role.name, fg='white', bold=True)}")
        click.echo(f"   {click.style('Descripción:', fg='green', bold=True)} {role.description}")
        
        if role.permissions:
            click.echo(f"   {click.style('Permisos:', fg='green', bold=True)}")
            # Agrupar permisos por recurso
            permissions_by_resource = defaultdict(list)
            for perm in role.permissions:
                permissions_by_resource[perm.resource._name].append(perm.action.value)
            
            for resource, actions in permissions_by_resource.items():
                count = len([action for action in actions if action != 'none'])
                click.echo(f"      {click.style('🔹', fg='magenta')} {click.style(resource, fg='yellow', bold=True)} {click.style(f'({count})', fg='blue')}: {click.style(', '.join(actions), fg='white')}")
            
        else:
            click.echo(f"      {click.style('❌ No tiene permisos asignados.', fg='red')}")
        
        if role.rls:
            click.echo(f"   {click.style('Seguridad a nivel de fila (RLS):', fg='green', bold=True)}")
            for rls in role.rls:
                conditions = ', '.join([f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}" for k, v in rls.condition.items()])
                click.echo(f"      {click.style('🔸', fg='magenta')} {click.style(rls.resource._name, fg='yellow', bold=True)}: {click.style(conditions, fg='white')}")

    sys.exit(0)

roles.add_command(show)