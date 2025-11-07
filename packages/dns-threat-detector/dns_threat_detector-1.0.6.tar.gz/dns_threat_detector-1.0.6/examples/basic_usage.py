"""
Basic Usage Example for DNS Threat Detector
"""

from dns_threat_detector import DNS_ThreatDetector


def main():
    print("DNS Threat Detector - Basic Usage Example")
    print("=" * 60)

    # Initialize detector with safelist enabled
    print("\n1. Initializing detector...")
    detector = DNS_ThreatDetector(use_safelist=True, safelist_tiers=[1, 2, 3])
    detector.load_models()

    # Test various domains
    print("\n2. Testing various domains:")
    print("-" * 60)

    test_domains = [
        ("google.com", "Legitimate brand"),
        ("gooogle.com", "Typosquatting (extra o)"),
        ("g00gle.com", "Typosquatting (digit substitution)"),
        ("facebook.com", "Legitimate brand"),
        ("faceb00k.com", "Typosquatting"),
        ("paypal.com", "Legitimate brand"),
        ("paypa1.com", "Typosquatting"),
        ("example.com", "Normal domain"),
        ("xj4k2mz9p.com", "DGA-like domain"),
    ]

    for domain, description in test_domains:
        result = detector.predict(domain)

        print(f"\nDomain: {domain}")
        print(f"Description: {description}")
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Reason: {result['reason']}")
        print(f"Method: {result['method']}")
        print(f"Latency: {result['latency_ms']:.3f}ms")

    # Show model statistics
    print("\n" + "=" * 60)
    print("3. Model Statistics:")
    print("-" * 60)

    info = detector.get_model_info()

    print(f"\nModel: {info['model_name']} v{info['version']}")
    print(f"F1-Score: {info['performance']['f1_score']:.4f}")
    print(f"Accuracy: {info['performance']['accuracy']:.4f}")
    print(f"Typosquatting Detection: {info['performance']['typosquatting_detection']:.2%}")

    if info["safelist"]["enabled"]:
        print(f"\nSafelist: Enabled")
        print(f"Total domains: {info['safelist']['total_domains']:,}")
        print(f"Tiers loaded: {info['safelist']['tiers_loaded']}")

    print(f"\nUsage statistics:")
    stats = info["usage_statistics"]
    print(f"  Total predictions: {stats['total_predictions']}")
    print(f"  Safelist hits: {stats['safelist_hits']}")
    print(f"  Brand whitelist hits: {stats['brand_whitelist_hits']}")
    print(f"  Typosquatting detections: {stats['typosquatting_detections']}")
    print(f"  Ensemble predictions: {stats['ensemble_predictions']}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
