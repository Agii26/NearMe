import { useState, useCallback } from "react";

// Quezon City fallback — used when geolocation is denied, unavailable, or
// the user hasn't granted permission yet. Matches the seeded demo data so
// the app is useful immediately rather than showing an empty state.
const FALLBACK_LOCATION = { lat: 14.6507, lng: 121.0494 };

export function useGeolocation() {
  const [location, setLocation] = useState(FALLBACK_LOCATION);
  const [isUsingDeviceLocation, setIsUsingDeviceLocation] = useState(false);
  const [error, setError] = useState(null);

  const requestDeviceLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError("Geolocation isn't supported on this device.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
        setIsUsingDeviceLocation(true);
        setError(null);
      },
      () => {
        setError("Couldn't get your location — showing Quezon City instead.");
        setIsUsingDeviceLocation(false);
      }
    );
  }, []);

  return { location, isUsingDeviceLocation, error, requestDeviceLocation };
}
