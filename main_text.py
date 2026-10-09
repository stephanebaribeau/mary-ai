import select
import sys

from tts import speak
import brain
from config import IDLE_CHECKIN_MAX_S, IDLE_CHECKIN_S


def input_with_timeout(prompt: str, timeout_s: float) -> str | None:
    """Retourne None si personne ne tape rien avant le délai."""
    print(prompt, end="", flush=True)
    ready, _, _ = select.select([sys.stdin], [], [], timeout_s)
    if ready:
        return sys.stdin.readline().rstrip("\n")
    print()
    return None

def main():
    print("=== Compagne virtuelle (mode texte) ===")
    print("Tape ton message, Ctrl+C pour quitter.\n")

    had_first_exchange = False
    idle_delay = IDLE_CHECKIN_S

    while True:
        try:
            timeout = idle_delay if had_first_exchange else None
            user_text = (
                    input_with_timeout("Toi : ", timeout)
                    if timeout
                    else input("Toi: ")
                    )
            
            if user_text is None:
                reply = brain.check_in()
                print(f"Elle : {reply}")
                speak(reply)
                idle_delay = min(idle_delay * 2, IDLE_CHECKIN_MAX_S)
                continue

            if not user_text.strip():
                continue

            reply = brain.ask(user_text)
            print(f"Elle : {reply}")
            speak(reply)

            had_first_exchange = True
            idle_delay = IDLE_CHECKIN_S

        except KeyboardInterrupt:
            print("\nElle retient ce qui compte de cette conversation...")
            brain.update_memory()
            print("\nÀ la prochaine !")
            break


if __name__ == "__main__":
    main()
