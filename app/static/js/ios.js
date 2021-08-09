// Detects if device is on iOS
const isIos = function() {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test( userAgent );
};

const isIpad = function() {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /ipad/.test( userAgent );
};

// Detects if device is in standalone mode
const isInStandaloneMode = function() { return ('standalone' in window.navigator) && (window.navigator.standalone); };
