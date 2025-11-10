import sys
import os
from datetime import datetime, timedelta

def main():
    if len(sys.argv) < 2:
        print("santaim CLI - Time Control System")
        print("=" * 50)
        print("\nUsage:")
        print("  python -m santaim <command> [args]")
        print("\nCommands:")
        print("  generate <date> <key>  - Generate time-locked script")
        print("  quick <days> <key>     - Quick generate (days from now)")
        print("  verify <date>          - Verify time format")
        print("  help                   - Show all commands")
        return
    
    command = sys.argv[1].lower()
    
    if command in ["generate", "gen", "g", "create", "make", "build", "new", "init"]:
        generate_command()
    elif command in ["quick", "q", "fast", "rapid", "express", "instant"]:
        quick_command()
    elif command in ["verify", "ver", "v", "check", "validate", "test-date"]:
        verify_command()
    elif command in ["version", "--version", "-v", "ver"]:
        print("santaim v1.0.0")
    elif command in ["info", "i", "about", "details", "status"]:
        show_info()
    elif command in ["help", "h", "--help", "-h", "?"]:
        show_help()
    elif command in ["list", "ls", "show", "all"]:
        list_commands()
    elif command in ["trial", "demo", "sample", "example"]:
        trial_command()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python -m santaim help' for all commands")

def generate_command():
    if len(sys.argv) < 3:
        print("Usage: python -m santaim generate YYYY-MM-DD-HH [key]")
        return
    
    date_str = sys.argv[2]
    key = sys.argv[3] if len(sys.argv) > 3 else "default-key"
    
    parts = date_str.split('-')
    if len(parts) < 4:
        print("Invalid date format. Use: YYYY-MM-DD-HH")
        return
    
    year, month, day, hour = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
    minute = int(parts[4]) if len(parts) > 4 else 0
    second = int(parts[5]) if len(parts) > 5 else 0
    
    script = f'''import santaim

santaim.san_tope(
    year={year},
    month={month},
    day={day},
    hour={hour},
    minute={minute},
    second={second},
    encryption_key="{key}"
)

print("Protected application running...")
while True:
    pass
'''
    
    with open('santaem.py', 'w') as f:
        f.write(script)
    
    print(f"Generated: santaem.py")
    print(f"Expiration: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
    print(f"Key: {key}")

def quick_command():
    if len(sys.argv) < 3:
        print("Usage: python -m santaim quick <days> [key]")
        return
    
    days = int(sys.argv[2])
    key = sys.argv[3] if len(sys.argv) > 3 else "quick-key"
    
    exp = datetime.now() + timedelta(days=days)
    
    script = f'''import santaim

santaim.san_tope(
    year={exp.year},
    month={exp.month},
    day={exp.day},
    hour={exp.hour},
    minute={exp.minute},
    second={exp.second},
    encryption_key="{key}"
)

print("Protected application running...")
while True:
    pass
'''
    
    with open('santaem.py', 'w') as f:
        f.write(script)
    
    print(f"Generated: santaem.py")
    print(f"Expires in {days} days: {exp.strftime('%Y-%m-%d %H:%M:%S')}")

def verify_command():
    if len(sys.argv) < 3:
        print("Usage: python -m santaim verify YYYY-MM-DD-HH")
        return
    
    date_str = sys.argv[2]
    parts = date_str.split('-')
    
    try:
        year, month, day, hour = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        dt = datetime(year, month, day, hour)
        print(f"Valid date: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Days from now: {(dt - datetime.now()).days}")
    except:
        print("Invalid date format")

def trial_command():
    days = 30
    if len(sys.argv) > 2:
        days = int(sys.argv[2])
    
    quick_command_with_days(days, "trial-key")

def quick_command_with_days(days, key):
    exp = datetime.now() + timedelta(days=days)
    
    script = f'''import santaim

santaim.san_tope(
    year={exp.year},
    month={exp.month},
    day={exp.day},
    hour=23,
    minute=59,
    second=59,
    encryption_key="{key}"
)

print("Trial version - {days} days")
while True:
    pass
'''
    
    with open('santaem.py', 'w') as f:
        f.write(script)
    
    print(f"Generated trial version: santaem.py ({days} days)")

def show_info():
    from . import __version__, __author__, __owner__
    print("santaim - Time Control System")
    print(f"Version: {__version__}")
    print(f"Author: {__author__}")
    print(f"Owner: {__owner__}")
    print("Platform: Universal (Windows/Linux/macOS/Android/iOS)")

def list_commands():
    cmds = [
        "generate", "gen", "g", "create", "make", "build", "new", "init",
        "quick", "q", "fast", "rapid", "express", "instant",
        "verify", "ver", "v", "check", "validate", "test-date",
        "version", "--version", "-v",
        "info", "i", "about", "details", "status",
        "help", "h", "--help", "-h", "?",
        "list", "ls", "show", "all",
        "trial", "demo", "sample", "example"
    ]
    
    print(f"Available Commands ({len(cmds)}):")
    for i, cmd in enumerate(cmds, 1):
        print(f"  {i}. {cmd}")

def show_help():
    commands = [
        ("generate, gen, g, create", "Generate time-locked script"),
        ("quick, q, fast, rapid", "Quick generate (days from now)"),
        ("verify, ver, v, check", "Verify time format"),
        ("version, --version, -v", "Show version"),
        ("info, i, about, status", "Show library info"),
        ("help, h, --help, ?", "Show this help"),
        ("list, ls, show, all", "List all commands"),
        ("trial, demo, sample", "Create trial version"),
    ]
    
    print("santaim - Complete Command Reference")
    print("=" * 60)
    print("\nCore Commands:")
    for cmd, desc in commands:
        print(f"  {cmd:30} {desc}")
    
    print("\nExamples:")
    print("  python -m santaim generate 2025-12-31-23 my-key")
    print("  python -m santaim quick 30 trial-key")
    print("  python -m santaim verify 2025-6-15-12")
    print("  python -m santaim trial 60")
    print(f"\nTotal Command Aliases: {41}")

if __name__ == "__main__":
    main()
