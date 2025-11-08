#!/usr/bin/env python3
"""
Code inspection test to verify all interactive menu commands are properly persisted.

This script checks that all menu commands have corresponding save/load logic.
"""

import sys
from pathlib import Path
import re

# Define what to check
CHECKS = {
    'rotation_angle': {
        'files': ['style.py', 'session.py'],
        'keywords': ['rotation_angle', '_rotation_angle'],
        'menus': ['XY', 'EC'],
    },
    'smooth_sigma (dQdV smoothing)': {
        'files': ['session.py', 'electrochem_interactive.py'],
        'keywords': ['smooth_sigma', 'smoothing', 'smooth_window'],
        'menus': ['EC'],
    },
    'spine_colors': {
        'files': ['style.py'],
        'keywords': ['spine.*color', 'edgecolor', 'spines.*get_edgecolor'],
        'menus': ['XY', 'EC', 'CPC'],
    },
    'cycle_lines (cycle selection/colors)': {
        'files': ['session.py'],
        'keywords': ['cycle_lines', 'visible_cycles', 'cycle.*color'],
        'menus': ['EC'],
    },
    '_orig_xdata_gc (capacity/ion conversion)': {
        'files': ['session.py', 'electrochem_interactive.py'],
        'keywords': ['_orig_xdata_gc', 'capacity.*ion', 'c_theoretical'],
        'menus': ['EC'],
    },
    'marker_sizes': {
        'files': ['style.py'],
        'keywords': ['markersize', 'get_markersize', 'set_markersize'],
        'menus': ['CPC', 'XY'],
    },
    'file_visibility (CPC)': {
        'files': ['session.py', 'cpc_interactive.py'],
        'keywords': ['file.*visible', 'visible_files', 'hidden_files'],
        'menus': ['CPC'],
    },
    'efficiency_visible (CPC)': {
        'files': ['session.py', 'cpc_interactive.py'],
        'keywords': ['efficiency.*visible', 'show_efficiency', 'ry_visible'],
        'menus': ['CPC'],
    },
    'operando_colormap': {
        'files': ['session.py', 'operando_ec_interactive.py'],
        'keywords': ['colormap', 'cmap', 'set_cmap'],
        'menus': ['Operando'],
    },
    'operando_width': {
        'files': ['session.py', 'operando_ec_interactive.py'],
        'keywords': ['op_width', 'operando.*width', 'panel.*width'],
        'menus': ['Operando'],
    },
    'intensity_range (oz)': {
        'files': ['session.py', 'operando_ec_interactive.py'],
        'keywords': ['intensity.*range', 'zlim', 'vmin.*vmax'],
        'menus': ['Operando'],
    },
    'reverse_plot': {
        'files': ['session.py', 'operando_ec_interactive.py'],
        'keywords': ['reverse', 'reversed', 'invert'],
        'menus': ['Operando'],
    },
    'ec_linewidth': {
        'files': ['session.py', 'operando_ec_interactive.py'],
        'keywords': ['ec.*linewidth', 'ec.*lw', 'ec_curve.*width'],
        'menus': ['Operando'],
    },
    'ec_width': {
        'files': ['session.py', 'operando_ec_interactive.py'],
        'keywords': ['ec_width', 'ec.*panel.*width'],
        'menus': ['Operando'],
    },
    'ec_time_range': {
        'files': ['session.py', 'operando_ec_interactive.py'],
        'keywords': ['ec.*xlim', 'ec.*time.*range', 'time_range'],
        'menus': ['Operando'],
    },
    'ec_y_type': {
        'files': ['session.py', 'operando_ec_interactive.py'],
        'keywords': ['ec.*y.*type', 'ec_yaxis', 'voltage.*capacity'],
        'menus': ['Operando'],
    },
}


def check_file_for_keywords(filepath, keywords):
    """Check if any of the keywords appear in the file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found = []
        for keyword in keywords:
            # Use regex for pattern matching
            if re.search(keyword, content, re.IGNORECASE):
                found.append(keyword)
        
        return found
    except Exception as e:
        return None


def main():
    """Run all checks"""
    print("=" * 80)
    print("COMMAND PERSISTENCE CODE INSPECTION")
    print("=" * 80)
    print()
    
    base_path = Path(__file__).parent.parent / 'batplot'
    
    total_checks = 0
    passed = 0
    failed = []
    
    for feature, config in CHECKS.items():
        total_checks += 1
        print(f"\nChecking: {feature}")
        print(f"  Menus: {', '.join(config['menus'])}")
        print(f"  Files to check: {', '.join(config['files'])}")
        
        all_found = True
        for filename in config['files']:
            filepath = base_path / filename
            if not filepath.exists():
                print(f"  ✗ {filename} not found!")
                all_found = False
                continue
            
            found_keywords = check_file_for_keywords(filepath, config['keywords'])
            if found_keywords is None:
                print(f"  ✗ Error reading {filename}")
                all_found = False
            elif found_keywords:
                print(f"  ✓ {filename}: Found {', '.join(found_keywords)}")
            else:
                print(f"  ✗ {filename}: None of {config['keywords']} found")
                all_found = False
        
        if all_found:
            passed += 1
            print(f"  ✅ PASS")
        else:
            failed.append(feature)
            print(f"  ❌ FAIL")
    
    # Summary
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed}/{total_checks} checks passed")
    print("=" * 80)
    
    if failed:
        print("\n⚠️  Failed checks (may need implementation):")
        for feature in failed:
            menus = ', '.join(CHECKS[feature]['menus'])
            print(f"  - {feature} ({menus})")
    else:
        print("\n✅ All checks passed!")
    
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
