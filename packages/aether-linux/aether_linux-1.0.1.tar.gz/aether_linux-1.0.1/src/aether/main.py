import sys
import time
import pyfiglet
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Importa tus comandos
from aether.cli.commands import (
    terminal_info,
    terminal_optimizar,
    terminal_uso_monitor,
    terminal_actualizar,
    terminal_ayuda,
    terminal_benchmark,
    terminal_limpieza_profunda,
    terminal_espacio,
    terminal_procesos,
    terminal_red,
    terminal_salud,
    terminal_servicios,
    terminal_soporte,      
)

console = Console()

def mostrar_banner():
    """Muestra el banner animado de Aether"""
    ascii_text = pyfiglet.figlet_format("Aether", font="slant")
    for line in ascii_text.split("\n"):
        console.print(f"[bold cyan]{line}[/bold cyan]")
        time.sleep(0.02)
    
    console.print("[dim]v1.0.0 - Sistema de Optimización Linux[/dim]\n")

def mostrar_menu():
    """Muestra el menú principal con todos los comandos"""
    mostrar_banner()
    
    # Panel de bienvenida
    console.print(Panel.fit(
        "[bold green]Bienvenido a AETHER[/bold green]\n"
        "Tu asistente de optimización y monitoreo del sistema",
        border_style="green"
    ))
    console.print()
    
    # Tabla de comandos básicos
    table_basico = Table(
        title="🚀 Comandos Básicos",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table_basico.add_column("Comando", style="green", no_wrap=True, width=20)
    table_basico.add_column("Descripción", style="white")
    
    comandos_basicos = [
        ("info", "Muestra información completa del sistema"),
        ("monitor", "Monitor de recursos en tiempo real (CPU, RAM, Disco)"),
        ("optimizar", "Optimiza y limpia el sistema"),
        ("actualizar", "Actualiza paquetes del sistema operativo"),
    ]
    
    for cmd, desc in comandos_basicos:
        table_basico.add_row(cmd, desc)
    
    console.print(table_basico)
    console.print()
    
    # Tabla de comandos avanzados
    table_avanzado = Table(
        title="⚙️  Comandos Avanzados",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    table_avanzado.add_column("Comando", style="magenta", no_wrap=True, width=20)
    table_avanzado.add_column("Descripción", style="white")
    
    comandos_avanzados = [
        ("procesos", "Top procesos por CPU y memoria RAM"),
        ("red", "Información de interfaces y estadísticas de red"),
        ("espacio", "Análisis detallado de uso de disco"),
        ("servicios", "Lista servicios activos del sistema"),
        ("salud", "Verificación completa de salud del sistema"),
        ("benchmark", "Ejecuta pruebas de rendimiento del sistema"),
    ]
    
    for cmd, desc in comandos_avanzados:
        table_avanzado.add_row(cmd, desc)
    
    console.print(table_avanzado)
    console.print()
    
    # Tabla de utilidades
    table_util = Table(
        title="🛠️  Utilidades",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold yellow"
    )
    table_util.add_column("Comando", style="yellow", no_wrap=True, width=20)
    table_util.add_column("Descripción", style="white")
    
    comandos_util = [
        ("soporte", "Genera informe de soporte técnico"),
        ("limpieza", "Limpieza profunda del sistema (¡Cuidado!)"),
        ("ayuda", "Muestra ayuda detallada de todos los comandos"),
    ]
    
    for cmd, desc in comandos_util:
        table_util.add_row(cmd, desc)
    
    console.print(table_util)
    console.print()
    
    # Ejemplos de uso
    console.print("[bold cyan]📚 Ejemplos de uso:[/bold cyan]")
    console.print("  [dim]$ aether info[/dim]")
    console.print("  [dim]$ aether optimizar[/dim]")
    console.print("  [dim]$ aether monitor[/dim]")
    console.print()
    
    console.print("[dim]💡 Tip: Ejecuta 'aether ayuda' para más información[/dim]")

def main():
    """Función principal del CLI"""
    
    # Si no hay argumentos, muestra el menú
    if len(sys.argv) < 2:
        mostrar_menu()
        return
    
    # Obtener el comando
    comando = sys.argv[1].lower()
    
    # Diccionario de comandos disponibles
    comandos = {
        "info": terminal_info,
        "optimizar": terminal_optimizar,
        "monitor": terminal_uso_monitor,
        "actualizar": terminal_actualizar,
        "soporte": terminal_soporte,
        "ayuda": terminal_ayuda,
        "benchmark": terminal_benchmark,
        "limpieza": terminal_limpieza_profunda,
        "espacio": terminal_espacio,
        "procesos": terminal_procesos,
        "red": terminal_red,
        "salud": terminal_salud,
        "servicios": terminal_servicios,
        # Alias alternativos
        "opt": terminal_optimizar,
        "mon": terminal_uso_monitor,
        "act": terminal_actualizar,
        "proc": terminal_procesos,
        "help": terminal_ayuda,
        "bench": terminal_benchmark,
        "health": terminal_salud,
        "network": terminal_red,
        "disk": terminal_espacio,
    }
    
    # Ejecutar el comando
    if comando in comandos:
        try:
            console.print()  # Espacio inicial
            comandos[comando]()
            console.print()  # Espacio final
        except KeyboardInterrupt:
            console.print("\n\n[yellow]⚠️  Operación cancelada por el usuario[/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"\n[bold red]❌ Error al ejecutar el comando:[/bold red] {str(e)}")
            console.print("[dim]Usa 'aether soporte' para generar un informe de errores[/dim]")
            sys.exit(1)
    else:
        # Comando no reconocido
        console.print(f"\n[bold red]❌ Comando no reconocido:[/bold red] '{comando}'")
        console.print()
        
        # Sugerencias de comandos similares
        sugerencias = []
        for cmd in comandos.keys():
            if comando in cmd or cmd in comando:
                sugerencias.append(cmd)
        
        if sugerencias:
            console.print("[yellow]¿Quisiste decir?[/yellow]")
            for sug in sugerencias[:3]:
                console.print(f"  • [green]aether {sug}[/green]")
            console.print()
        
        console.print("[cyan]💡 Usa 'aether' sin argumentos para ver todos los comandos disponibles[/cyan]")
        console.print("[cyan]💡 O ejecuta 'aether ayuda' para obtener ayuda detallada[/cyan]")
        sys.exit(1)

if __name__ == "__main__":
    main()