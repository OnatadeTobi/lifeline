import { Link } from 'react-router-dom';
import { Calendar, MapPin, Building } from 'lucide-react';
import BloodTypeBadge from './BloodTypeBadge';
import StatusBadge from './StatusBadge';

/**
 * RequestCard - Displays a blood request in a card format
 * Backend response fields: id, hospital_name, hospital_location, blood_type,
 *   contact_phone, notes, status, matched_donors_count, created_at, updated_at
 */
function RequestCard({ request }) {
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    return (
        <Link
            to={`/requests/${request.id}`}
            className="block card hover:shadow-lg transition-shadow duration-200"
        >
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                        <BloodTypeBadge bloodType={request.blood_type} size="lg" />
                        <StatusBadge status={request.status} />
                    </div>

                    <div className="space-y-2">
                        <div className="flex items-center text-lifeline-gray">
                            <Building className="w-4 h-4 mr-2" />
                            <span className="text-sm">{request.hospital_name || 'Hospital'}</span>
                        </div>

                        {request.hospital_location && (
                            <div className="flex items-center text-lifeline-gray">
                                <MapPin className="w-4 h-4 mr-2" />
                                <span className="text-sm">{request.hospital_location}</span>
                            </div>
                        )}

                        <div className="flex items-center text-lifeline-gray">
                            <Calendar className="w-4 h-4 mr-2" />
                            <span className="text-sm">Posted {formatDate(request.created_at)}</span>
                        </div>
                    </div>

                    {request.notes && (
                        <p className="mt-3 text-sm text-lifeline-gray line-clamp-2">
                            {request.notes}
                        </p>
                    )}
                </div>

                <div className="ml-4 text-right">
                    {request.matched_donors_count !== undefined && (
                        <div className="text-sm text-lifeline-gray">
                            <span className="font-semibold text-lifeline-dark">
                                {request.matched_donors_count}
                            </span>
                            {' '}response{request.matched_donors_count !== 1 ? 's' : ''}
                        </div>
                    )}
                </div>
            </div>
        </Link>
    );
}

export default RequestCard;
