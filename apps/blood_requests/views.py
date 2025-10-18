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

from apps.core.utils import mask_email

class BloodRequestCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BloodRequestCreateSerializer
    
    def perform_create(self, serializer):
        user = self.request.user
        masked_user = mask_email(user.email)
        logger.info(f"BloodRequestCreateView triggered by user: {masked_user}")

        try:
            blood_request = serializer.save()
            logger.info(
                f"Blood request created - ID: {blood_request.id}, "
                f"Hospital ID: {blood_request.hospital.id}, "
                f"Blood Type: {blood_request.blood_type}"
            )

            # Find and notify matching donors
            matching_donors = DonorMatchingService.find_compatible_donors(blood_request)
            logger.info(f"Found {len(matching_donors)} matching donors for request ID: {blood_request.id}")

            if not matching_donors:
                logger.warning(
                    f"No matching donors found - Request ID: {blood_request.id}, "
                    f"Blood Type: {blood_request.blood_type}"
                )

            for donor in matching_donors:
                try:
                    self.send_donor_notification(donor, blood_request)
                    logger.info(f"Notification sent - Donor ID: {donor.id}, Request ID: {blood_request.id}")
                except Exception as e:
                    logger.error(f"Failed to notify donor ID: {donor.id} for request ID: {blood_request.id}")

            return blood_request
        
        except Exception as e:
            logger.exception(f"Unexpected error creating blood request: {str(e)}")
            raise

    
    def send_donor_notification(self, donor, request):
        masked_donor = mask_email(donor.user.email)
        logger.debug(f"Preparing notification - Donor ID: {donor.id}, Request ID: {request.id}")

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
            logger.info(f"Sending email - Donor: {masked_donor}, Subject: {subject}")

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [donor.user.email],
                fail_silently=True
            )
            logger.info(f"Email sent successfully - Donor: {masked_donor}")

        except Exception as e:
            logger.error(f"Email failed - Donor: {masked_donor}, Error: {str(e)}")






class BloodRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BloodRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        masked_user = mask_email(user.email)
        user_role = getattr(user, 'role', 'unknown')

        logger.info(f"BloodRequestListView accessed - User: {masked_user}, Role: {user_role}")


        try:
            if user.role == 'HOSPITAL':
                
                # Get hospital profile safely
                hospital = getattr(user, 'hospital_profile', None)
                
                if not hospital:
                    logger.error(f"Hospital profile not found - User: {masked_user}")
                    return BloodRequest.objects.none()
                
                # Hospitals see their own requests
                queryset = BloodRequest.objects.filter(hospital=hospital)
                logger.info(
                    f"Hospital query completed - User: {masked_user}, "
                    f"Hospital ID: {hospital.id}, Count: {queryset.count()}"
                )

                return queryset
            
            elif user.role == 'DONOR':
                # Get donor profile safely
                donor = getattr(user, 'donor', None)
                
                if not donor:
                    logger.error(f"Donor profile not found - User: {masked_user}")
                    return BloodRequest.objects.none()
                
                # Donors see open requests in their service areas
                donor_service_areas = donor.service_locations.all()
                area_count = donor_service_areas.count()
                logger.debug(
                    f"Donor service areas - User: {masked_user}, "
                    f"Donor ID: {donor.id}, Area Count: {area_count}"
                )

                
                from apps.core.blood_compatibility import BloodCompatibility
                compatible_types = BloodCompatibility.get_compatible_donor_types(donor.blood_type)
                logger.debug(
                    f"Compatible types - Donor ID: {donor.id}, "
                    f"Blood Type: {donor.blood_type}, Compatible: {compatible_types}"
                )
                
                queryset = BloodRequest.objects.filter(
                    status='OPEN',
                    hospital__service_locations__in=donor_service_areas,
                    blood_type__in=compatible_types
                ).distinct()

                logger.info(
                    f"Donor query completed - User: {masked_user}, "
                    f"Donor ID: {donor.id}, Count: {queryset.count()}"
                )
                return queryset
            
            logger.warning(f"Unrecognized role - User: {masked_user}, Role: {user_role}")
            return BloodRequest.objects.none()
        
        except Exception as e:
            logger.exception(f"Error retrieving blood requests - User: {masked_user}, Error: {str(e)}")
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
        masked_user = mask_email(user.email)
        
        logger.info(f"Accept request attempt - User: {masked_user}, Request ID: {request_id}")

        # Role & Profile Check
        if not hasattr(user, 'role') or user.role != 'DONOR':
            user_role = getattr(user, 'role', 'unknown')
            logger.warning(f"Unauthorized accept attempt - User: {masked_user}, Role: {user_role}")

            return Response(
                {'detail': 'Forbidden: Only donors can accept requests'},
                status=status.HTTP_403_FORBIDDEN
            )

        donor = getattr(user, 'donor', None)
        if not donor:
            logger.error(f"Donor profile not found - User: {masked_user}")
            return Response(
                {'detail': 'Donor profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            blood_request = BloodRequest.objects.get(id=request_id)

            # Eligibility check
            if not donor.is_eligible_to_donate:

                logger.warning(
                    f"Ineligible donor attempt - Donor ID: {donor.id}, "
                    f"Request ID: {request_id}, Available from: {donor.available_from}"
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
                logger.warning(f"Duplicate accept attempt - Donor ID: {donor.id}, Request ID: {request_id}")
                return Response({'message': 'You have already accepted this request'})

            # Update blood request status
            blood_request.status = 'MATCHED'
            blood_request.save()

            # Notify hospital
            hospital_masked = mask_email(blood_request.hospital.user.email)
            try:
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
                    f"Hospital notification sent - Hospital: {hospital_masked}, "
                    f"Request ID: {request_id}"
                )

            except Exception as email_error:
                logger.error(
                    f"Failed to notify hospital - Hospital: {hospital_masked}, "
                    f"Request ID: {request_id}, Error: {str(email_error)}"
                )

            logger.info(
                f"Request accepted successfully - Donor ID: {donor.id}, "
                f"Request ID: {request_id}, Response ID: {donor_response.id}"
            )
                
            return Response({'message': 'Request accepted successfully'})

        except BloodRequest.DoesNotExist:
            logger.error(f"Request not found - ID: {request_id}, User: {masked_user}")
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.exception(
                f"Error accepting request - User: {masked_user}, "
                f"Request ID: {request_id}, Error: {str(e)}"
            )
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_fulfilled(request, request_id):
    """Hospital marks request as fulfilled"""

    user = request.user
    masked_user = mask_email(user.email)
    user_role = getattr(user, 'role', 'unknown')

    logger.info(f"Mark fulfilled attempt - User: {masked_user}, Request ID: {request_id}")

    # --- Explicit Role & Profile Check ---
    if not hasattr(request.user, 'role') or request.user.role != 'HOSPITAL':
        logger.warning(f"Unauthorized mark_fulfilled - User: {masked_user}, Role: {user_role}")
        return Response(
            {'detail': 'Forbidden: Only hospitals can mark requests as fulfilled'},
            status=status.HTTP_403_FORBIDDEN
        )

    hospital = getattr(request.user, 'hospital_profile', None)
    if not hospital:
        logger.error(f"Hospital profile not found - User: {masked_user}")
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
            f"Request marked fulfilled - Request ID: {request_id}, "
            f"Hospital ID: {hospital.id}, User: {masked_user}"
        )
        
        return Response({'message': 'Request marked as fulfilled'})
        
    except BloodRequest.DoesNotExist:
        logger.error(
            f"Request not found or unauthorized - Request ID: {request_id}, "
            f"Hospital ID: {hospital.id}, User: {masked_user}"
        )
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.exception(
            f"Error marking fulfilled - Request ID: {request_id}, "
            f"Hospital ID: {hospital.id}, Error: {str(e)}"
        )
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_donation(request, request_id, response_id):
    """Hospital confirms that a donor actually donated using the DonorResponse id."""

    user = request.user
    masked_user = mask_email(user.email)

    # Log the incoming request
    logger.info(
        f"Donation confirmation attempt - User: {masked_user}, "
        f"Request ID: {request_id}, Response ID: {response_id}"
    )
    
    # Ensure only hospitals can call this
    if not hasattr(user, 'role') or user.role != 'HOSPITAL':
        user_role = getattr(user, 'role', 'unknown')
        logger.warning(f"Unauthorized confirmation - User: {masked_user}, Role: {user_role}")
        return Response({'detail': 'Forbidden: Only hospitals can confirm donations.'}, status=403)
    
    hospital = getattr(user, 'hospital_profile', None)
    if not hospital:
        logger.error(f"Hospital profile not found - User: {masked_user}")
        return Response({'detail': 'Hospital profile not found.'}, status=400)

    try:
        blood_request = BloodRequest.objects.get(id=request_id, hospital=hospital)
        logger.debug(f"Blood request found - Request ID: {request_id}, Hospital ID: {hospital.id}")
        
    except BloodRequest.DoesNotExist:
        logger.error(f"Blood request not found - Request ID: {request_id}, Hospital ID: {hospital.id}")
        return Response({'error': 'Request not found.'}, status=404)

    try:
        donor_response = DonorResponse.objects.get(request=blood_request, id=response_id)
        donor_id = donor_response.donor.id
        logger.debug(f"Donor response found - Response ID: {response_id}, Donor ID: {donor_id}")

    except DonorResponse.DoesNotExist:
        logger.error(f"Donor response not found - Response ID: {response_id}, Request ID: {request_id}")
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
            f"Error confirming donation - Request ID: {request_id}, "
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
        masked_user = mask_email(user.email)
        request_id = self.kwargs.get('request_id')

        logger.info(f"DonorResponseListView accessed - User: {masked_user}, Request ID: {request_id}")

        hospital = getattr(user, 'hospital_profile', None)

        if not hospital:
            logger.warning(f"Non-hospital access attempt - User: {masked_user}, Request ID: {request_id}")
            raise exceptions.PermissionDenied('Only hospitals can view donor responses.')

        queryset = DonorResponse.objects.filter(
            request_id=request_id,
            request__hospital=hospital
        )

        response_count = queryset.count()
        logger.info(
            f"Donor responses retrieved - Hospital ID: {hospital.id}, "
            f"Request ID: {request_id}, Count: {response_count}"
        )

        if response_count == 0:
            logger.debug(f"No responses found - Hospital ID: {hospital.id}, Request ID: {request_id}")

        return queryset