[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e7a82459620646a99065198ee22233d3)](https://www.codacy.com/gh/dream-alpha/TimeshiftCockpit/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dream-alpha/TimeshiftCockpit&amp;utm_campaign=Badge_Grade)

<a href="https://gemfury.com/f/partner">
	<img src="https://badge.fury.io/fp/gemfury.svg" alt="Public Repository">
</a>

# TimeshiftCockpit (TSC)

## Features
TimeshiftCockpit is a plugin for DreamOS receivers that provides advanced timeshifting functionality.

## Limitations
- TSC supports Full HD (FHD) skins only
- TSC is being tested on DM 920 and DM ONE only

## Installation
To install TimeshiftCockpit execute the following command in a console on your dreambox:
- apt-get install wget (required the first time only)
- wget https://dream-alpha.github.io/TimeshiftCockpit/timeshiftcockpit.sh -O - | /bin/sh

The installation script will also install a feed source that enables a convenient upgrade to the latest version with the following commands or automatically as part of a DreamOS upgrade:
- apt-get update
- apt-get upgrade

## Conflicts
- TSC conflicts with the permanent timeshift plugin (PTS), so both plugins can't coexist on the box

## Usage
- Play/pause to start timeshift
- Stop to stop timeshift
- Fast forward/backward (left, right)
- Channel up/down for intelligent jump

## Links
- Feed: https://gemfury.com/dream-alpha
