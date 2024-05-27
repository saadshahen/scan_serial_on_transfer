odoo.define('scan_serial_transfer.beep', function (require) {
    'use strict';

    var bus = require('bus.bus');

    bus.on('beep', this, function () {
        // Play the beep sound here
        var audioContext = new (window.AudioContext || window.webkitAudioContext)();
        var oscillatorNode = audioContext.createOscillator();
        oscillatorNode.type = "sine";
        oscillatorNode.connect(audioContext.destination);
        oscillatorNode.frequency.setValueAtTime(2000, audioContext.currentTime);
        oscillatorNode.start();
        oscillatorNode.stop(audioContext.currentTime + 0.5);
    });

    return {
        // Export any functions if needed
    };
});
