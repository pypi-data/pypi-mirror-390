export class ControlsManager {
    constructor() {
        this.activeCommands = new Set();
        this.commandInterval = null;
        this.commandHandlers = [];
        this.isEnabled = false;
    }

    init() {
        this.setupKeyboardListeners();
        this.setupButtonListeners();
        this.setupStatusListener();
    }

    setupKeyboardListeners() {
        document.addEventListener('keydown', (e) => {
            if (!this.isEnabled) return;

            const key = e.key.toLowerCase();
            let command = null;

            switch(key) {
                case 'w': command = 'forward'; break;
                case 's': command = 'backward'; break;
                case 'a': command = 'left'; break;
                case 'd': command = 'right'; break;
                case 'm':
                    this.sendSoundCommand('moo');
                    e.preventDefault();
                    return;
                case 'b':
                    this.sendSoundCommand('beep');
                    e.preventDefault();
                    return;
            }

            if (command && !this.activeCommands.has(command)) {
                this.startCommand(command);
                e.preventDefault();
            } else if (key === ' ') {
                this.stopAllCommands();
                e.preventDefault();
            }
        });

        document.addEventListener('keyup', (e) => {
            const key = e.key.toLowerCase();
            let command = null;

            switch(key) {
                case 'w': command = 'forward'; break;
                case 's': command = 'backward'; break;
                case 'a': command = 'left'; break;
                case 'd': command = 'right'; break;
            }

            if (command && this.activeCommands.has(command)) {
                this.stopCommand(command);
                e.preventDefault();
            }
        });
    }

    setupButtonListeners() {
        const buttons = {
            'btn-forward': 'forward',
            'btn-backward': 'backward', 
            'btn-left': 'left',
            'btn-right': 'right',
            'btn-stop': 'stop',
            'btn-moo': 'moo',
            'btn-beep': 'beep'
        };

        Object.entries(buttons).forEach(([id, command]) => {
            const btn = document.getElementById(id);
            if (btn) {
                if (command === 'stop') {
                    btn.addEventListener('click', () => this.stopAllCommands());
                } else if (['moo', 'beep'].includes(command)) {
                    btn.addEventListener('click', () => this.sendSoundCommand(command));
                } else {
                    btn.addEventListener('mousedown', () => this.startCommand(command));
                    btn.addEventListener('mouseup', () => this.stopCommand(command));
                    btn.addEventListener('mouseleave', () => this.stopCommand(command));
                    btn.addEventListener('touchstart', (e) => {
                        e.preventDefault();
                        this.startCommand(command);
                    });
                    btn.addEventListener('touchend', (e) => {
                        e.preventDefault();
                        this.stopCommand(command);
                    });
                }
            }
        });
    }

    setupStatusListener() {
        document.addEventListener('websocket-status', (event) => {
            this.isEnabled = event.detail.status === 'connected';
        });
    }

    startCommand(command) {
        this.activeCommands.add(command);
        this.updateActiveCommandsDisplay();
        this.sendCombinedCommand();

        if (!this.commandInterval) {
            this.commandInterval = setInterval(() => {
                this.sendCombinedCommand();
            }, 100);
        }
    }

    stopCommand(command) {
        this.activeCommands.delete(command);
        this.updateActiveCommandsDisplay();

        if (this.activeCommands.size === 0) {
            this.stopSending();
            this.sendStop();
        } else {
            this.sendCombinedCommand();
        }
    }

    stopAllCommands() {
        this.activeCommands.clear();
        this.updateActiveCommandsDisplay();
        this.stopSending();
        this.sendStop();
    }

    sendCombinedCommand() {
        const channels = {
            channel1: 1500, // Steering
            channel2: 1500, // Throttle  
            channel3: 1500, // Moo
            channel4: 1500  // Beep
        };

        this.activeCommands.forEach(cmd => {
            switch(cmd) {
                case 'forward':
                    channels.channel2 = 1000;
                    break;
                case 'backward':
                    channels.channel2 = 2000;
                    break;
                case 'left':
                    channels.channel1 = 2000;
                    break;
                case 'right':
                    channels.channel1 = 1000;
                    break;
            }
        });

        this.notifyCommandHandlers(channels);
    }

    sendStop() {
        this.notifyCommandHandlers({
            channel1: 1500,
            channel2: 1500, 
            channel3: 1500,
            channel4: 1500
        });
    }

    sendSoundCommand(sound) {
        const channel = sound === 'moo' ? 'channel2' : 'channel4';
        const command = { channel1: 1500, channel2: 1500, channel3: 1500, channel4: 1500 };
        command[channel] = 1000;

        this.notifyCommandHandlers(command);

        setTimeout(() => {
            command[channel] = 1500;
            this.notifyCommandHandlers(command);
        }, 500);
    }

    stopSending() {
        if (this.commandInterval) {
            clearInterval(this.commandInterval);
            this.commandInterval = null;
        }
    }

    onCommand(handler) {
        this.commandHandlers.push(handler);
    }

    notifyCommandHandlers(command) {
        this.commandHandlers.forEach(handler => handler(command));
    }

    updateActiveCommandsDisplay() {
        const activeCommandsElement = document.getElementById('activeCommands');
        const commandsListElement = document.getElementById('commandsList');

        if (this.activeCommands.size > 0) {
            const commandNames = Array.from(this.activeCommands).map(cmd => {
                const names = { forward: 'Вперед', backward: 'Назад', left: 'Влево', right: 'Вправо' };
                return names[cmd] || cmd;
            });
            commandsListElement.innerHTML = commandNames.join(', ');
            activeCommandsElement.style.display = 'block';
        } else {
            activeCommandsElement.style.display = 'none';
        }
    }
}