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

class BloodRequestCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BloodRequestCreateSerializer
    
    def perform_create(self, serializer):
        blood_request = serializer.save()
        
        # Find and notify matching donors
        matching_donors = DonorMatchingService.find_compatible_donors(blood_request)
        
        for donor in matching_donors:
            self.send_donor_notification(donor, blood_request)
        
        return blood_request
    
    def send_donor_notification(self, donor, request):
        user = self.request.user
        """Send email notification to donor"""
        subject = f"Urgent: {request.blood_type} Blood Needed"
        message = f"""
        Hello {user.first_name},
        
        A blood request has been posted that matches your profile:
        
        Blood Type: {request.blood_type}
        Hospital: {request.hospital.name}
        Location: {request.hospital.primary_location.name}
        Contact: {request.contact_phone}
        
        If you can donate, please accept this request:
        Accept Link: {settings.FRONTEND_URL}/requests/{request.id}/accept/
        
        Thank you for being a lifesaver!
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [donor.user.email],
            fail_silently=True
        )




class BloodRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BloodRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'HOSPITAL':
            # Hospitals see their own requests
            return BloodRequest.objects.filter(hospital=user.hospital)
        elif user.role == 'DONOR':
            # Donors see open requests in their service areas
            donor = user.donor
            donor_service_areas = donor.service_locations.all()
            
            from apps.core.blood_compatibility import BloodCompatibility
            compatible_types = BloodCompatibility.get_compatible_donor_types(donor.blood_type)
            
            return BloodRequest.objects.filter(
                status='OPEN',
                hospital__service_locations__in=donor_service_areas,
                blood_type__in=compatible_types
            ).distinct()
        
        return BloodRequest.objects.none()







class BloodRequestDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BloodRequestSerializer
    queryset = BloodRequest.objects.all()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_request(request, request_id):
    """Donor accepts a blood request"""

    # --- Explicit Role & Profile Check ---

    if not hasattr(request.user, 'role') or request.user.role != 'DONOR':
        return Response(
            {'detail': 'Forbidden: Only donors can accept requests'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    donor = getattr(request.user, 'donor', None)
    if not donor:
        return Response(
            {'detail': 'Donor profile not found'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        blood_request = BloodRequest.objects.get(id=request_id)
        donor = request.user.donor
        
        # Check if donor is eligible
        if not donor.is_eligible_to_donate:
            return Response(
                {'error': 'You are not eligible to donate yet (56-day cooldown)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create donor response
        donor_response, created = DonorResponse.objects.get_or_create(
            request=blood_request,
            donor=donor
        )
        
        if not created:
            return Response({'message': 'You have already accepted this request'})
        
        # Update request status
        blood_request.status = 'MATCHED'
        blood_request.save()
        
        # Set donor cooldown
        #DonorMatchingService.set_donor_cooldown(donor)
        
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
        
        return Response({
            'message': 'Request accepted successfully',
            'next_available_date': donor.available_from
        })
        
    except BloodRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_fulfilled(request, request_id):
    """Hospital marks request as fulfilled"""

    # --- Explicit Role & Profile Check ---
    if not hasattr(request.user, 'role') or request.user.role != 'HOSPITAL':
        return Response(
            {'detail': 'Forbidden: Only hospitals can mark requests as fulfilled'},
            status=status.HTTP_403_FORBIDDEN
        )

    hospital = getattr(request.user, 'hospital', None)
    if not hospital:
        return Response(
            {'detail': 'Hospital profile not found'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        blood_request = BloodRequest.objects.get(
            id=request_id,
            hospital=request.user.hospital
        )
        blood_request.status = 'FULFILLED'
        blood_request.save()
        
        return Response({'message': 'Request marked as fulfilled'})
        
    except BloodRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_donation(request, request_id, response_id):
    """Hospital confirms that a donor actually donated using the DonorResponse id."""
    
    # Ensure only hospitals can call this
    if not hasattr(request.user, 'role') or request.user.role != 'HOSPITAL':
        return Response({'detail': 'Forbidden: Only hospitals can confirm donations.'}, status=403)
    
    hospital = getattr(request.user, 'hospital', None)
    if not hospital:
        return Response({'detail': 'Hospital profile not found.'}, status=400)

    try:
        blood_request = BloodRequest.objects.get(id=request_id, hospital=hospital)
    except BloodRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=404)

    try:
        donor_response = DonorResponse.objects.get(request=blood_request, id=response_id)
    except DonorResponse.DoesNotExist:
        return Response({'error': 'Donor response not found.'}, status=404)

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




class DonorResponseListView(generics.ListAPIView):
    """List all donors who responded to a specific request (Hospital only)"""
    permission_classes = [IsAuthenticated]
    serializer_class = DonorResponseSerializer
    
    def get_queryset(self):
        request_id = self.kwargs.get('request_id')
        return DonorResponse.objects.filter(
            request_id=request_id,
            request__hospital=self.request.user.hospital
        )