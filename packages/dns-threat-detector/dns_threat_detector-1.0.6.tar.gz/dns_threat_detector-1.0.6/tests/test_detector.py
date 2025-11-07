"""
Tests for DNS Threat Detector
"""

import pytest
from dns_threat_detector import DNS_ThreatDetector


class TestDetectorInitialization:
    """Test detector initialization"""

    def test_detector_creation(self):
        """Test detector can be created"""
        detector = DNS_ThreatDetector()
        assert detector is not None

    def test_detector_with_safelist(self):
        """Test detector creation with safelist enabled"""
        detector = DNS_ThreatDetector(use_safelist=True, safelist_tiers=[1])
        assert detector is not None
        assert detector.use_safelist is True


class TestModelLoading:
    """Test model loading"""

    def test_load_models_without_safelist(self):
        """Test models can be loaded without safelist"""
        detector = DNS_ThreatDetector(use_safelist=False)
        detector.load_models()

        assert detector.tokenizer is not None
        assert detector.lstm_model is not None
        assert detector.lgbm_model is not None
        assert detector.meta_learner is not None

    def test_load_models_with_safelist(self):
        """Test models can be loaded with safelist"""
        detector = DNS_ThreatDetector(use_safelist=True, safelist_tiers=[1, 2, 3])
        detector.load_models()

        assert detector.tokenizer is not None
        assert detector.lstm_model is not None
        assert detector.lgbm_model is not None
        assert detector.meta_learner is not None
        assert len(detector.safelist) > 0


class TestBrandWhitelist:
    """Test brand whitelist functionality"""

    @pytest.fixture
    def detector(self):
        detector = DNS_ThreatDetector(use_safelist=False)
        detector.load_models()
        return detector

    def test_exact_brand_match(self, detector):
        """Test exact brand matches are classified as benign"""
        brands = ["google.com", "microsoft.com", "facebook.com", "paypal.com"]

        for brand in brands:
            result = detector.predict(brand)
            assert result["prediction"] == "BENIGN"
            assert result["method"] == "brand_whitelist"
            assert result["confidence"] == 1.0


class TestTyposquattingDetection:
    """Test typosquatting detection"""

    @pytest.fixture
    def detector(self):
        detector = DNS_ThreatDetector(use_safelist=False)
        detector.load_models()
        return detector

    def test_typosquatting_extra_char(self, detector):
        """Test detection of typosquatting with extra character"""
        result = detector.predict("gooogle.com")

        assert result["prediction"] == "MALICIOUS"
        assert result["method"] == "typosquatting_rule"
        assert 0.7 <= result["confidence"] <= 1.0

    def test_typosquatting_digit_substitution(self, detector):
        """Test detection of typosquatting with digit substitution"""
        result = detector.predict("g00gle.com")

        assert result["prediction"] == "MALICIOUS"
        assert result["method"] == "typosquatting_rule"
        assert 0.7 <= result["confidence"] <= 1.0

    def test_typosquatting_missing_char(self, detector):
        """Test detection of typosquatting with missing character"""
        result = detector.predict("gogle.com")

        assert result["prediction"] == "MALICIOUS"
        assert result["method"] == "typosquatting_rule"
        assert 0.7 <= result["confidence"] <= 1.0

    def test_multiple_typosquatting_cases(self, detector):
        """Test multiple typosquatting cases"""
        typosquatting_domains = [
            "faceb00k.com",
            "paypa1.com",
            "amaz0n.com",
            "microsfot.com",
            "appple.com",
        ]

        for domain in typosquatting_domains:
            result = detector.predict(domain)
            assert result["prediction"] == "MALICIOUS"
            assert result["method"] == "typosquatting_rule"


class TestEnsemblePrediction:
    """Test ensemble prediction"""

    @pytest.fixture
    def detector(self):
        detector = DNS_ThreatDetector(use_safelist=False)
        detector.load_models()
        return detector

    def test_dga_domain_detection(self, detector):
        """Test detection of DGA-like domains"""
        dga_domains = [
            "xj4k2mz9p.com",
            "qwerty123xyz.com",
            "random456abc.com",
        ]

        for domain in dga_domains:
            result = detector.predict(domain)
            assert result["prediction"] in ["MALICIOUS", "BENIGN"]
            assert "confidence" in result
            assert 0.0 <= result["confidence"] <= 1.0


class TestBatchPrediction:
    """Test batch prediction functionality"""

    @pytest.fixture
    def detector(self):
        detector = DNS_ThreatDetector(use_safelist=False)
        detector.load_models()
        return detector

    def test_batch_prediction(self, detector):
        """Test batch prediction of multiple domains"""
        domains = [
            "google.com",
            "gooogle.com",
            "facebook.com",
            "faceb00k.com",
        ]

        results = detector.predict_batch(domains)

        assert len(results) == len(domains)
        assert all("prediction" in r for r in results)
        assert all("confidence" in r for r in results)
        assert all("method" in r for r in results)


class TestSafelistFunctionality:
    """Test safelist functionality"""

    def test_safelist_loading(self):
        """Test safelist can be loaded"""
        detector = DNS_ThreatDetector(use_safelist=True, safelist_tiers=[1])
        detector.load_models()

        info = detector.get_model_info()
        assert info["safelist"]["enabled"] is True
        assert info["safelist"]["total_domains"] > 0
        assert 1 in info["safelist"]["tiers_loaded"]

    def test_safelist_tier_selection(self):
        """Test selective tier loading"""
        detector = DNS_ThreatDetector(use_safelist=True, safelist_tiers=[1, 2])
        detector.load_models()

        info = detector.get_model_info()
        assert 1 in info["safelist"]["tiers_loaded"]
        assert 2 in info["safelist"]["tiers_loaded"]
        assert 3 not in info["safelist"]["tiers_loaded"]


class TestModelInfo:
    """Test model information retrieval"""

    @pytest.fixture
    def detector(self):
        detector = DNS_ThreatDetector(use_safelist=False)
        detector.load_models()
        return detector

    def test_get_model_info(self, detector):
        """Test model info retrieval"""
        info = detector.get_model_info()

        assert "model_name" in info
        assert "version" in info
        assert "components" in info
        assert "performance" in info
        assert "features" in info
        assert "protected_brands" in info

    def test_usage_statistics(self, detector):
        """Test usage statistics tracking"""
        detector.predict("google.com")
        detector.predict("gooogle.com")

        info = detector.get_model_info()
        stats = info["usage_statistics"]

        assert stats["total_predictions"] == 2
        assert stats["brand_whitelist_hits"] >= 1
        assert stats["typosquatting_detections"] >= 1


class TestPredictionOutput:
    """Test prediction output format"""

    @pytest.fixture
    def detector(self):
        detector = DNS_ThreatDetector(use_safelist=False)
        detector.load_models()
        return detector

    def test_prediction_output_format(self, detector):
        """Test prediction output contains all required fields"""
        result = detector.predict("example.com")

        assert "prediction" in result
        assert "confidence" in result
        assert "reason" in result
        assert "method" in result
        assert "latency_ms" in result

        assert result["prediction"] in ["MALICIOUS", "BENIGN"]
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["reason"], str)
        assert result["method"] in ["safelist", "brand_whitelist", "typosquatting_rule", "ensemble"]
        assert isinstance(result["latency_ms"], float)
        assert result["latency_ms"] > 0


class TestEdgeCases:
    """Test edge cases and special inputs"""

    @pytest.fixture
    def detector(self):
        detector = DNS_ThreatDetector(use_safelist=False)
        detector.load_models()
        return detector

    def test_empty_domain(self, detector):
        """Test handling of empty domain"""
        result = detector.predict("")
        assert "prediction" in result

    def test_domain_with_numbers(self, detector):
        """Test domain containing only numbers"""
        result = detector.predict("123456.com")
        assert "prediction" in result

    def test_long_domain(self, detector):
        """Test very long domain name"""
        result = detector.predict("verylongdomainnamethatexceedsusualength.com")
        assert "prediction" in result

    def test_subdomain_handling(self, detector):
        """Test domain with subdomains"""
        result = detector.predict("mail.google.com")
        assert "prediction" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
