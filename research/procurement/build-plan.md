# Build a duck together: purchasing and learning plan

**Updated buying baseline:** use [order-list.md](order-list.md). Following the
discussion, default to the full A1, advertised $352 kit, no soldering equipment
and deferred audio: £800.79 before / £875.79 including £75 reserve, incorporating
the user's actual £306.46 kit-plus-shipping payment and confirmation VAT is excluded. The expanded
scenarios below preserve the original research scope; they are not the current
shopping basket. The calculator and priced listings now use the revised defaults.

27 October 2026 · SO50, mainland Great Britain · target £800–£1,000.

**Recommendation:** print and assemble an XGO-Duck using the matched, assembled
electronics kit and an Arduino UNO Q 4GB. Use an A1 or A1 mini. Learn soldering
on inexpensive through-hole practice boards alongside the robot build. The
duck is a substantial first robotics project: manageable in stages for a handy
parent and a motivated teenager, but not a polished one-evening kit.

This is a researched buying plan, not an order or a final supplier quotation.
No products were bought and no supplier messages were sent. Public listings
and variant data were inspected; no delivery address or checkout was submitted.
Prices/stock can change. Full postcode-dependent freight remains unquoted.

## The budget you can actually audit

[Open the editable calculator](cost-calculator.html).
[See every priced listing](priced-listings.md).
[Compare finished-robot, DIY and phased-buying options](options-comparison.md).

| Selected scenario | Before reserve | With £75 reserve |
|---|---:|---:|
| Full-size A1, kit budgeted at $400, learning equipment and bench audio | £986.44 | £1,061.44 |
| Same, A1 mini instead | £936.44 | £1,011.44 |
| A1 with advertised $352 kit discount, **if confirmed** | £943.24 | £1,018.24 |
| Mini with that discount, **if confirmed** | £893.24 | £968.24 |

These are modelled totals, not guaranteed maxima. They use £0.75/USD, £40
international freight, £12 courier handling, £15 printer delivery, £6 Pi Hut
delivery and £15 for adhesive/labels/ties. Those charges are **allowances**.
Duty is unresolved: the calculator's 0% is an unset placeholder, not a confirmed
tariff. VAT is modelled at 20% on kit + international freight + any duty,
assuming Luwu has not collected UK VAT. Do not add it twice if a final quote
includes it. [HMRC import treatment](https://www.gov.uk/goods-sent-from-abroad/tax-and-duty),
[VAT rate](https://www.gov.uk/vat-rates).

The £530.44 selected UK-priced-goods subtotal excludes the imported robot kit.
For the full-size scenario the modelled kit is £300, its freight £40, VAT £68
and handling £12. This makes the complete robot electronics a £420 landed
allowance before unresolved duty. Arithmetic is in `costs.json` and the
calculator; actual foreign card rates may differ from the planning rate.

The following are **not** included: final mobile-audio power redesign, camera,
ToF/person-following hardware, spare servo, custom PCB manufacture, paid AI,
workbench furniture or large changes to the supplied mechanics. Reserve is
not a substitute for pricing those additions.

## Printer choice: we checked the files

| Listing | Price including VAT | Delivery evidence | Position |
|---|---:|---|---|
| [Additive-X A1, BAMA1-U1](https://www.additive-x.com/shop/bambu-lab-a1-3d-printer.html) | £189 | Listed in stock; next-working-day service offered, postcode-dependent | Preferred if you expect other projects; 256 mm cube |
| [Additive-X A1 mini, BAMA1M-U1](https://www.additive-x.com/shop/bambu-lab-a1-mini-3d-printer.html) | £139 | Listed in stock; next-working-day service offered | Lowest-cost suitable size; 180 mm cube |
| [3DJake A1](https://www.3djake.uk/bambu-lab/a1) | £215.61 + £30 bulky surcharge | Displayed 5 November; Austria dispatch | £245.61 published goods+surcharge, slower alternative |
| [3DJake A1 mini](https://www.3djake.uk/bambu-lab/a1-mini) | £161.47 + £30 bulky surcharge | Displayed 5 November | £191.47 published goods+surcharge |

Additive-X postage has not been quoted for SO50; £15 is our allowance. Its
product pages explain same-day DPD dispatch cutoffs and that some destinations
use a two-day service. The indexed special prices above supersede earlier,
higher estimates; recheck the selected printer-only SKU before paying.

I downloaded hardware commit `106186e1beda690c28f485a754538d6f41b5d025` and
measured all 30 STL files. Every individual part has axis-aligned dimensions
under 180 mm. The largest is `head_shell.stl`, about 88 × 124.10 × 48.08 mm.
Filename quantities imply 45 pieces including 10 optional roller pieces.
The measured inventory is in `print-dimensions.json`/`.csv`. STL units were
interpreted as mm, consistent with the project. This proves geometric size
clearance, not mesh quality, supports, fit or a working print recipe.

The files and prose inventory have small revision differences, so confirm
assembly counts against the matched guide. Print a servo mount and bearing
seat first. Upstream has not supplied a complete validated material/profile
set. Our PLA+ and 95A TPU choices are candidates for those checks, not certified
replacements. [Print inventory](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/docs/PRINTING.md).

The basic A1/mini can print the separate coloured parts without an AMS. Ordinary
TPU should be fed through the external spool path, not assumed compatible with
AMS lite. Start with rigid parts and learn TPU after drying it. Filament
purchases are whole spools for learning and retries, not measured consumption.

## Robot parts: one matched kit is the sensible starting point

[Luwu electronics kit](https://shop.xgorobot.com/products/xgo-duck-biped-robot-electronics-kit-arduino-uno-q)
excludes the Arduino and printed parts. The page advertises $352; the live
public variant data returned $400. Budget at $400 until the discount is
confirmed. The storefront lists the UK as USD, so this line **does not meet a
strict GBP-checkout requirement**; the calculator converts it transparently.

Seller's contents: expansion board, 15 HD1910-series servos, pack/charger,
cables, screws and bearings. The page says dispatch within 14 days, not
arrival within 14 days. It does not establish a battery-inclusive UK delivery
date or shipping charge. Its pack description alternates between 3C and 5C;
obtain the actual pack/charger specification and UK mains plug in writing.

**Unresolved before buying the kit:** board revision, exact servo variant and
lead inclusion, final price, battery delivery eligibility, taxes/freight and
estimated arrival in SO50. A buy button does not resolve any of those.

Use [UNO Q 4GB ABX00173 at CPC](https://cpc.farnell.com/arduino/abx00173/arduino-uno-q-4gb/dp/SC21880):
£54.42 including VAT, listed 12 in stock at the reviewed page. CPC publishes
free mainland standard delivery above £24.99 excluding VAT, usually 48 hours;
this board qualifies by itself. Its optional express service is £3.99 ex VAT
(£4.79 including VAT). [CPC delivery terms](https://cpc.farnell.com/help/delivery-information).
Backup: [Pi Hut 4GB variant](https://thepihut.com/products/arduino-uno-q?variant=54858352689537)
£71.20 including VAT from live variant data; RS £71.17 incl VAT; RobotShop
£80.10 with restock uncertainty. No need to pay a premium for the latter here.

### Kit coverage checklist — don't buy these twice

| Robot item | Current project requirement | Buying decision |
|---|---|---|
| Servos | 15, exact HD-1910-C001 / HD1910M variant | Included; confirm model, horns and output screws |
| Servo leads | 15, correct 3-pin housing and polarity | Included claim; confirm |
| Expansion board | 1, match V1.1 instructions | Included; seller revision not established |
| Battery and charger | Matched high-discharge pack and charger | Included; confirm pack details, connector, polarity, UK plug |
| Small screws | M2×6, M2.3×8, M3×16 with specified head/thread styles | Included; inventory against matched guide |
| Thin bearings | 16×22×4 and 10×15×3 mm | Included; verify dimensions and counts |
| Arduino | UNO Q 4GB | Buy separately |
| Structure/soft parts | Rigid and TPU STLs | Print yourselves |

Root README and older BOM notes disagree on one small-bearing count. Do not
resolve this by silently substituting sizes or ordering an arbitrary count.
The [current robot BOM](https://github.com/LuwuDynamics/xgoduck_hardware/blob/master/BOM.md)
and matched assembly drawings should be supplied with the kit.

## Separately sourcing every component: what I found

| Item / alternative | Actual listing evidence | Why not the selected route |
|---|---|---|
| [OpenELAB HD-1910-C001](https://openelab.com/products/feetech-hd1910-microduck-coreless-servo) | $34.99 per actual motor variant; 15 = $524.85, about £393.64 before UK import charges | Servos alone exceed full-kit advertised price; preorder/warehouse timing unclear |
| [Luwu bare finished expansion board](https://shop.xgorobot.com/products/robot-driver-board) | $20, about £15; separate pack/charger option $50, about £37.50 | Excludes everything else; dispatch claim 10 days, not delivered date |
| [Simply Bearings ET2216](https://www.simplybearings.co.uk/products/et-2216-mb) | £12.53 incl VAT each at single-unit price; 11 = £137.83 before any quantity saving | Correct envelope; seals/clearance still need checking; costly compared with bundled bearings |
| [ArmDojo servo sets](https://armdojo.com/products/feetech-hd-1910-c001-coreless-servo-microduck) | Exact-model sets offered; preorder, variant/currency/shipping dependent | Could be a backup quote, not a verified rapid UK-stock source |
| [TorqueMicro servo](https://torquemicro.com/products/feetech-hd1910-servo-motor) | $34, backordered | No confirmed short lead time |
| [eBay bearing assortment](https://www.ebay.co.uk/itm/307040670870) | GBP listing offers 16×22×4 among many variants | Displayed starting price is not the selected size/quantity quote; China dispatch |

I also checked UK component distributors, robotics stores and RC fastener
listings. I did not establish a complete, exact-match, UK-stocked servo/lead/
battery/fastener basket with a short delivery commitment. Cheap STS3215 servos,
ordinary hobby servos, M2.5 machine screws, or 4 mm-wide foot bearings are not
automatic substitutions. The kit avoids much of this procurement risk while
still leaving the actual robot build to you.

## Tools and soldering: fit what you already own

The selected station is [Duratool D03327](https://cpc.farnell.com/duratool/zd-931-89-3106/soldering-station-esd-bs-plug/dp/SD01120),
£47.75 excluding VAT = **£57.30 including VAT**. It has a digital temperature
setting, UK plug, integral enclosed holder and sponge. A better match to your
existing tools than buying another all-in-one hand-tool set. Keep your cutters,
drivers and knives; check the supplied fastener drives before adding bits.

[Duratool D03143A meter](https://cpc.farnell.com/duratool/d03143a/digital-multimeter/dp/IN10151)
is £5.95 ex VAT = £7.14 incl VAT. This is an inexpensive low-voltage continuity/
polarity tool. Confirm its included batteries against the supplied manual;
if they are omitted, they are an additional small purchase.

Alternative [Miniware TS101](https://thepihut.com/products/miniware-ts101-smart-soldering-iron)
is £57.50 for the iron and silicone USB cable, before its compatible stand and
PD power supply. It is a useful portable option but not cheaper as a complete
first setup. The Antex £69.90 toolkit duplicates existing tools and has a
fixed-power iron; retain it as an alternative, not an extra purchase.

Selected learning extras: two £4.50 Blinky kits, four AA cells (£5), lead-free
solder (£4.40), mat (£11), and two pairs of glasses (£8). The assembled robot
electronics do not inherently require soldering these practice boards: they
are a separate, inexpensive way to learn. Keep soldering fumes away from your
breathing zone with suitable extraction/ventilation. Use a supported, powered-
off robot for assembly and a matched ready-made battery pack for initial tests.

## Making your own circuit boards

An FDM printer melts plastic into brackets, shells and cases. It cannot make
normal copper traces, plated holes or multilayer circuit boards. Conductive
filament is not a practical substitute for this robot's power/control PCB.

The normal maker workflow is schematic and PCB layout on your PC, then order
manufacture of a bare board, or manufacture **and component assembly**. You
can design a board yourself without owning PCB-making machinery. Hand soldering
through-hole parts is approachable; small hidden-pad surface-mount devices
need much more equipment and experience.

I inspected the current V1.1 manufacturing files: **four copper layers, 1.6 mm
board, 1 oz outer / 0.5 oz inner copper**. Its BOM includes a 3×2.5 mm LGA IMU
and a 2×1.5 mm QFN regulator. This is not a first project for a basic soldering
iron. The source release includes Gerbers, drills, BOM and placement files;
it omits the V1.1 editable `.PcbDoc`, and some BOM descriptions conflict with
values. Manufacture requires a component/footprint review, not just uploading
an old board file. [V1.1 files](https://github.com/LuwuDynamics/xgoduck_hardware/tree/master/PCBA).

| PCB route | Cost evidence | Suitability here |
|---|---|---|
| Finished Luwu driver board | $20 before shipping/tax | Recommended first robot route; confirm revision |
| [JLCPCB assembly](https://jlcpcb.com/help/article/pcb-assembly-faqs) | Published setup $8 and stencil $1.50, plus board, parts, placements, extras and delivery | Requires actual reviewed BOM/CPL quote; those headline fees are not an assembled-board price |
| [PCB Train UK](https://www.pcbtrain.co.uk/products-and-services/pcb-assembly/) | Quote required; assembly from 3 working days with complete parts | Good UK engineering option, not a priced hobby-board substitute |
| [Clarydon UK prototypes](https://www.clarydon.com/manufacturing/prototype-printed-circuit-boards) | Advertises £425 lot price for four-layer bare prototypes; VAT/assembly/freight not established | Shows why a one-off local manufacturing run can exceed the finished board price |

PCB Train Express has separate low-cost prototype restrictions; don't select
it solely because it is fast without checking the required drill/track/mask
specification. I have not uploaded manufacturing files or requested supplier
quotes. The next custom board for you and your son should be a simple LED/
button/sensor accessory in KiCad, not the duck's power board. No PCB milling
machine, chemical etching kit or reflow oven is required for the initial plan.

## Voice hardware: an explicit prototype, not a solved mobile installation

The selected [ReSpeaker Lite/XIAO kit](https://thepihut.com/products/respeaker-lite-with-xiao-esp32s3)
is £28.80, with its [matched speaker](https://thepihut.com/products/mono-enclosed-speaker-4r-5w)
£2.40. It is a useful candidate with audio processing, rather than a claim that
a £5 microphone will work over servo noise. Its XMOS board can operate as USB
audio with the USB firmware; the XIAO's port and I2S firmware serve a different
purpose. [Seeed USB setup](https://wiki.seeedstudio.com/reSpeaker_usb_v3/).

Budgeted Arduino hub (£14.40) and another data cable (£5.10) make a **bench**
experiment, £50.70 total. The hub supplier requires external PD power. Do not
assume it works from the robot battery or that adding the hub, speaker and
microphone preserves gait balance. Final power wiring, audio device testing,
mounting and re-calibration remain. A simpler first step is the existing PC mic
and speaker while the duck is supported. Person following needs further
sensing/software and is not covered by this voice parts list.

The offline Vosk application has now been ported to the XGO UNO/Linux/STM32
runtime. See the project README and DEPLOYMENT.md for the current implementation.

## Delivery outlook and remaining supplier questions

| Supplier | Published evidence | What is actually known for this plan |
|---|---|---|
| Additive-X | UK stock, same-day dispatch cutoff and postcode-dependent DPD next/two-day service | Printer can plausibly arrive quickly; exact SO50 charge unquoted |
| CPC | UK stock, free standard mainland delivery above threshold, normally 48 h | Applicable to selected board/station/meter basket |
| Pi Hut | UK supplier; selected variant prices/availability checked | Exact SO50 carriage and service need checkout |
| 3DJake | Austria warehouse; £0 standard above £69.90; chosen dryer displays 5 November | GBP/VAT pricing; selected materials basket clears threshold; confirm combined delivery date |
| Luwu | Kit preorder dispatch within 14 days; board within 10 days | Transit and battery-inclusive UK arrival not confirmed |

Do not promise an all-parts-next-week build. You can start printing and learning
immediately after UK supplies arrive while specialist electronics are in transit.
The kit's actual delivery is the critical procurement question. Draft questions
are in [supplier-questions.md](supplier-questions.md), ready for review; none sent.

## A first build with clear milestones

1. Set up the printer, print a calibration piece and learn to measure fit.
2. Each assemble a Blinky board; identify voltage, ground, continuity and polarity.
3. Print one servo/bearing interface after receiving the actual hardware. Adjust
   the profile before a full batch. Buy no extra colours until happy with it.
4. Configure/label servos individually, then follow the matched mechanical guide.
5. Deploy the XGO runtime, inspect all servos/IMU, calibrate and test while supported.
6. Validate standing/walking before mounting extra audio mass or changing policies.
7. Add the conversation experiment, then design your own printed head/accessories.

My effort estimate is several weekends with troubleshooting, not one guaranteed
build day. Printing elapsed time and material consumption still need slicing
with an agreed material/profile; the existing files alone do not establish them.

The project is young. Upstream's final file-level licensing is still being
clarified; preserve provenance and check terms before publishing modified
hardware packages. This does not prevent us from preparing the personal-build
costing, and no designs have been republished as our own.

**Practical choice:** A1 mini keeps the strongest chance of landing near £1,000
with reserves. A1 is my preferred long-term workshop choice if the extra £50
is comfortable. Keep the full robot-kit purchase conditional on written price,
revision and UK-delivery confirmation. You do not need to make the PCB yourself
to have built the robot yourselves.
