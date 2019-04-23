## First Talk
Simple conversation with Mycroft

## Description
When Mycroft is wake up with a talk word, then it will repeat what you said except if you ask him about him or help.

## Examples
 - "Talk with me"
 - "Talk"
 - "Let's talk"
 - (When conversation is activated) "Help"
 - (When conversation is activated) "Who are you?"
 - (When conversation is activated) "Quit" or "Exit"


## Credits
Campora

## Common issues
- No module named 'Crypto' -> rebuilt the venv environnement
```bash
mycroft-core$ sudo rm -R .venv/
mycroft-core$ ./dev_setup.sh
```
[Mycroft Documentation](https://mycroft.ai/documentation/linux/)
