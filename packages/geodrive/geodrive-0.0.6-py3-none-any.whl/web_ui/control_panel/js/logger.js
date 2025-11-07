export class Logger {
  constructor(containerSelector = ".config-console .console-content") {
    this.containerSelector = containerSelector;
  }

  log(message, type = "info") {
    const consoleContent = document.querySelector(this.containerSelector);
    if (!consoleContent) return;

    const line = document.createElement("div");
    line.className = `console-line ${type}`;

    const timestamp = new Date().toLocaleTimeString();
    line.innerHTML = `<span class="timestamp">[${timestamp}]</span> ${message}`;

    consoleContent.appendChild(line);
    consoleContent.scrollTop = consoleContent.scrollHeight;
  }

  error(message) {
    this.log(message, "error");
  }

  warning(message) {
    this.log(message, "warning");
  }

  success(message) {
    this.log(message, "success");
  }
}

export const logger = new Logger();
