"""
Pytest tests for Glassbox utility functions.
"""

import pytest
from glassbox_sdk.utils import (
    calculate_cost,
    extract_tokens,
    extract_model,
    generate_prompt_id,
    get_timestamp,
    validate_output
)


class TestCalculateCost:
    """Test cost calculation."""
    
    def test_gpt4_cost(self):
        """Test GPT-4 cost calculation."""
        cost = calculate_cost("gpt-4", 1000, 500)
        # GPT-4: $0.03/1k input, $0.06/1k output
        expected = (1000 * 0.03 / 1000) + (500 * 0.06 / 1000)
        assert abs(cost - expected) < 0.0001
    
    def test_gpt35_cost(self):
        """Test GPT-3.5 cost calculation."""
        cost = calculate_cost("gpt-3.5-turbo", 1000, 500)
        # GPT-3.5: $0.0015/1k input, $0.002/1k output
        expected = (1000 * 0.0015 / 1000) + (500 * 0.002 / 1000)
        assert abs(cost - expected) < 0.0001
    
    def test_unknown_model_fallback(self):
        """Test unknown model uses fallback pricing."""
        cost = calculate_cost("unknown-model", 1000, 500)
        # Fallback: $0.002/1k total
        expected = (1000 + 500) * 0.002 / 1000
        assert abs(cost - expected) < 0.0001
    
    def test_partial_match(self):
        """Test partial model name matching."""
        cost = calculate_cost("gpt-4-0125", 1000, 500)
        # Should match "gpt-4" pricing
        expected = (1000 * 0.03 / 1000) + (500 * 0.06 / 1000)
        assert abs(cost - expected) < 0.0001


class TestExtractTokens:
    """Test token extraction."""
    
    def test_openai_format(self):
        """Test OpenAI response format."""
        class Usage:
            prompt_tokens = 100
            completion_tokens = 50
        
        class Response:
            usage = Usage()
        
        input_tokens, output_tokens = extract_tokens(Response())
        assert input_tokens == 100
        assert output_tokens == 50
    
    def test_dict_format(self):
        """Test dictionary response format."""
        response = {
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50
            }
        }
        input_tokens, output_tokens = extract_tokens(response)
        assert input_tokens == 100
        assert output_tokens == 50
    
    def test_no_usage(self):
        """Test response without usage info."""
        response = {}
        input_tokens, output_tokens = extract_tokens(response)
        assert input_tokens == 0
        assert output_tokens == 0


class TestExtractModel:
    """Test model extraction."""
    
    def test_model_attribute(self):
        """Test model from attribute."""
        class Response:
            model = "gpt-4"
        
        model = extract_model(Response(), "default")
        assert model == "gpt-4"
    
    def test_model_dict(self):
        """Test model from dictionary."""
        response = {"model": "gpt-4"}
        model = extract_model(response, "default")
        assert model == "gpt-4"
    
    def test_default_fallback(self):
        """Test default fallback."""
        response = {}
        model = extract_model(response, "default-model")
        assert model == "default-model"


class TestValidateOutput:
    """Test output validation."""
    
    def test_openai_valid(self):
        """Test valid OpenAI response."""
        class Choice:
            pass
        
        class Response:
            choices = [Choice(), Choice()]
        
        assert validate_output(Response()) is True
    
    def test_dict_valid(self):
        """Test valid dictionary response."""
        response = {"choices": [{"text": "hello"}]}
        assert validate_output(response) is True
    
    def test_string_valid(self):
        """Test valid string response."""
        assert validate_output("hello world") is True
    
    def test_none_invalid(self):
        """Test None is invalid."""
        assert validate_output(None) is False
    
    def test_empty_invalid(self):
        """Test empty response is invalid."""
        assert validate_output("") is False


class TestGeneratePromptId:
    """Test prompt ID generation."""
    
    def test_generates_uuid(self):
        """Test generates UUID string."""
        prompt_id = generate_prompt_id()
        assert isinstance(prompt_id, str)
        assert len(prompt_id) == 36  # UUID format
    
    def test_unique_ids(self):
        """Test generates unique IDs."""
        id1 = generate_prompt_id()
        id2 = generate_prompt_id()
        assert id1 != id2


class TestGetTimestamp:
    """Test timestamp generation."""
    
    def test_generates_iso_format(self):
        """Test generates ISO format timestamp."""
        timestamp = get_timestamp()
        assert isinstance(timestamp, str)
        assert 'T' in timestamp or 'Z' in timestamp or '+' in timestamp

