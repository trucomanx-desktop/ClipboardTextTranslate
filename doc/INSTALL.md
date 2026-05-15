# clipboard_text_translate

Program that collects text from the clipboard and translates it.

## Install from PYPI

The homepage in pipy is https://pypi.org/project/clipboard_text_translate/

```bash
pip install --upgrade clipboard_text_translate
```

Using:

```bash
clipboard-text-translate-indicator
```

## Install from source
Installing `clipboard-text-translate-indicator` program

```bash
git clone https://github.com/trucomanx-desktop/ClipboardTextTranslate.git
cd ClipboardTextTranslate
pip install -r requirements.txt
cd src
python3 setup.py sdist
pip install dist/clipboard_text_translate-*.tar.gz
```
Using:

```bash
clipboard-text-translate-indicator
```

## Add the program to Linux start session

Add the program to the bar indicator on Linux startup session.

```bash
clipboard-text-translate-indicator --autostart
```


## Uninstall

```bash
pip uninstall clipboard_text_translate
```
