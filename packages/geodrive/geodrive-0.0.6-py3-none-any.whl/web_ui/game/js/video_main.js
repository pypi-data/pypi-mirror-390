window.addEventListener('load', () => {
    if (typeof ControlManager === 'undefined') {
            throw new Error('ControlManager не загружен');
        }

    ControlManager.init();

    if (typeof VideoManager === 'undefined') {
            throw new Error('VideoManager не загружен');
        }
    VideoManager.init();
});