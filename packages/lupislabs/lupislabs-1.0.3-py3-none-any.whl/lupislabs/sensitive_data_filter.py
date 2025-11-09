import re
import json
from typing import Any, Dict, List, Union
from .types import SensitiveDataFilter


class SensitiveDataFilterUtil:
    def __init__(self, filter_config: SensitiveDataFilter):
        self.filter = filter_config
        self.default_patterns = [
            # API Keys
            r'sk-[a-zA-Z0-9]{20,}',
            r'pk_[a-zA-Z0-9]{20,}',
            r'ak-[a-zA-Z0-9]{20,}',
            r'Bearer [a-zA-Z0-9._-]+',
            r'x-api-key',
            r'authorization',
            
            # Tokens
            r'token',
            r'access_token',
            r'refresh_token',
            r'session_token',
            
            # Passwords
            r'password',
            r'passwd',
            r'pwd',
            
            # Secrets
            r'secret',
            r'private_key',
            r'privateKey',
            r'api_secret',
            r'apiSecret',
            
            # Personal Data
            r'ssn',
            r'social_security',
            r'credit_card',
            r'card_number',
            r'cvv',
            r'cvc',
        ]
        
        # Use custom patterns if provided, otherwise use defaults
        if filter_config.sensitive_data_patterns and len(filter_config.sensitive_data_patterns) > 0:
            self.patterns = filter_config.sensitive_data_patterns
        else:
            self.patterns = self.default_patterns

    def filter_object(self, obj: Any) -> Any:
        """Filter sensitive data from any object recursively."""
        if not self.filter.filter_sensitive_data:
            return obj

        if isinstance(obj, str):
            return self._filter_string(obj)

        if isinstance(obj, list):
            return [self.filter_object(item) for item in obj]

        if isinstance(obj, dict):
            filtered = {}
            for key, value in obj.items():
                if self._is_sensitive_key(key):
                    filtered[key] = self._get_redacted_value()
                else:
                    filtered[key] = self.filter_object(value)
            return filtered

        return obj

    def _filter_string(self, text: str) -> str:
        """Filter sensitive data from a string."""
        if not self.filter.filter_sensitive_data:
            return text

        filtered = text
        for pattern in self.patterns:
            regex = re.compile(pattern, re.IGNORECASE)
            filtered = regex.sub(lambda match: self._get_redacted_value(match.group()), filtered)

        return filtered

    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a key is sensitive based on patterns."""
        lower_key = key.lower()
        for pattern in self.patterns:
            if re.search(pattern, lower_key, re.IGNORECASE):
                return True
        return False

    def _get_redacted_value(self, original: str = None) -> str:
        """Get redacted value based on redaction mode."""
        if self.filter.redaction_mode == "remove":
            return "[REDACTED]"
        elif self.filter.redaction_mode == "hash":
            if original:
                # Simple hash for debugging (not cryptographically secure)
                hash_value = hash(original) & 0xFFFFFFFF
                return f"[HASH:{hash_value:08x}]"
            return "[HASHED]"
        else:  # mask
            if original and len(original) > 8:
                # Show first 4 and last 4 characters
                start = original[:4]
                end = original[-4:]
                return f"{start}***{end}"
            return "***"

    def filter_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Filter sensitive data from HTTP headers."""
        if not self.filter.filter_sensitive_data:
            return headers

        filtered = {}
        for key, value in headers.items():
            if self._is_sensitive_key(key):
                filtered[key] = self._get_redacted_value(value)
            else:
                filtered[key] = self._filter_string(value)

        return filtered

    def filter_request_body(self, body: str) -> str:
        """Filter sensitive data from request body."""
        if not self.filter.filter_sensitive_data:
            return body

        try:
            parsed = json.loads(body)
            filtered = self.filter_object(parsed)
            return json.dumps(filtered)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, filter as string
            return self._filter_string(body)

    def filter_response_body(self, body: str) -> str:
        """Filter sensitive data from response body."""
        return self.filter_request_body(body)  # Same logic for request/response
