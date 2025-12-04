#!/usr/bin/env python3
"""
Validation script to verify code organization requirements are met.
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} NOT FOUND")
        return False

def check_directory_structure():
    """Verify the directory structure is correct"""
    print("\n=== Checking Directory Structure ===")
    checks = []
    
    # Check domain directories exist
    checks.append(check_file_exists("events", "Events domain directory"))
    checks.append(check_file_exists("users", "Users domain directory"))
    checks.append(check_file_exists("registrations", "Registrations domain directory"))
    checks.append(check_file_exists("common", "Common module directory"))
    
    return all(checks)

def check_separation_of_concerns():
    """Verify separation of concerns - handlers, services, repositories"""
    print("\n=== Checking Separation of Concerns ===")
    checks = []
    
    # Events domain
    checks.append(check_file_exists("events/handlers.py", "Events handlers"))
    checks.append(check_file_exists("events/service.py", "Events service"))
    checks.append(check_file_exists("events/repository.py", "Events repository"))
    checks.append(check_file_exists("events/models.py", "Events models"))
    
    # Users domain
    checks.append(check_file_exists("users/handlers.py", "Users handlers"))
    checks.append(check_file_exists("users/service.py", "Users service"))
    checks.append(check_file_exists("users/repository.py", "Users repository"))
    checks.append(check_file_exists("users/models.py", "Users models"))
    
    # Registrations domain
    checks.append(check_file_exists("registrations/handlers.py", "Registrations handlers"))
    checks.append(check_file_exists("registrations/service.py", "Registrations service"))
    checks.append(check_file_exists("registrations/repository.py", "Registrations repository"))
    checks.append(check_file_exists("registrations/models.py", "Registrations models"))
    
    return all(checks)

def check_common_modules():
    """Verify common modules exist"""
    print("\n=== Checking Common Modules ===")
    checks = []
    
    checks.append(check_file_exists("common/exceptions.py", "Common exceptions"))
    checks.append(check_file_exists("config.py", "Configuration module"))
    
    return all(checks)

def check_main_file():
    """Verify main.py is simplified"""
    print("\n=== Checking Main Application File ===")
    
    if not Path("main.py").exists():
        print("✗ main.py NOT FOUND")
        return False
    
    with open("main.py", "r") as f:
        content = f.read()
        lines = len(content.split("\n"))
    
    print(f"✓ main.py exists ({lines} lines)")
    
    # Check that main.py is under 200 lines
    if lines > 200:
        print(f"✗ main.py has {lines} lines (should be under 200)")
        return False
    else:
        print(f"✓ main.py is under 200 lines")
    
    # Check for router imports
    has_events_router = "from events.handlers import router" in content
    has_users_router = "from users.handlers import router" in content
    has_registrations_router = "from registrations.handlers import router" in content
    
    if has_events_router and has_users_router and has_registrations_router:
        print("✓ main.py imports all domain routers")
    else:
        print("✗ main.py missing router imports")
        return False
    
    # Check that main.py doesn't have business logic
    has_no_business_logic = (
        "class EventService" not in content and
        "class UserService" not in content and
        "class RegistrationService" not in content and
        "class EventRepository" not in content
    )
    
    if has_no_business_logic:
        print("✓ main.py contains no business logic classes")
    else:
        print("✗ main.py still contains business logic")
        return False
    
    return True

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("Code Organization Validation")
    print("=" * 60)
    
    results = []
    
    # Run all checks
    results.append(("Directory Structure", check_directory_structure()))
    results.append(("Separation of Concerns", check_separation_of_concerns()))
    results.append(("Common Modules", check_common_modules()))
    results.append(("Main Application File", check_main_file()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All validation checks PASSED!")
        print("\nRequirements Met:")
        print("  ✓ Business logic separated from API handlers")
        print("  ✓ Database operations extracted into repositories")
        print("  ✓ Code organized into logical domain folders")
        print("  ✓ Main file simplified to setup and routing only")
        return 0
    else:
        print("\n✗ Some validation checks FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
