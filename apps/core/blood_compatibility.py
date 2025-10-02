class BloodCompatibility:
    """
    Blood type donation compatibility matrix
    Key: Blood type that CAN RECEIVE from value list
    """
    COMPATIBILITY = {
        'O-': ['O-'],
        'O+': ['O-', 'O+'],
        'A-': ['O-', 'A-'],
        'A+': ['O-', 'O+', 'A-', 'A+'],
        'B-': ['O-', 'B-'],
        'B+': ['O-', 'O+', 'B-', 'B+'],
        'AB-': ['O-', 'A-', 'B-', 'AB-'],
        'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],  # Universal receiver
    }
    
    @classmethod
    def get_compatible_donor_types(cls, recipient_blood_type):
        """
        Get list of blood types that can donate to recipient
        e.g. A+ can receive from: O-, O+, A-, A+
        """
        return cls.COMPATIBILITY.get(recipient_blood_type, [])
    
    @classmethod
    def can_donate_to(cls, donor_blood_type, recipient_blood_type):
        """Check if donor can give to recipient"""
        return donor_blood_type in cls.get_compatible_donor_types(recipient_blood_type)