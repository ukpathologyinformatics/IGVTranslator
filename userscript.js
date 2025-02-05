// ==UserScript==
// @name         Fabric FE3: Move IGV port for Liftover Redirect
// @namespace    http://tampermonkey.net/
// @version      2025-02-05
// @description  Replaces FE3 IGV bam viewer port with 60152 to point to a liftover redirect application
// @author       Caylin Hickey
// @match        https://app.fabricgenomics.com/w/<insert_workspace_id>/
// @icon         https://www.google.com/s2/favicons?sz=64&domain=fabricgenomics.com
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    setInterval(function() {
        // Looking for element
        const bamViewerLink = document.querySelector('a.bam-linkout');
        if (bamViewerLink != null && bamViewerLink.href.indexOf('localhost:60151') > -1) {
            // Found unchanged port
            console.log('Replacing BAM viewer port with 60152');
            bamViewerLink.href = bamViewerLink.href.replaceAll('localhost:60151','localhost:60152');
        }
    }, 100);
})();
