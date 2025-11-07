"""
DNS Threat Detector CLI

Command-line interface for DNS threat detection
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List
from .detector import DNS_ThreatDetector


def predict_single(
    detector: DNS_ThreatDetector, domain: str, json_output: bool = False
):
    """Predict a single domain"""
    result = detector.predict(domain)

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nDomain: {domain}")
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Reason: {result['reason']}")
        print(f"Method: {result['method']}")
        print(f"Latency: {result['latency_ms']:.3f}ms")


def predict_batch(detector: DNS_ThreatDetector, file_path: str, output_path: str):
    """Predict domains from file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]

        print(f"Processing {len(domains)} domains...")
        results = []

        for i, domain in enumerate(domains, 1):
            if i % 100 == 0:
                print(f"  Processed {i}/{len(domains)} domains")
            result = detector.predict(domain)
            results.append({"domain": domain, **result})

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {output_path}")

        malicious_count = sum(1 for r in results if r["prediction"] == "MALICIOUS")
        benign_count = len(results) - malicious_count

        print(f"\nSummary:")
        print(f"  Total domains: {len(results)}")
        print(
            f"  Malicious: {malicious_count} ({malicious_count/len(results)*100:.1f}%)"
        )
        print(f"  Benign: {benign_count} ({benign_count/len(results)*100:.1f}%)")

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing batch: {e}")
        sys.exit(1)


def show_info(detector: DNS_ThreatDetector):
    """Show model information"""
    info = detector.get_model_info()

    print("\nDNS Threat Detector Information")
    print("=" * 60)
    print(f"Version: {info['version']}")
    print(f"Model: {info['model_name']}")

    print("\nComponents:")
    for key, value in info["components"].items():
        print(f"  {key}: {value}")

    print("\nPerformance:")
    for key, value in info["performance"].items():
        if isinstance(value, float):
            if value < 1:
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")

    print("\nFeatures:")
    for key, value in info["features"].items():
        print(f"  {key}: {value}")

    if info["safelist"]["enabled"]:
        print("\nSafelist:")
        print(f"  Status: Enabled")
        print(f"  Total domains: {info['safelist']['total_domains']:,}")
        print(f"  Tiers loaded: {info['safelist']['tiers_loaded']}")
        for tier, count in info["safelist"]["tier_counts"].items():
            print(f"    Tier {tier}: {count:,} domains")
    else:
        print("\nSafelist: Disabled")

    print(f"\nProtected brands: {info['protected_brands']}")

    if info["usage_statistics"]["total_predictions"] > 0:
        print("\nUsage Statistics:")
        for key, value in info["usage_statistics"].items():
            print(f"  {key}: {value}")


def run_tests(detector: DNS_ThreatDetector):
    """Run self-tests"""
    print("\nRunning DNS Threat Detector Tests")
    print("=" * 60)

    test_cases = [
        ("google.com", "BENIGN", ["safelist", "brand_whitelist"]),
        ("gooogle.com", "MALICIOUS", ["typosquatting_rule"]),
        ("facebook.com", "BENIGN", ["safelist", "brand_whitelist"]),
        ("faceb00k.com", "MALICIOUS", ["typosquatting_rule"]),
        ("paypa1.com", "MALICIOUS", ["typosquatting_rule"]),
        ("amazon.com", "BENIGN", ["safelist", "brand_whitelist"]),
    ]

    passed = 0
    failed = 0

    for domain, expected_prediction, expected_methods in test_cases:
        result = detector.predict(domain)

        if (
            result["prediction"] == expected_prediction
            and result["method"] in expected_methods
        ):
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1

        print(f"\n[{status}] {domain}")
        print(f"  Expected: {expected_prediction} ({' or '.join(expected_methods)})")
        print(f"  Got: {result['prediction']} ({result['method']})")
        print(f"  Confidence: {result['confidence']:.2%}")

    print("\n" + "=" * 60)
    print(f"Tests passed: {passed}/{len(test_cases)}")
    print(f"Tests failed: {failed}/{len(test_cases)}")

    if failed > 0:
        print("\nSome tests failed!")
        sys.exit(1)
    else:
        print("\nAll tests passed!")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="DNS Threat Detector - Detect malicious domains using ML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dns-detect predict google.com
  dns-detect predict gooogle.com --json
  dns-detect batch domains.txt
  dns-detect batch domains.txt --output results.json
  dns-detect info
  dns-detect test
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    predict_parser = subparsers.add_parser("predict", help="Predict single domain")
    predict_parser.add_argument("domain", help="Domain to analyze")
    predict_parser.add_argument("--json", action="store_true", help="Output as JSON")
    predict_parser.add_argument(
        "--no-safelist", action="store_true", help="Disable safelist"
    )
    predict_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed loading messages"
    )

    batch_parser = subparsers.add_parser(
        "batch", help="Batch process domains from file"
    )
    batch_parser.add_argument("file", help="Input file (one domain per line)")
    batch_parser.add_argument(
        "--output", default="results.json", help="Output JSON file"
    )
    batch_parser.add_argument(
        "--no-safelist", action="store_true", help="Disable safelist"
    )
    batch_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed loading messages"
    )

    info_parser = subparsers.add_parser("info", help="Show model information")
    info_parser.add_argument(
        "--no-safelist", action="store_true", help="Show info without loading safelist"
    )
    info_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed loading messages"
    )

    test_parser = subparsers.add_parser("test", help="Run self-tests")
    test_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed loading messages"
    )

    check_parser = subparsers.add_parser(
        "check", help="Check installation and dependencies"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle check command separately (doesn't need detector)
    if args.command == "check":
        from .check_install import check_installation

        success = check_installation()
        sys.exit(0 if success else 1)

    try:
        use_safelist = not getattr(args, "no_safelist", False)
        verbose = getattr(args, "verbose", False)

        if verbose:
            print("Initializing DNS Threat Detector...")
        detector = DNS_ThreatDetector(use_safelist=use_safelist)
        if verbose:
            print("Loading models...")
        detector.load_models()
        if verbose:
            print("Ready!")

        if args.command == "predict":
            predict_single(detector, args.domain, args.json)

        elif args.command == "batch":
            predict_batch(detector, args.file, args.output)

        elif args.command == "info":
            show_info(detector)

        elif args.command == "test":
            run_tests(detector)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
