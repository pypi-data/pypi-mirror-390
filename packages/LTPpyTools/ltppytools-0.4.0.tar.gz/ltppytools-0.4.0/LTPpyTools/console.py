import datetime

class Console:
    def __init__(self):
        self.log_file = None

    def _log(self, message):
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(message + "\n")

    def enable_log(self, filename="console.log"):
        self.log_file = filename
        self.info(f"Log enabled → {filename}")

    def _output(self, emoji, text):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] {emoji} {text}"
        print(message)
        self._log(message)

    def info(self, text):
        self._output("✅", text)

    def warn(self, text):
        self._output("⚠️", text)

    def error(self, text):
        self._output("❌", text)

    def success(self, text):
        self._output("🎉", text)

    def custom(self, text, emoji="🌀"):
        self._output(emoji, text)

console = Console()
