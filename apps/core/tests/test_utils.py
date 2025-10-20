"""
Test suite for core utilities.
"""
import pytest
from apps.core.utils import mask_email
from apps.core.blood_compatibility import BloodCompatibility

class TestEmailMasking:
    @pytest.mark.parametrize("email,expected", [
        ("test@example.com", "t**t@example.com"),
        ("john.doe@test.com", "j**n.doe@test.com"),
        ("a@b.com", "a@b.com"),
        ("short@test.com", "s**rt@test.com"),
    ])
    def test_mask_email(self, email, expected):
        """Test email masking with various email formats"""
        assert mask_email(email) == expected


class TestBloodCompatibility:
    def test_get_compatible_donor_types_returns_correct_list(self):
        """Ensure each blood type returns correct compatible donor types"""
        expected = {
            'O-': ['O-'],
            'O+': ['O-', 'O+'],
            'A-': ['O-', 'A-'],
            'A+': ['O-', 'O+', 'A-', 'A+'],
            'B-': ['O-', 'B-'],
            'B+': ['O-', 'O+', 'B-', 'B+'],
            'AB-': ['O-', 'A-', 'B-', 'AB-'],
            'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        }

        for blood_type, expected_donors in expected.items():
            result = BloodCompatibility.get_compatible_donor_types(blood_type)
            assert set(result) == set(expected_donors), f"Mismatch for {blood_type}"

    def test_get_compatible_donor_types_returns_empty_for_invalid_type(self):
        """Should return an empty list for invalid blood types"""
        assert BloodCompatibility.get_compatible_donor_types('X+') == []

    @pytest.mark.parametrize(
        "donor,recipient,expected", [
            ('O-', 'O-', True),
            ('O-', 'A+', True),
            ('A-', 'B+', False),
            ('B+', 'AB+', True),
            ('AB-', 'A-', False),
            ('O+', 'O-', False),
            ('AB+', 'AB+', True),
        ]
    )
    def test_can_donate_to(self, donor, recipient, expected):
        """Test donation compatibility logic"""
        result = BloodCompatibility.can_donate_to(donor, recipient)
        assert result == expected, f"Failed for donor={donor}, recipient={recipient}"