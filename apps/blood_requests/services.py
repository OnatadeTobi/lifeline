from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from apps.donors.models import Donor
from apps.core.blood_compatibility import BloodCompatibility

import logging

logger = logging.getLogger('apps.blood_requests')

class DonorMatchingService:
    @staticmethod
    def find_compatible_donors(blood_request):
        """
        Find donors who:
        1. Have compatible blood type
        2. Are available and eligible (past 56-day cooldown)
        3. Are verified
        4. Service locations overlap with hospital's service locations
        """
        hospital = blood_request.hospital
        required_blood_type = blood_request.blood_type

        logger.info(
            f"Finding compatible donors for BloodRequest ID: {blood_request.id}, "
            f"Hospital: {hospital.name}, Required Type: {required_blood_type}"
        )

        try:
            # Get compatible blood types
            compatible_types = BloodCompatibility.get_compatible_donor_types(required_blood_type)
            logger.debug(f"Compatible blood types for {required_blood_type}: {compatible_types}")
            
            # Get hospital's service locations
            hospital_service_areas = hospital.service_locations.all()
            logger.debug(f"Hospital {hospital.name} has {hospital_service_areas.count()} service locations")
            
            # Build query
            today = timezone.now().date()
            
            matching_donors = Donor.objects.filter(
                blood_type__in=compatible_types,
                is_available=True,
                user__is_verified=True,
                service_locations__in=hospital_service_areas
            ).filter(
                Q(available_from__isnull=True) | Q(available_from__lte=today)
            ).distinct()
            
            return matching_donors
        
        except Exception as e:
            logger.exception(f"Error finding compatible donors for BloodRequest ID: {blood_request.id} - {str(e)}")
            return Donor.objects.none()
        
        
    
    @staticmethod
    def set_donor_cooldown(donor):
        """Set 56-day cooldown after donation acceptance"""
        from django.utils import timezone

        logger.info(f"Setting cooldown for donor {donor.user.email}")

        try:
            donor.is_available = False
            donor.last_donation_date = timezone.now() # Changed: removed .date()
            donor.available_from = (timezone.now() + timedelta(days=56)).date() #donor.available_from = donor.last_donation_date + timedelta(days=56)
            donor.save()

            logger.info(
                    f"Cooldown set successfully - Donor: {donor.user.email}, "
                    f"Available from: {donor.available_from}"
                )
            
        except Exception as e:
            logger.exception(
                f"Failed to set cooldown for donor {donor.user.email}: {str(e)}"
            )
            raise