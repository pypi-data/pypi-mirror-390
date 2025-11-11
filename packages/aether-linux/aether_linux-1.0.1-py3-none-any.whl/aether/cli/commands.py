from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from aether.core.config import load_config
import psutil
import platform
import subprocess
import os
import time
from datetime import datetime

console = Console()

def terminal_info():
    """Muestra información completa del sistema"""
    config = load_config()
    
    # Panel principal
    console.print(Panel.fit(
        "[bold cyan]AETHER[/] - Información del Sistema",
        border_style="cyan"
    ))
    console.print()
    
    # Tabla 1: Sistema Operativo
    table_os = Table(title="🖥️  Sistema Operativo", box=box.ROUNDED, show_header=False)
    table_os.add_column("Info", style="cyan", width=20)
    table_os.add_column("Valor", style="yellow")
    
    table_os.add_row("OS", platform.system())
    table_os.add_row("Versión", platform.release())
    table_os.add_row("Arquitectura", platform.machine())
    table_os.add_row("Hostname", platform.node())
    
    try:
        distro_info = platform.freedesktop_os_release()
        table_os.add_row("Distribución", distro_info.get("PRETTY_NAME", "N/A"))
    except:
        pass
    
    console.print(table_os)
    console.print()
    
    # Tabla 2: Hardware
    table_hw = Table(title="⚙️  Hardware", box=box.ROUNDED, show_header=False)
    table_hw.add_column("Component", style="cyan", width=20)
    table_hw.add_column("Info", style="yellow")
    
    cpu_count = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    table_hw.add_row("CPU Cores", f"{cpu_count} físicos, {cpu_threads} lógicos")
    if cpu_freq:
        table_hw.add_row("Frecuencia CPU", f"{cpu_freq.current:.2f} MHz")
    
    mem = psutil.virtual_memory()
    table_hw.add_row("RAM Total", f"{mem.total / (1024**3):.2f} GB")
    table_hw.add_row("RAM Disponible", f"{mem.available / (1024**3):.2f} GB")
    
    disk = psutil.disk_usage('/')
    table_hw.add_row("Disco Total", f"{disk.total / (1024**3):.2f} GB")
    table_hw.add_row("Disco Libre", f"{disk.free / (1024**3):.2f} GB")
    
    console.print(table_hw)
    console.print()
    
    # Tabla 3: Estado Actual
    table_status = Table(title="📊 Estado Actual", box=box.ROUNDED, show_header=False)
    table_status.add_column("Metric", style="cyan", width=20)
    table_status.add_column("Value", style="magenta")
    
    cpu_percent = psutil.cpu_percent(interval=1)
    table_status.add_row("Uso de CPU", f"{cpu_percent}%")
    table_status.add_row("Uso de RAM", f"{mem.percent}%")
    table_status.add_row("Uso de Disco", f"{disk.percent}%")
    
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    table_status.add_row("Uptime", f"{days}d {hours}h {minutes}m")
    
    # Temperatura (si está disponible)
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current:
                        table_status.add_row("Temperatura", f"{entry.current:.1f}°C")
                        break
                break
    except:
        pass
    
    console.print(table_status)
    console.print()
    
    # Tabla 4: Configuración AETHER
    if config:
        table_config = Table(title="⚡ Configuración AETHER", box=box.ROUNDED)
        table_config.add_column("Key", style="cyan")
        table_config.add_column("Value", style="white")
        
        for key, value in config.items():
            table_config.add_row(key, str(value))
        
        console.print(table_config)

def run(cmd: str, silent: bool = False):
    """Ejecuta comandos del sistema mostrando salida en tiempo real."""
    if not silent:
        console.print(f"[bold blue]$ {cmd}[/bold blue]")
    try:
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )
        for line in process.stdout:
            if not silent:
                console.print(f"   {line.strip()}")
        process.wait()
        
        if process.returncode != 0:
            if not silent:
                console.print(f"[bold red]⚠ Comando falló con código {process.returncode}[/bold red]")
            return False
        return True
    except Exception as e:
        if not silent:
            console.print(f"[bold red]❌ Error ejecutando comando: {e}[/bold red]")
        return False

def terminal_optimizar():
    """Optimiza el sistema con barra de progreso"""
    console.print(Panel.fit(
        "[bold green]🚀 Optimización del Sistema[/bold green]",
        border_style="green"
    ))
    
    tareas = [
        ("Limpiando caché del sistema", "sync && sudo sysctl -w vm.drop_caches=3 2>/dev/null || true"),
        ("Borrando archivos temporales", "sudo rm -rf /tmp/* 2>/dev/null || true"),
        ("Limpiando caché de usuario", "rm -rf ~/.cache/* 2>/dev/null || true"),
        ("Limpiando logs antiguos", "sudo journalctl --vacuum-time=7d 2>/dev/null || true"),
        ("Limpiando journald", "sudo journalctl --vacuum-size=100M 2>/dev/null || true"),
        ("Borrando miniaturas", "rm -rf ~/.cache/thumbnails/* 2>/dev/null || true"),
        ("Limpiando systemd coredumps", "sudo rm -rf /var/lib/systemd/coredump/* 2>/dev/null || true"),
        ("Limpiando caché de pip", "pip cache purge 2>/dev/null || true"),
        ("Limpiando caché de npm", "npm cache clean --force 2>/dev/null || true"),
        ("Limpiando Firefox", "rm -rf ~/.mozilla/firefox/*.default*/cache2/* 2>/dev/null || true"),
        ("Limpiando Chrome", "rm -rf ~/.cache/google-chrome/* 2>/dev/null || true"),
        ("Limpiando Papelera", "rm -rf ~/.local/share/Trash/* 2>/dev/null || true"),
        ("Optimizando swap", "sudo swapoff -a && sudo swapon -a 2>/dev/null || true"),
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        for descripcion, comando in tareas:
            task = progress.add_task(descripcion, total=None)
            run(comando, silent=True)
            progress.remove_task(task)
    
    # Optimización específica por distro
    try:
        distro = platform.freedesktop_os_release().get("ID", "").lower()
    except:
        distro = ""
    
    console.print("\n[bold cyan]📦 Optimizando gestor de paquetes...[/bold cyan]")
    
    if distro in ["ubuntu", "debian", "pop", "mint", "elementary"]:
        console.print("[yellow]Detectado: Ubuntu/Debian[/yellow]")
        run("sudo apt-get autoremove -y")
        run("sudo apt-get autoclean -y")
        run("sudo apt-get clean")
        console.print("[cyan]Limpiando kernels antiguos...[/cyan]")
        run("sudo apt autoremove --purge -y")
    elif distro in ["fedora", "centos", "rhel", "rocky", "almalinux"]:
        console.print("[yellow]Detectado: Fedora/RHEL[/yellow]")
        run("sudo dnf autoremove -y")
        run("sudo dnf clean all")
    elif distro in ["arch", "manjaro", "endeavouros"]:
        console.print("[yellow]Detectado: Arch Linux[/yellow]")
        run("sudo pacman -Rns $(pacman -Qtdq) --noconfirm 2>/dev/null || true")
        run("sudo pacman -Scc --noconfirm")
        run("sudo paccache -rk1 2>/dev/null || true")
    else:
        console.print(f"[bold yellow]⚠ Distribución '{distro}' no reconocida[/bold yellow]")
        console.print("[yellow]Se omitió la limpieza del gestor de paquetes[/yellow]")
    
    # Actualizar base de datos de archivos
    console.print("\n[cyan]📑 Actualizando base de datos de archivos...[/cyan]")
    run("sudo updatedb 2>/dev/null || true", silent=True)
    
    console.print("\n[bold green]✅ Optimización completada. ¡Sistema más limpio y rápido![/bold green]")

def terminal_actualizar():
    """Actualiza el sistema con detección mejorada"""
    current_platform = platform.system()
    
    console.print(Panel.fit(
        f"[bold yellow]🔄 Actualización del Sistema[/bold yellow]\n"
        f"Plataforma: {current_platform}",
        border_style="yellow"
    ))
    
    if current_platform == "Linux":
        try:
            distro = platform.freedesktop_os_release().get("ID", "").lower()
        except:
            console.print("[bold red]❌ No se pudo detectar la distribución[/bold red]")
            return
        
        console.print(f"[cyan]Distribución detectada: {distro}[/cyan]\n")
        
        if distro in ["ubuntu", "debian", "pop", "mint", "elementary"]:
            console.print("[bold cyan]📦 Actualizando Ubuntu/Debian...[/bold cyan]")
            run("sudo apt-get update")
            run("sudo apt-get upgrade -y")
            run("sudo apt-get dist-upgrade -y")
        elif distro in ["fedora", "centos", "rhel", "rocky", "almalinux"]:
            console.print("[bold cyan]📦 Actualizando Fedora/RHEL...[/bold cyan]")
            run("sudo dnf update -y")
            run("sudo dnf upgrade -y")
        elif distro in ["arch", "manjaro", "endeavouros"]:
            console.print("[bold cyan]📦 Actualizando Arch Linux...[/bold cyan]")
            run("sudo pacman -Syu --noconfirm")
        else:
            console.print(f"[bold red]❌ Distribución '{distro}' no soportada[/bold red]")
            
    elif current_platform == "Windows":
        console.print("[bold cyan]📦 Actualizando Windows (Chocolatey)...[/bold cyan]")
        run("powershell -Command \"choco upgrade all -y\"")
        
    elif current_platform == "Darwin":
        console.print("[bold cyan]📦 Actualizando macOS (Homebrew)...[/bold cyan]")
        run("brew update")
        run("brew upgrade")
        run("brew cleanup")
        
    else:
        console.print(f"[bold red]❌ Sistema operativo '{current_platform}' no soportado[/bold red]")
        return
    
    console.print("\n[bold green]✅ Actualización completada exitosamente[/bold green]")

def terminal_uso_monitor():
    """Monitor mejorado con más detalles"""
    console.print(Panel.fit(
        "[bold purple]📊 Monitor del Sistema[/bold purple]",
        border_style="purple"
    ))
    console.print()
    
    # Tabla CPU
    tabla_cpu = Table(title="🔥 CPU", box=box.ROUNDED, show_header=False)
    tabla_cpu.add_column("Métrica", justify="left", style="cyan", no_wrap=True)
    tabla_cpu.add_column("Valor", justify="right", style="yellow")
    
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    cpu_freq = psutil.cpu_freq()
    
    tabla_cpu.add_row("Uso Promedio", f"{sum(cpu_percent)/len(cpu_percent):.1f}%")
    for i, percent in enumerate(cpu_percent):
        tabla_cpu.add_row(f"Core {i}", f"{percent}%")
    
    if cpu_freq:
        tabla_cpu.add_row("Frecuencia Actual", f"{cpu_freq.current:.0f} MHz")
        tabla_cpu.add_row("Frecuencia Máxima", f"{cpu_freq.max:.0f} MHz")
    
    console.print(tabla_cpu)
    console.print()
    
    # Tabla Memoria
    tabla_mem = Table(title="💾 Memoria RAM", box=box.ROUNDED, show_header=False)
    tabla_mem.add_column("Métrica", justify="left", style="cyan", no_wrap=True)
    tabla_mem.add_column("Valor", justify="right", style="magenta")
    
    memory_info = psutil.virtual_memory()
    swap_info = psutil.swap_memory()
    
    tabla_mem.add_row("Total", f"{memory_info.total / (1024**3):.2f} GB")
    tabla_mem.add_row("Disponible", f"{memory_info.available / (1024**3):.2f} GB")
    tabla_mem.add_row("En Uso", f"{memory_info.used / (1024**3):.2f} GB")
    tabla_mem.add_row("Uso", f"{memory_info.percent}%")
    tabla_mem.add_row("Swap Total", f"{swap_info.total / (1024**3):.2f} GB")
    tabla_mem.add_row("Swap Usado", f"{swap_info.used / (1024**3):.2f} GB")
    
    console.print(tabla_mem)
    console.print()
    
    # Tabla Disco
    tabla_disco = Table(title="💿 Disco", box=box.ROUNDED, show_header=False)
    tabla_disco.add_column("Métrica", justify="left", style="cyan", no_wrap=True)
    tabla_disco.add_column("Valor", justify="right", style="magenta")
    
    disk_info = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()
    
    tabla_disco.add_row("Total", f"{disk_info.total / (1024**3):.2f} GB")
    tabla_disco.add_row("Libre", f"{disk_info.free / (1024**3):.2f} GB")
    tabla_disco.add_row("En Uso", f"{disk_info.used / (1024**3):.2f} GB")
    tabla_disco.add_row("Uso", f"{disk_info.percent}%")
    
    if disk_io:
        tabla_disco.add_row("Lecturas", f"{disk_io.read_count}")
        tabla_disco.add_row("Escrituras", f"{disk_io.write_count}")
        tabla_disco.add_row("Bytes Leídos", f"{disk_io.read_bytes / (1024**3):.2f} GB")
        tabla_disco.add_row("Bytes Escritos", f"{disk_io.write_bytes / (1024**3):.2f} GB")
    
    console.print(tabla_disco)
    console.print()

def terminal_procesos():
    """Muestra los procesos que más recursos consumen"""
    console.print(Panel.fit(
        "[bold red]🔴 Top Procesos[/bold red]",
        border_style="red"
    ))
    console.print()
    
    # Por CPU
    table_cpu = Table(title="🔥 Top 10 por CPU", box=box.ROUNDED)
    table_cpu.add_column("PID", style="cyan", justify="right")
    table_cpu.add_column("Nombre", style="yellow")
    table_cpu.add_column("CPU %", style="red", justify="right")
    table_cpu.add_column("RAM %", style="magenta", justify="right")
    
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    procs_sorted_cpu = sorted(procs, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:10]
    
    for proc in procs_sorted_cpu:
        table_cpu.add_row(
            str(proc['pid']),
            proc['name'][:30] if proc['name'] else "N/A",
            f"{proc['cpu_percent']:.1f}" if proc['cpu_percent'] else "0.0",
            f"{proc['memory_percent']:.1f}" if proc['memory_percent'] else "0.0"
        )
    
    console.print(table_cpu)
    console.print()
    
    # Por Memoria
    table_mem = Table(title="💾 Top 10 por RAM", box=box.ROUNDED)
    table_mem.add_column("PID", style="cyan", justify="right")
    table_mem.add_column("Nombre", style="yellow")
    table_mem.add_column("RAM %", style="magenta", justify="right")
    table_mem.add_column("RAM MB", style="blue", justify="right")
    
    procs_sorted_mem = sorted(procs, key=lambda p: p['memory_percent'] or 0, reverse=True)[:10]
    
    for proc in procs_sorted_mem:
        try:
            p = psutil.Process(proc['pid'])
            mem_mb = p.memory_info().rss / (1024 * 1024)
            table_mem.add_row(
                str(proc['pid']),
                proc['name'][:30] if proc['name'] else "N/A",
                f"{proc['memory_percent']:.1f}" if proc['memory_percent'] else "0.0",
                f"{mem_mb:.1f}"
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    console.print(table_mem)

def terminal_red():
    """Muestra información de red"""
    console.print(Panel.fit(
        "[bold blue]🌐 Información de Red[/bold blue]",
        border_style="blue"
    ))
    console.print()
    
    net_io = psutil.net_io_counters()
    net_if = psutil.net_if_addrs()
    net_stats = psutil.net_if_stats()
    
    table = Table(title="Interfaces de Red", box=box.ROUNDED)
    table.add_column("Interfaz", style="cyan")
    table.add_column("IP", style="yellow")
    table.add_column("Estado", style="green")
    table.add_column("Velocidad", style="magenta")
    
    for interface, addrs in net_if.items():
        ip = next((addr.address for addr in addrs if addr.family == 2), "N/A")
        
        if interface in net_stats:
            stats = net_stats[interface]
            estado = "🟢 UP" if stats.isup else "🔴 DOWN"
            velocidad = f"{stats.speed} Mbps" if stats.speed else "N/A"
        else:
            estado = "N/A"
            velocidad = "N/A"
        
        table.add_row(interface, ip, estado, velocidad)
    
    console.print(table)
    console.print()
    
    # Estadísticas globales
    table_stats = Table(title="Estadísticas de Red", box=box.ROUNDED, show_header=False)
    table_stats.add_column("Métrica", style="cyan")
    table_stats.add_column("Valor", style="yellow")
    
    table_stats.add_row("Bytes Enviados", f"{net_io.bytes_sent / (1024**3):.2f} GB")
    table_stats.add_row("Bytes Recibidos", f"{net_io.bytes_recv / (1024**3):.2f} GB")
    table_stats.add_row("Paquetes Enviados", f"{net_io.packets_sent:,}")
    table_stats.add_row("Paquetes Recibidos", f"{net_io.packets_recv:,}")
    table_stats.add_row("Errores Envío", f"{net_io.errout}")
    table_stats.add_row("Errores Recepción", f"{net_io.errin}")
    
    console.print(table_stats)

def terminal_espacio():
    """Analiza qué está ocupando espacio"""
    console.print(Panel.fit(
        "[bold yellow]📁 Análisis de Espacio en Disco[/bold yellow]",
        border_style="yellow"
    ))
    console.print()
    
    dirs_to_check = [
        ("~/.cache", "Caché de Usuario"),
        ("~/.local/share/Trash", "Papelera"),
        ("/var/log", "Logs del Sistema"),
        ("/tmp", "Temporales"),
        ("~/.npm", "Caché NPM"),
        ("~/.cargo", "Caché Cargo/Rust"),
        ("~/Downloads", "Descargas"),
        ("~/.mozilla", "Firefox"),
        ("~/.cache/google-chrome", "Chrome"),
        ("/var/cache", "Caché del Sistema")
    ]
    
    table = Table(title="Uso de Espacio por Directorio", box=box.ROUNDED)
    table.add_column("Directorio", style="cyan")
    table.add_column("Descripción", style="white")
    table.add_column("Tamaño", style="yellow", justify="right")
    
    console.print("[cyan]Analizando directorios... (esto puede tomar unos segundos)[/cyan]\n")
    
    for dir_path, descripcion in dirs_to_check:
        expanded = os.path.expanduser(dir_path)
        if os.path.exists(expanded):
            try:
                result = subprocess.run(
                    f"du -sh '{expanded}' 2>/dev/null", 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                size = result.stdout.split()[0] if result.stdout else "N/A"
                table.add_row(dir_path, descripcion, size)
            except:
                table.add_row(dir_path, descripcion, "Error")
        else:
            table.add_row(dir_path, descripcion, "No existe")
    
    console.print(table)
    console.print()
    
    # Particiones
    console.print("[bold cyan]📊 Particiones del Sistema[/bold cyan]\n")
    table_part = Table(box=box.ROUNDED)
    table_part.add_column("Dispositivo", style="cyan")
    table_part.add_column("Punto de Montaje", style="yellow")
    table_part.add_column("Tipo", style="white")
    table_part.add_column("Total", style="green", justify="right")
    table_part.add_column("Usado", style="red", justify="right")
    table_part.add_column("Libre", style="magenta", justify="right")
    table_part.add_column("Uso %", style="yellow", justify="right")
    
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            table_part.add_row(
                partition.device,
                partition.mountpoint,
                partition.fstype,
                f"{usage.total / (1024**3):.1f} GB",
                f"{usage.used / (1024**3):.1f} GB",
                f"{usage.free / (1024**3):.1f} GB",
                f"{usage.percent}%"
            )
        except PermissionError:
            continue
    
    console.print(table_part)

def terminal_servicios():
    """Lista servicios activos y su estado"""
    console.print(Panel.fit(
        "[bold magenta]⚙️  Servicios del Sistema[/bold magenta]",
        border_style="magenta"
    ))
    console.print()
    
    if platform.system() != "Linux":
        console.print("[yellow]Esta función solo está disponible en Linux con systemd[/yellow]")
        return
    
    console.print("[cyan]Servicios activos (ejecutándose):[/cyan]\n")
    run("systemctl list-units --type=service --state=running --no-pager | head -n 20")
    
    console.print("\n[bold yellow]⚠️  Servicios opcionales que podrías deshabilitar:[/bold yellow]")
    console.print("[dim]Nota: Solo desactiva si no los necesitas[/dim]\n")
    
    servicios_opcionales = [
        ("bluetooth.service", "Bluetooth", "Si no usas dispositivos Bluetooth"),
        ("cups.service", "Impresión", "Si no tienes impresoras"),
        ("avahi-daemon.service", "mDNS/Bonjour", "Descubrimiento de red local"),
        ("ModemManager.service", "Gestor de Módems", "Si no usas módem 3G/4G"),
        ("whoopsie.service", "Reportes de errores", "Envía errores a Ubuntu"),
    ]
    
    table = Table(box=box.ROUNDED)
    table.add_column("Servicio", style="cyan")
    table.add_column("Descripción", style="white")
    table.add_column("Estado", style="yellow")
    table.add_column("Nota", style="dim")
    
    for servicio, desc, nota in servicios_opcionales:
        try:
            result = subprocess.run(
                f"systemctl is-active {servicio}", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            estado = result.stdout.strip()
            
            if estado == "active":
                estado_str = "[green]🟢 ACTIVO[/green]"
            elif estado == "inactive":
                estado_str = "[red]🔴 INACTIVO[/red]"
            else:
                estado_str = f"[yellow]{estado}[/yellow]"
            
            table.add_row(servicio, desc, estado_str, nota)
        except:
            pass
    
    console.print(table)
    console.print("\n[dim]Para desactivar un servicio: sudo systemctl disable --now <servicio>[/dim]")

def terminal_benchmark():
    """Realiza un benchmark básico del sistema"""
    console.print(Panel.fit(
        "[bold cyan]🏃 Benchmark del Sistema[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    resultados = {}
    
    # Test CPU
    console.print("[yellow]⏳ Ejecutando test de CPU...[/yellow]")
    start = time.time()
    sum([i**2 for i in range(1000000)])
    cpu_time = time.time() - start
    resultados["CPU (cálculo)"] = f"{cpu_time:.3f}s"
    
    # Test Memoria
    console.print("[yellow]⏳ Ejecutando test de RAM...[/yellow]")
    start = time.time()
    test_list = [i for i in range(5000000)]
    del test_list
    mem_time = time.time() - start
    resultados["RAM (asignación)"] = f"{mem_time:.3f}s"
    
    # Test Disco - Escritura
    console.print("[yellow]⏳ Ejecutando test de Disco (write)...[/yellow]")
    test_file = "/tmp/aether_benchmark_test"
    test_size = 50 * 1024 * 1024  # 50MB
    
    start = time.time()
    try:
        with open(test_file, "wb") as f:
            f.write(b"0" * test_size)
        disk_write = time.time() - start
        resultados["Disco (write 50MB)"] = f"{disk_write:.3f}s ({(test_size/(1024*1024))/disk_write:.2f} MB/s)"
    except:
        resultados["Disco (write)"] = "Error"
    
    # Test Disco - Lectura
    console.print("[yellow]⏳ Ejecutando test de Disco (read)...[/yellow]")
    start = time.time()
    try:
        with open(test_file, "rb") as f:
            data = f.read()
        disk_read = time.time() - start
        resultados["Disco (read 50MB)"] = f"{disk_read:.3f}s ({(test_size/(1024*1024))/disk_read:.2f} MB/s)"
        os.remove(test_file)
    except:
        resultados["Disco (read)"] = "Error"
    
    console.print()
    
    # Mostrar resultados
    table = Table(title="📊 Resultados del Benchmark", box=box.ROUNDED)
    table.add_column("Test", style="cyan")
    table.add_column("Resultado", style="yellow", justify="right")
    
    for test, resultado in resultados.items():
        table.add_row(test, resultado)
    
    console.print(table)
    console.print("\n[dim]Menor tiempo = Mejor rendimiento[/dim]")

def terminal_salud():
    """Verifica la salud del sistema"""
    console.print(Panel.fit(
        "[bold green]💚 Estado de Salud del Sistema[/bold green]",
        border_style="green"
    ))
    console.print()
    
    # Verificar espacio en disco
    def check_disk():
        usage = psutil.disk_usage('/')
        return usage.percent < 90
    
    # Verificar RAM
    def check_ram():
        mem = psutil.virtual_memory()
        return mem.percent < 90
    
    # Verificar temperatura
    def check_temp():
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.current and entry.current > 80:
                            return False
            return True
        except:
            return None
    
    # Verificar errores en logs
    def check_logs():
        try:
            if platform.system() == "Linux":
                result = subprocess.run(
                    "journalctl -p err -b --no-pager | wc -l",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                error_count = int(result.stdout.strip())
                return error_count < 50
        except:
            return None
    
    # Verificar swap
    def check_swap():
        swap = psutil.swap_memory()
        if swap.total > 0:
            return swap.percent < 75
        return True
    
    # Verificar procesos zombies
    def check_zombies():
        try:
            zombies = 0
            for proc in psutil.process_iter(['status']):
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    zombies += 1
            return zombies == 0
        except:
            return None
    
    checks = [
        ("💿 Espacio en Disco (<90%)", check_disk, "Considera limpiar archivos o expandir disco"),
        ("💾 Uso de RAM (<90%)", check_ram, "Cierra aplicaciones no usadas"),
        ("🌡️  Temperatura CPU (<80°C)", check_temp, "Verifica ventilación y refrigeración"),
        ("📝 Errores en Logs (<50)", check_logs, "Revisa logs con: journalctl -p err -b"),
        ("💫 Uso de Swap (<75%)", check_swap, "Considera aumentar RAM"),
        ("🧟 Procesos Zombie", check_zombies, "Reinicia el sistema si es necesario"),
    ]
    
    table = Table(title="Verificación de Salud", box=box.ROUNDED)
    table.add_column("Check", style="cyan", width=30)
    table.add_column("Estado", style="yellow", width=15)
    table.add_column("Recomendación", style="white")
    
    all_ok = True
    
    for nombre, check_func, recomendacion in checks:
        try:
            resultado = check_func()
            if resultado is None:
                estado = "[yellow]? N/A[/yellow]"
                rec = "No disponible en este sistema"
            elif resultado:
                estado = "[green]✓ OK[/green]"
                rec = "Todo bien"
            else:
                estado = "[red]✗ ATENCIÓN[/red]"
                rec = recomendacion
                all_ok = False
        except Exception as e:
            estado = "[yellow]? ERROR[/yellow]"
            rec = f"Error al verificar: {str(e)[:50]}"
        
        table.add_row(nombre, estado, rec)
    
    console.print(table)
    console.print()
    
    if all_ok:
        console.print("[bold green]🎉 ¡Sistema saludable! Todo funciona correctamente.[/bold green]")
    else:
        console.print("[bold yellow]⚠️  Se detectaron problemas. Revisa las recomendaciones arriba.[/bold yellow]")
    
    # Información adicional
    console.print("\n[bold cyan]📊 Estadísticas Adicionales[/bold cyan]\n")
    
    table_stats = Table(box=box.ROUNDED, show_header=False)
    table_stats.add_column("Métrica", style="cyan")
    table_stats.add_column("Valor", style="yellow")
    
    # Uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    table_stats.add_row("Uptime del Sistema", f"{days}d {hours}h {minutes}m")
    
    # Procesos
    table_stats.add_row("Procesos Activos", str(len(psutil.pids())))
    
    # Carga promedio (solo Linux)
    try:
        if hasattr(os, 'getloadavg'):
            load1, load5, load15 = os.getloadavg()
            table_stats.add_row("Carga Promedio (1/5/15 min)", f"{load1:.2f} / {load5:.2f} / {load15:.2f}")
    except:
        pass
    
    # Usuarios conectados
    try:
        users = len(psutil.users())
        table_stats.add_row("Usuarios Conectados", str(users))
    except:
        pass
    
    console.print(table_stats)

def terminal_soporte():
    """Genera un informe de soporte del sistema"""
    console.print(Panel.fit(
        "[bold red]🆘 Informe de Soporte del Sistema[/bold red]",
        border_style="red"
    ))
    console.print()
    
    console.print("[cyan]Generando informe completo...[/cyan]\n")
    
    informe = []
    
    # Información del Sistema
    informe.append("=" * 60)
    informe.append("INFORMACIÓN DEL SISTEMA")
    informe.append("=" * 60)
    informe.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    informe.append(f"Sistema Operativo: {platform.system()}")
    informe.append(f"Versión: {platform.release()}")
    informe.append(f"Arquitectura: {platform.machine()}")
    informe.append(f"Hostname: {platform.node()}")
    informe.append(f"Python: {platform.python_version()}")
    
    try:
        distro_info = platform.freedesktop_os_release()
        informe.append(f"Distribución: {distro_info.get('PRETTY_NAME', 'N/A')}")
    except:
        pass
    
    # Hardware
    informe.append("\n" + "=" * 60)
    informe.append("HARDWARE")
    informe.append("=" * 60)
    informe.append(f"CPU Cores: {psutil.cpu_count(logical=False)} físicos, {psutil.cpu_count(logical=True)} lógicos")
    
    cpu_freq = psutil.cpu_freq()
    if cpu_freq:
        informe.append(f"Frecuencia CPU: {cpu_freq.current:.2f} MHz (Max: {cpu_freq.max:.2f} MHz)")
    
    mem = psutil.virtual_memory()
    informe.append(f"RAM Total: {mem.total / (1024**3):.2f} GB")
    informe.append(f"RAM Disponible: {mem.available / (1024**3):.2f} GB")
    informe.append(f"RAM Uso: {mem.percent}%")
    
    disk = psutil.disk_usage('/')
    informe.append(f"Disco Total: {disk.total / (1024**3):.2f} GB")
    informe.append(f"Disco Libre: {disk.free / (1024**3):.2f} GB")
    informe.append(f"Disco Uso: {disk.percent}%")
    
    # Estado Actual
    informe.append("\n" + "=" * 60)
    informe.append("ESTADO ACTUAL")
    informe.append("=" * 60)
    informe.append(f"Uso de CPU: {psutil.cpu_percent(interval=1)}%")
    informe.append(f"Procesos Activos: {len(psutil.pids())}")
    
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    informe.append(f"Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m")
    
    # Top 5 Procesos por CPU
    informe.append("\n" + "=" * 60)
    informe.append("TOP 5 PROCESOS (CPU)")
    informe.append("=" * 60)
    
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procs.append(proc.info)
        except:
            pass
    
    procs_sorted = sorted(procs, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:5]
    for proc in procs_sorted:
        informe.append(f"PID {proc['pid']}: {proc['name']} - CPU: {proc['cpu_percent']:.1f}% - RAM: {proc['memory_percent']:.1f}%")
    
    # Errores recientes en logs (solo Linux)
    if platform.system() == "Linux":
        informe.append("\n" + "=" * 60)
        informe.append("ERRORES RECIENTES EN LOGS (últimos 10)")
        informe.append("=" * 60)
        try:
            result = subprocess.run(
                "journalctl -p err -b --no-pager -n 10",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.stdout:
                informe.append(result.stdout)
            else:
                informe.append("No hay errores recientes")
        except:
            informe.append("No se pudieron obtener los logs")
    
    # Guardar informe
    filename = f"/tmp/aether_soporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(filename, 'w') as f:
            f.write('\n'.join(informe))
        console.print(f"[bold green]✅ Informe guardado en: {filename}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Error al guardar informe: {e}[/bold red]")
    
    # Mostrar resumen
    console.print("\n[bold cyan]📋 Resumen del Informe:[/bold cyan]\n")
    
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("Sección", style="cyan")
    table.add_column("Info", style="yellow")
    
    table.add_row("Sistema", f"{platform.system()} {platform.release()}")
    table.add_row("CPU", f"{psutil.cpu_count()} cores @ {psutil.cpu_percent(interval=1)}% uso")
    table.add_row("RAM", f"{mem.total / (1024**3):.1f} GB total, {mem.percent}% usado")
    table.add_row("Disco", f"{disk.total / (1024**3):.1f} GB total, {disk.percent}% usado")
    table.add_row("Procesos", f"{len(psutil.pids())} activos")
    table.add_row("Archivo", filename)
    
    console.print(table)
    console.print("\n[dim]Envía este archivo al soporte técnico si necesitas ayuda[/dim]")

def terminal_limpieza_profunda():
    """Limpieza profunda y agresiva del sistema"""
    console.print(Panel.fit(
        "[bold red]🧹 LIMPIEZA PROFUNDA DEL SISTEMA[/bold red]\n"
        "[yellow]⚠️  ADVERTENCIA: Esta operación eliminará muchos archivos[/yellow]",
        border_style="red"
    ))
    console.print()
    
    respuesta = input("¿Estás seguro de continuar? (escribe 'SI' para confirmar): ")
    
    if respuesta != "SI":
        console.print("[yellow]Operación cancelada[/yellow]")
        return
    
    console.print("\n[bold red]Iniciando limpieza profunda...[/bold red]\n")
    
    tareas_profundas = [
        ("Limpiando todos los logs del sistema", "sudo find /var/log -type f -name '*.log' -delete 2>/dev/null || true"),
        ("Limpiando archivos .old", "sudo find / -type f -name '*.old' -delete 2>/dev/null || true"),
        ("Limpiando archivos .bak", "sudo find / -type f -name '*.bak' -delete 2>/dev/null || true"),
        ("Limpiando core dumps", "sudo rm -rf /var/crash/* 2>/dev/null || true"),
        ("Limpiando cache de apt", "sudo rm -rf /var/cache/apt/archives/* 2>/dev/null || true"),
        ("Limpiando thumbnails", "find ~/.cache/thumbnails -type f -delete 2>/dev/null || true"),
        ("Limpiando Firefox completamente", "rm -rf ~/.mozilla/firefox/*/cache* ~/.mozilla/firefox/*/thumbnails 2>/dev/null || true"),
        ("Limpiando Chrome completamente", "rm -rf ~/.config/google-chrome/*/Cache ~/.config/google-chrome/*/Code* 2>/dev/null || true"),
        ("Limpiando archivos temporales antiguos", "sudo find /tmp -type f -atime +7 -delete 2>/dev/null || true"),
        ("Vaciando papelera completamente", "rm -rf ~/.local/share/Trash/{files,info}/* 2>/dev/null || true"),
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        for descripcion, comando in tareas_profundas:
            task = progress.add_task(descripcion, total=None)
            run(comando, silent=True)
            progress.remove_task(task)
    
    console.print("\n[bold green]✅ Limpieza profunda completada[/bold green]")
    console.print("[yellow]Se recomienda reiniciar el sistema[/yellow]")

# Función de ayuda para mostrar todos los comandos disponibles
def terminal_ayuda():
    """Muestra todos los comandos disponibles"""
    console.print(Panel.fit(
        "[bold cyan]📖 AETHER - Comandos Disponibles[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    comandos = [
        ("terminal_info()", "Información completa del sistema"),
        ("terminal_optimizar()", "Optimiza y limpia el sistema"),
        ("terminal_actualizar()", "Actualiza paquetes del sistema"),
        ("terminal_uso_monitor()", "Monitor de recursos (CPU, RAM, Disco)"),
        ("terminal_procesos()", "Top procesos por CPU y RAM"),
        ("terminal_red()", "Información de interfaces de red"),
        ("terminal_espacio()", "Análisis de uso de espacio en disco"),
        ("terminal_servicios()", "Lista servicios activos del sistema"),
        ("terminal_benchmark()", "Benchmark de rendimiento del sistema"),
        ("terminal_salud()", "Verificación de salud del sistema"),
        ("terminal_soporte()", "Genera informe para soporte técnico"),
        ("terminal_limpieza_profunda()", "Limpieza agresiva del sistema (¡Cuidado!)"),
        ("terminal_ayuda()", "Muestra esta ayuda"),
    ]
    
    table = Table(title="Comandos Disponibles", box=box.ROUNDED)
    table.add_column("Comando", style="cyan", no_wrap=True)
    table.add_column("Descripción", style="yellow")
    
    for comando, desc in comandos:
        table.add_row(comando, desc)
    
    console.print(table)
    console.print("\n[dim]Importa las funciones con: from terminal_utils import *[/dim]")