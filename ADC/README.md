# ADC0834 Python Library — README

A reference guide for the `ADC0834.py` bit-banged driver used to read analog values
into a Raspberry Pi via GPIO. Works with any analog voltage source connected to one
of the chip's 4 channels — a potentiometer, photoresistor, thermistor, joystick axis,
flex sensor, etc. A potentiometer wiring example is included in section 7 as a
concrete reference, but the library and wiring guidance apply generally.

---

## 1. What is the ADC0834?

The **ADC0834** is an 8-bit, 4-channel **analog-to-digital converter (ADC)** chip.

Raspberry Pi GPIO pins are digital only — they can only read HIGH (3.3V) or LOW (0V).
They cannot directly measure a varying voltage like the wiper output of a potentiometer,
a light sensor, or any other analog signal. The ADC0834 solves this: it measures an
analog voltage on one of its input channels and reports back an 8-bit digital number
(0–255) representing where that voltage falls between 0V and the reference voltage
(VREF). The Pi then talks to the ADC0834 over a simple serial protocol to request a
reading and receive that number.

- **Resolution:** 8-bit (256 possible values, 0–255)
- **Channels:** 4 analog input channels (CH0–CH3)
- **Interface:** simple 3-wire serial protocol (not full SPI, but similar in spirit)
- **Power:** 5V or 3.3V compatible (VCC also typically doubles as VREF)

---

## 2. Pinout — what each pin means

The ADC0834 comes in a **14-pin DIP package**. Pin 1 is usually marked with a notch
or dot at the top-left corner of the chip. Looking down at the chip with the
notch/pin-1 marker on the left, the pins run counter-clockwise: bottom row left→right
is pins 1–7, top row right→left is pins 8–14.

**Bottom row (pins 1–7):**

| Pin | Name     | Purpose |
|-----|----------|---------|
| 1   | **V+**   | Positive supply voltage. |
| 2   | **CS**   | Chip Select. Pulled LOW to begin a conversion/transaction, HIGH to end it. |
| 3   | **CH0**  | Analog input channel 0. |
| 4   | **CH1**  | Analog input channel 1. |
| 5   | **CH2**  | Analog input channel 2. |
| 6   | **CH3**  | Analog input channel 3. |
| 7   | **DGND** | Digital ground. |

**Top row (pins 8–14):**

| Pin | Name     | Purpose |
|-----|----------|---------|
| 8   | **AGND** | Analog ground. |
| 9   | **VREF** | Reference voltage. A reading of 255 corresponds to an input voltage equal to VREF. |
| 10  | **DO**   | Data Out — the chip drives this line to send the conversion result back. |
| 11  | **SARS** | Successive Approximation Register Status — goes low during an active conversion. Not used by this library; safe to leave unconnected. |
| 12  | **CLK**  | Clock. The Pi toggles this manually; one bit is read/written per pulse. |
| 13  | **DI**   | Data In — the Pi drives this line to send configuration/command bits. |
| 14  | **VCC**  | Digital supply voltage. |

> **Note on grounds/supplies:** AGND and DGND are typically tied together to the same
> common ground as the Pi and the analog source. V+ and VCC are typically tied
> together to the same supply rail. VREF must be solidly connected (commonly to the
> same supply as VCC/V+) — a floating or grounded VREF will produce unstable or
> stuck readings.

> **Note on DI vs. DO:** the chip has *separate* Data In (pin 13) and Data Out
> (pin 10) lines. This library, however, only exposes a single `ADC_DIO` GPIO pin.
> That's because the library ties DI and DO together to the **same** Pi GPIO pin
> and switches that pin's direction in software — `GPIO.setup(ADC_DIO, GPIO.OUT)`
> while sending command bits, then `GPIO.setup(ADC_DIO, GPIO.IN)` before reading the
> result. This is a common simplification for this chip and works fine as long as DI
> and DO are physically wired together to that one GPIO pin.

In this library, three GPIO pins are used (BCM numbering, configurable in `setup()`):

```python
ADC_CS  = 17   # Chip Select   → chip pin 2  (CS)
ADC_CLK = 18   # Clock         → chip pin 12 (CLK)
ADC_DIO = 27   # Data In/Out   → chip pins 10 (DO) and 13 (DI), wired together
```

---

## 3. How a reading is taken (the protocol)

Each call to `getResult(channel)` performs one full conversion by manually toggling
CLK and DIO in a specific sequence:

1. **CS goes LOW** — tells the chip a new transaction is starting.
2. **Start bit** — DIO held HIGH for one clock, marks the beginning of the command.
3. **Single-ended mode bit** — DIO HIGH, tells the chip to measure the channel against
   ground rather than differentially between two channels.
4. **ODD bit** — the low bit of the channel number (0–3), used with the SELECT bit to
   choose the channel.
5. **SELECT bit** — the high bit of the channel number.
6. **Mux settle clock** — one extra clock pulse after switching DIO to input. This
   gives the chip's internal multiplexer time to switch to the selected channel and
   begin the actual conversion before the real data bits appear. Skipping this causes
   every reading to be shifted down by one bit position (values cap out at 127 instead
   of 255).
7. **8-bit read (MSB-first)** — the Pi pulses CLK 8 times, reading one bit per pulse.
   This builds the result value, most-significant-bit first, into `dat1` (0–255).
8. **8-bit echo read (LSB-first)** — immediately after the MSB-first result, the chip
   re-sends the *same* result a second time, but LSB-first, as a built-in
   cross-check. Because the chip has already placed bit 0 on the line as a side
   effect of the last clock in step 7 (no new clock pulse is needed to produce it),
   this second pass only needs **7** more clock pulses, seeded with `dat1 & 1` as its
   first bit. Reading a full 8 fresh clocks here (the naive approach) reads one clock
   too far and produces a value that is exactly `dat1 >> 1` — a subtle, consistent
   off-by-one that looks like a wiring/noise problem but isn't.
9. **CS goes HIGH** — ends the transaction.
10. **Compare `dat1` and `dat2`.** If they match, the reading is trusted and returned.
    If they don't, the read is discarded and `0` is returned instead — this catches
    a corrupted/glitched read rather than silently returning bad data.

---

## 4. Library API

```python
import ADC0834

ADC0834.setup()                    # default pins: CS=17, CLK=18, DIO=27
# or with custom pins:
ADC0834.setup(cs=17, clk=18, dio=27)

value = ADC0834.getResult(0)       # read channel 0 → int 0-255

ADC0834.destroy()                  # calls GPIO.cleanup()
```

### `setup(cs=17, clk=18, dio=27)`
Configures GPIO in BCM mode, sets CS and CLK as outputs, and stores the pin numbers
for use by `getResult()`. Call once before reading.

### `getResult(channel=0)`
Runs one full conversion cycle on the given channel (0–3) as described above and
returns an integer 0–255, or `0` if the two internal cross-check reads didn't match.

### `destroy()`
Calls `GPIO.cleanup()`. Equivalent to calling `GPIO.cleanup()` yourself at the end of
your program.

---

## 5. Minimal usage example

```python
import RPi.GPIO as GPIO
import ADC0834
from time import sleep

GPIO.setmode(GPIO.BCM)
ADC0834.setup()

try:
    while True:
        value = ADC0834.getResult(0)   # read channel 0
        print(value)
        sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()
```

---

## 6. Wiring checklist (general)

This applies regardless of what analog source you're reading — a potentiometer,
photoresistor, thermistor, flex sensor, joystick axis, whatever puts out a variable
voltage.

- **CS (pin 2)** → your chosen `ADC_CS` GPIO pin.
- **CLK (pin 12)** → your chosen `ADC_CLK` GPIO pin.
- **DO (pin 10) and DI (pin 13) wired together**, then both to your chosen `ADC_DIO`
  GPIO pin. This library treats DI/DO as a single bidirectional line, so the two
  chip pins must be physically joined on the breadboard for it to work.
- **V+ (pin 1) and VCC (pin 14)** tied together to your supply rail (3.3V or 5V,
  matching what the Pi GPIO can tolerate — use 3.3V if in doubt).
- **VREF (pin 9)** tied to the same supply as V+/VCC (or another stable reference) —
  this determines what voltage maps to a reading of 255.
- **DGND (pin 7) and AGND (pin 8)** tied together to the same common ground as the
  Pi and whatever analog source you're reading. A missing or loose ground is one of
  the most common causes of unstable/garbage readings.
- **SARS (pin 11)** can be left unconnected — this library doesn't use it.
- Your analog source connects to one (or more) of CH0–CH3 (pins 3–6).
- Short, solid jumper wires on CLK/DIO — the timing in this library uses very short
  (microsecond-scale) delays between clock edges, so long or loose breadboard wires
  can introduce noise. If readings seem unstable, try slowing the delays down
  (e.g. `0.00002` instead of `0.000002`) as a diagnostic step.

---

## 7. Worked example: reading a potentiometer

This is the circuit this library was originally built and tested against — a single
potentiometer feeding one ADC channel — included here as a concrete reference for
wiring a new project. Verified against the project's own KiCad netlist.

**Circuit:**
- Potentiometer end A → 5V rail
- Potentiometer end B → GND
- Potentiometer wiper → ADC0834 **CH0** (pin 3)

**Pin connections (BCM/GPIO numbering on the Pi side):**

| ADC0834 pin | Function | Connects to |
|---|---|---|
| 1 (V+)   | Supply       | 5V rail (shared with pot end A, and VCC/VREF below) |
| 2 (CS)   | Chip Select  | Pi GPIO17 |
| 3 (CH0)  | Analog input | Potentiometer wiper |
| 4–6 (CH1–CH3) | Analog input | Unused |
| 7 (DGND) | Digital ground | Common ground (Pi GND, pot end B) |
| 8 (AGND) | Analog ground  | Common ground |
| 9 (VREF) | Reference voltage | 5V rail |
| 10 (DO)  | Data out | Pi GPIO27 (tied to pin 13 below) |
| 11 (SARS)| Status   | Unused / unconnected |
| 12 (CLK) | Clock    | Pi GPIO18 |
| 13 (DI)  | Data in  | Pi GPIO27 (tied to pin 10 above) |
| 14 (VCC) | Supply   | 5V rail |

Corresponding library setup:

```python
import ADC0834
ADC0834.setup(cs=17, clk=18, dio=27)   # matches the wiring above

value = ADC0834.getResult(0)           # potentiometer is on CH0
```

**Adapting this to a new project:** the pattern is always the same — pick 3 free
GPIO pins for CS/CLK/DIO, tie DO and DI together to the DIO pin, put your supply on
V+/VCC/VREF, put common ground on DGND/AGND, and wire your analog source into
whichever of CH0–CH3 you prefer (passing that channel number to `getResult()`). A
potentiometer is just the simplest possible analog source to test with — anything
that outputs a voltage between GND and VREF will work the same way.

---

## 8. Troubleshooting notes (lessons learned)

- **Readings stuck at 0 almost always, with one "magic" value at one dial position:**
  the cross-check (`dat1`/`dat2`) is comparing mismatched bit orders, so it only
  matches by coincidence. Verify the LSB-first echo pass is decoded as an *increasing*
  bit-shift (`dat2 |= bit << i`), not a left-shift like the MSB-first pass.
- **Readings consistently max out at 127 instead of 255:** the MSB is being lost.
  This means the mux-settle clock pulse (step 6 above) is missing — the first bit
  read is a settling artifact rather than the true top bit.
- **`dat2` is consistently exactly `dat1 >> 1`:** the echo read is starting one clock
  late. Seed `dat2` with `dat1 & 1` and only clock 7 more times, rather than reading
  a fresh 8 bits.
- **To debug the echo/cross-check logic in isolation**, test against a *fixed* known
  voltage (e.g. an input pin tied straight to VCC or straight to GND) rather than a
  moving potentiometer. With a moving analog source, a mismatch between `dat1` and
  `dat2` could mean either a decoding bug *or* the voltage genuinely changing
  mid-read — a fixed voltage removes that ambiguity.