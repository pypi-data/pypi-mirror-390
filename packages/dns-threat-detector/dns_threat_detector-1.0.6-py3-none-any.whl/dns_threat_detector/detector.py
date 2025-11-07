"""
DNS Threat Detector - Production Model with Safelist Integration

This module provides a production-ready DNS threat detection system that combines:
1. Safelist checking for instant benign classification
2. Brand whitelist for exact matches to top brands
3. Typosquatting detection using edit distance
4. ML ensemble (LightGBM + LSTM + Meta-learner) for general threats

Performance: 99.68% F1-score, 100% typosquatting detection, <0.5ms latency
"""

import pickle
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import json
from datetime import datetime
import math
from collections import Counter
import time
import re
import tldextract


class CharacterTokenizer:
    """Character-level tokenizer for domain names"""

    def __init__(self):
        self.char_to_idx = {}
        self.idx_to_char = {}
        self.vocab_size = 0

    def fit(self, texts):
        """Build vocabulary from texts"""
        chars = set()
        for text in texts:
            chars.update(text)

        self.char_to_idx = {char: idx + 1 for idx, char in enumerate(sorted(chars))}
        self.char_to_idx["<PAD>"] = 0
        self.idx_to_char = {idx: char for char, idx in self.char_to_idx.items()}
        self.vocab_size = len(self.char_to_idx)

    def encode(self, text):
        """Convert text to sequence of indices"""
        return [self.char_to_idx.get(char, 0) for char in text]

    def texts_to_sequences(self, texts):
        """Convert multiple texts to sequences"""
        return [self.encode(text) for text in texts]

    def decode(self, indices):
        """Convert indices back to text"""
        return "".join([self.idx_to_char.get(idx, "") for idx in indices])


class LSTMModel(nn.Module):
    """Bidirectional LSTM for character-level domain classification"""

    def __init__(
        self,
        vocab_size=41,
        embedding_dim=32,
        lstm_hidden=64,
        lstm_layers=2,
        dropout=0.3,
    ):
        super(LSTMModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embedding_dim,
            lstm_hidden,
            lstm_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if lstm_layers > 1 else 0,
        )
        self.fc = nn.Sequential(
            nn.Linear(lstm_hidden * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 2),
        )

    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, (hidden, cell) = self.lstm(embedded)

        hidden_fwd = hidden[-2, :, :]
        hidden_bwd = hidden[-1, :, :]
        hidden_cat = torch.cat([hidden_fwd, hidden_bwd], dim=1)

        output = self.fc(hidden_cat)
        return output


class DNS_ThreatDetector:
    """
    Production DNS Threat Detector with Safelist Support

    Features:
    - Multi-tier safelist checking (O(1) lookup for tiers 1-3)
    - Brand whitelist (99 top global brands)
    - Typosquatting detection (edit distance 1-3)
    - ML ensemble (LightGBM + LSTM + Meta-learner)

    Usage:
        detector = DNS_ThreatDetector(use_safelist=True, safelist_tiers=[1, 2, 3])
        detector.load_models()
        result = detector.predict('example.com')
    """

    TOP_BRANDS = [
        "google",
        "microsoft",
        "facebook",
        "paypal",
        "amazon",
        "apple",
        "netflix",
        "twitter",
        "instagram",
        "linkedin",
        "ebay",
        "yahoo",
        "adobe",
        "salesforce",
        "oracle",
        "ibm",
        "intel",
        "cisco",
        "samsung",
        "sony",
        "youtube",
        "gmail",
        "outlook",
        "hotmail",
        "icloud",
        "dropbox",
        "github",
        "stackoverflow",
        "reddit",
        "imgur",
        "twitch",
        "discord",
        "spotify",
        "steam",
        "nvidia",
        "amd",
        "walmart",
        "target",
        "costco",
        "ikea",
        "hulu",
        "disney",
        "hbo",
        "espn",
        "cnn",
        "bbc",
        "nytimes",
        "washingtonpost",
        "guardian",
        "chase",
        "wellsfargo",
        "bankofamerica",
        "citibank",
        "capitalone",
        "visa",
        "mastercard",
        "amex",
        "discover",
        "stripe",
        "square",
        "venmo",
        "zelle",
        "fedex",
        "ups",
        "usps",
        "dhl",
        "alibaba",
        "tencent",
        "baidu",
        "zoom",
        "slack",
        "teams",
        "skype",
        "whatsapp",
        "telegram",
        "signal",
        "photoshop",
        "wordpress",
        "wix",
        "shopify",
        "etsy",
        "airbnb",
        "uber",
        "lyft",
        "doordash",
        "grubhub",
        "peacock",
        "paramount",
        "verizon",
        "att",
        "tmobile",
        "sprint",
        "comcast",
        "spectrum",
        "cox",
    ]

    # v1.0.6: Legitimate domains that should never be flagged as typosquatting
    # These are common organizations, government sites, universities, and companies
    # that happen to have short names or edit distances close to brands
    LEGITIMATE_DOMAINS = {
        # Universities and Educational Institutions
        "mit",
        "stanford",
        "harvard",
        "oxford",
        "cambridge",
        "ucl",
        "eth",
        "caltech",
        "yale",
        "princeton",
        "cornell",
        "duke",
        "columbia",
        "upenn",
        "brown",
        "dartmouth",
        "usc",
        "ucla",
        "nyu",
        "northwestern",
        "georgetown",
        "vanderbilt",
        "iit",
        "iitb",
        "iitk",
        "iitm",
        "iitkgp",
        "iitd",
        "kiit",
        "nit",
        "nus",
        "ntu",
        # Government and Organizations
        "gov",
        "nic",
        "nasa",
        "nih",
        "cdc",
        "fda",
        "epa",
        "fbi",
        "cia",
        "nsa",
        "cbse",
        "ugc",
        "india",
        "bihar",
        "delhi",
        "mumbai",
        "pune",
        # Technology and Companies
        "tcs",
        "wipro",
        "infosys",
        "hcl",
        "cognizant",
        "accenture",
        "ibm",
        "sap",
        "vmware",
        "dell",
        "hp",
        "lenovo",
        "asus",
        "msi",
        "acer",
        # Platforms and Services
        "netlify",
        "vercel",
        "heroku",
        "firebase",
        "firebaseapp",
        "cloudflare",
        "staging",
        "app",
        # Nonprofits and NGOs
        "unicef",
        "who",
        "unesco",
        "oxfam",
        "redcross",
        "wwf",
        "cry",
        "care",
        "smile",
        "smilefoundationindia",
        # Schools and Educational Organizations
        "dav",
        "davps",
        "davpsgurgaon",
    }

    # Phishing service tokens commonly used in suspicious domains
    SERVICE_TOKENS = [
        "login",
        "verify",
        "verification",
        "support",
        "helpdesk",
        "account",
        "refund",
        "recovery",
        "secure",
        "fileshare",
        "customer",
        "payments",
        "payment",
        "wallet",
        "banking",
        "signin",
        "signup",
        "auth",
        "reset",
        "unlock",
        "confirm",
        "update",
        "service",
        "portal",
        "help",
    ]

    # Suspicious/unusual TLDs often used in phishing
    SUSPICIOUS_TLDS = [
        "tk",
        "ml",
        "ga",
        "cf",
        "gq",  # Free domains
        "xyz",
        "top",
        "win",
        "bid",
        "loan",  # Commonly abused
        "work",
        "click",
        "link",
        "download",  # Action-oriented
        "web",
        "site",
        "online",
        "website",  # Generic
        "help",
        "support",
        "host",  # Service-oriented
    ]

    # RFC 2606 Reserved TLDs - Always BENIGN (test/documentation/private use)
    RESERVED_TLDS = [
        "test",  # RFC 2606 - Reserved for testing
        "example",  # RFC 2606 - Reserved for documentation
        "invalid",  # RFC 2606 - Reserved for invalid domains
        "localhost",  # RFC 2606 - Reserved for loopback
        "local",  # RFC 6762 - Reserved for mDNS/local networks
        "internal",  # RFC 6761 - Reserved for internal networks
        "private",  # Common private network usage
        "corp",  # Common corporate internal usage
        "home",  # Common home network usage
        "lan",  # Common LAN usage
    ]

    # Trusted PaaS and Developer Platform Base Domains
    # Subdomains of these are typically benign developer/staging environments
    TRUSTED_PAAS_DOMAINS = [
        # Major cloud/PaaS platforms
        "herokuapp.com",
        "herokussl.com",
        "github.io",
        "githubusercontent.com",
        "netlify.app",
        "netlify.com",
        "vercel.app",
        "vercel.sh",
        "now.sh",
        "railway.app",
        "render.com",
        "onrender.com",
        "fly.dev",
        "fly.io",
        # Cloud providers
        "azurewebsites.net",
        "cloudapp.azure.com",
        "azurestaticapps.net",
        "cloudfront.net",
        "amplifyapp.com",
        "s3.amazonaws.com",
        "firebaseapp.com",
        "web.app",
        "appspot.com",
        "cloudfunctions.net",
        "run.app",
        # Development/testing platforms
        "repl.co",
        "replit.dev",
        "glitch.me",
        "codepen.io",
        "codesandbox.io",
        "stackblitz.io",
        "ngrok.io",
        "ngrok-free.app",
        "localhost.run",
        "loca.lt",
        # CI/CD platforms
        "travis-ci.org",
        "travis-ci.com",
        "circleci.com",
        "gitlab.io",
        "pages.dev",
        # Other trusted platforms
        "wordpress.com",
        "wixsite.com",
        "weebly.com",
        "shopify.com",
        "myshopify.com",
        "squarespace.com",
        "tumblr.com",
        "blogspot.com",
        "medium.com",
        "substack.com",
    ]

    def __init__(
        self,
        models_dir: Optional[str] = None,
        use_safelist: bool = False,
        safelist_dir: Optional[str] = None,
        safelist_tiers: List[int] = [1, 2, 3],
        verbose: bool = False,
        enable_suspicious_detection: bool = True,
    ):
        """
        Initialize DNS Threat Detector

        Args:
            models_dir: Directory containing model files (default: bundled models/)
            use_safelist: Whether to enable safelist checking
            safelist_dir: Directory containing tier files (default: bundled safelists/)
            safelist_tiers: List of tiers to load (1=Critical, 2=High Trust, 3=General)
            verbose: Whether to print detailed loading messages (default: False)
            enable_suspicious_detection: Whether to enable 3-tier classification (default: True)
        """
        if models_dir is None:
            models_dir = Path(__file__).parent / "models"
        self.models_dir = Path(models_dir)

        self.use_safelist = use_safelist
        self.safelist_tiers = safelist_tiers
        self.enable_suspicious_detection = enable_suspicious_detection

        if safelist_dir is None:
            safelist_dir = Path(__file__).parent / "safelists"
        self.safelist_dir = Path(safelist_dir)

        self.verbose = verbose
        self.tokenizer = None
        self.lstm_model = None
        self.lgbm_model = None
        self.meta_learner = None

        self.safelist = set()
        self.safelist_stats = {
            "enabled": use_safelist,
            "tiers_loaded": [],
            "total_domains": 0,
            "tier_counts": {},
        }

        self.prediction_count = 0
        self.safelist_hits = 0
        self.brand_whitelist_hits = 0
        self.typosquatting_hits = 0
        self.ensemble_predictions = 0
        self.suspicious_detections = 0

    def load_models(self):
        """Load all model components"""
        if self.verbose:
            print("Loading models...")

        tokenizer_path = self.models_dir / "tokenizer.pkl"
        with open(tokenizer_path, "rb") as f:
            self.tokenizer = pickle.load(f)
        if self.verbose:
            print(f"  Tokenizer loaded: {tokenizer_path}")

        lstm_path = self.models_dir / "lstm_model.pth"
        self.lstm_model = LSTMModel()
        self.lstm_model.load_state_dict(
            torch.load(lstm_path, map_location=torch.device("cpu"))
        )
        self.lstm_model.eval()
        if self.verbose:
            print(f"  LSTM model loaded: {lstm_path}")

        lgbm_path = self.models_dir / "lgbm_typo_enhanced.pkl"
        with open(lgbm_path, "rb") as f:
            self.lgbm_model = pickle.load(f)
        if self.verbose:
            print(f"  LightGBM model loaded: {lgbm_path}")

        meta_path = self.models_dir / "meta_learner.pkl"
        with open(meta_path, "rb") as f:
            self.meta_learner = pickle.load(f)
        if self.verbose:
            print(f"  Meta-learner loaded: {meta_path}")

        if self.use_safelist:
            self._load_safelist()

        if self.verbose:
            print("All models loaded successfully")

    def _load_safelist(self):
        """Load safelist from tier files"""
        if self.verbose:
            print(f"Loading safelist from: {self.safelist_dir}")

        tier_names = {
            1: "tier1_critical.txt",
            2: "tier2_high_trust.txt",
            3: "tier3_general.txt",
            4: "tier4_supplementary.txt",
        }

        for tier in self.safelist_tiers:
            tier_file = self.safelist_dir / tier_names[tier]

            if not tier_file.exists():
                if self.verbose:
                    print(f"  Warning: Tier {tier} file not found: {tier_file}")
                continue

            tier_domains = set()
            with open(tier_file, "r", encoding="utf-8") as f:
                for line in f:
                    domain = line.strip()
                    if domain and not domain.startswith("#"):
                        tier_domains.add(domain.lower())

            self.safelist.update(tier_domains)
            self.safelist_stats["tiers_loaded"].append(tier)
            self.safelist_stats["tier_counts"][tier] = len(tier_domains)

            if self.verbose:
                print(f"  Tier {tier} loaded: {len(tier_domains):,} domains")

        self.safelist_stats["total_domains"] = len(self.safelist)
        if self.verbose:
            print(f"Total safelist domains: {len(self.safelist):,}")

    def _is_safelisted(self, domain: str) -> bool:
        """Check if domain is in safelist"""
        if not self.use_safelist:
            return False
        return domain.lower() in self.safelist

    def _is_reserved_tld(self, domain: str) -> Tuple[bool, Optional[str]]:
        """
        Check if domain uses a reserved/non-routable TLD (RFC 2606, RFC 6762, RFC 6761).

        These TLDs are explicitly reserved for testing, documentation, or private use
        and should ALWAYS be classified as BENIGN.

        Args:
            domain: Full domain name

        Returns:
            Tuple of (is_reserved, tld)

        Examples:
            example.test → (True, 'test')
            login.example → (True, 'example')
            myapp.local → (True, 'local')
            staging.internal → (True, 'internal')
        """
        parts = domain.lower().split(".")
        if len(parts) < 2:
            return False, None

        tld = parts[-1]
        if tld in self.RESERVED_TLDS:
            return True, tld

        return False, None

    def _is_trusted_paas_domain(self, domain: str) -> Tuple[bool, Optional[str]]:
        """
        Check if domain is hosted on a trusted PaaS/developer platform.

        Subdomains of trusted platforms (e.g., *.herokuapp.com, *.github.io)
        are typically benign developer/staging environments and should not be
        flagged by aggressive suspicious rules.

        Args:
            domain: Full domain name

        Returns:
            Tuple of (is_trusted_paas, base_domain)

        Examples:
            myapp.herokuapp.com → (True, 'herokuapp.com')
            username.github.io → (True, 'github.io')
            old-login-page.netlify.app → (True, 'netlify.app')
        """
        domain_lower = domain.lower()

        for paas_domain in self.TRUSTED_PAAS_DOMAINS:
            if domain_lower.endswith("." + paas_domain) or domain_lower == paas_domain:
                return True, paas_domain

        return False, None

    def _extract_domain_label(self, domain: str) -> str:
        """
        Extract just the domain label (without suffix or subdomain) using tldextract.

        This is the CORRECT way to extract domain labels for consistent feature extraction.

        Examples:
            oxford.ac.uk → oxford
            login.paypal.com → paypal
            davrecruit.davcmc.in → davcmc
            therkvvm.org → therkvvm

        Args:
            domain: Full domain name (FQDN)

        Returns:
            Just the domain label (without TLD or subdomain)
        """
        # Remove any protocol, path, port
        domain = domain.strip().lower()
        domain = re.sub(r"^https?://", "", domain)
        domain = domain.split("/")[0]
        domain = domain.split(":")[0]

        # Use tldextract to properly parse - this handles ALL TLDs correctly
        extracted = tldextract.extract(domain, include_psl_private_domains=True)

        # Return just the domain part
        return extracted.domain if extracted.domain else domain

    def _extract_registered_domain(self, domain: str) -> str:
        """
        Extract the registered domain (domain + suffix) using tldextract.

        This correctly handles multi-level TLDs like ac.uk, co.in, gov.in, etc.

        Examples:
            oxford.ac.uk → oxford.ac.uk
            login.paypal.com → paypal.com
            davrecruit.davcmc.in → davcmc.in
            therkvvm.org → therkvvm.org

        Args:
            domain: Full domain name (FQDN)

        Returns:
            The registered domain (domain.suffix)
        """
        # Remove any protocol, path, port
        domain = domain.strip().lower()
        domain = re.sub(r"^https?://", "", domain)
        domain = domain.split("/")[0]
        domain = domain.split(":")[0]

        # Use tldextract to properly parse the domain
        extracted = tldextract.extract(domain, include_psl_private_domains=True)

        # Return domain.suffix (e.g., "paypal.com", "oxford.ac.uk")
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        elif extracted.domain:
            # No suffix (e.g., localhost, internal names)
            return extracted.domain
        else:
            # Fallback to original if parsing fails
            return domain

    def _has_excessive_repetition(
        self, domain: str, threshold: int = 3
    ) -> Tuple[bool, int, str]:
        """
        Detect excessive character repetition in domain name.

        Args:
            domain: Domain name to check
            threshold: Minimum consecutive repetitions to flag (default: 3)

        Returns:
            Tuple of (has_repetition, max_repeat_count, repeated_char)

        Examples:
            gooooogle.com → (True, 5, 'o')
            google.com → (False, 1, '')
            appplle.store → (True, 3, 'p')
        """
        # Extract domain name only (before first dot)
        domain_name = domain.split(".")[0]

        # Find all consecutive character repetitions
        pattern = r"(.)\1{" + str(threshold) + ",}"
        matches = re.finditer(pattern, domain_name)

        max_repeat = 0
        repeated_char = ""

        for match in matches:
            repeat_len = len(match.group(0))
            if repeat_len > max_repeat:
                max_repeat = repeat_len
                repeated_char = match.group(1)

        has_repetition = max_repeat > 0
        return has_repetition, max_repeat, repeated_char

    def _normalize_repetitions(self, text: str, max_repeat: int = 2) -> str:
        """
        Normalize excessive character repetitions.

        Args:
            text: Input text
            max_repeat: Maximum allowed consecutive repetitions

        Returns:
            Text with repetitions normalized

        Examples:
            gooooooogle → goooogle (with max_repeat=2)
            appplle → applle (with max_repeat=2)
        """
        pattern = r"(.)\1{" + str(max_repeat) + ",}"
        normalized = re.sub(pattern, r"\1" * max_repeat, text)
        return normalized

    def _contains_brand_token(self, domain: str) -> Tuple[bool, Optional[str]]:
        """
        Check if domain contains a brand token (exact match or close variant).

        Args:
            domain: Full domain name

        Returns:
            Tuple of (has_brand_token, matched_brand_name)
        """
        etld_plus_one = self._extract_registered_domain(domain)
        domain_name = etld_plus_one.split(".")[0].lower()

        # Check exact brand match
        for brand in self.TOP_BRANDS:
            if brand in domain_name:
                return True, brand

        # Check close Levenshtein distance (≤ 2)
        for brand in self.TOP_BRANDS:
            distance = self._calculate_edit_distance(domain_name, brand)
            if distance <= 2 and distance > 0:  # Close but not exact
                return True, brand

        return False, None

    def _contains_service_token(self, domain: str) -> Tuple[bool, List[str]]:
        """
        Check if domain contains phishing service tokens.

        Args:
            domain: Full domain name

        Returns:
            Tuple of (has_service_token, list_of_matched_tokens)
        """
        domain_lower = domain.lower()
        matched_tokens = []

        for token in self.SERVICE_TOKENS:
            if token in domain_lower:
                matched_tokens.append(token)

        return len(matched_tokens) > 0, matched_tokens

    def _has_suspicious_tld(self, domain: str) -> Tuple[bool, Optional[str]]:
        """
        Check if domain uses a suspicious/unusual TLD.

        Args:
            domain: Full domain name

        Returns:
            Tuple of (is_suspicious_tld, tld)
        """
        parts = domain.lower().split(".")
        if len(parts) < 2:
            return False, None

        tld = parts[-1]
        if tld in self.SUSPICIOUS_TLDS:
            return True, tld

        return False, None

    def _calculate_suspicious_score(self, domain: str) -> Dict:
        """
        Calculate suspicious score based on multiple signals.

        Scoring system:
        - brand_token_present: 40 points
        - brand_levenshtein_≤2: 30 points
        - service_token_present: 20 points
        - suspicious_tld: 15 points
        - high_entropy (>4.5): 15 points
        - short_domain (<5 chars): 10 points
        - multiple_hyphens (≥2): 10 points

        Thresholds:
        - score ≥ 60: SUSPICIOUS
        - 40 ≤ score < 60: REVIEW (borderline suspicious)
        - score < 40: Not suspicious by these rules

        **v1.0.5 FIX**: Excludes reserved TLDs and trusted PaaS domains to prevent
        false positives on internal/developer domains.

        Args:
            domain: Domain name to analyze

        Returns:
            Dict with score, signals, and classification
        """
        score = 0
        signals = {}

        # **CRITICAL FIX**: Check for reserved TLD first (highest priority)
        is_reserved, reserved_tld = self._is_reserved_tld(domain)
        if is_reserved:
            return {
                "score": 0,
                "classification": "NOT_SUSPICIOUS",
                "signals": {"reserved_tld": reserved_tld},
                "has_brand": False,
                "has_service_token": False,
                "is_reserved_tld": True,
            }

        # **CRITICAL FIX**: Check for trusted PaaS domain
        is_paas, paas_domain = self._is_trusted_paas_domain(domain)
        if is_paas:
            # Significantly reduce suspicious scoring for trusted PaaS domains
            # These often have "login", "secure", etc. in subdomains but are benign
            signals["trusted_paas"] = paas_domain

            # Apply dampening factor for PaaS domains
            paas_dampening = 0.3  # Reduce all scores by 70%
        else:
            paas_dampening = 1.0  # No dampening for non-PaaS domains

        # Brand token detection (40 or 30 points)
        has_brand, brand_name = self._contains_brand_token(domain)
        etld_plus_one = self._extract_registered_domain(domain)
        domain_name = etld_plus_one.split(".")[0].lower()

        if has_brand:
            # Check if exact match or close variant
            if brand_name in domain_name:
                score += int(40 * paas_dampening)
                signals["brand_token_exact"] = brand_name
            else:
                # Close Levenshtein distance
                distance = self._calculate_edit_distance(domain_name, brand_name)
                if distance <= 2:
                    score += int(30 * paas_dampening)
                    signals["brand_lev2"] = brand_name

        # Service token detection (20 points)
        has_service, service_tokens = self._contains_service_token(domain)
        if has_service:
            # **FIX**: For PaaS domains, service tokens are expected (dev.myapp.com, etc.)
            # Only add reduced score for PaaS, full score for others
            score += int(20 * paas_dampening)
            signals["service_tokens"] = service_tokens

        # Suspicious TLD (15 points)
        has_sus_tld, tld = self._has_suspicious_tld(domain)
        if has_sus_tld:
            score += int(15 * paas_dampening)
            signals["suspicious_tld"] = tld

        # Entropy check (15 points)
        entropy = self._calculate_entropy(domain_name)
        if entropy > 4.5:
            score += int(15 * paas_dampening)
            signals["high_entropy"] = round(entropy, 2)

        # Short domain name (10 points)
        if len(domain_name) < 5:
            score += int(10 * paas_dampening)
            signals["short_domain"] = len(domain_name)

        # Multiple hyphens (10 points) - common in phishing
        hyphen_count = domain_name.count("-")
        if hyphen_count >= 2:
            score += int(10 * paas_dampening)
            signals["multiple_hyphens"] = hyphen_count

        # Determine classification
        if score >= 60:
            classification = "SUSPICIOUS"
        elif score >= 40:
            classification = "REVIEW"
        else:
            classification = "NOT_SUSPICIOUS"

        return {
            "score": score,
            "classification": classification,
            "signals": signals,
            "has_brand": has_brand,
            "has_service_token": has_service,
            "is_paas_domain": is_paas,
        }

    def _calculate_edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance"""
        if len(s1) < len(s2):
            return self._calculate_edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _check_typosquatting(self, domain: str) -> Optional[Dict]:
        """
        Check for typosquatting against top brands using proper eTLD+1 matching.

        SECURITY FIX v1.0.3: Enhanced to detect excessive character repetitions
        - Detects extreme elongations (gooooooooooooooogle.in)
        - Normalizes repetitions before distance calculation
        - Catches repetition-based typosquatting attempts

        SECURITY FIX v1.0.2: Now uses eTLD+1 extraction instead of substring matching.
        This prevents false positives like:
        - paypal.verify-login.info (SHOULD BE MALICIOUS)
        - support.google.com.phishing.net (SHOULD BE MALICIOUS)

        Returns:
            None if not typosquatting, dict with details if detected

        Examples:
            ✅ paypal.com → brand match (eTLD+1 = paypal.com)
            ✅ login.paypal.com → brand match (eTLD+1 = paypal.com)
            ❌ paypal.verify.info → NOT a brand (eTLD+1 = verify.info)
            ❌ support.google.com.evil.net → NOT a brand (eTLD+1 = evil.net)
            ❌ gooooooooooooooogle.in → MALICIOUS (excessive repetition)
        """
        # Extract the registered domain (eTLD+1) for proper brand matching
        etld_plus_one = self._extract_registered_domain(domain)

        # Create full brand domains (e.g., "paypal" → "paypal.com")
        # TOP_BRANDS contains just the brand names like "paypal", "google", etc.
        brand_domains = {f"{brand}.com" for brand in self.TOP_BRANDS}

        # Also check common variants (co.uk, etc.) for major brands
        # Add more if needed based on your TOP_BRANDS list
        brand_domains.update(
            {
                "paypal.co.uk",
                "amazon.co.uk",
                "google.co.uk",
                "microsoft.co.uk",
                "apple.co.uk",
            }
        )

        # Check if the eTLD+1 exactly matches a known brand domain
        if etld_plus_one in brand_domains:
            # Extract the brand name for reporting
            brand_name = etld_plus_one.split(".")[0]
            return {
                "is_typosquatting": False,
                "is_brand": True,
                "brand": brand_name,
                "distance": 0,
            }

        # Check for typosquatting by comparing the domain name portion
        # Extract just the domain name (not TLD) for edit distance comparison
        domain_name_only = etld_plus_one.split(".")[0]

        # v1.0.6: Check if this is a known legitimate domain before checking edit distance
        if domain_name_only.lower() in self.LEGITIMATE_DOMAINS:
            return None  # Don't flag legitimate domains as typosquatting

        # FIX: Check for excessive character repetition first
        has_repetition, max_repeat_count, repeated_char = (
            self._has_excessive_repetition(domain_name_only, threshold=3)
        )

        # If excessive repetition is detected, check if it resembles a brand
        if has_repetition:
            # Normalize the domain name to compare with brands
            normalized_domain = self._normalize_repetitions(
                domain_name_only, max_repeat=2
            )

            # Check if normalized version matches or is close to a brand
            for brand in self.TOP_BRANDS:
                # Check exact match after normalization
                if normalized_domain == brand:
                    return {
                        "is_typosquatting": True,
                        "is_brand": False,
                        "brand": brand,
                        "distance": 0,
                        "reason": f"excessive_repetition",
                        "repetition_details": {
                            "char": repeated_char,
                            "count": max_repeat_count,
                            "original": domain_name_only,
                            "normalized": normalized_domain,
                        },
                    }

                # Check close match after normalization (distance 1-3)
                distance = self._calculate_edit_distance(normalized_domain, brand)
                if distance <= 3:
                    return {
                        "is_typosquatting": True,
                        "is_brand": False,
                        "brand": brand,
                        "distance": distance,
                        "reason": f"excessive_repetition+edit_distance",
                        "repetition_details": {
                            "char": repeated_char,
                            "count": max_repeat_count,
                            "original": domain_name_only,
                            "normalized": normalized_domain,
                        },
                    }

        # Standard edit distance check (without repetition normalization)
        min_distance = float("inf")
        closest_brand = None

        for brand in self.TOP_BRANDS:
            distance = self._calculate_edit_distance(domain_name_only, brand)
            if distance < min_distance:
                min_distance = distance
                closest_brand = brand

        # FIX v1.0.6: Avoid false positives on very short legitimate domains
        # Short domain names (2-4 chars) like "mit", "tcs", "ucl" can have low edit distance
        # to brands by pure chance. Only flag as typosquatting if:
        # 1. Distance is 1-2 (very close), OR
        # 2. Distance is 3 AND domain is longer than 4 characters
        # This prevents false positives while catching real typosquatting

        domain_len = len(domain_name_only)

        if min_distance == 1 or min_distance == 2:
            # Very close match - likely typosquatting
            return {
                "is_typosquatting": True,
                "is_brand": False,
                "brand": closest_brand,
                "distance": min_distance,
            }
        elif min_distance == 3 and domain_len > 4:
            # Distance of 3, but only for longer domains (reduces false positives)
            return {
                "is_typosquatting": True,
                "is_brand": False,
                "brand": closest_brand,
                "distance": min_distance,
            }

        return None

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy"""
        if not text:
            return 0.0

        counts = Counter(text)
        length = len(text)
        entropy = 0.0

        for count in counts.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy

    def _extract_fqdn_features(self, domain: str) -> Dict[str, float]:
        """Extract FQDN features (4 features)"""
        domain_name = self._extract_domain_label(domain)

        features = {
            "domain_length": len(domain_name),
            "subdomain_count": domain.count("."),
            "numeric_chars": sum(c.isdigit() for c in domain_name),
            "entropy": self._calculate_entropy(domain_name),
        }

        return features

    def _extract_typosquatting_features(self, domain: str) -> Dict[str, float]:
        """Extract typosquatting features (7 features)"""
        domain_name = self._extract_domain_label(domain)

        distances = [
            self._calculate_edit_distance(domain_name, brand)
            for brand in self.TOP_BRANDS
        ]
        min_distance = min(distances)
        closest_brand_idx = distances.index(min_distance)
        closest_brand = self.TOP_BRANDS[closest_brand_idx]

        features = {
            "min_edit_distance": min_distance,
            "edit_distance_ratio": (
                min_distance / len(closest_brand) if len(closest_brand) > 0 else 0
            ),
            "length_diff_to_closest": abs(len(domain_name) - len(closest_brand)),
            "has_extra_char": (
                1 if min_distance == 1 and len(domain_name) > len(closest_brand) else 0
            ),
            "has_missing_char": (
                1 if min_distance == 1 and len(domain_name) < len(closest_brand) else 0
            ),
            "has_swapped_char": 1 if min_distance == 2 else 0,
            "digit_substitution": (
                1 if any(c.isdigit() for c in domain_name) and min_distance <= 2 else 0
            ),
        }

        return features

    def _extract_all_features(self, domain: str) -> pd.DataFrame:
        """Extract all 11 features for ML model"""
        fqdn_features = self._extract_fqdn_features(domain)
        typo_features = self._extract_typosquatting_features(domain)

        all_features = {**fqdn_features, **typo_features}

        feature_names = [
            "domain_length",
            "subdomain_count",
            "numeric_chars",
            "entropy",
            "min_edit_distance",
            "edit_distance_ratio",
            "length_diff_to_closest",
            "has_extra_char",
            "has_missing_char",
            "has_swapped_char",
            "digit_substitution",
        ]

        return pd.DataFrame([all_features], columns=feature_names)

    def _predict_lstm(self, domain: str) -> float:
        """Get LSTM prediction probability"""
        domain_name = self._extract_domain_label(domain)
        tokens = self.tokenizer.texts_to_sequences([domain_name])

        max_len = 64
        padded = torch.zeros((1, max_len), dtype=torch.long)
        token_len = min(len(tokens[0]), max_len)
        if token_len > 0:
            padded[0, :token_len] = torch.tensor(tokens[0][:token_len])

        with torch.no_grad():
            output = self.lstm_model(padded)
            probabilities = torch.softmax(output, dim=1)
            malicious_prob = probabilities[0][1].item()

        return malicious_prob

    def _predict_lgbm(self, domain: str) -> float:
        """Get LightGBM prediction probability"""
        features = self._extract_all_features(domain)
        probabilities = self.lgbm_model.predict_proba(features)
        return probabilities[0][1]

    def _predict_ensemble(self, domain: str) -> Tuple[str, float]:
        """Get ensemble prediction using meta-learner"""
        lstm_prob = self._predict_lstm(domain)
        lgbm_prob = self._predict_lgbm(domain)

        meta_input = np.array([[lgbm_prob, lstm_prob]])
        prediction = self.meta_learner.predict(meta_input)[0]

        if hasattr(self.meta_learner, "predict_proba"):
            probabilities = self.meta_learner.predict_proba(meta_input)
            confidence = probabilities[0][
                int(prediction)
            ]  # Convert to int for indexing
        else:
            confidence = max(lgbm_prob, lstm_prob)

        prediction_label = "MALICIOUS" if prediction == 1 else "BENIGN"
        return prediction_label, confidence

    def predict(self, domain: str) -> Dict:
        """
        Predict if domain is malicious, suspicious, or benign (3-tier classification)

        Prediction flow (v1.0.5 - FIXED):
        1. Check reserved TLDs (.test, .example, .local, .internal, etc.) -> BENIGN [NEW]
        2. Check safelist (if enabled) -> BENIGN
        3. Check exact brand match -> BENIGN
        4. Check typosquatting (distance 1-3) -> MALICIOUS
        5. Check suspicious patterns (with PaaS exception) -> SUSPICIOUS [IMPROVED]
        6. Use ML ensemble -> MALICIOUS/BENIGN

        **v1.0.5 CRITICAL FIXES**:
        - Reserved TLDs (RFC 2606) are now always BENIGN (highest priority)
        - Trusted PaaS domains (.herokuapp.com, .github.io, etc.) no longer flagged
        - Reduced false positives on internal/developer domains

        Args:
            domain: Domain name to classify

        Returns:
            {
                'prediction': 'MALICIOUS' or 'SUSPICIOUS' or 'BENIGN',
                'confidence': float (0.0 to 1.0),
                'reason': str (human-readable explanation),
                'method': str (detection method used),
                'latency_ms': float (inference time in milliseconds),
                'suspicious_score': int (optional, if SUSPICIOUS),
                'suspicious_signals': dict (optional, if SUSPICIOUS)
            }
        """
        start_time = time.time()
        self.prediction_count += 1

        domain = domain.lower().strip()

        # **PRIORITY 1**: Check reserved/non-routable TLDs (RFC 2606, RFC 6762, RFC 6761)
        # These are ALWAYS benign (test/documentation/private use)
        is_reserved, reserved_tld = self._is_reserved_tld(domain)
        if is_reserved:
            return {
                "prediction": "BENIGN",
                "confidence": 1.0,
                "reason": f"Reserved TLD '.{reserved_tld}' (RFC 2606/6762/6761 - test/documentation/private use)",
                "method": "reserved_tld_rule",
                "latency_ms": (time.time() - start_time) * 1000,
            }

        # **PRIORITY 2**: Check safelist
        if self._is_safelisted(domain):
            self.safelist_hits += 1
            return {
                "prediction": "BENIGN",
                "confidence": 1.0,
                "reason": f"Domain in safelist",
                "method": "safelist",
                "latency_ms": (time.time() - start_time) * 1000,
            }

        # **PRIORITY 3**: Check exact brand match
        typo_result = self._check_typosquatting(domain)

        if typo_result:
            if typo_result["is_brand"]:
                self.brand_whitelist_hits += 1
                return {
                    "prediction": "BENIGN",
                    "confidence": 1.0,
                    "reason": f'Exact match to brand: {typo_result["brand"]}',
                    "method": "brand_whitelist",
                    "latency_ms": (time.time() - start_time) * 1000,
                }
            elif typo_result["is_typosquatting"]:
                # **PRIORITY 4**: Typosquatting detection
                self.typosquatting_hits += 1

                # Enhanced confidence calculation for repetition-based attacks
                if (
                    "reason" in typo_result
                    and "excessive_repetition" in typo_result["reason"]
                ):
                    # High confidence for excessive repetition attacks
                    confidence = 0.95
                    reason = f'Character repetition attack on brand "{typo_result["brand"]}" ({typo_result["repetition_details"]["char"]} repeated {typo_result["repetition_details"]["count"]} times)'
                else:
                    # Standard typosquatting confidence
                    confidence = 1.0 - (typo_result["distance"] / 10)
                    reason = f'Typosquatting (dist={typo_result["distance"]} to {typo_result["brand"]})'

                return {
                    "prediction": "MALICIOUS",
                    "confidence": confidence,
                    "reason": reason,
                    "method": "typosquatting_rule",
                    "latency_ms": (time.time() - start_time) * 1000,
                }

        # **PRIORITY 5**: Check for suspicious patterns (with PaaS exception)
        if self.enable_suspicious_detection:
            suspicious_analysis = self._calculate_suspicious_score(domain)

            # If domain has brand+service tokens (classic phishing pattern)
            # BUT not if it's a reserved TLD or trusted PaaS domain
            if suspicious_analysis["classification"] == "SUSPICIOUS":
                self.suspicious_detections += 1

                # Build detailed reason
                signals = suspicious_analysis["signals"]
                reason_parts = []

                if "brand_token_exact" in signals:
                    reason_parts.append(f"brand '{signals['brand_token_exact']}'")
                elif "brand_lev2" in signals:
                    reason_parts.append(f"brand variant of '{signals['brand_lev2']}'")

                if "service_tokens" in signals:
                    reason_parts.append(
                        f"service keywords: {', '.join(signals['service_tokens'])}"
                    )

                if "suspicious_tld" in signals:
                    reason_parts.append(
                        f"suspicious TLD '.{signals['suspicious_tld']}'"
                    )

                if "high_entropy" in signals:
                    reason_parts.append(f"high entropy ({signals['high_entropy']})")

                reason = f"Suspicious: {' + '.join(reason_parts)} (score: {suspicious_analysis['score']})"

                return {
                    "prediction": "SUSPICIOUS",
                    "confidence": min(
                        0.80 + (suspicious_analysis["score"] - 60) / 200, 0.95
                    ),
                    "reason": reason,
                    "method": "suspicious_rule",
                    "suspicious_score": suspicious_analysis["score"],
                    "suspicious_signals": signals,
                    "latency_ms": (time.time() - start_time) * 1000,
                }

        # **PRIORITY 6**: Use ML ensemble for final classification
        self.ensemble_predictions += 1
        prediction, confidence = self._predict_ensemble(domain)

        reason = "ML ensemble prediction"
        if prediction == "MALICIOUS":
            reason = "Detected as DGA or malware domain"
        else:
            reason = "Classified as legitimate domain"

        return {
            "prediction": prediction,
            "confidence": confidence,
            "reason": reason,
            "method": "ensemble",
            "latency_ms": (time.time() - start_time) * 1000,
        }

    def predict_batch(self, domains: List[str]) -> List[Dict]:
        """Predict multiple domains"""
        return [self.predict(domain) for domain in domains]

    def get_model_info(self) -> Dict:
        """Get model information and statistics"""
        return {
            "model_name": "DNS_ThreatDetector",
            "version": "1.0.5",
            "classification_tiers": 3 if self.enable_suspicious_detection else 2,
            "components": {
                "lstm": "Bidirectional LSTM (159K params)",
                "lgbm": "LightGBM with 11 features",
                "meta_learner": "Logistic Regression",
                "typosquatting": "Rule-based + ML hybrid",
                "suspicious_detection": (
                    "Enabled" if self.enable_suspicious_detection else "Disabled"
                ),
                "safelist": (
                    "Multi-tier (O(1) lookup)" if self.use_safelist else "Disabled"
                ),
                "reserved_tld_protection": f"{len(self.RESERVED_TLDS)} reserved TLDs",
                "paas_exceptions": f"{len(self.TRUSTED_PAAS_DOMAINS)} trusted platforms",
            },
            "performance": {
                "f1_score": 0.9968,
                "accuracy": 0.9938,
                "precision": 0.9715,
                "recall": 0.9995,
                "typosquatting_detection": 1.0,
                "avg_latency_ms": 0.439,
            },
            "features": {
                "fqdn_features": 4,
                "typosquatting_features": 7,
                "total_features": 11,
            },
            "suspicious_detection": {
                "enabled": self.enable_suspicious_detection,
                "service_tokens": len(self.SERVICE_TOKENS),
                "suspicious_tlds": len(self.SUSPICIOUS_TLDS),
                "scoring_threshold": 60,
            },
            "safelist": self.safelist_stats,
            "protected_brands": len(self.TOP_BRANDS),
            "reserved_tlds": {
                "count": len(self.RESERVED_TLDS),
                "tlds": self.RESERVED_TLDS,
                "description": "RFC 2606/6762/6761 reserved for testing/documentation/private use",
            },
            "trusted_paas_domains": {
                "count": len(self.TRUSTED_PAAS_DOMAINS),
                "description": "Developer/PaaS platforms with reduced false positive rates",
            },
            "usage_statistics": {
                "total_predictions": self.prediction_count,
                "safelist_hits": self.safelist_hits,
                "brand_whitelist_hits": self.brand_whitelist_hits,
                "typosquatting_detections": self.typosquatting_hits,
                "suspicious_detections": self.suspicious_detections,
                "ensemble_predictions": self.ensemble_predictions,
            },
            "v1_0_5_improvements": {
                "reserved_tld_fix": "Added highest-priority rule for RFC 2606 reserved TLDs",
                "paas_exception_fix": "Trusted PaaS domains no longer flagged as suspicious",
                "false_positive_reduction": "Reduced FP on internal/developer domains with lexical cues",
                "backward_compatible": "Output format unchanged for existing integrations",
            },
        }

    def save_metadata(self, output_path: str):
        """Save model metadata to JSON"""
        metadata = self.get_model_info()

        with open(output_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"Metadata saved to: {output_path}")
