"""
DNS Threat Detector - Production-ready ML-based DNS threat detection

A machine learning system for detecting malicious domains including:
- DGA (Domain Generation Algorithm) domains
- Typosquatting attempts
- Malware C&C domains
- Phishing domains

Performance: 99.68% F1-score, <1ms latency, 100% typosquatting detection

v1.0.6 Critical Fix:
- Fixed false positives on legitimate domains with multi-level TLDs (oxford.ac.uk, etc.)
- Replaced broken TLD parsing with industry-standard tldextract library
- Consistent domain extraction across all detection methods (rules + ML)
- Eliminates false positives on domains like therkvvm.org, davrecruit.davcmc.in

v1.0.5 Improvements:
- Fixed false positives on RFC 2606 reserved TLDs (.test, .example, .local, .internal)
- Added trusted PaaS domain exceptions (.herokuapp.com, .github.io, etc.)
- Reduced false positives on internal/developer domains
"""

__version__ = "1.0.6"
__author__ = "UMUDGA Project"
__license__ = "MIT"

# Suppress sklearn version warnings
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Import with helpful error messages
try:
    from .detector import DNS_ThreatDetector, LSTMModel, CharacterTokenizer
except ImportError as e:
    if "torch" in str(e).lower():
        import sys

        print("\n" + "=" * 70)
        print("ERROR: PyTorch Installation Issue Detected")
        print("=" * 70)
        print("\nThe PyTorch library failed to load. This is usually due to:")
        print("1. Missing Visual C++ Redistributables on Windows")
        print("2. Incompatible PyTorch version for your system")
        print("\nSOLUTIONS:")
        print("\n1. Install Visual C++ Redistributables (Windows):")
        print("   Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("   Run the installer and restart your computer")
        print("\n2. Reinstall PyTorch with CPU support:")
        print("   pip uninstall torch")
        print("   pip install torch --index-url https://download.pytorch.org/whl/cpu")
        print("\n3. Try installing in a fresh virtual environment:")
        print("   python -m venv dns_env")
        if sys.platform == "win32":
            print("   dns_env\\Scripts\\activate")
        else:
            print("   source dns_env/bin/activate")
        print("   pip install dns-threat-detector")
        print("\n4. Alternative: Install specific PyTorch version:")
        print(
            "   pip install torch==2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html"
        )
        print("\nFor more help, visit:")
        print(
            "  - PyTorch Installation Guide: https://pytorch.org/get-started/locally/"
        )
        print("  - Package Issues: https://github.com/SubratDash67/DNS-Security/issues")
        print("=" * 70 + "\n")
        raise
    else:
        raise

__all__ = [
    "DNS_ThreatDetector",
    "LSTMModel",
    "CharacterTokenizer",
    "__version__",
]
