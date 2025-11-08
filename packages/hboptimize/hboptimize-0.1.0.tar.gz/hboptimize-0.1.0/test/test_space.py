"""
Test space transforms and other core functionality.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from hboptimize.core.search_space import SearchSpace # type: ignore
from hboptimize.types import Real, Integer, Categorical # type: ignore


def test_space_roundtrip():
    """Test that to_array/from_array is consistent."""
    print("Testing space round-trip...")
    
    # Create search space
    space = SearchSpace({
        'alpha': Real(1e-4, 1e2, log10=True),
        'max_iter': Integer(100, 1000),
        'model': Categorical(('ridge', 'lasso', 'rf')),
        'learning_rate': Real(0.001, 0.1, log10=False),
    })
    
    # Test multiple random samples
    n_tests = 100
    max_error = 0.0
    failures = []
    
    for i in range(n_tests):
        # Generate random config
        original = space.sample(method='sobol', n=1)[0]
        
        # Round-trip transform
        x_vec = space.to_array(original)
        reconstructed = space.from_array(x_vec)
        
        # Check each parameter
        for key in original:
            orig_val = original[key]
            recon_val = reconstructed[key]
            
            if isinstance(orig_val, (int, float)):
                # Numerical comparison
                error = abs(orig_val - recon_val)
                max_error = max(max_error, error)
                
                if isinstance(orig_val, int):
                    # Integers should match exactly
                    if orig_val != recon_val:
                        failures.append(f"Integer mismatch: {key}={orig_val} -> {recon_val}")
                else:
                    # Floats should be very close
                    rel_error = error / (abs(orig_val) + 1e-10)
                    if rel_error > 1e-6:
                        failures.append(f"Float mismatch: {key}={orig_val} -> {recon_val} (error={error})")
            else:
                # Categorical comparison
                if orig_val != recon_val:
                    failures.append(f"Categorical mismatch: {key}={orig_val} -> {recon_val}")
    
    if failures:
        print(f"✗ FAILED: {len(failures)} round-trip errors:")
        for f in failures[:10]:  # Show first 10
            print(f"  {f}")
        return False
    else:
        print(f"✓ PASSED: {n_tests} round-trips, max numerical error={max_error:.2e}")
        return True


def test_space_bounds():
    """Test that sampled points respect bounds."""
    print("\nTesting space bounds...")
    
    space = SearchSpace({
        'x1': Real(0.0, 1.0),
        'x2': Real(1e-5, 1e5, log10=True),
        'n': Integer(1, 100),
    })
    
    n_samples = 1000
    violations = []
    
    for method in ['sobol', 'lhs', 'random']:
        samples = space.sample(method=method, n=n_samples)
        
        for i, cfg in enumerate(samples):
            # Check x1 bounds
            if not (0.0 <= cfg['x1'] <= 1.0):
                violations.append(f"{method}: x1={cfg['x1']} out of [0,1]")
            
            # Check x2 bounds (log scale)
            if not (1e-5 <= cfg['x2'] <= 1e5):
                violations.append(f"{method}: x2={cfg['x2']} out of [1e-5,1e5]")
            
            # Check n bounds
            if not (1 <= cfg['n'] <= 100):
                violations.append(f"{method}: n={cfg['n']} out of [1,100]")
    
    if violations:
        print(f"✗ FAILED: {len(violations)} bound violations:")
        for v in violations[:10]:
            print(f"  {v}")
        return False
    else:
        print(f"✓ PASSED: {3*n_samples} samples respect bounds")
        return True


def test_log_transform():
    """Test that log10 transform works correctly."""
    print("\nTesting log10 transform...")
    
    space = SearchSpace({'alpha': Real(1e-4, 1e2, log10=True)})
    
    # Test specific values
    test_vals = [1e-4, 1e-2, 1.0, 10.0, 1e2]
    errors = []
    
    for val in test_vals:
        cfg = {'alpha': val}
        x_vec = space.to_array(cfg)
        reconstructed = space.from_array(x_vec)
        
        rel_error = abs(val - reconstructed['alpha']) / val
        if rel_error > 1e-6:
            errors.append(f"alpha={val} -> {reconstructed['alpha']} (error={rel_error:.2e})")
    
    if errors:
        print(f"✗ FAILED: Log transform errors:")
        for e in errors:
            print(f"  {e}")
        return False
    else:
        print(f"✓ PASSED: Log transform preserves values")
        return True


def main():
    print("=" * 70)
    print("Space Transform Tests")
    print("=" * 70)
    
    results = []
    results.append(("Round-trip", test_space_roundtrip()))
    results.append(("Bounds", test_space_bounds()))
    results.append(("Log transform", test_log_transform()))
    
    print("\n" + "=" * 70)
    print("Summary:")
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
