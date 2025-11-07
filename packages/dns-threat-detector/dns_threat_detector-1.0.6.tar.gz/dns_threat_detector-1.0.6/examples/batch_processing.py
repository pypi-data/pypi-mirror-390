"""
Batch Processing Example for DNS Threat Detector
"""

import json
import time
from pathlib import Path
from dns_threat_detector import DNS_ThreatDetector


def create_sample_domains_file():
    """Create a sample domains file for testing"""
    sample_domains = [
        "google.com",
        "gooogle.com",
        "facebook.com",
        "faceb00k.com",
        "microsoft.com",
        "microsfot.com",
        "paypal.com",
        "paypa1.com",
        "amazon.com",
        "amaz0n.com",
        "apple.com",
        "appple.com",
        "netflix.com",
        "netfl1x.com",
        "example.com",
        "test-domain.com",
        "legitimate-site.org",
        "xj4k2mz9p.com",
        "random123xyz.com",
        "abcdef456789.com",
    ]

    with open("sample_domains.txt", "w") as f:
        for domain in sample_domains:
            f.write(domain + "\n")

    return "sample_domains.txt"


def process_batch(detector, input_file, output_file):
    """Process domains in batch"""
    print(f"\nReading domains from: {input_file}")

    with open(input_file, "r") as f:
        domains = [line.strip() for line in f if line.strip()]

    print(f"Found {len(domains)} domains to process")

    print("\nProcessing domains...")
    start_time = time.time()

    results = []
    for i, domain in enumerate(domains, 1):
        if i % 5 == 0:
            print(f"  Processed {i}/{len(domains)} domains")

        result = detector.predict(domain)
        results.append({"domain": domain, **result})

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\nCompleted in {total_time:.2f} seconds")
    print(f"Average time per domain: {total_time/len(domains)*1000:.3f}ms")

    # Save results
    print(f"\nSaving results to: {output_file}")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    return results


def analyze_results(results):
    """Analyze batch results"""
    print("\nResults Analysis:")
    print("=" * 60)

    total = len(results)
    malicious_count = sum(1 for r in results if r["prediction"] == "MALICIOUS")
    benign_count = total - malicious_count

    print(f"\nTotal domains: {total}")
    print(f"Malicious: {malicious_count} ({malicious_count/total*100:.1f}%)")
    print(f"Benign: {benign_count} ({benign_count/total*100:.1f}%)")

    # Breakdown by method
    methods = {}
    for r in results:
        method = r["method"]
        methods[method] = methods.get(method, 0) + 1

    print("\nDetection methods used:")
    for method, count in sorted(methods.items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count} ({count/total*100:.1f}%)")

    # Average confidence
    avg_confidence = sum(r["confidence"] for r in results) / total
    print(f"\nAverage confidence: {avg_confidence:.2%}")

    # List malicious domains
    print("\nMalicious domains detected:")
    for r in results:
        if r["prediction"] == "MALICIOUS":
            print(f"  {r['domain']}")
            print(f"    Confidence: {r['confidence']:.2%}")
            print(f"    Reason: {r['reason']}")


def main():
    print("DNS Threat Detector - Batch Processing Example")
    print("=" * 60)

    # Initialize detector
    print("\n1. Initializing detector...")
    detector = DNS_ThreatDetector(use_safelist=True, safelist_tiers=[1, 2, 3])
    detector.load_models()

    # Create sample domains file
    print("\n2. Creating sample domains file...")
    input_file = create_sample_domains_file()
    print(f"Created: {input_file}")

    # Process batch
    print("\n3. Processing batch...")
    output_file = "batch_results.json"
    results = process_batch(detector, input_file, output_file)

    # Analyze results
    print("\n4. Analyzing results...")
    analyze_results(results)

    print("\n" + "=" * 60)
    print("Batch processing completed successfully!")
    print(f"\nOutput files created:")
    print(f"  - {input_file}")
    print(f"  - {output_file}")


if __name__ == "__main__":
    main()
