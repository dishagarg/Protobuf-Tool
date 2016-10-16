# Requirements

- python 2.7
- protobuf-compiler (linux only)
  - Ubuntu eg: `sudo apt-get install protobuf-compiler`

# Installation

```python
pip install git+https://github.com/redbrickmedia/rbm-protobuf-tool.git
```
Then, just pip install the .whl file in the `pbtool/pbtool_gui/wheels` directory.

# Usage

Run `pbtool_bin` and `pbtool_gui` for help.


# Examples

## Using UI:

### Saving to a file:

This example takes an example proto file (tutorial.proto) and generates the corresponding json and the binary data.

```bash
pbtool_gui tutorial.proto Person
```

### Copying to the clipboard:

After running the above command, a dialog box wil appear in which you can enter your data and press OK. This will save the binary data in the data.bin file and will create a pop-up. Pressing the button on the pop-up will copy the bin data to your clipboard.

## Instead of Using UI:

### Posting to a server:

This example takes the json data from `data.json`, loads it into the `Person` message defined in `tutorial.proto`, and sends it to `http://myserver.com/tutorial`.

```bash
pbtool_bin tutorial.proto Person data.json --http-url http://myserver.com/tutorial --http-add-header="Content-Type: application/x-protobuf"
```

### Saving to a file:

This example takes the json data from `data.json`, loads it into the `Person` message defined in `tutorial.proto`, and saves it to `data.bin`.

```bash
pbtool_bin tutorial.proto Person data.json -o data.bin
```
