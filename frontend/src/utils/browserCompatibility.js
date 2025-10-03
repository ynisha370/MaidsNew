/**
 * Browser compatibility utilities
 * Provides functions to check browser support and handle compatibility issues
 */

/**
 * Check if the current browser supports a specific feature
 * @param {string} feature - The feature to check (e.g., 'localStorage', 'fetch', 'promises')
 * @returns {boolean} - True if the feature is supported
 */
export const isFeatureSupported = (feature) => {
  switch (feature) {
    case 'localStorage':
      try {
        return typeof Storage !== 'undefined' && window.localStorage !== null;
      } catch (e) {
        return false;
      }
    case 'sessionStorage':
      try {
        return typeof Storage !== 'undefined' && window.sessionStorage !== null;
      } catch (e) {
        return false;
      }
    case 'fetch':
      return typeof fetch !== 'undefined';
    case 'promises':
      return typeof Promise !== 'undefined';
    case 'asyncAwait':
      try {
        return eval('(async () => {})()') !== undefined;
      } catch (e) {
        return false;
      }
    case 'webWorkers':
      return typeof Worker !== 'undefined';
    case 'serviceWorkers':
      return 'serviceWorker' in navigator;
    case 'pushNotifications':
      return 'Notification' in window;
    case 'geolocation':
      return 'geolocation' in navigator;
    case 'camera':
      return navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
    case 'fileReader':
      return typeof FileReader !== 'undefined';
    case 'dragAndDrop':
      return 'draggable' in document.createElement('div');
    case 'touchEvents':
      return 'ontouchstart' in window;
    case 'webGL':
      try {
        const canvas = document.createElement('canvas');
        return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
      } catch (e) {
        return false;
      }
    default:
      return false;
  }
};

/**
 * Get the current browser name and version
 * @returns {object} - Object with browser name and version
 */
export const getBrowserInfo = () => {
  const userAgent = navigator.userAgent;
  let browserName = 'Unknown';
  let browserVersion = 'Unknown';

  if (userAgent.indexOf('Chrome') > -1) {
    browserName = 'Chrome';
    browserVersion = userAgent.match(/Chrome\/(\d+)/)?.[1] || 'Unknown';
  } else if (userAgent.indexOf('Firefox') > -1) {
    browserName = 'Firefox';
    browserVersion = userAgent.match(/Firefox\/(\d+)/)?.[1] || 'Unknown';
  } else if (userAgent.indexOf('Safari') > -1 && userAgent.indexOf('Chrome') === -1) {
    browserName = 'Safari';
    browserVersion = userAgent.match(/Version\/(\d+)/)?.[1] || 'Unknown';
  } else if (userAgent.indexOf('Edge') > -1) {
    browserName = 'Edge';
    browserVersion = userAgent.match(/Edge\/(\d+)/)?.[1] || 'Unknown';
  } else if (userAgent.indexOf('MSIE') > -1 || userAgent.indexOf('Trident') > -1) {
    browserName = 'Internet Explorer';
    browserVersion = userAgent.match(/(?:MSIE |rv:)(\d+)/)?.[1] || 'Unknown';
  }

  return { name: browserName, version: browserVersion };
};

/**
 * Check if the browser is Internet Explorer
 * @returns {boolean} - True if the browser is IE
 */
export const isInternetExplorer = () => {
  const userAgent = navigator.userAgent;
  return userAgent.indexOf('MSIE') > -1 || userAgent.indexOf('Trident') > -1;
};

/**
 * Check if the browser is Safari
 * @returns {boolean} - True if the browser is Safari
 */
export const isSafari = () => {
  const userAgent = navigator.userAgent;
  return userAgent.indexOf('Safari') > -1 && userAgent.indexOf('Chrome') === -1;
};

/**
 * Check if the browser is Chrome
 * @returns {boolean} - True if the browser is Chrome
 */
export const isChrome = () => {
  const userAgent = navigator.userAgent;
  return userAgent.indexOf('Chrome') > -1 && userAgent.indexOf('Edge') === -1;
};

/**
 * Check if the browser is Firefox
 * @returns {boolean} - True if the browser is Firefox
 */
export const isFirefox = () => {
  const userAgent = navigator.userAgent;
  return userAgent.indexOf('Firefox') > -1;
};

/**
 * Check if the browser is Edge
 * @returns {boolean} - True if the browser is Edge
 */
export const isEdge = () => {
  const userAgent = navigator.userAgent;
  return userAgent.indexOf('Edge') > -1;
};

/**
 * Check if the device is mobile
 * @returns {boolean} - True if the device is mobile
 */
export const isMobile = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

/**
 * Check if the device is tablet
 * @returns {boolean} - True if the device is tablet
 */
export const isTablet = () => {
  return /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent);
};

/**
 * Check if the device is desktop
 * @returns {boolean} - True if the device is desktop
 */
export const isDesktop = () => {
  return !isMobile() && !isTablet();
};

/**
 * Get the screen size category
 * @returns {string} - 'mobile', 'tablet', or 'desktop'
 */
export const getScreenSize = () => {
  if (isMobile()) return 'mobile';
  if (isTablet()) return 'tablet';
  return 'desktop';
};

/**
 * Check if the browser supports modern JavaScript features
 * @returns {boolean} - True if the browser supports modern JS
 */
export const supportsModernJS = () => {
  return isFeatureSupported('promises') && 
         isFeatureSupported('asyncAwait') && 
         typeof Symbol !== 'undefined' &&
         typeof Map !== 'undefined' &&
         typeof Set !== 'undefined';
};

/**
 * Get browser capabilities object
 * @returns {object} - Object with various browser capabilities
 */
export const getBrowserCapabilities = () => {
  return {
    localStorage: isFeatureSupported('localStorage'),
    sessionStorage: isFeatureSupported('sessionStorage'),
    fetch: isFeatureSupported('fetch'),
    promises: isFeatureSupported('promises'),
    asyncAwait: isFeatureSupported('asyncAwait'),
    webWorkers: isFeatureSupported('webWorkers'),
    serviceWorkers: isFeatureSupported('serviceWorkers'),
    pushNotifications: isFeatureSupported('pushNotifications'),
    geolocation: isFeatureSupported('geolocation'),
    camera: isFeatureSupported('camera'),
    fileReader: isFeatureSupported('fileReader'),
    dragAndDrop: isFeatureSupported('dragAndDrop'),
    touchEvents: isFeatureSupported('touchEvents'),
    webGL: isFeatureSupported('webGL'),
    isIE: isInternetExplorer(),
    isSafari: isSafari(),
    isChrome: isChrome(),
    isFirefox: isFirefox(),
    isEdge: isEdge(),
    isMobile: isMobile(),
    isTablet: isTablet(),
    isDesktop: isDesktop(),
    screenSize: getScreenSize(),
    modernJS: supportsModernJS()
  };
};

/**
 * Show browser compatibility warning if needed
 * @param {string} feature - The feature that's not supported
 * @param {string} fallbackMessage - Message to show as fallback
 */
export const showCompatibilityWarning = (feature, fallbackMessage = '') => {
  if (!isFeatureSupported(feature)) {
    console.warn(`Browser does not support ${feature}. ${fallbackMessage}`);
    // You can extend this to show user-facing warnings
    return true;
  }
  return false;
};

/**
 * Polyfill for missing features
 * @param {string} feature - The feature to polyfill
 */
export const polyfillFeature = (feature) => {
  switch (feature) {
    case 'fetch':
      if (!isFeatureSupported('fetch')) {
        // You can add fetch polyfill here
        console.warn('Fetch polyfill not implemented');
      }
      break;
    case 'promises':
      if (!isFeatureSupported('promises')) {
        // You can add Promise polyfill here
        console.warn('Promise polyfill not implemented');
      }
      break;
    default:
      console.warn(`Polyfill for ${feature} not implemented`);
  }
};

/**
 * Format a date universally across different browsers and locales
 * @param {Date|string|number} date - The date to format
 * @param {object} options - Formatting options
 * @returns {string} - Formatted date string
 */
export const formatDateUniversal = (date, options = {}) => {
  try {
    // Handle different input types
    let dateObj;
    if (date instanceof Date) {
      dateObj = date;
    } else if (typeof date === 'string' || typeof date === 'number') {
      dateObj = new Date(date);
    } else {
      throw new Error('Invalid date input');
    }

    // Check if date is valid
    if (isNaN(dateObj.getTime())) {
      throw new Error('Invalid date');
    }

    // Default options
    const defaultOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'short'
    };

    // Merge with provided options
    const formatOptions = { ...defaultOptions, ...options };

    // Try to use Intl.DateTimeFormat for better browser compatibility
    if (typeof Intl !== 'undefined' && Intl.DateTimeFormat) {
      try {
        const formatter = new Intl.DateTimeFormat('en-US', formatOptions);
        return formatter.format(dateObj);
      } catch (e) {
        console.warn('Intl.DateTimeFormat failed, falling back to manual formatting');
      }
    }

    // Fallback to manual formatting
    const year = dateObj.getFullYear();
    const month = dateObj.getMonth() + 1;
    const day = dateObj.getDate();
    const hours = dateObj.getHours();
    const minutes = dateObj.getMinutes();
    const seconds = dateObj.getSeconds();

    // Format based on options
    if (formatOptions.year === 'numeric' && formatOptions.month === 'long' && formatOptions.day === 'numeric') {
      const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
      ];
      
      let result = `${monthNames[dateObj.getMonth()]} ${day}, ${year}`;
      
      if (formatOptions.hour && formatOptions.minute) {
        const timeStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
        if (formatOptions.second) {
          result += ` ${timeStr}:${seconds.toString().padStart(2, '0')}`;
        } else {
          result += ` ${timeStr}`;
        }
      }
      
      return result;
    }

    // Simple fallback
    return dateObj.toLocaleDateString('en-US', formatOptions);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid Date';
  }
};

export default {
  isFeatureSupported,
  getBrowserInfo,
  isInternetExplorer,
  isSafari,
  isChrome,
  isFirefox,
  isEdge,
  isMobile,
  isTablet,
  isDesktop,
  getScreenSize,
  supportsModernJS,
  getBrowserCapabilities,
  showCompatibilityWarning,
  polyfillFeature,
  formatDateUniversal
};
