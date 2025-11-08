#!/usr/bin/env python3
"""
Automated tests to verify all interactive menu commands are properly persisted.

This script performs CODE INSPECTION to verify that all menu commands have
corresponding save/load logic in style.py and session.py files.

Tests check for:
1. Style commands (p/i persistence via style.py)
2. Geometry commands (s/b persistence via session.py)
"""

import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestResult:
    """Store test results"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.skipped = []
    
    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"  ✓ {test_name}")
    
    def add_fail(self, test_name, reason):
        self.failed.append((test_name, reason))
        print(f"  ✗ {test_name}: {reason}")
    
    def add_skip(self, test_name, reason):
        self.skipped.append((test_name, reason))
        print(f"  ⊘ {test_name}: {reason}")
    
    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.skipped)
        print(f"\n{'='*80}")
        print(f"RESULTS: {len(self.passed)}/{total} passed, {len(self.failed)} failed, {len(self.skipped)} skipped")
        print(f"{'='*80}")
        if self.failed:
            print("\nFailed tests:")
            for name, reason in self.failed:
                print(f"  - {name}: {reason}")
        return len(self.failed) == 0


def create_mock_xy_plot():
    """Create a mock XY plot for testing"""
    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    ax.plot(x, y1, label='sin')
    ax.plot(x, y2, label='cos')
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    return fig, ax


def test_rotation_angle_persistence(results):
    """Test rotation_angle in style export/import"""
    print("\n[Test: rotation_angle persistence]")
    
    fig, ax = create_mock_xy_plot()
    
    # Set rotation angle
    ax._rotation_angle = 90
    
    # Export style
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        style_file = f.name
    
    try:
        # Create mock data for export
        y_data_list = [np.sin(np.linspace(0, 10, 100)), np.cos(np.linspace(0, 10, 100))]
        labels = ['sin', 'cos']
        offsets_list = [0.0, 0.0]
        tick_state = {'bx': True, 'tx': False, 'ly': True, 'ry': False}
        
        class MockArgs:
            stack = False
        
        # Export
        style.export_style_config(
            style_file, fig, ax, y_data_list, labels, 0.0, MockArgs(),
            tick_state, offsets_list, None, None
        )
        
        # Check if saved
        with open(style_file, 'r') as f:
            cfg = json.load(f)
        
        if 'rotation_angle' in cfg and cfg['rotation_angle'] == 90:
            results.add_pass("rotation_angle saved in export")
        else:
            results.add_fail("rotation_angle saved in export", f"Got: {cfg.get('rotation_angle', 'MISSING')}")
        
        # Import to new figure
        fig2, ax2 = create_mock_xy_plot()
        ax2._rotation_angle = 0
        
        style.import_style_config(
            style_file, fig2, ax2, y_data_list, labels, offsets_list,
            MockArgs(), tick_state, None
        )
        
        # Verify restored
        restored_angle = getattr(ax2, '_rotation_angle', 0)
        if restored_angle == 90:
            results.add_pass("rotation_angle restored in import")
        else:
            results.add_fail("rotation_angle restored in import", f"Expected 90, got {restored_angle}")
    
    finally:
        if os.path.exists(style_file):
            os.unlink(style_file)
        plt.close(fig)


def test_spine_colors_persistence(results):
    """Test spine colors in style export/import"""
    print("\n[Test: spine colors persistence]")
    
    fig, ax = create_mock_xy_plot()
    
    # Set custom spine colors
    ax.spines['bottom'].set_edgecolor('red')
    ax.spines['left'].set_edgecolor('blue')
    ax.spines['top'].set_edgecolor('green')
    ax.spines['right'].set_edgecolor('yellow')
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        style_file = f.name
    
    try:
        y_data_list = [np.sin(np.linspace(0, 10, 100))]
        labels = ['sin']
        offsets_list = [0.0]
        tick_state = {'bx': True, 'ly': True}
        
        class MockArgs:
            stack = False
        
        # Export
        style.export_style_config(
            style_file, fig, ax, y_data_list, labels, 0.0, MockArgs(),
            tick_state, offsets_list, None, None
        )
        
        # Check if saved
        with open(style_file, 'r') as f:
            cfg = json.load(f)
        
        if 'spines' in cfg:
            spines_cfg = cfg['spines']
            if (spines_cfg.get('bottom', {}).get('color') == 'red' and
                spines_cfg.get('left', {}).get('color') == 'blue'):
                results.add_pass("spine colors saved in export")
            else:
                results.add_fail("spine colors saved in export", f"Colors not correct: {spines_cfg}")
        else:
            results.add_fail("spine colors saved in export", "spines section missing")
        
        # Import
        fig2, ax2 = create_mock_xy_plot()
        style.import_style_config(
            style_file, fig2, ax2, y_data_list, labels, offsets_list,
            MockArgs(), tick_state, None
        )
        
        # Verify
        if (ax2.spines['bottom'].get_edgecolor()[0] == 1.0 and  # red = (1,0,0,1)
            ax2.spines['left'].get_edgecolor()[2] == 1.0):      # blue = (0,0,1,1)
            results.add_pass("spine colors restored in import")
        else:
            results.add_fail("spine colors restored in import", 
                           f"Bottom: {ax2.spines['bottom'].get_edgecolor()}, Left: {ax2.spines['left'].get_edgecolor()}")
    
    finally:
        if os.path.exists(style_file):
            os.unlink(style_file)
        plt.close(fig)


def test_xy_session_persistence(results):
    """Test XY plot session save/load with offsets and rearrangement"""
    print("\n[Test: XY session persistence (offsets, rearrangement)]")
    
    fig, ax = create_mock_xy_plot()
    
    # Set offsets and rotation
    ax._rotation_angle = 45
    offsets = [0.0, 1.5]
    
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        session_file = f.name
    
    try:
        x_full_list = [np.linspace(0, 10, 100), np.linspace(0, 10, 100)]
        y_full_list = [np.sin(x_full_list[0]), np.cos(x_full_list[1])]
        labels = ['sin', 'cos']
        
        class MockArgs:
            files = ['file1.txt', 'file2.txt']
            stack = False
        
        # Save session
        session.dump_session(
            session_file, fig, ax, x_full_list, y_full_list, labels,
            offsets, 0.0, MockArgs(), {}
        )
        
        # Check if saved
        with open(session_file, 'rb') as f:
            sess = pickle.load(f)
        
        if 'offsets' in sess and sess['offsets'] == offsets:
            results.add_pass("offsets saved in session")
        else:
            results.add_fail("offsets saved in session", f"Expected {offsets}, got {sess.get('offsets', 'MISSING')}")
        
        if 'rotation_angle' in sess and sess['rotation_angle'] == 45:
            results.add_pass("rotation_angle saved in session")
        else:
            results.add_fail("rotation_angle saved in session", f"Got {sess.get('rotation_angle', 'MISSING')}")
    
    finally:
        if os.path.exists(session_file):
            os.unlink(session_file)
        plt.close(fig)


def test_ec_session_smoothing(results):
    """Test EC session save/load with smoothing parameters"""
    print("\n[Test: EC session smoothing (dQdV smooth_sigma)]")
    
    # This test requires checking if smooth_sigma is saved
    # Since we don't have full EC infrastructure here, we'll check the session.py code
    
    try:
        # Read session.py to verify smooth_sigma is saved
        session_file_path = Path(__file__).parent.parent / 'batplot' / 'session.py'
        with open(session_file_path, 'r') as f:
            content = f.read()
        
        if 'smooth_sigma' in content:
            results.add_pass("smooth_sigma appears in session.py (code check)")
        else:
            results.add_fail("smooth_sigma in session.py", "smooth_sigma not found in session.py")
    except Exception as e:
        results.add_skip("smooth_sigma check", f"Could not read session.py: {e}")


def test_ec_session_cycle_selection(results):
    """Test EC session save/load with cycle selection"""
    print("\n[Test: EC session cycle selection/colors]")
    
    try:
        session_file_path = Path(__file__).parent.parent / 'batplot' / 'session.py'
        with open(session_file_path, 'r') as f:
            content = f.read()
        
        # Check for cycle_lines or similar
        if 'cycle_lines' in content and 'dump_ec_session' in content:
            results.add_pass("cycle_lines appears in session.py (code check)")
        else:
            results.add_fail("cycle_lines in session.py", "cycle_lines not found in dump_ec_session")
    except Exception as e:
        results.add_skip("cycle_lines check", f"Could not read session.py: {e}")


def test_ec_capacity_conversion(results):
    """Test EC capacity/ion conversion state"""
    print("\n[Test: EC capacity/ion conversion state]")
    
    try:
        session_file_path = Path(__file__).parent.parent / 'batplot' / 'session.py'
        with open(session_file_path, 'r') as f:
            content = f.read()
        
        # Check for _orig_xdata_gc which stores original capacity before conversion
        if '_orig_xdata_gc' in content:
            results.add_pass("_orig_xdata_gc appears in session.py (code check)")
        else:
            results.add_fail("_orig_xdata_gc in session.py", "_orig_xdata_gc not found")
    except Exception as e:
        results.add_skip("capacity conversion check", f"Could not read session.py: {e}")


def test_cpc_marker_sizes(results):
    """Test CPC marker sizes in style export/import"""
    print("\n[Test: CPC marker sizes persistence]")
    
    fig, ax = create_mock_xy_plot()
    
    # Set different marker sizes
    ax.lines[0].set_marker('o')
    ax.lines[0].set_markersize(10)
    ax.lines[1].set_marker('s')
    ax.lines[1].set_markersize(15)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        style_file = f.name
    
    try:
        y_data_list = [np.sin(np.linspace(0, 10, 100)), np.cos(np.linspace(0, 10, 100))]
        labels = ['sin', 'cos']
        offsets_list = [0.0, 0.0]
        tick_state = {}
        
        class MockArgs:
            stack = False
        
        # Export
        style.export_style_config(
            style_file, fig, ax, y_data_list, labels, 0.0, MockArgs(),
            tick_state, offsets_list, None, None
        )
        
        # Check if saved
        with open(style_file, 'r') as f:
            cfg = json.load(f)
        
        if 'lines' in cfg:
            if cfg['lines'][0].get('markersize') == 10 and cfg['lines'][1].get('markersize') == 15:
                results.add_pass("marker sizes saved in export")
            else:
                results.add_fail("marker sizes saved in export", 
                               f"Line 0: {cfg['lines'][0].get('markersize')}, Line 1: {cfg['lines'][1].get('markersize')}")
        else:
            results.add_fail("marker sizes saved in export", "lines section missing")
    
    finally:
        if os.path.exists(style_file):
            os.unlink(style_file)
        plt.close(fig)


def test_cpc_visibility_toggles(results):
    """Test CPC file visibility and efficiency toggles"""
    print("\n[Test: CPC file/efficiency visibility]")
    
    try:
        session_file_path = Path(__file__).parent.parent / 'batplot' / 'session.py'
        with open(session_file_path, 'r') as f:
            content = f.read()
        
        # Check for visibility flags
        has_file_vis = 'file_visibility' in content or 'visible_files' in content
        has_eff_vis = 'efficiency_visible' in content or 'show_efficiency' in content
        
        if has_file_vis:
            results.add_pass("file visibility appears in session.py")
        else:
            results.add_fail("file visibility in session.py", "Not found")
        
        if has_eff_vis:
            results.add_pass("efficiency visibility appears in session.py")
        else:
            results.add_fail("efficiency visibility in session.py", "Not found")
    
    except Exception as e:
        results.add_skip("CPC visibility check", f"Could not read session.py: {e}")


def test_operando_parameters(results):
    """Test operando session parameters (colormap, width, intensity, reverse)"""
    print("\n[Test: Operando parameters (oc/ow/oz/r)]")
    
    try:
        session_file_path = Path(__file__).parent.parent / 'batplot' / 'session.py'
        with open(session_file_path, 'r') as f:
            content = f.read()
        
        # Check for operando parameters
        checks = {
            'colormap': 'cmap' in content or 'colormap' in content,
            'width': 'op_width' in content or 'operando_width' in content,
            'intensity_range': 'intensity_range' in content or 'zlim' in content,
            'reverse': 'reverse' in content or 'reversed' in content,
        }
        
        for param, found in checks.items():
            if found:
                results.add_pass(f"operando {param} appears in session.py")
            else:
                results.add_fail(f"operando {param} in session.py", "Not found")
    
    except Exception as e:
        results.add_skip("operando parameters check", f"Could not read session.py: {e}")


def test_operando_ec_parameters(results):
    """Test operando EC panel parameters (el/ew/et/ey/er)"""
    print("\n[Test: Operando EC panel parameters]")
    
    try:
        session_file_path = Path(__file__).parent.parent / 'batplot' / 'session.py'
        with open(session_file_path, 'r') as f:
            content = f.read()
        
        # Check for EC panel parameters
        checks = {
            'ec_linewidth': 'ec_linewidth' in content or 'ec_lw' in content,
            'ec_width': 'ec_width' in content or 'ec_panel_width' in content,
            'ec_time_range': 'ec_xlim' in content or 'ec_time_range' in content,
            'ec_y_type': 'ec_y_type' in content or 'ec_yaxis' in content,
        }
        
        for param, found in checks.items():
            if found:
                results.add_pass(f"EC panel {param} appears in session.py")
            else:
                results.add_fail(f"EC panel {param} in session.py", "Not found")
    
    except Exception as e:
        results.add_skip("EC panel parameters check", f"Could not read session.py: {e}")


def main():
    """Run all tests"""
    print("=" * 80)
    print("AUTOMATED COMMAND PERSISTENCE TESTS")
    print("=" * 80)
    
    results = TestResult()
    
    # Style export/import tests (p/i commands)
    print("\n" + "=" * 80)
    print("STYLE PERSISTENCE TESTS (p/i commands)")
    print("=" * 80)
    test_rotation_angle_persistence(results)
    test_spine_colors_persistence(results)
    test_cpc_marker_sizes(results)
    
    # Session save/load tests (s/b commands)
    print("\n" + "=" * 80)
    print("SESSION PERSISTENCE TESTS (s/b commands)")
    print("=" * 80)
    test_xy_session_persistence(results)
    test_ec_session_smoothing(results)
    test_ec_session_cycle_selection(results)
    test_ec_capacity_conversion(results)
    test_cpc_visibility_toggles(results)
    test_operando_parameters(results)
    test_operando_ec_parameters(results)
    
    # Summary
    success = results.summary()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
