from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import BloodRequest, DonorResponse
from .serializers import (
    BloodRequestCreateSerializer,
    BloodRequestSerializer,
    DonorResponseSerializer
)
from .services import DonorMatchingService
from rest_framework.views import APIView
from rest_framework import exceptions

import logging
logger = logging.getLogger('apps.blood_requests')

class BloodRequestCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BloodRequestCreateSerializer
    
    def perform_create(self, serializer):
        user = self.request.user
        logger.info(f"BloodRequestCreateView triggered by user: {user.email}")

        try:
            blood_request = serializer.save()
            logger.info(f"Blood request created successfully - ID: {blood_request.id}, Hospital: {blood_request.hospital.name}")

            # Find and notify matching donors
            matching_donors = DonorMatchingService.find_compatible_donors(blood_request)
            logger.info(f"Found {len(matching_donors)} matching donors for request ID: {blood_request.id}")

            if not matching_donors:
                logger.warning(f"No matching donors found for blood type {blood_request.blood_type}")


            for donor in matching_donors:
                self.send_donor_notification(donor, blood_request)
                logger.info(f"Notification sent to donor: {donor.user.email} for request ID: {blood_request.id}")

            return blood_request
        
        except Exception as e:
            logger.exception(f"Unexpected error creating blood request: {str(e)}")
            raise

    
    def send_donor_notification(self, donor, request):

        user = self.request.user
        logger.debug(f"Preparing donor notification - Donor: {donor.user.email}, Request ID: {request.id}")

        """Send email notification to donor"""
        try:
            subject = f"Urgent: {request.blood_type} Blood Needed"
            message = f"""
            Hello {donor.user.first_name},
            
            A blood request has been posted that matches your profile:
            
            Blood Type: {request.blood_type}
            Hospital: {request.hospital.name}
            Address: {request.hospital.address}
            Location: {request.hospital.primary_location.name}
            Contact: {request.contact_phone}
            
            If you can donate, please accept this request:
            Accept Link: {settings.FRONTEND_URL}/requests/{request.id}/accept/
            
            Thank you for being a lifesaver!
            """
            logger.info(f"Sending email to donor: {donor.user.email} - Subject: {subject}")

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [donor.user.email],
                fail_silently=True
            )
            logger.info(f"Email successfully sent to donor: {donor.user.email}")

        except Exception as e:
            logger.error(f"Failed to send email to donor: {donor.user.email} - {str(e)}")
            logger.exception(e)






class BloodRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BloodRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        logger.info(f"BloodRequestListView accessed by user: {user.email} (role: {user.role})")


        try:
            if user.role == 'HOSPITAL':
                
                # Get hospital profile safely
                hospital = getattr(user, 'hospital_profile', None)
                
                if not hospital:
                    logger.error(f"Hospital profile not found for user {user.email}")
                    return BloodRequest.objects.none()
                
                # Hospitals see their own requests
                queryset = BloodRequest.objects.filter(hospital=hospital)
                logger.info(f"Hospital user {user.email} retrieving {queryset.count()} blood requests.")
                return queryset
            
            elif user.role == 'DONOR':
                # Get donor profile safely
                donor = getattr(user, 'donor', None)
                
                if not donor:
                    logger.error(f"Donor profile not found for user {user.email}")
                    return BloodRequest.objects.none()
                
                # Donors see open requests in their service areas
                donor_service_areas = donor.service_locations.all()
                logger.debug(f"Donor {user.email} service areas: {[loc.name for loc in donor_service_areas]}")

                
                from apps.core.blood_compatibility import BloodCompatibility
                compatible_types = BloodCompatibility.get_compatible_donor_types(donor.blood_type)
                logger.debug(f"Donor {user.email} compatible blood types: {compatible_types}")
                
                queryset = BloodRequest.objects.filter(
                    status='OPEN',
                    hospital__service_locations__in=donor_service_areas,
                    blood_type__in=compatible_types
                ).distinct()

                logger.info(f"Donor {user.email} retrieving {queryset.count()} open compatible blood requests.")
                return queryset
            
            logger.warning(f"User {user.email} with unrecognized role '{user.role}' attempted to list blood requests.")
            return BloodRequest.objects.none()
        
        except Exception as e:
            logger.exception(f"Unexpected error retrieving blood requests for user {user.email}: {str(e)}")
            raise
        
        







class BloodRequestDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BloodRequestSerializer
    queryset = BloodRequest.objects.all()



# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def accept_request(request, request_id):
#     """Donor accepts a blood request"""

#     # Log the incoming request
#     logger.info(
#         f"Donation Accept attempt - User: {request.user.email}, "
#         f"Request ID: {request_id}"
#     )

#     # --- Explicit Role & Profile Check ---

#     if not hasattr(request.user, 'role') or request.user.role != 'DONOR':
#         logger.warning(
#             f"Unauthorized donation Accept Request by {request.user.email} "
#             f"(role: {getattr(request.user, 'role', 'unknown')})"
#         )
        
#         return Response(
#             {'detail': 'Forbidden: Only donors can accept requests'},
#             status=status.HTTP_403_FORBIDDEN
#         )
    
#     donor = getattr(request.user, 'donor', None)
#     if not donor:
#         return Response(
#             {'detail': 'Donor profile not found'},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     try:
#         blood_request = BloodRequest.objects.get(id=request_id)
#         donor = request.user.donor
        
#         # Check if donor is eligible
#         if not donor.is_eligible_to_donate:
#             return Response(
#                 {'error': 'You are not eligible to donate yet (56-day cooldown)'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         # Create donor response
#         donor_response, created = DonorResponse.objects.get_or_create(
#             request=blood_request,
#             donor=donor
#         )
        
#         if not created:
#             return Response({'message': 'You have already accepted this request'})
        
#         # Update request status
#         blood_request.status = 'MATCHED'
#         blood_request.save()
        
#         # Set donor cooldown
#         #DonorMatchingService.set_donor_cooldown(donor)
        
#         # Notify hospital
#         send_mail(
#             subject=f"Donor Accepted: {blood_request.blood_type} Request",
#             message=f"""
#             Good news! A donor has accepted your blood request.
            
#             Donor Phone: {donor.phone}
#             Blood Type: {donor.blood_type}
#             Accepted At: {donor_response.accepted_at}
            
#             Please contact them immediately at {donor.phone}
#             """,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[blood_request.hospital.user.email],
#             fail_silently=True
#         )
        
#         return Response({
#             'message': 'Request accepted successfully',
#         })
        
#     except BloodRequest.DoesNotExist:
#         return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class AcceptRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        """Donor accepts a blood request"""

        user = request.user
        logger.info(f"Donation Accept attempt - User: {user.email}, Request ID: {request_id}")

        # Role & Profile Check
        if not hasattr(user, 'role') or user.role != 'DONOR':
            logger.warning(f"Unauthorized donation accept attempt by {user.email} (role: {getattr(user, 'role', 'unknown')})")
            return Response(
                {'detail': 'Forbidden: Only donors can accept requests'},
                status=status.HTTP_403_FORBIDDEN
            )

        donor = getattr(user, 'donor', None)
        if not donor:
            return Response(
                {'detail': 'Donor profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            blood_request = BloodRequest.objects.get(id=request_id)

            # Eligibility check
            if not donor.is_eligible_to_donate:

                logger.warning(
                f"Donor {request.user.email} tried to accept request {request_id} "
                f"but is ineligible due to 56-day cooldown"
                )

                return Response(
                    {'error': 'You are not eligible to donate yet (56-day cooldown)'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            donor_response, created = DonorResponse.objects.get_or_create(
                request=blood_request,
                donor=donor
            )

            if not created:
                logger.warning(f"Donor {request.user.email} tried to accept request {request_id} again ")
                return Response({'message': 'You have already accepted this request'})

            # Update blood request status
            blood_request.status = 'MATCHED'
            blood_request.save()

            # Optional donor cooldown logic
            # DonorMatchingService.set_donor_cooldown(donor)

            # Notify hospital
            send_mail(
                subject=f"Donor Accepted: {blood_request.blood_type} Request",
                message=f"""
                Good news! A donor has accepted your blood request.

                Donor Phone: {donor.phone}
                Blood Type: {donor.blood_type}
                Accepted At: {donor_response.accepted_at}

                Please contact them immediately at {donor.phone}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[blood_request.hospital.user.email],
                fail_silently=True
            )

            logger.info(
            f"Request {request_id} successfully accepted by donor {request.user.email}"
            )
            
            return Response({'message': 'Request accepted successfully'})

        except BloodRequest.DoesNotExist:
            logger.error(f"Request not found: ID={request_id} (by {request.user.email})")
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.warning(
                f"Unexpected error in accept_request (User: {request.user.email}, "
                f"Request ID: {request_id}): {str(e)}"
            )
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_fulfilled(request, request_id):
    """Hospital marks request as fulfilled"""

    user_email = getattr(request.user, 'email', 'Unknown')
    user_role = getattr(request.user, 'role', 'Unknown')

    # --- Explicit Role & Profile Check ---
    if not hasattr(request.user, 'role') or request.user.role != 'HOSPITAL':
        logger.warning(f"Unauthorized mark_fulfilled attempt by user {user_email} with role {user_role}.")
        return Response(
            {'detail': 'Forbidden: Only hospitals can mark requests as fulfilled'},
            status=status.HTTP_403_FORBIDDEN
        )

    hospital = getattr(request.user, 'hospital_profile', None)
    if not hospital:
        logger.error(f"Hospital profile missing for user {user_email}.")
        return Response(
            {'detail': 'Hospital profile not found'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        blood_request = BloodRequest.objects.get(
            id=request_id,
            hospital=hospital
        )
        blood_request.status = 'FULFILLED'
        blood_request.save()

        logger.info(
            f"BloodRequest {request_id} marked as fulfilled by hospital {hospital.name} ({user_email})."
        )
        
        return Response({'message': 'Request marked as fulfilled'})
        
    except BloodRequest.DoesNotExist:
        logger.info(f"BloodRequest {request_id} marked as fulfilled by hospital {hospital.name} ({user_email}).")
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.exception(f"Unexpected error fulfilling request {request_id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_donation(request, request_id, response_id):
    """Hospital confirms that a donor actually donated using the DonorResponse id."""

    # Log the incoming request
    logger.info(
        f"Donation confirmation attempt - User: {request.user.email}, "
        f"Request ID: {request_id}, Response ID: {response_id}"
    )
    
    # Ensure only hospitals can call this
    if not hasattr(request.user, 'role') or request.user.role != 'HOSPITAL':
        logger.warning(
            f"Unauthorized donation confirmation attempt by {request.user.email} "
            f"(role: {getattr(request.user, 'role', 'unknown')})"
        )
        return Response({'detail': 'Forbidden: Only hospitals can confirm donations.'}, status=403)
    
    hospital = getattr(request.user, 'hospital_profile', None)
    if not hospital:
        logger.error(f"Hospital profile not found for user {request.user.email}")
        return Response({'detail': 'Hospital profile not found.'}, status=400)

    try:
        blood_request = BloodRequest.objects.get(id=request_id, hospital=hospital)
        logger.debug(f"Blood request {request_id} found for hospital {hospital.name}")
        
    except BloodRequest.DoesNotExist:
        logger.error(
            f"Blood request {request_id} not found for hospital {hospital.name} "
            f"(ID: {hospital.id})"
        )
        return Response({'error': 'Request not found.'}, status=404)

    try:
        donor_response = DonorResponse.objects.get(request=blood_request, id=response_id)
        logger.debug(
            f"Donor response {response_id} found for donor "
            f"{donor_response.donor.user.email}"
        )
    except DonorResponse.DoesNotExist:
        logger.error(
            f"Donor response {response_id} not found for request {request_id}"
        )
        return Response({'error': 'Donor response not found.'}, status=404)

    try:
        # Apply donor cooldown
        DonorMatchingService.set_donor_cooldown(donor_response.donor)
        
        # Optionally mark response as processed (no 'fulfilled' field expected on model)
        # If you need to track that, add a BooleanField to DonorResponse model (e.g. 'processed')
        # donor_response.processed = True
        # donor_response.save(update_fields=['processed'])
        
        # Optionally check if all donors have donated
        # If you only needed one, mark request as fulfilled
        blood_request.status = BloodRequest.RequestStatus.FULFILLED
        blood_request.save(update_fields=['status'])

        return Response({'message': 'Donation confirmed and donor cooldown applied.'})
    
    except Exception as e:
        # This logs the full stack trace
        logger.exception(
            f"Unexpected error confirming donation - Request: {request_id}, "
            f"Response: {response_id}, Error: {str(e)}"
        )
        return Response(
            {'error': 'Internal server error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )





class DonorResponseListView(generics.ListAPIView):
    """List all donors who responded to a specific request (Hospital only)"""
    permission_classes = [IsAuthenticated]
    serializer_class = DonorResponseSerializer
    
    def get_queryset(self):
        user = self.request.user
        request_id = self.kwargs.get('request_id')
        hospital = getattr(self.request.user, 'hospital_profile', None)

        logger.info(f"DonorResponseListView triggered by user: {user.email}, request_id={request_id}")

        if not hospital:
            logger.warning(f"DonorResponseListView triggered by user: {user.email}, request_id={request_id}")
            raise exceptions.PermissionDenied('Only hospitals can view donor responses.')

        queryset = DonorResponse.objects.filter(
            request_id=request_id,
            request__hospital=hospital
        )

        response_count = queryset.count()
        logger.debug(f"Hospital {hospital.name} retrieved {response_count} donor response(s) for request ID {request_id}")

        if response_count == 0:
            logger.info(f"No donor responses found for request ID {request_id} (Hospital: {hospital.name})")

        return queryset