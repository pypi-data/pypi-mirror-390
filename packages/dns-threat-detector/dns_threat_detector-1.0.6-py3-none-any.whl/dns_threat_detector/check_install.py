"""
DNS Threat Detector - Installation Diagnostic Tool
===================================================
This script checks if all dependencies are correctly installed.
"""

import sys
import platform


def check_installation():
    """Check if all dependencies are properly installed."""
    print("\n" + "=" * 70)
    print("DNS Threat Detector - Installation Diagnostics")
    print("=" * 70 + "\n")

    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    print("\nChecking dependencies...\n")

    issues = []
    success = []

    # Check PyTorch
    try:
        import torch

        print(f"✓ PyTorch: {torch.__version__}")
        success.append("PyTorch")
    except ImportError as e:
        print(f"✗ PyTorch: NOT FOUND")
        issues.append(("PyTorch", str(e)))
    except Exception as e:
        print(f"✗ PyTorch: ERROR - {str(e)}")
        issues.append(("PyTorch", str(e)))

    # Check LightGBM
    try:
        import lightgbm

        print(f"✓ LightGBM: {lightgbm.__version__}")
        success.append("LightGBM")
    except ImportError as e:
        print(f"✗ LightGBM: NOT FOUND")
        issues.append(("LightGBM", str(e)))

    # Check scikit-learn
    try:
        import sklearn

        print(f"✓ scikit-learn: {sklearn.__version__}")
        success.append("scikit-learn")
    except ImportError as e:
        print(f"✗ scikit-learn: NOT FOUND")
        issues.append(("scikit-learn", str(e)))

    # Check pandas
    try:
        import pandas

        print(f"✓ pandas: {pandas.__version__}")
        success.append("pandas")
    except ImportError as e:
        print(f"✗ pandas: NOT FOUND")
        issues.append(("pandas", str(e)))

    # Check numpy
    try:
        import numpy

        print(f"✓ numpy: {numpy.__version__}")
        success.append("numpy")
    except ImportError as e:
        print(f"✗ numpy: NOT FOUND")
        issues.append(("numpy", str(e)))

    print("\n" + "=" * 70)

    if not issues:
        print("✓ ALL DEPENDENCIES INSTALLED CORRECTLY!")
        print("=" * 70 + "\n")

        # Try loading the detector
        print("Testing DNS Threat Detector initialization...\n")
        try:
            from dns_threat_detector import DNS_ThreatDetector

            detector = DNS_ThreatDetector()
            detector.load_models()

            # Quick test
            test_domain = "google.com"
            result = detector.predict(test_domain)
            print(f"✓ Test prediction successful!")
            print(f"  Domain: {test_domain}")
            print(f"  Prediction: {result['prediction']}")
            print(f"  Method: {result['method']}")

            print("\n" + "=" * 70)
            print("✓ INSTALLATION IS WORKING PERFECTLY!")
            print("=" * 70 + "\n")
            return True

        except Exception as e:
            print(f"✗ Error initializing detector: {str(e)}")
            print("\n" + "=" * 70)
            print("INSTALLATION TEST FAILED")
            print("=" * 70 + "\n")
            return False
    else:
        print("✗ MISSING OR BROKEN DEPENDENCIES")
        print("=" * 70 + "\n")

        print("Issues found:\n")
        for dep, error in issues:
            print(f"  {dep}:")
            print(f"    {error}\n")

        print("=" * 70)
        print("TROUBLESHOOTING STEPS")
        print("=" * 70 + "\n")

        if any("torch" in dep.lower() for dep, _ in issues):
            print("PyTorch Issue Detected:")
            print("\n1. Windows: Install Visual C++ Redistributables")
            print("   Download: https://aka.ms/vs/17/release/vc_redist.x64.exe")
            print("   Install and restart your computer")
            print("\n2. Reinstall PyTorch:")
            print("   pip uninstall torch")
            print(
                "   pip install torch --index-url https://download.pytorch.org/whl/cpu"
            )
            print("\n3. Or use specific version:")
            print(
                "   pip install torch==2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html"
            )

        print("\nGeneral fix for missing packages:")
        print("  pip install --upgrade dns-threat-detector")
        print("\nOr reinstall all dependencies:")
        print("  pip uninstall dns-threat-detector")
        print("  pip install dns-threat-detector")

        print("\n" + "=" * 70 + "\n")
        return False


if __name__ == "__main__":
    success = check_installation()
    sys.exit(0 if success else 1)
